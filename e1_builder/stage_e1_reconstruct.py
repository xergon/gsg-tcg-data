#!/usr/bin/env python3
"""Stage E1 fresh-code reconstruction for the SPARC/RAR X_A residual line.

Intent: keep the reconstruction small, explicit, and auditable. This script
uses only raw SPARC tables plus the Stage E1 frozen constants/formulas, writes
fresh tables first, and only then scans older Stage C/D result files for a
post-freeze comparison summary.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from astropy.io import ascii
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor


OUT_DIR = Path(__file__).resolve().parent
PLOTS_DIR = OUT_DIR / "stage_e1_plots"

RAW_SPARC_DIR = Path("/Users/resorb/Documents/Claude Sessions/Gravity Data Analysis/data/raw/sparc")
METADATA_PATH = Path("/Users/resorb/Documents/Claude Sessions/Transaction Calculus/data/sparc/SPARC_Lelli2016c.mrt")

INPUTS = {
    "MassModels_Lelli2016c.mrt": RAW_SPARC_DIR / "MassModels_Lelli2016c.mrt",
    "Rotmod_LTG.zip": RAW_SPARC_DIR / "Rotmod_LTG.zip",
    "SPARC_index.html": RAW_SPARC_DIR / "SPARC_index.html",
    "RAR.mrt": RAW_SPARC_DIR / "RAR.mrt",
    "RARbins.mrt": RAW_SPARC_DIR / "RARbins.mrt",
    "SPARC_Lelli2016c.mrt": METADATA_PATH,
}

EXPECTED_HASHES = {
    "MassModels_Lelli2016c.mrt": "9108994b12cc401b94a1768beca61c53ec354779385c9c9cc571049f3043244c",
    "Rotmod_LTG.zip": "0a80cc90714828cc28b7dd57923576714d209f2490328c087c4a4ad607faf588",
    "SPARC_index.html": "ee7e3eab83de7d698bc14d9eeb91d87a939221dd452e907ea5ad7dedae886038",
    "RAR.mrt": "24aa7059dab7fa44787f7c11191052489899819370f6508621674769f3b72833",
    "RARbins.mrt": "d543cab7b720a4f14152ccc8158f7823072ce65a9c5b403d7c401b3f039a79d7",
    # Metadata was absent from the Gravity raw folder but present as official raw
    # SPARC Table1 in the local Transaction Calculus cache; hash is recorded here.
    "SPARC_Lelli2016c.mrt": "5aa0501f6b0d881fa579030e315e7b5b6ef561a5bd3a07472f9929c7e5728243",
}

A0 = 1.1141506080465188e-10
L_STAR = 0.39992170918182096
Q_EXP = 0.6663695144357871
UPSILON_D = 0.5
UPSILON_B = 0.7
KMS2_PER_KPC_TO_M_PER_S2 = 1000.0**2 / 3.0856775814913673e19
N_PERM = 5000
RNG_SEED = 20260627


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def append_log(event: str, **payload) -> None:
    row = {"ts_utc": now_iso(), "event": event, **payload}
    with (OUT_DIR / "WORKER_LOG.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_inputs() -> dict:
    hashes = {}
    for label, path in INPUTS.items():
        if not path.exists():
            raise FileNotFoundError(f"required input missing: {path}")
        actual = sha256_file(path)
        hashes[label] = {
            "path": str(path),
            "sha256": actual,
            "expected_sha256": EXPECTED_HASHES[label],
            "matches_expected": actual == EXPECTED_HASHES[label],
        }
    append_log("input_hashes_checked", hashes=hashes)
    return hashes


def parse_metadata(path: Path) -> pd.DataFrame:
    names = [
        "galaxy_id",
        "T",
        "D",
        "e_D",
        "f_D",
        "Inc",
        "e_Inc",
        "L36",
        "e_L36",
        "Reff",
        "SBeff",
        "Rdisk",
        "SBdisk_meta",
        "MHI",
        "RHI",
        "Vflat",
        "e_Vflat",
        "Q",
        "Ref",
    ]
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[98:]:
        parts = line.split()
        if len(parts) != len(names):
            raise ValueError(f"metadata parse failed on line: {line!r}")
        rows.append(parts)
    df = pd.DataFrame(rows, columns=names)
    for col in names[1:-1]:
        df[col] = pd.to_numeric(df[col], errors="raise")

    # Frozen stellar-dominated cut: helium-corrected HI gas fraction relative to
    # the fixed stellar M/L convention. The <0.5 threshold yields the canonical
    # 77 parent galaxies before the >=4 strict-W row retention step.
    gas_mass = 1.33 * df["MHI"]
    star_mass = UPSILON_D * df["L36"]
    df["f_gas_proxy"] = gas_mass / (star_mass + gas_mass)
    return df


def load_mass_models(path: Path) -> pd.DataFrame:
    table = ascii.read(path, format="mrt")
    df = table.to_pandas().rename(columns={"ID": "galaxy_id"})
    return df


def select_parent_sample(meta: pd.DataFrame) -> pd.DataFrame:
    cut = (
        (meta["f_gas_proxy"] < 0.5)
        & (meta["Q"] <= 2)
        & (meta["Inc"] >= 30)
        & (meta["Vflat"] > 0)
    )
    return meta.loc[cut].copy()


def add_radius_quantities(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["g_obs"] = (out["Vobs"] ** 2 / out["R"]) * KMS2_PER_KPC_TO_M_PER_S2
    out["g_bar"] = (
        out["Vgas"] * out["Vgas"].abs()
        + UPSILON_D * out["Vdisk"] ** 2
        + UPSILON_B * out["Vbul"] ** 2
    ) / out["R"] * KMS2_PER_KPC_TO_M_PER_S2
    out["Y_total_gbar_over_a0"] = out["g_bar"] / A0
    out["g_RAR"] = out["g_bar"] / (1.0 - np.exp(-np.sqrt(out["g_bar"] / A0)))

    chunks = []
    for galaxy_id, g in out.groupby("galaxy_id", sort=False):
        g = g.sort_values("R").copy()
        if len(g) < 2:
            raise ValueError(f"cannot compute gradient for {galaxy_id}: fewer than 2 rows")
        grad = np.gradient(np.log(g["g_bar"].to_numpy()), np.log(g["R"].to_numpy()))
        lb = g["R"].to_numpy() / np.maximum(np.abs(grad), 1e-3)
        g["dln_gbar_dlnR"] = grad
        g["L_b_kpc"] = lb
        g["G_L_total"] = 1.0 - np.exp(-((lb / L_STAR) ** Q_EXP))
        chunks.append(g)

    out = pd.concat(chunks, ignore_index=True)
    out["g_GSG"] = out["g_bar"] + out["G_L_total"] * (out["g_RAR"] - out["g_bar"])
    out["F_P120"] = (out["g_GSG"] - out["g_bar"]) / (out["g_RAR"] - out["g_bar"])
    out["delta_RAR"] = np.log10(out["g_obs"] / out["g_RAR"])
    out["delta_GSG"] = np.log10(out["g_obs"] / out["g_GSG"])
    out["W_strict_v1"] = (
        (out["Y_total_gbar_over_a0"] >= 0.03)
        & (out["Y_total_gbar_over_a0"] <= 1.0)
        & (out["G_L_total"] >= 0.8)
    )
    out["source_map_inputs_used"] = "stellar_only:0.5*SBdisk+0.7*SBbul"
    return out


def source_metrics(g: pd.DataFrame) -> dict:
    g = g.sort_values("R")
    radii = g["R"].to_numpy(dtype=float)
    source = (UPSILON_D * g["SBdisk"] + UPSILON_B * g["SBbul"]).to_numpy(dtype=float)

    # Simple annuli: the k-th listed radius is the outer edge, with R_inner=0
    # for the first row and previous listed radius thereafter. The R95 annulus
    # is clipped exactly so A_eff is computed on the frozen R95 source domain.
    edges = np.concatenate([[0.0], radii])
    areas = math.pi * (edges[1:] ** 2 - edges[:-1] ** 2)
    weights = source * areas
    total = float(weights.sum())
    if total <= 0:
        raise ValueError(f"non-positive source total for {g['galaxy_id'].iloc[0]}")

    target = 0.95 * total
    cumulative = np.cumsum(weights)
    idx = int(np.searchsorted(cumulative, target))
    previous = float(cumulative[idx - 1]) if idx > 0 else 0.0
    needed = max(target - previous, 0.0)
    if source[idx] > 0:
        r95 = math.sqrt(edges[idx] ** 2 + needed / (source[idx] * math.pi))
    else:
        r95 = float(edges[idx + 1])

    clipped_areas = []
    clipped_source = []
    for k, value in enumerate(source):
        r_in = float(edges[k])
        r_out = min(float(edges[k + 1]), r95)
        if r_out > r_in:
            clipped_areas.append(math.pi * (r_out**2 - r_in**2))
            clipped_source.append(float(value))
        if edges[k + 1] >= r95:
            break

    area_arr = np.asarray(clipped_areas)
    source_arr = np.asarray(clipped_source)
    numerator = float((source_arr * area_arr).sum() ** 2)
    denominator = float((source_arr**2 * area_arr).sum())
    a_eff = numerator / denominator
    r_ipr = math.sqrt(a_eff / math.pi)
    return {
        "R95": r95,
        "A_eff": a_eff,
        "R_IPR": r_ipr,
        "X_A": math.log10(r_ipr),
    }


def build_tables(meta: pd.DataFrame, mass: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    parent = select_parent_sample(meta)
    merged = mass.merge(parent, on="galaxy_id", how="inner", suffixes=("", "_meta"))
    per_radius_parent = add_radius_quantities(merged)

    strict_counts = per_radius_parent.groupby("galaxy_id")["W_strict_v1"].sum()
    retained_ids = strict_counts.loc[strict_counts >= 4].index
    per_radius = per_radius_parent.loc[per_radius_parent["galaxy_id"].isin(retained_ids)].copy()

    source_rows = []
    for galaxy_id, g in per_radius.groupby("galaxy_id", sort=True):
        row = {"galaxy_id": galaxy_id}
        row.update(source_metrics(g))
        source_rows.append(row)
    source = pd.DataFrame(source_rows)

    strict_only = per_radius.loc[per_radius["W_strict_v1"]]
    galaxy = (
        strict_only.groupby("galaxy_id")
        .agg(
            T_RAR=("delta_RAR", "median"),
            T_GSG=("delta_GSG", "median"),
            F_P120_median=("F_P120", "median"),
            n_rows_strictW=("W_strict_v1", "sum"),
        )
        .reset_index()
    )
    total_counts = per_radius.groupby("galaxy_id").size().rename("n_rows_total").reset_index()
    galaxy = galaxy.merge(total_counts, on="galaxy_id").merge(source, on="galaxy_id").merge(parent, on="galaxy_id")
    galaxy["sample_flag_74"] = True
    galaxy["logVflat"] = np.log10(galaxy["Vflat"])
    galaxy["logSBeff"] = np.log10(galaxy["SBeff"])
    galaxy["logD"] = np.log10(galaxy["D"])

    # Primary orthogonal axis requested by Thread 8.
    x_controls = sm.add_constant(galaxy[["logVflat", "logSBeff"]], has_constant="add")
    galaxy["X_A_perp"] = sm.OLS(galaxy["X_A"], x_controls).fit().resid
    full_controls = sm.add_constant(galaxy[["logVflat", "logSBeff", "T", "Inc"]], has_constant="add")
    galaxy["X_A_perp_full"] = sm.OLS(galaxy["X_A"], full_controls).fit().resid

    keep_cols = [
        "galaxy_id",
        "sample_flag_74",
        "Inc",
        "T",
        "D",
        "logD",
        "Vflat",
        "logVflat",
        "SBeff",
        "logSBeff",
        "Rdisk",
        "MHI",
        "f_gas_proxy",
        "Q",
        "R95",
        "A_eff",
        "R_IPR",
        "X_A",
        "X_A_perp",
        "X_A_perp_full",
        "n_rows_total",
        "n_rows_strictW",
        "T_RAR",
        "T_GSG",
        "F_P120_median",
    ]
    galaxy = galaxy[keep_cols].sort_values("galaxy_id").reset_index(drop=True)

    per_cols = [
        "galaxy_id",
        "R",
        "Vobs",
        "Vgas",
        "Vdisk",
        "Vbul",
        "SBdisk",
        "SBbul",
        "g_obs",
        "g_bar",
        "g_RAR",
        "G_L_total",
        "g_GSG",
        "F_P120",
        "Y_total_gbar_over_a0",
        "dln_gbar_dlnR",
        "L_b_kpc",
        "delta_RAR",
        "delta_GSG",
        "W_strict_v1",
        "source_map_inputs_used",
    ]
    per_radius = per_radius[per_cols].rename(columns={"R": "R_kpc"}).sort_values(["galaxy_id", "R_kpc"])
    return parent, galaxy, per_radius.reset_index(drop=True)


def residualize(series: pd.Series, controls: pd.DataFrame) -> np.ndarray:
    if controls.empty:
        return series.to_numpy(dtype=float) - float(series.mean())
    x = sm.add_constant(controls, has_constant="add")
    return sm.OLS(series, x).fit().resid


def loo_rmse(df: pd.DataFrame, target: str, predictors: list[str]) -> float:
    y_true = []
    y_pred = []
    for idx in df.index:
        train = df.drop(index=idx)
        test = df.loc[[idx]]
        x_train = sm.add_constant(train[predictors], has_constant="add")
        fit = sm.OLS(train[target], x_train).fit()
        x_test = sm.add_constant(test[predictors], has_constant="add")
        x_test = x_test.reindex(columns=x_train.columns, fill_value=1.0)
        y_true.append(float(test[target].iloc[0]))
        y_pred.append(float(fit.predict(x_test).iloc[0]))
    return float(np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2)))


def vif_note(df: pd.DataFrame, predictors: list[str]) -> str:
    if len(predictors) < 2:
        return "single_predictor"
    x = sm.add_constant(df[predictors], has_constant="add")
    vals = []
    for i, col in enumerate(x.columns):
        if col == "const":
            continue
        try:
            vals.append((col, float(variance_inflation_factor(x.to_numpy(), i))))
        except Exception:
            vals.append((col, float("nan")))
    max_col, max_val = max(vals, key=lambda item: -1 if math.isnan(item[1]) else item[1])
    return f"max_vif={max_val:.3f} ({max_col})"


def fit_model(
    df: pd.DataFrame,
    target: str,
    model_name: str,
    predictors: list[str],
    coefficient_axis: str,
    rng: np.random.Generator,
) -> dict:
    y = df[target]
    x = sm.add_constant(df[predictors], has_constant="add")
    fit_plain = sm.OLS(y, x).fit()
    fit_robust = sm.OLS(y, x).fit(cov_type="HC3")

    nuisance = [p for p in predictors if p != coefficient_axis]
    if nuisance:
        x_base = sm.add_constant(df[nuisance], has_constant="add")
    else:
        x_base = pd.DataFrame({"const": np.ones(len(df))}, index=df.index)
    fit_base = sm.OLS(y, x_base).fit()

    axis_resid = residualize(df[coefficient_axis], df[nuisance] if nuisance else pd.DataFrame(index=df.index))
    target_resid = residualize(y, df[nuisance] if nuisance else pd.DataFrame(index=df.index))
    partial_r = float(stats.pearsonr(axis_resid, target_resid).statistic)

    jack = []
    for idx in df.index:
        train = df.drop(index=idx)
        x_train = sm.add_constant(train[predictors], has_constant="add")
        jack.append(float(sm.OLS(train[target], x_train).fit().params[coefficient_axis]))
    jack = np.asarray(jack)

    beta = float(fit_robust.params[coefficient_axis])
    y_hat_base = fit_base.fittedvalues.to_numpy()
    resid_base = fit_base.resid.to_numpy()
    perm_betas = []
    for _ in range(N_PERM):
        y_perm = y_hat_base + rng.permutation(resid_base)
        perm_betas.append(float(sm.OLS(y_perm, x).fit().params[coefficient_axis]))
    perm_betas = np.asarray(perm_betas)
    permutation_p = float((1 + np.sum(np.abs(perm_betas) >= abs(beta))) / (N_PERM + 1))

    rmse_full = loo_rmse(df, target, predictors)
    rmse_base = loo_rmse(df, target, nuisance) if nuisance else float(np.std(y, ddof=1))

    return {
        "target": target,
        "model_name": model_name,
        "n_galaxies": int(len(df)),
        "coefficient_axis": coefficient_axis,
        "beta": beta,
        "robust_se": float(fit_robust.bse[coefficient_axis]),
        "p_value": float(fit_robust.pvalues[coefficient_axis]),
        "partial_r": partial_r,
        "bic": float(fit_plain.bic),
        "bic_delta": float(fit_plain.bic - fit_base.bic),
        "loo_rmse": rmse_full,
        "loo_rmse_baseline": rmse_base,
        "loo_rmse_delta": float(rmse_base - rmse_full),
        "jackknife_negative_fraction": float(np.mean(jack < 0)),
        "jackknife_min_beta": float(jack.min()),
        "jackknife_max_beta": float(jack.max()),
        "permutation_p": permutation_p,
        "vif_note": vif_note(df, predictors),
        "status": "ok",
    }


def regression_tables(galaxy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(RNG_SEED)
    specs = [
        ("T_RAR", "A_T_RAR_X_A", ["X_A"], "X_A"),
        ("T_RAR", "A2_T_RAR_X_A_plus_logD", ["X_A", "logD"], "X_A"),
        ("T_RAR", "B_T_RAR_X_A_mass_sb", ["X_A", "logVflat", "logSBeff"], "X_A"),
        ("T_RAR", "C_T_RAR_X_A_full_controls", ["X_A", "logVflat", "logSBeff", "T", "Inc"], "X_A"),
        (
            "T_RAR",
            "D_T_RAR_X_A_perp_mass_sb_full_controls",
            ["X_A_perp", "logVflat", "logSBeff", "T", "Inc"],
            "X_A_perp",
        ),
        (
            "T_RAR",
            "E_T_RAR_X_A_perp_full_controls",
            ["X_A_perp_full", "logVflat", "logSBeff", "T", "Inc"],
            "X_A_perp_full",
        ),
        ("T_GSG", "A_T_GSG_X_A", ["X_A"], "X_A"),
        ("T_GSG", "B_T_GSG_X_A_mass_sb", ["X_A", "logVflat", "logSBeff"], "X_A"),
        ("T_GSG", "C_T_GSG_X_A_full_controls", ["X_A", "logVflat", "logSBeff", "T", "Inc"], "X_A"),
        (
            "T_GSG",
            "D_T_GSG_X_A_perp_mass_sb_full_controls",
            ["X_A_perp", "logVflat", "logSBeff", "T", "Inc"],
            "X_A_perp",
        ),
    ]
    rows = [fit_model(galaxy, *spec, rng=rng) for spec in specs]
    reg = pd.DataFrame(rows)

    suppression = galaxy[
        [
            "galaxy_id",
            "X_A",
            "X_A_perp",
            "X_A_perp_full",
            "logVflat",
            "logSBeff",
            "T",
            "Inc",
            "T_RAR",
            "T_GSG",
        ]
    ].copy()
    return reg, suppression


def pass_conditions(summary: dict, reg: pd.DataFrame) -> dict:
    model_c = reg.loc[reg["model_name"] == "C_T_RAR_X_A_full_controls"].iloc[0]
    model_d = reg.loc[reg["model_name"] == "D_T_RAR_X_A_perp_mass_sb_full_controls"].iloc[0]
    beta_targets = [-0.3009, -0.3022]
    beta_close = min(abs(float(model_c["beta"]) - target) for target in beta_targets) <= 0.03
    return {
        "N_equals_74": summary["retained_galaxies"] == 74,
        "per_radius_rows_equal_1968": summary["retained_per_radius_rows"] == 1968,
        "strictW_rows_equal_1328": summary["strictW_rows"] == 1328,
        "model_C_beta_negative": float(model_c["beta"]) < 0,
        "model_C_beta_within_0p03_of_target": beta_close,
        "model_C_p_lt_0p01": float(model_c["p_value"]) < 0.01,
        "model_C_jackknife_stable": float(model_c["jackknife_negative_fraction"]) >= 0.95,
        "model_D_X_A_perp_negative": float(model_d["beta"]) < 0,
        "model_D_X_A_perp_p_lt_0p01": float(model_d["p_value"]) < 0.01,
        "model_D_jackknife_stable": float(model_d["jackknife_negative_fraction"]) >= 0.95,
    }


def write_csvs(galaxy: pd.DataFrame, per_radius: pd.DataFrame, reg: pd.DataFrame, suppression: pd.DataFrame) -> None:
    galaxy.to_csv(OUT_DIR / "stage_e1_galaxy_level_table.csv", index=False)
    per_radius.to_csv(OUT_DIR / "stage_e1_per_radius_table.csv", index=False)
    reg.to_csv(OUT_DIR / "stage_e1_regression_table.csv", index=False)
    suppression.to_csv(OUT_DIR / "stage_e1_suppression_decomposition.csv", index=False)
    append_log("fresh_reconstruction_tables_frozen", files=[
        "stage_e1_galaxy_level_table.csv",
        "stage_e1_per_radius_table.csv",
        "stage_e1_regression_table.csv",
        "stage_e1_suppression_decomposition.csv",
    ])


def write_plots(galaxy: pd.DataFrame) -> None:
    PLOTS_DIR.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.scatter(galaxy["X_A"], galaxy["T_RAR"], s=32, color="#2f6f8f", alpha=0.85)
    line = sm.OLS(galaxy["T_RAR"], sm.add_constant(galaxy[["X_A"]], has_constant="add")).fit()
    xs = np.linspace(galaxy["X_A"].min(), galaxy["X_A"].max(), 100)
    ax.plot(xs, line.params["const"] + line.params["X_A"] * xs, color="#a23b3b", lw=2)
    ax.set_xlabel("X_A = log10(R_IPR / kpc)")
    ax.set_ylabel("T_RAR = median strict-W log10(g_obs/g_RAR)")
    ax.set_title("Stage E1 bivariate residual check")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "stage_e1_T_RAR_vs_X_A.png", dpi=180)
    plt.close(fig)

    controls = sm.add_constant(galaxy[["logVflat", "logSBeff", "T", "Inc"]], has_constant="add")
    y_resid = sm.OLS(galaxy["T_RAR"], controls).fit().resid
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.scatter(galaxy["X_A_perp"], y_resid, s=32, color="#3b7f55", alpha=0.85)
    line = sm.OLS(y_resid, sm.add_constant(galaxy[["X_A_perp"]], has_constant="add")).fit()
    xs = np.linspace(galaxy["X_A_perp"].min(), galaxy["X_A_perp"].max(), 100)
    ax.plot(xs, line.params["const"] + line.params["X_A_perp"] * xs, color="#a23b3b", lw=2)
    ax.set_xlabel("X_A_perp")
    ax.set_ylabel("T_RAR residual after controls")
    ax.set_title("Stage E1 orthogonal-axis check")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "stage_e1_T_RAR_residual_vs_X_A_perp.png", dpi=180)
    plt.close(fig)
    append_log("plots_written", plot_dir=str(PLOTS_DIR))


def compare_to_stage_cd(galaxy: pd.DataFrame, per_radius: pd.DataFrame, reg: pd.DataFrame) -> pd.DataFrame:
    base = OUT_DIR.parent
    old_dirs = [
        base / "phase120_stage_c_strictW_2026_06_26",
        base / "phase120_stage_d1_hostile_nulls_2026_06_26",
        base / "phase120_stage_d2_fixed_ml_stress_2026_06_26",
        base / "phase120_stage_c_d1_d2_hostile_review_packet_2026_06_26",
    ]
    rows = []
    for old_dir in old_dirs:
        if not old_dir.exists():
            rows.append({
                "old_artifact": str(old_dir),
                "comparison": "directory_presence",
                "old_value": "missing",
                "stage_e1_value": "present",
                "delta": "",
                "status": "not_found",
            })
            continue
        for path in sorted(old_dir.rglob("*")):
            if path.suffix.lower() not in {".csv", ".json"}:
                continue
            if path.name.endswith(".sha256"):
                continue
            lower = path.name.lower()
            try:
                if path.suffix.lower() == ".csv":
                    old_df = pd.read_csv(path)
                    if "galaxy" in lower:
                        rows.append({
                            "old_artifact": str(path),
                            "comparison": "galaxy_csv_row_count",
                            "old_value": len(old_df),
                            "stage_e1_value": len(galaxy),
                            "delta": len(galaxy) - len(old_df),
                            "status": "post_freeze_read",
                        })
                    elif "radius" in lower or "per" in lower or "audit" in lower:
                        rows.append({
                            "old_artifact": str(path),
                            "comparison": "per_radius_csv_row_count",
                            "old_value": len(old_df),
                            "stage_e1_value": len(per_radius),
                            "delta": len(per_radius) - len(old_df),
                            "status": "post_freeze_read",
                        })
                    elif "regression" in lower or "model" in lower:
                        rows.append({
                            "old_artifact": str(path),
                            "comparison": "regression_csv_row_count",
                            "old_value": len(old_df),
                            "stage_e1_value": len(reg),
                            "delta": len(reg) - len(old_df),
                            "status": "post_freeze_read",
                        })
                elif path.suffix.lower() == ".json" and ("result" in lower or "summary" in lower):
                    data = json.loads(path.read_text(encoding="utf-8"))
                    text = json.dumps(data, sort_keys=True)
                    rows.append({
                        "old_artifact": str(path),
                        "comparison": "json_contains_canonical_beta_token",
                        "old_value": str(("-0.302" in text) or ("-0.3009" in text)),
                        "stage_e1_value": f"{float(reg.loc[reg['model_name'] == 'C_T_RAR_X_A_full_controls', 'beta'].iloc[0]):.6f}",
                        "delta": "",
                        "status": "post_freeze_read",
                    })
            except Exception as exc:
                rows.append({
                    "old_artifact": str(path),
                    "comparison": "read_error",
                    "old_value": repr(exc),
                    "stage_e1_value": "",
                    "delta": "",
                    "status": "error",
                })
    if not rows:
        rows.append({
            "old_artifact": "",
            "comparison": "stage_c_d_scan",
            "old_value": "no candidate csv/json files found",
            "stage_e1_value": "",
            "delta": "",
            "status": "not_found",
        })
    comparison = pd.DataFrame(rows)
    comparison.to_csv(OUT_DIR / "stage_e1_reconstruction_comparison_to_stage_c_d.csv", index=False)
    append_log("post_freeze_stage_c_d_comparison_written", rows=len(comparison))
    return comparison


def write_method(input_hashes: dict) -> None:
    lines = [
        "# Stage E1 Reconstruction Method",
        "",
        "Intent: independent fresh-code reconstruction only. No Stage E2 gas-aware test, gas inversion, B_chi inference, M/L fitting, formula tuning, W tolerance, or claim change was performed.",
        "",
        "## Inputs",
    ]
    for label, info in input_hashes.items():
        lines.append(f"- `{label}`: `{info['path']}` sha256 `{info['sha256']}` match_expected={info['matches_expected']}")
    lines += [
        "",
        "## Frozen Choices",
        "",
        "- Residual orientation follows the Stage E1 handoff and decision memo: `T_RAR = median_W log10(g_obs/g_RAR)`.",
        "- The planning packet contains one conflicting line using `log10(g_RAR/g_obs)`; this run keeps the handoff/decision convention and logs the discrepancy.",
        "- Parent filter: helium-corrected `f_gas_proxy = 1.33*MHI / (0.5*L[3.6] + 1.33*MHI)`, `Q<=2`, `Inc>=30`, `Vflat>0`.",
        "- Retained sample: parent galaxies with at least 4 strict-W rows.",
        "- Strict W: `0.03 <= g_bar/a0 <= 1` and `G_L_total >= 0.8`, no tolerance.",
        "- Source map: `s_star = 0.5*SBdisk + 0.7*SBbul`, stellar-only.",
        "- Annuli: listed SPARC radius is the outer annulus edge; first inner edge is 0, later inner edge is the previous listed radius.",
        "- R95: radius enclosing 95 percent of annular stellar source; final annulus is clipped at R95 before IPR/A_eff calculation.",
        "- `X_A_perp`: residual of `X_A ~ logVflat + logSBeff`.",
        "",
        "## Constants",
        "",
        f"- `a0 = {A0}`",
        f"- `L_star = {L_STAR} kpc`",
        f"- `q = {Q_EXP}`",
        f"- `Upsilon_d = {UPSILON_D}`",
        f"- `Upsilon_b = {UPSILON_B}`",
    ]
    (OUT_DIR / "E1_RECONSTRUCTION_METHOD.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_results(summary: dict, conditions: dict, reg: pd.DataFrame, input_hashes: dict, comparison: pd.DataFrame) -> None:
    verdict = "PASS_RECONSTRUCTION" if all(conditions.values()) else "FAIL_RECONSTRUCTION"
    model_c = reg.loc[reg["model_name"] == "C_T_RAR_X_A_full_controls"].iloc[0].to_dict()
    model_d = reg.loc[reg["model_name"] == "D_T_RAR_X_A_perp_mass_sb_full_controls"].iloc[0].to_dict()

    payload = {
        "verdict": verdict,
        "created_utc": now_iso(),
        "summary": summary,
        "pass_conditions": conditions,
        "key_models": {
            "C_T_RAR_X_A_full_controls": model_c,
            "D_T_RAR_X_A_perp_mass_sb_full_controls": model_d,
        },
        "input_hashes": input_hashes,
        "comparison_rows": int(len(comparison)),
        "blockers": [] if verdict == "PASS_RECONSTRUCTION" else ["one_or_more_stage_e1_conditions_failed"],
        "forbidden_actions_observed": False,
    }
    (OUT_DIR / "STAGE_E1_INDEPENDENT_RECONSTRUCTION_RESULTS.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    cond_lines = "\n".join(f"- {k}: {v}" for k, v in conditions.items())
    hash_lines = "\n".join(
        f"- `{label}`: `{info['sha256']}` match_expected={info['matches_expected']}"
        for label, info in input_hashes.items()
    )
    md = f"""# Stage E1 Independent Reconstruction Results

