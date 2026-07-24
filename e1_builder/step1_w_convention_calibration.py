#!/usr/bin/env python3
"""STEP 1 — W-convention calibration by reproduction. READ-ONLY on all inputs.

Rebuilds the Stage-E1 in-cohort galaxy-level quantities from raw SPARC under BOTH
candidate W-window conventions, and checks which one reproduces C-Triangle's own
delivered E1 design matrix.

  convention LOGLOG (stage_e1_reconstruct.py:175-176)
      grad = d ln g_bar / d ln R ;  L_b = R / max(|grad|, 1e-3)
  convention LINEAR (cat_aeff_ipr_scout.py:101-102)
      dg = d g_bar / d R ;          L_b = g_bar / |dg|

Writes step1_w_convention_calibration_result.json in this directory only.
"""
from __future__ import annotations

import json
import math
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.io import ascii

OUT = Path(__file__).resolve().parent

RAW_SPARC = Path("/Users/resorb/Documents/Claude Sessions/Gravity Data Analysis/data/raw/sparc")
META = Path("/Users/resorb/Documents/Claude Sessions/Transaction Calculus/data/sparc/SPARC_Lelli2016c.mrt")
DELIVERED = Path("/Users/resorb/Documents/Claude Sessions/Transaction Calculus/data/"
                 "sparc_derived_tables_2026_07_22/C_Triangle_E1_74gal_design_matrix.csv")

A0 = 1.1141506080465188e-10
L_STAR = 0.39992170918182096
Q_EXP = 0.6663695144357871
UPS_D = 0.5
UPS_B = 0.7
CONV = 1000.0**2 / 3.0856775814913673e19


def parse_metadata(path: Path) -> pd.DataFrame:
    names = ["galaxy_id", "T", "D", "e_D", "f_D", "Inc", "e_Inc", "L36", "e_L36", "Reff",
             "SBeff", "Rdisk", "SBdisk_meta", "MHI", "RHI", "Vflat", "e_Vflat", "Q", "Ref"]
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[98:]:
        parts = line.split()
        if len(parts) != len(names):
            raise ValueError(f"metadata parse failed: {line!r}")
        rows.append(parts)
    df = pd.DataFrame(rows, columns=names)
    for c in names[1:-1]:
        df[c] = pd.to_numeric(df[c], errors="raise")
    df["f_gas_proxy"] = (1.33 * df["MHI"]) / (UPS_D * df["L36"] + 1.33 * df["MHI"])
    return df


def source_metrics(radii: np.ndarray, source: np.ndarray) -> dict:
    """Verbatim port of stage_e1_reconstruct.py source_metrics()."""
    edges = np.concatenate([[0.0], radii])
    areas = math.pi * (edges[1:] ** 2 - edges[:-1] ** 2)
    weights = source * areas
    total = float(weights.sum())
    if total <= 0:
        raise ValueError("non-positive source total")
    target = 0.95 * total
    cumulative = np.cumsum(weights)
    idx = int(np.searchsorted(cumulative, target))
    previous = float(cumulative[idx - 1]) if idx > 0 else 0.0
    needed = max(target - previous, 0.0)
    if source[idx] > 0:
        r95 = math.sqrt(edges[idx] ** 2 + needed / (source[idx] * math.pi))
    else:
        r95 = float(edges[idx + 1])
    ca, cs = [], []
    for k, value in enumerate(source):
        r_in = float(edges[k])
        r_out = min(float(edges[k + 1]), r95)
        if r_out > r_in:
            ca.append(math.pi * (r_out ** 2 - r_in ** 2))
            cs.append(float(value))
        if edges[k + 1] >= r95:
            break
    a = np.asarray(ca)
    s = np.asarray(cs)
    a_eff = float((s * a).sum() ** 2) / float((s ** 2 * a).sum())
    r_ipr = math.sqrt(a_eff / math.pi)
    return {"R95": r95, "A_eff": a_eff, "R_IPR": r_ipr, "X_A": math.log10(r_ipr)}


