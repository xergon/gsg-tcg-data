#!/usr/bin/env python3
"""
T3 gamma-stratified held-out entropy reduction -- PASS 1.

Streams the 2.13 GB Brody Poisson-clicks parquet and emits, per chunk, a compact
record of the signed prefix evidence D_1..D_20 for every QUALIFYING trial.

Frozen procedure (T3):
  * left click s = -1, right click s = +1
  * if |first_L - first_R| < 1e-7 s -> drop that simultaneous stereo pair
  * sort remaining clicks by time, retain first 20 informative clicks
  * D_n = sum_{k<=n} s_k, n = 1..20
"""
import os, sys, json, time, hashlib
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


def to_f64(arr):
    """Arrow scalar column -> float64 numpy with nulls as NaN (dtype-agnostic)."""
    nullmask = np.asarray(arr.is_null())
    fill = False if pa.types.is_boolean(arr.type) else 0
    v = np.asarray(pc.fill_null(arr, fill).to_numpy(zero_copy_only=False),
                   dtype=np.float64)
    if nullmask.any():
        v[nullmask] = np.nan
    return v

KEEP_PER_SIDE = 21          # 20 informative + 1 possibly-dropped stereo click
NMAX = 20
STEREO_TOL = 1e-7

SRC = sys.argv[1]
OUT = sys.argv[2]
BATCH = int(sys.argv[3]) if len(sys.argv) > 3 else 400_000

os.makedirs(OUT, exist_ok=True)


def truncate_list(offsets, values, k):
    """Keep first k entries of each list. Returns (new_offsets, taken_values, kept_lens)."""
    lens = np.diff(offsets)
    keep = np.minimum(lens, k)
    new_off = np.empty(len(keep) + 1, dtype=np.int64)
    new_off[0] = 0
    np.cumsum(keep, out=new_off[1:])
    total = int(new_off[-1])
    if total == 0:
        return new_off, np.empty(0, dtype=values.dtype), keep
    shift = offsets[:-1] - new_off[:-1]
    idx = np.arange(total, dtype=np.int64) + np.repeat(shift, keep)
    return new_off, values[idx], keep


def flat_list(col):
    """Array of list<double> -> (absolute offsets int64, child values float64).

    pyarrow returns ABSOLUTE offsets into the (unsliced) child array, verified
    for both whole and sliced ListArrays, so no rebasing is required.
    """
    if hasattr(col, "num_chunks"):
        col = col.combine_chunks()
    offs = np.asarray(col.offsets, dtype=np.int64)
    vals = np.asarray(col.values, dtype=np.float64)
    return offs, vals