Verdict: `{verdict}`

## Row Counts

- Metadata rows: {summary['metadata_rows']}
- Raw mass-model rows: {summary['raw_mass_model_rows']}
- Parent sample before strict-W minimum: {summary['parent_galaxies']}
- Retained galaxies: {summary['retained_galaxies']}
- Retained per-radius rows: {summary['retained_per_radius_rows']}
- Strict-W rows: {summary['strictW_rows']}

## Key Model Results

- Model C `T_RAR ~ X_A + logVflat + logSBeff + T + Inc`: beta `{model_c['beta']:.9f}`, robust SE `{model_c['robust_se']:.9f}`, p `{model_c['p_value']:.6g}`, jackknife negative fraction `{model_c['jackknife_negative_fraction']:.3f}`.
- Model D `T_RAR ~ X_A_perp + logVflat + logSBeff + T + Inc`: beta `{model_d['beta']:.9f}`, robust SE `{model_d['robust_se']:.9f}`, p `{model_d['p_value']:.6g}`, jackknife negative fraction `{model_d['jackknife_negative_fraction']:.3f}`.

## Pass Conditions

{cond_lines}

## Raw Hashes

{hash_lines}

## Boundary Note

This was Stage E1 only. No gas-aware test, gas inversion, `B_chi` inference, M/L fitting, source-gate rescue, GSG confirmation/retirement, or DM/MOND/cosmology claim was performed.
"""
    (OUT_DIR / "STAGE_E1_INDEPENDENT_RECONSTRUCTION_RESULTS.md").write_text(md, encoding="utf-8")

    status = f"""# Worker Status