def build(convention: str) -> pd.DataFrame:
    meta = parse_metadata(META)
    mass = ascii.read(RAW_SPARC / "MassModels_Lelli2016c.mrt", format="mrt").to_pandas() \
        .rename(columns={"ID": "galaxy_id"})
    parent = meta.loc[(meta["f_gas_proxy"] < 0.5) & (meta["Q"] <= 2)
                      & (meta["Inc"] >= 30) & (meta["Vflat"] > 0)].copy()
    m = mass.merge(parent, on="galaxy_id", how="inner", suffixes=("", "_meta"))

    m["g_obs"] = (m["Vobs"] ** 2 / m["R"]) * CONV
    m["g_bar"] = (m["Vgas"] * m["Vgas"].abs() + UPS_D * m["Vdisk"] ** 2
                  + UPS_B * m["Vbul"] ** 2) / m["R"] * CONV
    m["Y"] = m["g_bar"] / A0
    m["g_RAR"] = m["g_bar"] / (1.0 - np.exp(-np.sqrt(m["g_bar"] / A0)))

    chunks = []
    for gid, g in m.groupby("galaxy_id", sort=False):
        g = g.sort_values("R").copy()
        R = g["R"].to_numpy(float)
        gb = g["g_bar"].to_numpy(float)
        if convention == "LOGLOG":
            grad = np.gradient(np.log(gb), np.log(R))
            lb = R / np.maximum(np.abs(grad), 1e-3)
        elif convention == "LINEAR":
            dg = np.gradient(gb, R)
            lb = np.where(np.abs(dg) > 0, gb / np.abs(dg), np.inf)
        else:
            raise ValueError(convention)
        g["L_b_kpc"] = lb
        g["G_L_total"] = 1.0 - np.exp(-((np.clip(lb, 1e-6, None) / L_STAR) ** Q_EXP))
        chunks.append(g)
    m = pd.concat(chunks, ignore_index=True)

    m["delta_RAR"] = np.log10(m["g_obs"] / m["g_RAR"])
    m["W"] = (m["Y"] >= 0.03) & (m["Y"] <= 1.0) & (m["G_L_total"] >= 0.8)

    counts = m.groupby("galaxy_id")["W"].sum()
    keep = counts.loc[counts >= 4].index
    m = m.loc[m["galaxy_id"].isin(keep)].copy()

    rows = []
    for gid, g in m.groupby("galaxy_id", sort=True):
        g = g.sort_values("R")
        src = (UPS_D * g["SBdisk"] + UPS_B * g["SBbul"]).to_numpy(float)
        r = {"galaxy_id": gid}
        r.update(source_metrics(g["R"].to_numpy(float), src))
        rows.append(r)
    src_df = pd.DataFrame(rows)

    sw = m.loc[m["W"]]
    gal = sw.groupby("galaxy_id").agg(
        T_RAR=("delta_RAR", "median"), n_rows_strictW=("W", "sum")).reset_index()
    gal = gal.merge(src_df, on="galaxy_id").merge(parent, on="galaxy_id")
    gal["logVflat"] = np.log10(gal["Vflat"])
    gal["logSBeff"] = np.log10(gal["SBeff"])
    gal["strictW_rows_total"] = int(m["W"].sum())
    gal["per_radius_rows_total"] = int(len(m))
    return gal.sort_values("galaxy_id").reset_index(drop=True)


def main() -> None:
    d = pd.read_csv(DELIVERED)
    out = {"utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "delivered_file": str(DELIVERED), "delivered_rows": int(len(d)),
           "conventions": {}}
    for conv in ("LOGLOG", "LINEAR"):
        g = build(conv)
        rec = {"n_galaxies": int(len(g)),
               "strictW_rows_total": int(g["strictW_rows_total"].iloc[0]),
               "per_radius_rows_total": int(g["per_radius_rows_total"].iloc[0])}
        common = sorted(set(d["Galaxy"]) & set(g["galaxy_id"]))
        rec["n_common_with_delivered"] = len(common)
        rec["galaxy_set_identical"] = bool(set(d["Galaxy"]) == set(g["galaxy_id"]))
        gi = g.set_index("galaxy_id").loc[common]
        di = d.set_index("Galaxy").loc[common]
        for a, b in (("T_RAR_resid", "T_RAR"), ("X_A", "X_A"), ("A_eff", "A_eff"),
                     ("R_IPR", "R_IPR"), ("R95", "R95"), ("logVflat", "logVflat"),
                     ("logSBeff", "logSBeff"), ("n_rows_strictW", "n_rows_strictW")):
            rec[f"max_abs_diff__{a}"] = float(np.abs(di[a].to_numpy(float)
                                                     - gi[b].to_numpy(float)).max())
        # per-galaxy calibration target
        for tgt in ("NGC3198", "NGC2403", "F571-8"):
            if tgt in gi.index:
                rec[f"target_{tgt}"] = {
                    "T_RAR_rebuilt": float(gi.loc[tgt, "T_RAR"]),
                    "T_RAR_delivered": float(di.loc[tgt, "T_RAR_resid"]),
                    "X_A_rebuilt": float(gi.loc[tgt, "X_A"]),
                    "X_A_delivered": float(di.loc[tgt, "X_A"]),
                    "n_rows_strictW_rebuilt": int(gi.loc[tgt, "n_rows_strictW"]),
                    "n_rows_strictW_delivered": int(di.loc[tgt, "n_rows_strictW"]),
                }
        out["conventions"][conv] = rec
    (OUT / "step1_w_convention_calibration_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
