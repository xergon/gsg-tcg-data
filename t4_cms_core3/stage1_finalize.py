"""STAGE 1b — merge the per-file CORE3 parts into one parquet and write SUMMARY_sim.json."""
from __future__ import annotations

import glob
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
OUT = HERE / "T4_HOJD_CMS2011A_CORE3_v1_features_SIM.parquet"

parts = sorted(glob.glob(str(HERE / "sim" / "parts" / "*.parquet")))
print(f"[finalize] {len(parts)} parts")

schema = pq.ParquetFile(parts[0]).schema_arrow
writer = pq.ParquetWriter(OUT, schema, compression="snappy")
n_rows = 0
per_file = []
for p in parts:
    t = pq.read_table(p)
    if t.schema != schema:
        raise SystemExit(f"schema drift in {p}")
    writer.write_table(t)
    n_rows += t.num_rows
    per_file.append({
        "part": Path(p).name,
        "n_jets": t.num_rows,
        "source_filename": t["source_filename"][0].as_py(),
        "source_subdataset": t["source_subdataset"][0].as_py(),
        "source_file_sha256": t["source_file_sha256"][0].as_py(),
    })
    del t
writer.close()
print(f"[finalize] wrote {OUT.name}: {n_rows} rows, {OUT.stat().st_size/1e6:.1f} MB")

sha = hashlib.sha256()
with open(OUT, "rb") as fh:
    while (b := fh.read(8 << 20)):
        sha.update(b)
sha = sha.hexdigest()

by_sub: dict[str, int] = {}
for r in per_file:
    by_sub[r["source_subdataset"]] = by_sub.get(r["source_subdataset"], 0) + r["n_jets"]

summary = {
    "dataset": "T4 HOJD CMS 2011A CORE3 v1 — SIM (detector-level Pythia6 QCD) leg",
    "convention": "PtYPhiM",
    "convention_note": (
        "Per ChatGPT thread T4's ruling of 2026-07-24: PtYPhiM is canonical — the MOD "
        "field is rapidity y (not pseudorapidity), matching EnergyFlow's hadronic "
        "coordinate convention. Four-vectors are built as mT=sqrt(pt^2+m^2), "
        "E=mT*cosh(y), px=pt*cos(phi), py=pt*sin(phi), pz=mT*sinh(y). Edge behavior: "
        "n_pfc_selected==1 -> raw PFC mass; n_pfc_selected==0 -> 0.0."
    ),
    "extractor": "t4_hojd_extractor.py (T4 canonical, used verbatim and unmodified)",
    "pfc_selection": "vertex == 0 AND pt >= 0.5 GeV; no JEC applied to individual PFCs",
    "weight": "weight_nb = raw MOD jets_f['weight'] in nanobarns; no EnergyFlow k-factor",
    "n_files": len(per_file),
    "n_jets": n_rows,
    "n_jets_by_subdataset": by_sub,
    "parquet_filename": OUT.name,
    "parquet_sha256": sha,
    "parquet_bytes": OUT.stat().st_size,
    "columns": [f.name for f in schema],
    "n_columns": len(schema),
    "source": {
        "records": [
            {"doi": "10.5281/zenodo.3341498", "zenodo_record": "3341498",
             "title": "CMS 2011A Simulation | Pythia 6 QCD 300-470 | pT > 375 GeV | MOD HDF5",
             "subdataset": "QCD300to470", "pthat_min_GeV": 300.0, "pthat_max_GeV": 470.0},
            {"doi": "10.5281/zenodo.3341500", "zenodo_record": "3341500",
             "title": "CMS 2011A Simulation | Pythia 6 QCD 170-300 | pT > 375 GeV | MOD HDF5",
             "subdataset": "QCD170to300", "pthat_min_GeV": 170.0, "pthat_max_GeV": 300.0},
        ],
        "files_used": (
            "SIM* (detector-level) files only. The GEN* files in the same records carry "
            "no `pfcs` dataset and no jec/jet_area/jet_max_nef/npv/quality columns, so the "
            "frozen 33-column HOJD schema is not computable from them."
        ),
        "integrity": "every raw .h5 verified against the Zenodo-published MD5 before parsing",
    },
    "license": "CC-BY-4.0",
    "date_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "per_file": per_file,
}
(HERE / "SUMMARY_sim.json").write_text(json.dumps(summary, indent=1))
print(f"[finalize] sha256={sha}")
print(f"[finalize] jets by subdataset: {by_sub}")
