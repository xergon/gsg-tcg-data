"""STAGE 2b — verify the 32 non-mass columns against v0.1, then emit v0.2.

v0.2 == v0.1 with ONLY pfc_mass_GeV replaced by the recomputed PtYPhiM values.
Every other column is carried over from the v0.1 table itself (not recomputed),
so those columns are byte-identical by construction; the recomputation is used
purely as an independent CHECK that nothing beyond pfc_mass moved.
"""
from __future__ import annotations

import glob
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
V01 = HERE / "parity" / "v0_1.parquet"
OUT = HERE / "T4_HOJD_CMS2011_v0_2_features_CMS.parquet"

EXACT_COLS = ["fn", "rn", "lbn", "evn", "npv", "quality", "n_pfc_selected"]
RAW_COLS = ["jet_pt_GeV", "jet_eta", "jet_y", "jet_phi", "jet_m_GeV",
            "jec", "jet_area", "jet_max_nef", "weight_nb"]
PFC_COLS = ["pfc_pt_sum_GeV",
            "e2_beta_0p5", "e3_beta_0p5", "D2_beta_0p5",
            "e2_beta_1p0", "e3_beta_1p0", "D2_beta_1p0",
            "e2_beta_2p0", "e3_beta_2p0", "D2_beta_2p0"]


def main() -> int:
    parts = sorted(glob.glob(str(HERE / "cms" / "parts" / "*.parquet")))
    print(f"[stage2b] {len(parts)} part files")
    if len(parts) != 18:
        print(f"STOP: expected 18 CMS containers, found {len(parts)}")
        return 2

    rec = pd.concat([pq.read_table(p).to_pandas() for p in parts], ignore_index=True)
    print(f"[stage2b] recomputed rows: {len(rec)}")

    v = pq.read_table(V01).to_pandas()
    print(f"[stage2b] v0.1 rows: {len(v)}")
    if len(rec) != len(v):
        print(f"STOP: row count {len(rec)} != v0.1 {len(v)}")
        return 2

    # ---- align on jet_row_id ----
    if rec["jet_row_id"].duplicated().any() or v["jet_row_id"].duplicated().any():
        print("STOP: duplicate jet_row_id")
        return 2
    order = pd.Index(v["jet_row_id"])
    rec = rec.set_index("jet_row_id").reindex(order)
    if rec.isna().all(axis=1).any():
        print("STOP: some v0.1 jet_row_id absent from recomputation")
        return 2
    print("[stage2b] aligned 1:1 on jet_row_id")

    fails = []
    report = {}

    def chk_exact(col):
        a = v[col].values
        b = rec[col].values
        bad = int((a != b).sum())
        report[col] = {"rule": "exact", "mismatches": bad}
        if bad:
            fails.append((col, "exact", bad))

    def chk_close(col, rtol, atol):
        a = v[col].values.astype(np.float64)
        b = rec[col].values.astype(np.float64)
        both_nan = np.isnan(a) & np.isnan(b)
        ok = np.isclose(a, b, rtol=rtol, atol=atol, equal_nan=False) | both_nan
        bad = int((~ok).sum())
        fin = np.isfinite(a) & np.isfinite(b) & (a != 0)
        mx = float(np.max(np.abs((b[fin] - a[fin]) / a[fin]))) if fin.any() else 0.0
        report[col] = {"rule": f"rtol={rtol},atol={atol}",
                       "mismatches": bad, "max_rel_dev": mx}
        if bad:
            fails.append((col, f"rtol={rtol}", bad))

    for c in EXACT_COLS:
        chk_exact(c)
    for c in RAW_COLS:
        chk_close(c, 0.0, 0.0)          # bit-exact
    chk_close("corr_jet_pt_GeV", 1e-14, 1e-12)
    for c in PFC_COLS:
        chk_close(c, 1e-10, 1e-12)

    n_checked = len(EXACT_COLS) + len(RAW_COLS) + 1 + len(PFC_COLS)
    print(f"[stage2b] checked {n_checked} recomputed columns")
    if fails:
        print("STOP — non-mass columns changed:")
        for col, rule, n in fails:
            print(f"   {col} [{rule}]: {n} mismatches")
        (HERE / "stage2_column_check.json").write_text(json.dumps(report, indent=1))
        return 2
    print("[stage2b] ALL non-mass columns match v0.1 at the prior tolerances")

    # ---- pfc_mass delta ----
    old = v["pfc_mass_GeV"].values.astype(np.float64)
    new = rec["pfc_mass_GeV"].values.astype(np.float64)
    changed = old != new
    n_changed = int(changed.sum())
    nz = changed & (old != 0) & np.isfinite(old) & np.isfinite(new)
    rel = np.abs(new[nz] - old[nz]) / np.abs(old[nz])
    med_rel = float(np.median(rel)) if rel.size else 0.0
    print(f"[stage2b] pfc_mass_GeV changed in {n_changed}/{len(v)} rows "
          f"({100*n_changed/len(v):.2f}%), median rel change {med_rel:.6e}")

    # ---- emit v0.2: v0.1 with ONLY pfc_mass_GeV replaced ----
    tbl = pq.read_table(V01)
    idx = tbl.schema.get_field_index("pfc_mass_GeV")
    tbl2 = tbl.set_column(idx, tbl.schema.field(idx), pa.array(new, type=pa.float64()))
    pq.write_table(tbl2, OUT, compression="snappy")
    sha = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(f"[stage2b] wrote {OUT.name} sha256={sha} bytes={OUT.stat().st_size}")

    summary = {
        "n_rows": int(len(v)),
        "n_columns": int(tbl2.num_columns),
        "pfc_mass_changed_rows": n_changed,
        "pfc_mass_changed_frac": n_changed / len(v),
        "pfc_mass_median_rel_change": med_rel,
        "pfc_mass_p99_rel_change": float(np.percentile(rel, 99)) if rel.size else 0.0,
        "pfc_mass_max_rel_change": float(rel.max()) if rel.size else 0.0,
        "non_mass_column_check": report,
        "sha256": sha,
        "bytes": OUT.stat().st_size,
    }
    (HERE / "stage2_column_check.json").write_text(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
