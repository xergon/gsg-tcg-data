#!/usr/bin/env python3
"""STEP 2 — build EXT-CMK-1 external held-out design matrix for C-Triangle.

BUILD ONLY. No CMK, no p-value, no beta-hat, no evaluation, no comparison of
n_valid against any floor.

Reads ONLY the staged external products (de Blok+2008 ROTMAS, Walter+2008 VizieR
J/AJ/136/2563) plus the lane's own crossmatch membership labels. NO SPARC row is
read into the product; SPARC is touched only to (a) report coverage as a separate
fact and (b) run a descriptive provenance consistency note on T / Inc.

Writes, in this directory only:
  C_Triangle_EXT_THINGS_LITTLETHINGS_E1heldout_design_matrix.csv
  C_Triangle_EXT_THINGS_LITTLETHINGS_manifest.txt
  ext_cmk1_exclusion_ledger.csv
  ext_cmk1_build_report.json
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
STAGED = Path("/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/"
              "phase23_external_heldout_sources_2026_07_22")
C = STAGED / "C_things_littlethings"
XM = STAGED / "_crossmatch"

MASSMODELS = C / "things_deblok2008_massmodels_tidy.csv"
FITHDRS = C / "things_deblok2008_fit_headers.csv"
WALTER = C / "walter2008_table1_things_sample.csv"
CROSSMATCH = XM / "crossmatch_vs_SPARC_and_StageE1_74.csv"
AMBIG = XM / "ambiguous_or_unmatched_names.csv"
E1COHORT = XM / "reference_stageE1_74_cohort.csv"
OH2015 = STAGED / "B_little_things_oh2015" / "oh2015_table1_galaxy_properties.csv"

# SPARC — read for the SEPARATE-FACT coverage statement and the descriptive T/Inc
# provenance note ONLY. Nothing from these files is written into the product.
SPARC_META = Path("/Users/resorb/Documents/Claude Sessions/Transaction Calculus/data/sparc/SPARC_Lelli2016c.mrt")
E1_TABLE = Path("/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/"
                "sparc_rar_aeff_ipr/phase120_stage_e1_independent_reconstruction_2026_06_27/"
                "stage_e1_galaxy_level_table.csv")

HEADER = ["Galaxy", "Survey", "SourceRef", "overlap_E1", "T_RAR_resid", "X_A", "logVflat",
          "logSBeff", "T", "Inc", "n_rows_strictW", "A_eff", "R_IPR", "R95"]

SOURCE_REF_THINGS = ("deBlok2008_AJ_136_2648_ROTMAS_ISOfixREV_dietSalpeter"
                     "|Walter2008_AJ_136_2563_VizieR_table1")

# Obstruction codes, resolved once and applied per column.
OBSTRUCTIONS = {
    "O1_no_36um_surface_brightness_profile": {
        "kills": ["X_A", "A_eff", "R_IPR", "R95"],
        "detail": ("Stage-E1 source_metrics() builds the source map as "
                   "s = 0.5*SBdisk + 0.7*SBbul from the SPARC 3.6um surface-brightness "
                   "profile columns. de Blok+2008's ROTMAS files carry exactly eight "
                   "columns (Radius|vgas|vdisk|vbulge|vobs|err vobs|Vu|Vt) and no surface "
                   "brightness of any kind; Walter+2008 Table 1 carries integrated B-band "
                   "Bmag and logD25 only. No 3.6um radial profile exists anywhere in the "
                   "staged external product, so R95, A_eff, R_IPR and X_A have no input."),
    },
    "O2_stellar_velocity_carries_undeclared_per_galaxy_Upsilon_star": {
        "kills": ["T_RAR_resid", "n_rows_strictW"],
        "detail": ("Stage-E1 g_bar = (Vgas*|Vgas| + 0.5*Vdisk^2 + 0.7*Vbul^2)/R requires "
                   "Vdisk/Vbul normalised to Upsilon_star = 1, which is the SPARC "
                   "convention. de Blok's own README states verbatim of column 3: "
                   "'Rotation velocity of the main disk component (km/s). This includes "
                   "any M/L* scaling.' The staged ISO.fix headers all record par_MD = 1.0 "
                   "with err_MD = 0.0 - MD is a multiplier ON de Blok's adopted "
                   "Upsilon_star, not Upsilon_star itself, and the adopted value is "
                   "recorded nowhere in the staged bytes. It is also not guaranteed to be "
                   "a single scalar per galaxy (de Blok's .grad / .nocol variants exist "
                   "precisely because a colour-gradient Upsilon_star was used for some "
                   "galaxies). Applying E1's 0.5 to an already-scaled Vdisk would "
                   "double-count; un-scaling is impossible without the missing value. So "
                   "E1-comparable g_bar, and therefore delta_RAR, the strict-W window and "
                   "n_rows_strictW, cannot be formed."),
    },
    "O3_no_Vflat_and_Vmax_Vlast_substitution_forbidden": {
        "kills": ["logVflat"],
        "detail": ("logVflat = log10(Vflat) where Vflat is SPARC's fitted flat-part "
                   "rotation velocity. No de Blok or Walter product publishes Vflat. "
                   "C-Triangle's binding constraint forbids substituting V_max or V_last "
                   "in the primary file, which is the only thing the external rotation "
                   "curves could supply. Column left null by instruction."),
    },
    "O4_no_36um_effective_surface_brightness": {
        "kills": ["logSBeff"],
        "detail": ("logSBeff = log10(SBeff), SPARC's 3.6um effective surface brightness "
                   "in Lsun/pc^2 inside Reff. The external product carries no 3.6um "
                   "photometry. Walter+2008 Table 1 has B-band Bmag and logD25, from "
                   "which a B-band surface brightness could be formed - a different band "
                   "and a different definition, not the frozen quantity, and therefore "
                   "not comparable to the in-cohort rows."),
    },
}

BUILDABLE = ["Galaxy", "Survey", "SourceRef", "overlap_E1", "T", "Inc"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    ts = utc()
    inputs = {}
    for p in (MASSMODELS, FITHDRS, WALTER, CROSSMATCH, AMBIG, E1COHORT, OH2015):
        inputs[str(p)] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}

    mm = pd.read_csv(MASSMODELS)
    galaxies = sorted(mm["galaxy"].unique())
    assert len(galaxies) == 17, len(galaxies)

    cm = pd.read_csv(CROSSMATCH)
    mmx = cm[cm["dataset"] == "C_deBlok2008_MASSMODELS_17"].set_index("target_name")
    assert set(mmx.index) == set(galaxies)

    walter = pd.read_csv(WALTER)
    walter["key"] = walter["Name"].str.replace(" ", "", regex=False).str.upper()
    wk = walter.set_index("key")

    rows = []
    for g in galaxies:
        w = wk.loc[g]
        rows.append({
            "Galaxy": g,
            "Survey": "THINGS",
            "SourceRef": SOURCE_REF_THINGS,
            "overlap_E1": bool(mmx.loc[g, "in_stageE1_74"]),
            "T_RAR_resid": np.nan,
            "X_A": np.nan,
            "logVflat": np.nan,
            "logSBeff": np.nan,
            "T": float(w["TT_type"]),
            "Inc": float(w["incl_deg"]),
            "n_rows_strictW": np.nan,
            "A_eff": np.nan,
            "R_IPR": np.nan,
            "R95": np.nan,
        })
    df = pd.DataFrame(rows, columns=HEADER).sort_values("Galaxy").reset_index(drop=True)

    n_valid = int((df[HEADER].notna().all(axis=1)).sum())
    nulls = {c: int(df[c].isna().sum()) for c in HEADER}

    # ---------------- exclusion ledger ----------------
    led = []
    for g in galaxies:
        e1 = bool(mmx.loc[g, "in_stageE1_74"])
        led.append({
            "Galaxy": g, "Survey": "THINGS", "stage": "design_matrix_row_validity",
            "excluded": True, "overlap_E1": e1,
            "reason_code": "O1+O2+O3+O4",
            "reason": ("8 of 14 required columns (T_RAR_resid, X_A, logVflat, logSBeff, "
                       "n_rows_strictW, A_eff, R_IPR, R95) cannot be built from the "
                       "external product; no SPARC fill permitted"),
        })
    # THINGS galaxies that never reached a mass model at all
    for g, why in [
        ("NGC3627", "de Blok+2008: dynamics severely affected by non-circular motions; "
                    "excluded from the mass-model sample (rotation curve exists, no mass model)"),
        ("NGC4826", "de Blok+2008: dynamics severely affected by non-circular motions; "
                    "excluded from the mass-model sample (rotation curve exists, no mass model)"),
    ]:
        led.append({"Galaxy": g, "Survey": "THINGS", "stage": "no_mass_model_in_source",
                    "excluded": True, "overlap_E1": False,
                    "reason_code": "SRC_NO_MASSMODEL", "reason": why})
    wal_keys = set(walter["key"])
    not_modelled = sorted(wal_keys - set(galaxies) - {"NGC3627", "NGC4826"})
    for g in not_modelled:
        led.append({"Galaxy": g, "Survey": "THINGS", "stage": "outside_deBlok2008_sample",
                    "excluded": True, "overlap_E1": False,
                    "reason_code": "SRC_SAMPLE_CUT",
                    "reason": ("outside de Blok+2008's mass-model selection (i >~ 40 deg and "
                               "rotation-dominated, plus NGC 6946 added back); no baryonic "
                               "decomposition published")})
    oh = pd.read_csv(OH2015)
    oh_names = sorted(oh.iloc[:, 0].astype(str).str.strip().unique())
    for g in oh_names:
        led.append({"Galaxy": g, "Survey": "LITTLE THINGS",
                    "stage": "no_public_baryonic_decomposition", "excluded": True,
                    "overlap_E1": False, "reason_code": "LT_NO_DECOMPOSITION",
                    "reason": ("no public LITTLE THINGS product carries V_gas / V_disk / "
                               "V_bulge - not VizieR J/AJ/149/180, not the Oh+2015 AJ "
                               "article, not the NRAO survey site, not Iorio+2017 "
                               "finalrot (whose Vd column is the velocity dispersion "
                               "sigma_v, not a disk velocity). g_bar cannot be formed at "
                               "all, so no column of the design matrix is buildable")})
    led.append({"Galaxy": "(41-26 LITTLE THINGS survey remainder)", "Survey": "LITTLE THINGS",
                "stage": "outside_Oh2015_subsample", "excluded": True, "overlap_E1": False,
                "reason_code": "LT_IRREGULAR_ROTATION",
                "reason": ("15 of the 41 Hunter+2012 LITTLE THINGS galaxies fall outside "
                           "Oh+2015's regular-rotation subsample and have no rotation-curve "
                           "product at all")})
    ledger = pd.DataFrame(led)

    # ---------------- SPARC coverage, reported as a SEPARATE FACT ----------------
    e1ids = set(pd.read_csv(E1COHORT)["galaxy_id"])
    in_sparc = sorted(mmx.index[mmx["in_sparc"].astype(bool)])
    in_e1 = sorted(mmx.index[mmx["in_stageE1_74"].astype(bool)])
    non_e1 = sorted(set(galaxies) - set(in_e1))
    assert set(in_e1) <= e1ids

    # descriptive provenance consistency note on T / Inc (NOT a fill, NOT an evaluation)
    e1t = pd.read_csv(E1_TABLE).set_index("galaxy_id")
    tnote = []
    for g in in_e1:
        tnote.append({"Galaxy": g,
                      "T_external_Walter2008": float(wk.loc[g, "TT_type"]),
                      "T_sparc_E1": float(e1t.loc[g, "T"]),
                      "Inc_external_Walter2008": float(wk.loc[g, "incl_deg"]),
                      "Inc_sparc_E1": float(e1t.loc[g, "Inc"])})
    tnote = pd.DataFrame(tnote)
    tnote["dT"] = tnote["T_external_Walter2008"] - tnote["T_sparc_E1"]
    tnote["dInc"] = tnote["Inc_external_Walter2008"] - tnote["Inc_sparc_E1"]

    ambig = pd.read_csv(AMBIG)

    # ---------------- write product ----------------
    prod = OUT / "C_Triangle_EXT_THINGS_LITTLETHINGS_E1heldout_design_matrix.csv"
    df.to_csv(prod, index=False, float_format="%.17g", na_rep="")
    ledger.to_csv(OUT / "ext_cmk1_exclusion_ledger.csv", index=False)
    tnote.to_csv(OUT / "ext_cmk1_T_Inc_provenance_consistency_note.csv", index=False,
                 float_format="%.17g")

    report = {
        "utc_true_date_u": ts,
        "status": "BUILT",
        "product": str(prod),
        "product_sha256": sha256_file(prod),
        "product_bytes": prod.stat().st_size,
        "rows": int(len(df)),
        "cols": len(HEADER),
        "header": HEADER,
        "n_valid_rows_complete_on_all_14_columns": n_valid,
        "per_column_nulls": nulls,
        "galaxies_in": {"THINGS": len(galaxies), "LITTLE_THINGS": 0},
        "e1_74_excluded": len(in_e1),
        "non_e1_retained_as_candidates": len(non_e1),
        "non_e1_candidate_list": non_e1,
        "e1_74_overlap_list": in_e1,
        "exclusions_total_rows_in_ledger": int(len(ledger)),
        "obstructions": OBSTRUCTIONS,
        "buildable_columns": BUILDABLE,
        "sparc_coverage_separate_fact": {
            "deblok17_in_sparc": len(in_sparc),
            "deblok17_in_sparc_list": in_sparc,
            "note": ("SPARC independently carries a full Rotmod decomposition for all 13 of "
                     "these. No SPARC row entered the product: every populated cell in the "
                     "product comes from de Blok+2008 ROTMAS or Walter+2008 VizieR "
                     "J/AJ/136/2563."),
        },
        "T_Inc_provenance_consistency": {
            "max_abs_dT": float(tnote["dT"].abs().max()),
            "max_abs_dInc": float(tnote["dInc"].abs().max()),
            "n_compared": int(len(tnote)),
        },
        "ambiguous_names": ambig.to_dict(orient="records"),
        "input_hashes": inputs,
    }
    (OUT / "ext_cmk1_build_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("obstructions", "input_hashes", "ambiguous_names")},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
