#!/usr/bin/env python3
"""Synthetic self-test of the pass-1 vectorised click-merge / D_n construction."""
import os, sys, json, subprocess, shutil
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, "_selftest")
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)

rng = np.random.default_rng(7)
rows = []
# 3 rats x 300 trials, random Poisson-ish clicks, some with a stereo first pair
for r in range(3):
    for t in range(300):
        rate = 20 + 20 * rng.random()
        dur = 0.2 + rng.random()
        nl = rng.poisson(rate * dur); nr = rng.poisson(rate * dur)
        tl = np.sort(rng.random(nl) * dur); tr = np.sort(rng.random(nr) * dur)
        if t % 3 == 0 and nl and nr:      # inject an exact stereo first pair
            tl = np.concatenate([[0.0], tl]); tr = np.concatenate([[0.0], tr])
        rows.append(dict(rat_id=f"R{r}", trial_idx=t,
                         click_times_L=tl.tolist(), click_times_R=tr.tolist(),
                         choice_R=int(rng.random() < 0.5), correct=1,
                         stim_duration_s=dur, gamma=float(rng.choice([-2., -1., -0.5, 0., 0.5, 1., 2.])),
                         reward_rule=int(rng.random() < 0.5)))

tbl = pa.Table.from_pylist(rows)
src = os.path.join(TMP, "syn.parquet")
pq.write_table(tbl, src, row_group_size=137)

env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
           MKL_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
subprocess.run([sys.executable, os.path.join(HERE, "pass1_extract.py"), src,
                os.path.join(TMP, "chunks"), "97"], check=True, env=env)

# ---- naive reference implementation ----
ref = {}
for i, row in enumerate(rows):
    tl = list(row["click_times_L"]); tr = list(row["click_times_R"])
    if tl and tr and abs(tl[0] - tr[0]) < 1e-7:
        tl = tl[1:]; tr = tr[1:]
    ev = sorted([(t, 0) for t in tl] + [(t, 1) for t in tr])
    if len(ev) < 20:
        continue
    s = [1 if e[1] == 1 else -1 for e in ev[:20]]
    ref[(row["rat_id"], row["trial_idx"])] = np.cumsum(s)

import glob
got = {}
meta = json.load(open(os.path.join(TMP, "chunks", "pass1_meta.json")))
inv = {v: k for k, v in meta["rat_lookup"].items()}
for f in sorted(glob.glob(os.path.join(TMP, "chunks", "chunk_*.npz"))):
    z = np.load(f)
    for k in range(len(z["rat"])):
        got[(inv[int(z["rat"][k])], int(z["trial_idx"][k]))] = z["D"][k]

assert set(got) == set(ref), (len(got), len(ref), list(set(got) ^ set(ref))[:5])
bad = [k for k in ref if not np.array_equal(np.asarray(ref[k]), np.asarray(got[k], dtype=int))]
print(f"trials compared: {len(ref)}   mismatches: {len(bad)}")
assert not bad, bad[:5]
print("stereo dropped:", meta["n_dropped_stereo"], " qualifying:", meta["n_qualifying"],
      " seen:", meta["n_trials_seen"])
print("SELFTEST PASS")
