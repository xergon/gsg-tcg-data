#!/usr/bin/env python3
"""End-to-end smoke test of pass2 on synthetic data with a KNOWN structure.

Rat choices are generated from a sigmoid on D_k for a k that depends on the
|gamma| tercile, so the recovered horizons should order the way the generator
was built. This validates plumbing, not physiology.
"""
import os, sys, json, subprocess, shutil, glob
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, "_selftest2")
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(os.path.join(TMP, "chunks"))

rng = np.random.default_rng(11)
GAMMAS = np.array([0.0, 0.5, 1.0, 2.0, 4.0])
rows = []
for r in range(40):
    for t in range(900):
        dur = 1.2
        rate = 40.0
        nl = rng.poisson(rate * dur / 2); nr = rng.poisson(rate * dur / 2)
        tl = np.sort(rng.random(nl) * dur); tr = np.sort(rng.random(nr) * dur)
        tl = np.concatenate([[0.0], tl]); tr = np.concatenate([[0.0], tr])
        g = float(rng.choice(GAMMAS)) * rng.choice([-1., 1.])
        ev = sorted([(x, -1) for x in tl[1:]] + [(x, 1) for x in tr[1:]])
        s = np.array([e[1] for e in ev[:20]])
        if len(s) < 20:
            continue
        D = np.cumsum(s)
        k = {0: 20, 1: 8, 2: 3}[0 if abs(g) <= 0.25 else (1 if abs(g) <= 1.5 else 2)]
        p = 1.0 / (1.0 + np.exp(-0.8 * D[k - 1]))
        rows.append(dict(rat_id=f"R{r}", trial_idx=t,
                         click_times_L=tl.tolist(), click_times_R=tr.tolist(),
                         choice_R=int(rng.random() < p), correct=1,
                         stim_duration_s=dur, gamma=g,
                         reward_rule=int(rng.random() < 0.5)))

src = os.path.join(TMP, "syn2.parquet")
pq.write_table(pa.Table.from_pylist(rows), src, row_group_size=5000)
env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
           MKL_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
subprocess.run([sys.executable, os.path.join(HERE, "pass1_extract.py"), src,
                os.path.join(TMP, "chunks"), "20000"], check=True, env=env)
subprocess.run([sys.executable, os.path.join(HERE, "pass2_horizons.py"), TMP],
               check=True, env=env)
res = json.load(open(os.path.join(TMP, "pass2_raw_results.json")))
for k in ("primary|all|allgamma", "primary|all|lowgamma", "primary|all|midgamma",
          "primary|all|highgamma", "ctrl_choice_shuffle_s0|all|allgamma",
          "ctrl_trial_mismatch|all|allgamma"):
    r = res[k]
    print(f"{k:38s} H_pool={r['H_pooled']}  H_med={r.get('H_rat_median')}  "
          f"dE={r['E1_minus_E20_bits']:.4f}  nrats={r['n_rats_used']}")
json.dump({"parquet_sha256": "SYNTHETIC"}, open(os.path.join(TMP, "RELEASE_SUMMARY.json"), "w"))
json.dump({"sha256": "SYNTHETIC", "bytes": 0}, open(os.path.join(TMP, "input_sha256.json"), "w"))
for fn in ("pass1_extract.py", "pass2_horizons.py", "pass3_finalize.py"):
    shutil.copy(os.path.join(HERE, fn), os.path.join(TMP, fn))
subprocess.run([sys.executable, os.path.join(HERE, "pass3_finalize.py"), TMP,
                "9.99", "1s"], check=True, env=env)
print("outputs:", sorted(os.path.basename(p) for p in glob.glob(os.path.join(TMP, "*"))))
print("SELFTEST2 DONE")
