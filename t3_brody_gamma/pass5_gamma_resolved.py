#!/usr/bin/env python3
"""Sensitivity: |gamma| is heavily discretised and BOTH frozen tercile cut points
(1.5 and 2.5) land exactly on high-mass values, so the tercile membership of those
values depends on the tie rule. This script reports

  (a) the same horizons under the ALTERNATIVE tie rule (strict <), and
  (b) the horizon computed separately for each of the dominant single |gamma|
      values, which sidesteps the tie question entirely.

Same estimator as pass 2 (odd/even symmetric 2-fold, Jeffreys, 1/e crossing).
"""
import os, sys, json, glob, time
import numpy as np

WORK = sys.argv[1]
NMAX, NBIN, MINT, SEED, NBOOT = 20, 41, 200, 20260724, 2000
INV_E = float(np.exp(-1.0))
t0 = time.time()

acc = {k: [] for k in ("rat", "parity", "choice", "gamma", "D")}
for f in sorted(glob.glob(os.path.join(WORK, "chunks", "chunk_*.npz"))):
    z = np.load(f)
    for k in acc:
        acc[k].append(z[k])
rat = np.concatenate(acc["rat"]).astype(np.int64)
fold = np.concatenate(acc["parity"]).astype(np.int64)
choice = np.concatenate(acc["choice"]).astype(np.float64)
gamma = np.abs(np.concatenate(acc["gamma"]).astype(np.float64))
D = np.concatenate(acc["D"]); del acc

nc = int(rat.max()) + 1
qual = np.where(np.bincount(rat, minlength=nc) >= MINT)[0]
keep = np.isin(rat, qual)
rat, fold, choice, gamma, D = rat[keep], fold[keep], choice[keep], gamma[keep], D[keep]
remap = -np.ones(nc, np.int64); remap[qual] = np.arange(len(qual))
rat = remap[rat]; R = len(qual)
Dp = D.astype(np.int64) + NMAX
print(f"loaded R={R} N={len(rat):,} {time.time()-t0:.0f}s", flush=True)


def horizon(E):
    E = np.asarray(E, float); den = E[0] - E[-1]
    if not np.isfinite(den) or den <= 0:
        return np.nan
    q = (E - E[-1]) / den
    for i in range(1, NMAX):
        if q[i] <= INV_E:
            q0, q1 = q[i - 1], q[i]
            return float(i + ((q0 - INV_E) / (q0 - q1) if q0 != q1 else 0.0) - 1.0)
    return np.nan


def run(strat, S, names):
    base = (((rat * S + strat) * 2 + fold) * NMAX) * NBIN
    SZ = R * S * 2 * NMAX * NBIN
    tot = np.zeros(SZ); pos = np.zeros(SZ)
    for n in range(NMAX):
        idx = base + n * NBIN + Dp[:, n]
        tot += np.bincount(idx, minlength=SZ)
        pos += np.bincount(idx, weights=choice, minlength=SZ)
    tot = tot.reshape(R, S, 2, NMAX, NBIN); pos = pos.reshape(R, S, 2, NMAX, NBIN)
    res = {}
    rng = np.random.default_rng(SEED)
    for s in range(S):
        t, p = tot[:, s], pos[:, s]
        CE = np.zeros((R, NMAX)); NH = np.zeros((R, NMAX))
        for f in range(2):
            ph = np.clip((p[:, 1 - f] + .5) / (t[:, 1 - f] + 1.), 1e-15, 1 - 1e-15)
            CE += -(p[:, f] * np.log2(ph) + (t[:, f] - p[:, f]) * np.log2(1 - ph)).sum(-1)
            NH += t[:, f].sum(-1)
        ok = NH[:, 0] >= MINT
        if ok.sum() < 30:
            res[names[s]] = {"H": None, "n_rats": int(ok.sum()),
                             "n_trials": float(NH[:, 0].sum()),
                             "note": "fewer than 30 rats with >=200 trials in this stratum"}
            continue
        H = horizon(CE[ok].sum(0) / NH[ok].sum(0))
        io = np.where(ok)[0]
        rng2 = np.random.default_rng(SEED + 3)
        bb = np.empty(NBOOT)
        for b in range(NBOOT):
            ss = io[rng2.integers(0, len(io), len(io))]
            bb[b] = horizon(CE[ss].sum(0) / NH[ss].sum(0))
        res[names[s]] = {"H": H, "n_rats": int(ok.sum()), "n_trials": float(NH[ok, 0].sum()),
                         "ci95": [float(np.nanpercentile(bb, 2.5)),
                                  float(np.nanpercentile(bb, 97.5))],
                         "boot_sd": float(np.nanstd(bb))}
    return res


out = {"note": "Sensitivity to the tercile tie rule and to |gamma| resolved value by value."}

# (a) alternative tie rule: strict <
c1, c2 = 1.5, 2.5
alt = np.where(gamma < c1, 0, np.where(gamma < c2, 1, 2))
out["alt_tie_rule_strict_lt"] = {
    "rule": "T_low: |g| < 1.5 ; T_mid: 1.5 <= |g| < 2.5 ; T_high: |g| >= 2.5",
    "trial_counts": [int(x) for x in np.bincount(alt, minlength=3)],
    "horizons": run(alt, 3, ["lowgamma", "midgamma", "highgamma"])}
print("alt tie:", json.dumps(out["alt_tie_rule_strict_lt"]["horizons"], default=float), flush=True)

# (b) per single |gamma| value, dominant values
gr = np.round(gamma, 6)
vals, cnts = np.unique(gr, return_counts=True)
pick = vals[np.argsort(-cnts)][:10]
pick = np.sort(pick)
sid = np.full(len(gr), len(pick), np.int64)
for i, v in enumerate(pick):
    sid[gr == v] = i
names = [f"absgamma_{v:g}" for v in pick] + ["other"]
out["per_absgamma_value"] = {"values": [float(v) for v in pick],
                             "horizons": run(sid, len(pick) + 1, names)}
print("per value:", json.dumps(out["per_absgamma_value"]["horizons"], default=float), flush=True)
out["wall_seconds"] = time.time() - t0
with open(os.path.join(WORK, "gamma_resolved_sensitivity.json"), "w") as f:
    json.dump(out, f, indent=1, default=float)
print("PASS5 DONE", f"{time.time()-t0:.0f}s")
