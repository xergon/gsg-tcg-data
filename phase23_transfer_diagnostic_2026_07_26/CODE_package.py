#!/usr/bin/env python3
"""Shard + manifest + provenance for the Phase-23 transfer diagnostic."""
import os, sys, hashlib, shutil, subprocess
import numpy as np, pandas as pd

SCRATCH = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SCRATCH, "phase23_transfer_diagnostic_2026_07_26")
KPC_M = 3.0856775814913673e19
MAXB = 900_000

# --- patch V_bar (was NaN for sparc: source table had no Vb2 column) --------
r = pd.read_csv(os.path.join(OUT, "per_ring_FULL.csv"))
r["V_bar_kms"] = np.sign(r["g_bar"]) * np.sqrt(
    np.abs(r["g_bar"]) * r["R_kpc"] * KPC_M) / 1000.0
r["V_obs_kms"] = np.sign(r["g_obs"]) * np.sqrt(
    np.abs(r["g_obs"]) * r["R_kpc"] * KPC_M) / 1000.0
r.to_csv(os.path.join(OUT, "per_ring_FULL.csv"), index=False)

# --- shard ------------------------------------------------------------------
def shard(path, stem):
    df = pd.read_csv(path)
    hdr = ",".join(df.columns) + "\n"
    total = os.path.getsize(path)
    if total <= MAXB:
        return [os.path.basename(path)]
    nsh = int(np.ceil(total / (MAXB * 0.80)))
    parts, bounds = [], np.array_split(np.arange(len(df)), nsh)
    for i, idx in enumerate(bounds, 1):
        p = os.path.join(OUT, f"{stem}_shard{i:02d}.csv")
        df.iloc[idx].to_csv(p, index=False)
        assert os.path.getsize(p) < MAXB, (p, os.path.getsize(p))
        parts.append(os.path.basename(p))
    os.remove(path)
    return parts

ring_parts = shard(os.path.join(OUT, "per_ring_FULL.csv"), "per_ring")
gal_parts = shard(os.path.join(OUT, "per_galaxy.csv"), "per_galaxy")
print("ring shards:", ring_parts, "galaxy shards:", gal_parts)

# --- copy the frozen inputs used --------------------------------------------
shutil.copy(os.path.join(SCRATCH, "little_things_sample.yaml"),
            os.path.join(OUT, "INPUT_little_things_sample.yaml"))
for s in ("build_tables.py", "analyze.py", "package.py"):
    shutil.copy(os.path.join(SCRATCH, s), os.path.join(OUT, "CODE_" + s))

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

rows = []
for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    if not os.path.isfile(p) or f == "MANIFEST.csv":
        continue
    n = 0
    if f.endswith(".csv"):
        n = sum(1 for _ in open(p)) - 1
    rows.append(dict(filename=f, bytes=os.path.getsize(p), rows=n, sha256=sha(p)))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "MANIFEST.csv"), index=False)
print(pd.DataFrame(rows).to_string(index=False))

# --- source checksums --------------------------------------------------------
SRC = [
 "/Users/resorb/Documents/Claude Sessions/Transaction Calculus/data/sparc/SPARC_Lelli2016c.mrt",
 "/Users/resorb/Documents/Claude Sessions/Transaction Calculus/data/sparc/MassModels_Lelli2016c.mrt",
 "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/phase23_external_heldout_sources_2026_07_22/C_things_littlethings/things_deblok2008_massmodels_tidy.csv",
 "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/phase23_external_heldout_sources_2026_07_22/C_things_littlethings/walter2008_table1_things_sample.csv",
 "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/phase23_external_heldout_sources_2026_07_22/B_little_things_oh2015/oh2015_table1_galaxy_properties.csv",
 "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/phase23_external_heldout_sources_2026_07_22/B_little_things_oh2015/oh2015_table2_massmodel_results.csv",
 "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/phase23_locked_evaluator_spec_2026_07_22/phase23_locked_evaluator.py",
 os.path.join(SCRATCH, "little_things_sample.yaml"),
]
with open(os.path.join(OUT, "SOURCE_CHECKSUMS.txt"), "w") as fh:
    for p in SRC:
        fh.write(f"{sha(p)}  {os.path.getsize(p):>10d}  {p}\n")
print(open(os.path.join(OUT, "SOURCE_CHECKSUMS.txt")).read())
