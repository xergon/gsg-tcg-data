#!/usr/bin/env python3
"""Diagnostic: does the >=20-informative-click trial cut depend on |gamma|?

Reads only the scalar columns (cheap), so it does not touch the click-time lists.
n_informative = n_clicks_L + n_clicks_R - 2*[the trial opened with a stereo pair];
the stereo flag is not available here, so BOTH bounds are reported:
  optimistic  n_clicks_total >= 20   (no stereo pair)
  strict      n_clicks_total >= 22   (stereo pair present, i.e. 2 clicks removed)
Pass 1 gives the exact overall qualifying count for calibration.
"""
import os, sys, json, time
import numpy as np
import pyarrow.parquet as pq

SRC, WORK = sys.argv[1], sys.argv[2]
cuts = json.load(open(os.path.join(WORK, "tercile_cutpoints.json")))
c1, c2 = cuts["cut1_abs_gamma_q33"], cuts["cut2_abs_gamma_q67"]

pf = pq.ParquetFile(SRC)
tot_by_g = {}; q20_by_g = {}; q22_by_g = {}
terc_tot = np.zeros(3); terc_q20 = np.zeros(3); terc_q22 = np.zeros(3)
dur_sum = np.zeros(3); dur_n = np.zeros(3)
t0 = time.time()
for b in pf.iter_batches(batch_size=1_000_000,
                         columns=["gamma", "n_clicks_L", "n_clicks_R", "stim_duration_s"]):
    g = np.abs(np.asarray(b.column("gamma").to_numpy(zero_copy_only=False), dtype=np.float64))
    nc = (np.asarray(b.column("n_clicks_L").to_numpy(zero_copy_only=False), dtype=np.int64)
          + np.asarray(b.column("n_clicks_R").to_numpy(zero_copy_only=False), dtype=np.int64))
    du = np.asarray(b.column("stim_duration_s").to_numpy(zero_copy_only=False), dtype=np.float64)
    ok = np.isfinite(g)
    g, nc, du = g[ok], nc[ok], du[ok]
    gr = np.round(g, 6)
    for v, c in zip(*np.unique(gr, return_counts=True)):
        tot_by_g[float(v)] = tot_by_g.get(float(v), 0) + int(c)
    for v, c in zip(*np.unique(gr[nc >= 20], return_counts=True)):
        q20_by_g[float(v)] = q20_by_g.get(float(v), 0) + int(c)
    for v, c in zip(*np.unique(gr[nc >= 22], return_counts=True)):
        q22_by_g[float(v)] = q22_by_g.get(float(v), 0) + int(c)
    t = np.where(g <= c1, 0, np.where(g <= c2, 1, 2))
    terc_tot += np.bincount(t, minlength=3)
    terc_q20 += np.bincount(t[nc >= 20], minlength=3)
    terc_q22 += np.bincount(t[nc >= 22], minlength=3)
    dur_sum += np.bincount(t, weights=np.nan_to_num(du), minlength=3)
    dur_n += np.bincount(t[np.isfinite(du)], minlength=3)

out = {
 "note": ("Qualification-rate diagnostic computed on ALL trials in the release, using "
          "the tercile cut points frozen in pass 2. Bounds bracket the unknown stereo "
          "removal per trial."),
 "tercile_cutpoints_used": [c1, c2],
 "all_trials_per_tercile": [int(x) for x in terc_tot],
 "qualify_rate_per_tercile_optimistic_ge20_clicks": [float(a / b) if b else None
                                                     for a, b in zip(terc_q20, terc_tot)],
 "qualify_rate_per_tercile_strict_ge22_clicks": [float(a / b) if b else None
                                                 for a, b in zip(terc_q22, terc_tot)],
 "mean_stim_duration_s_per_tercile": [float(a / b) if b else None
                                      for a, b in zip(dur_sum, dur_n)],
 "per_abs_gamma_value": sorted(
     [{"abs_gamma": k, "n_trials": v,
       "qualify_rate_ge20": (q20_by_g.get(k, 0) / v) if v else None,
       "qualify_rate_ge22": (q22_by_g.get(k, 0) / v) if v else None}
      for k, v in tot_by_g.items()], key=lambda d: -d["n_trials"])[:40],
 "wall_seconds": time.time() - t0,
}
with open(os.path.join(WORK, "qualification_diagnostic.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({k: out[k] for k in
                  ("all_trials_per_tercile",
                   "qualify_rate_per_tercile_optimistic_ge20_clicks",
                   "qualify_rate_per_tercile_strict_ge22_clicks",
                   "mean_stim_duration_s_per_tercile")}, indent=1))