Status: `{verdict}`

Updated: {now_iso()}

Owned folder: `{OUT_DIR}`

Stage E1 independent reconstruction is complete. Fresh tables were written before post-freeze Stage C/D comparison scanning.
"""
    (OUT_DIR / "WORKER_STATUS.md").write_text(status, encoding="utf-8")

    handoff = f"""# Compact Handoff

Verdict: `{verdict}`

Stage E1 fresh-code reconstruction completed in this folder only.

Counts: retained galaxies `{summary['retained_galaxies']}`, retained per-radius rows `{summary['retained_per_radius_rows']}`, strict-W rows `{summary['strictW_rows']}`.

Model C beta_XA `{model_c['beta']:.9f}`, p `{model_c['p_value']:.6g}`. Model D beta_X_A_perp `{model_d['beta']:.9f}`, p `{model_d['p_value']:.6g}`.

Blockers: `{'; '.join(payload['blockers']) if payload['blockers'] else 'none'}`

Forbidden later-stage actions were not performed.
"""
    (OUT_DIR / "COMPACT_HANDOFF.md").write_text(handoff, encoding="utf-8")


def write_manifest() -> None:
    manifest_path = OUT_DIR / "MANIFEST.sha256"
    rows = []
    for path in sorted(OUT_DIR.rglob("*")):
        if path.is_dir() or path == manifest_path:
            continue
        rel = path.relative_to(OUT_DIR)
        rows.append((sha256_file(path), str(rel)))
    with manifest_path.open("w", encoding="utf-8") as f:
        for digest, rel in rows:
            f.write(f"{digest}  {rel}\n")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "WORKER_LOG.jsonl").write_text("", encoding="utf-8")
    append_log("stage_e1_reconstruction_started", output_dir=str(OUT_DIR))

    input_hashes = check_inputs()
    if not all(info["matches_expected"] for info in input_hashes.values()):
        append_log("input_hash_mismatch", hashes=input_hashes)
        raise RuntimeError("one or more input hashes did not match expected values")

    meta = parse_metadata(METADATA_PATH)
    mass = load_mass_models(INPUTS["MassModels_Lelli2016c.mrt"])
    parent, galaxy, per_radius = build_tables(meta, mass)
    reg, suppression = regression_tables(galaxy)

    summary = {
        "metadata_rows": int(len(meta)),
        "raw_mass_model_rows": int(len(mass)),
        "raw_mass_model_galaxies": int(mass["galaxy_id"].nunique()),
        "parent_galaxies": int(len(parent)),
        "parent_per_radius_rows": int(mass.merge(parent[["galaxy_id"]], on="galaxy_id", how="inner").shape[0]),
        "retained_galaxies": int(len(galaxy)),
        "retained_per_radius_rows": int(len(per_radius)),
        "strictW_rows": int(per_radius["W_strict_v1"].sum()),
        "f571_8_r022_G_L_total": float(
            per_radius.loc[
                (per_radius["galaxy_id"] == "F571-8") & np.isclose(per_radius["R_kpc"], 0.22),
                "G_L_total",
            ].iloc[0]
        ),
    }
    append_log("row_counts_computed", summary=summary)

    write_csvs(galaxy, per_radius, reg, suppression)
    write_plots(galaxy)
    comparison = compare_to_stage_cd(galaxy, per_radius, reg)

    conditions = pass_conditions(summary, reg)
    write_method(input_hashes)
    write_results(summary, conditions, reg, input_hashes, comparison)
    append_log("stage_e1_reconstruction_finished", verdict="PASS_RECONSTRUCTION" if all(conditions.values()) else "FAIL_RECONSTRUCTION")
    append_log("manifest_about_to_be_written")
    write_manifest()


if __name__ == "__main__":
    main()