def main():
    pf = pq.ParquetFile(SRC)
    cols = ["rat_id", "trial_idx", "click_times_L", "click_times_R",
            "choice_R", "gamma", "reward_rule"]
    schema_names = [f.name for f in pf.schema_arrow]
    for c in cols:
        assert c in schema_names, f"missing column {c} in {schema_names}"

    rat_lookup = {}
    meta = {"chunks": [], "n_trials_seen": 0, "n_qualifying": 0,
            "n_dropped_stereo": 0, "n_short": 0, "n_bad_choice": 0,
            "n_bad_gamma": 0, "clicklen_hist": np.zeros(64, dtype=np.int64)}
    t0 = time.time()
    ci = 0
    for batch in pf.iter_batches(batch_size=BATCH, columns=cols):
        n = batch.num_rows
        meta["n_trials_seen"] += n

        dcol = batch.column("rat_id").dictionary_encode()
        loc_vals = dcol.dictionary.to_pylist()
        loc_idx = np.asarray(dcol.indices.to_numpy(zero_copy_only=False), dtype=np.int64)
        loc_map = np.empty(len(loc_vals), dtype=np.int32)
        for j, r in enumerate(loc_vals):
            c = rat_lookup.get(r)
            if c is None:
                c = len(rat_lookup)
                rat_lookup[r] = c
            loc_map[j] = c
        rcode = loc_map[loc_idx]
        del dcol, loc_idx

        tidx = to_f64(batch.column("trial_idx")).astype(np.int64)
        chR = to_f64(batch.column("choice_R"))
        gam = to_f64(batch.column("gamma"))
        rw = to_f64(batch.column("reward_rule"))
        rw = np.where(np.isnan(rw), -99, rw)

        offL, valL = flat_list(batch.column("click_times_L"))
        offR, valR = flat_list(batch.column("click_times_R"))

        nL_full = np.diff(offL)
        nR_full = np.diff(offR)
        tot_full = nL_full + nR_full
        h = np.bincount(np.minimum(tot_full, 63), minlength=64)
        meta["clicklen_hist"] += h

        noL, tL, keepL = truncate_list(offL, valL, KEEP_PER_SIDE)
        noR, tR, keepR = truncate_list(offR, valR, KEEP_PER_SIDE)

        # --- stereo first-pair removal -------------------------------------
        has_both = (keepL > 0) & (keepR > 0)
        firstL = np.full(n, np.nan)
        firstR = np.full(n, np.nan)
        firstL[keepL > 0] = tL[noL[:-1][keepL > 0]]
        firstR[keepR > 0] = tR[noR[:-1][keepR > 0]]
        stereo = has_both & (np.abs(firstL - firstR) < STEREO_TOL)
        meta["n_dropped_stereo"] += int(stereo.sum())

        dropL = np.zeros(len(tL), dtype=bool)
        dropR = np.zeros(len(tR), dtype=bool)
        if stereo.any():
            dropL[noL[:-1][stereo]] = True
            dropR[noR[:-1][stereo]] = True

        tidL = np.repeat(np.arange(n, dtype=np.int64), keepL)
        tidR = np.repeat(np.arange(n, dtype=np.int64), keepR)

        times = np.concatenate([tL[~dropL], tR[~dropR]])
        # side code 0 = L (s=-1), 1 = R (s=+1); used as deterministic tiebreak
        sidec = np.concatenate([np.zeros((~dropL).sum(), dtype=np.int8),
                                np.ones((~dropR).sum(), dtype=np.int8)])
        tid = np.concatenate([tidL[~dropL], tidR[~dropR]])
        del tidL, tidR

        # sort by (trial, time); np.lexsort is STABLE and the L clicks were
        # concatenated first, so exact time ties break L-before-R deterministically
        order = np.lexsort((times, tid))
        tid = tid[order]; sidec = sidec[order]
        del times, order

        cnt = np.bincount(tid, minlength=n)
        starts = np.zeros(n + 1, dtype=np.int64)
        np.cumsum(cnt, out=starts[1:])
        rank = np.arange(len(tid), dtype=np.int64) - np.repeat(starts[:-1], cnt)

        qual_len = cnt >= NMAX
        good_choice = np.isin(chR, (0.0, 1.0))
        good_gamma = np.isfinite(gam)
        qual = qual_len & good_choice & good_gamma
        meta["n_short"] += int((~qual_len).sum())
        meta["n_bad_choice"] += int((~good_choice).sum())
        meta["n_bad_gamma"] += int((~good_gamma).sum())

        sel = (rank < NMAX) & qual[tid]
        s = np.where(sidec[sel] == 1, np.int8(1), np.int8(-1)).reshape(-1, NMAX)
        D = np.cumsum(s.astype(np.int16), axis=1).astype(np.int8)
        del s, sel, rank, tid, sidec, cnt, starts

        nq = D.shape[0]
        assert nq == int(qual.sum()), (nq, int(qual.sum()))
        meta["n_qualifying"] += nq

        if nq:
            np.savez(os.path.join(OUT, f"chunk_{ci:04d}.npz"),
                     rat=rcode[qual].astype(np.int16),
                     parity=(tidx[qual] % 2).astype(np.int8),
                     choice=chR[qual].astype(np.int8),
                     gamma=gam[qual].astype(np.float32),
                     reward_rule=rw[qual].astype(np.int8),
                     trial_idx=tidx[qual].astype(np.int64),
                     D=D)
            meta["chunks"].append(f"chunk_{ci:04d}.npz")
        ci += 1
        if ci % 10 == 0:
            print(f"  batch {ci}: seen={meta['n_trials_seen']:,} "
                  f"qual={meta['n_qualifying']:,} t={time.time()-t0:.0f}s", flush=True)

    meta["clicklen_hist"] = meta["clicklen_hist"].tolist()
    meta["rat_lookup"] = {str(k): int(v) for k, v in rat_lookup.items()}
    meta["wall_seconds"] = time.time() - t0
    with open(os.path.join(OUT, "pass1_meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("PASS1 DONE", meta["n_trials_seen"], meta["n_qualifying"],
          f"{meta['wall_seconds']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
