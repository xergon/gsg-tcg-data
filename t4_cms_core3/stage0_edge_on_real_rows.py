"""STAGE 0 (confirmatory) — verify the n_pfc_selected==1 edge behavior on the
ACTUAL delivered rows, by re-reading the source HDF5 and comparing the emitted
pfc_mass_GeV against the raw PFC `m` field of the single surviving PFC.
"""
from __future__ import annotations

import glob
import subprocess
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from t4_hojd_extractor import compute_pfc_features  # noqa: E402

WORK = HERE / "work"

# collect every delivered row with n_pfc_selected <= 1
lo = []
for p in sorted(glob.glob(str(HERE / "sim" / "parts" / "*.parquet"))):
    d = pq.read_table(p, columns=["source_filename", "jet_row_id",
                                  "n_pfc_selected", "pfc_mass_GeV"]).to_pandas()
    lo.append(d[d["n_pfc_selected"] <= 1])
edge = pd.concat(lo, ignore_index=True)
print(f"delivered rows with n_pfc_selected <= 1: {len(edge)}")
if edge.empty:
    print("EDGE CASE UNREACHABLE — nothing to verify")
    raise SystemExit(0)
print(edge.to_string(index=False))

# verify one source file's worth (the one with the most edge rows)
target = edge["source_filename"].value_counts().index[0]
sub = edge[edge["source_filename"] == target]
url = ("https://zenodo.org/api/records/3341498/files/" + target + "/content")
raw = WORK / target
if not raw.exists():
    print(f"\nfetching {target} ...")
    subprocess.run(["curl", "-sSL", "--fail", "--retry", "5", "--retry-delay", "3", "-C", "-", "-o", str(raw), url], check=True)

with h5py.File(raw, "r") as f:
    pfcs = f["pfcs"][:]
    pidx = f["pfcs_index"][:]
    cols = list(f["pfcs"].attrs["cols"])
cm = {(c.decode() if isinstance(c, bytes) else c): i for i, c in enumerate(cols)}

ok = True
for _, r in sub.iterrows():
    i = int(r["jet_row_id"])
    jp = pfcs[int(pidx[i]):int(pidx[i + 1])]
    sel = (jp[:, cm["vertex"]] == 0) & (jp[:, cm["pt"]] >= 0.5)
    keep = jp[sel]
    res = compute_pfc_features(jp, cols)
    raw_m = float(keep[0, cm["m"]])
    match = np.isclose(res["pfc_mass_GeV"], raw_m, rtol=1e-12, atol=0.0)
    ok &= bool(match) and res["n_pfc_selected"] == 1
    print(f"  jet {i}: n_sel={res['n_pfc_selected']} "
          f"delivered={r['pfc_mass_GeV']!r} recomputed={res['pfc_mass_GeV']!r} "
          f"raw_m={raw_m!r} pt={keep[0, cm['pt']]:.3f} y={keep[0, cm['y']]:.4f} "
          f"rtol1e-12_match={match}")

raw.unlink()
print("\nEDGE CHECK ON REAL DELIVERED ROWS:", "PASS" if ok else "FAIL")
