#!/usr/bin/env python3
"""Merge the 8 v2 chunk parts into transpositions_2014-07_v2.npz (contract emitted separately)."""
import numpy as np, json, os, sys, hashlib

D = os.path.dirname(os.path.abspath(__file__))
NP = 8
PARTS = [os.path.join(D, "part2_%d.npz" % i) for i in range(NP)]
OUT = os.path.join(D, "transpositions_2014-07_v2.npz")

COLS = {
    "state": np.int64, "state_fen5": np.int64, "repetition_ledger_hash": np.int64,
    "hist1": np.int64, "hist4": np.int64, "nxt": np.int64,
    "gidx": np.int32, "eband": np.int8, "tclass": np.int8, "ply": np.int8,
    "current_position_occurrence_count": np.uint8,
    "can_claim_threefold_now": np.bool_,
    "can_claim_threefold_after_one_move": np.bool_,
    # v2 additions
    "state_hash128_lo": np.int64, "state_hash128_hi": np.int64,
    "player_hash": np.int64, "player_fold": np.uint8,
}

metas, meta2s, ns = [], [], []
for p in PARTS:
    with np.load(p) as z:
        m = z["meta"]; metas.append(m.tolist()); meta2s.append(z["meta2"].tolist())
        ns.append(int(m[1]))
        assert len(z["state"]) == int(m[1])
N = sum(ns)
TG = sum(m[0] for m in metas)
print("parts:", ns, "total records:", N, "total games:", TG, flush=True)

out = {k: np.empty(N, dtype=dt) for k, dt in COLS.items()}
off = 0
gof = 0
for p, n, m in zip(PARTS, ns, metas):
    with np.load(p) as z:
        for k in COLS:
            out[k][off:off + n] = z[k]
        out["gidx"][off:off + n] += gof
    off += n
    gof += m[0]
    print("  merged", os.path.basename(p), "records=%d gidx_offset_next=%d" % (n, gof), flush=True)
assert off == N and gof == TG

meta = np.array([TG, N, metas[0][2], metas[0][3],
                 sum(m[4] for m in metas), sum(m[5] for m in metas)], dtype=np.int64)
# meta2[0] = games having a move at ply index MAX_PLY (= records a ply-30-INCLUSIVE build adds)
# meta2[1] = per-chunk distinct-name counts are NOT globally unique; recomputed globally later, stored as -1
meta2 = np.array([sum(m[0] for m in meta2s), -1], dtype=np.int64)
print("meta ", meta.tolist())
print("meta2", meta2.tolist(), " (per-chunk name counts:", [m[1] for m in meta2s], ")")

np.savez_compressed(OUT, meta=meta, meta2=meta2, **out)
print("wrote", OUT, os.path.getsize(OUT), flush=True)

h = hashlib.sha256()
with open(OUT, "rb") as f:
    for b in iter(lambda: f.read(1 << 22), b""):
        h.update(b)
print("sha256", h.hexdigest())
json.dump({"bytes": os.path.getsize(OUT), "sha256": h.hexdigest(),
           "n_records": int(N), "n_games": int(TG),
           "meta": meta.tolist(), "meta2": meta2.tolist()},
          open(os.path.join(D, "merge2_result.json"), "w"), indent=2)
print("MERGE DONE")
