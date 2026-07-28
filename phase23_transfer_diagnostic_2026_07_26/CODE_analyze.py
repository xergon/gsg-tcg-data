#!/usr/bin/env python3
"""Phase-23 locked-vector transfer diagnostic: per-galaxy + per-ring decomposition.
COMPUTE ONLY.  No refitting, no model modification, no tuning.
"""
from __future__ import annotations
import os, sys, json, math
import numpy as np
import pandas as pd

SCRATCH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRATCH)
from build_tables import (EV, evidence_pair, per_ring_dln, LANES, KPC_M,  # noqa
                          Y_DISK, Y_BULGE)

OUT = os.path.join(SCRATCH, "phase23_transfer_diagnostic_2026_07_26")
os.makedirs(OUT, exist_ok=True)

SRC_C = os.path.join(LANES, "phase23_external_heldout_sources_2026_07_22",
                     "C_things_littlethings")
SRC_B = os.path.join(LANES, "phase23_external_heldout_sources_2026_07_22",
                     "B_little_things_oh2015")

# --------------------------------------------------------------- load tables
sparc = pd.read_pickle(os.path.join(SCRATCH, "tierA_sparc.pkl"))
lt_pub = pd.read_pickle(os.path.join(SCRATCH, "tierA_lt12_pub.pkl"))
lt_y05 = pd.read_pickle(os.path.join(SCRATCH, "tierA_lt12_y05.pkl"))
th_wb = pd.read_pickle(os.path.join(SCRATCH, "tierA_things4_bulge.pkl"))
th_nb = pd.read_pickle(os.path.join(SCRATCH, "tierA_things4_nobulge.pkl"))
sp_t1 = pd.read_pickle(os.path.join(SCRATCH, "sparc_table1.pkl"))
lt_meta = json.load(open(os.path.join(SCRATCH, "lt_meta.json")))

PRIMARY = {"sparc": sparc, "little_things_12": lt_pub, "things_4": th_wb}
ALT = {"little_things_12": lt_y05, "things_4": th_nb}


def joint_and_per_galaxy(tab):
    p = EV.prepare(tab)
    joint = evidence_pair(p)
    dln, gp_g, gp_m = per_ring_dln(p, joint["sigma_int_gate"], joint["sigma_int_mond"])
    t = p["table"].copy()
    t["dlnB_ring"] = dln
    t["g_pred_gate"] = gp_g
    t["g_pred_mond"] = gp_m
    rows = []
    for gal, sub in t.groupby("Galaxy", sort=True):
        pg = EV.prepare(sub)
        r = evidence_pair(pg)
        rows.append(dict(galaxy=gal, n_rings=int(pg["N"]),
                         dlnB_locked_minus_MOND=r["dlnB"],
                         lnZ_gate=r["lnZ_gate"], lnZ_mond=r["lnZ_mond"],
                         sigma_int_gate_dex=r["sigma_int_gate"],
                         sigma_int_mond_dex=r["sigma_int_mond"],
                         dlnL_sum_at_joint_sigma=float(sub["dlnB_ring"].sum())))
    return joint, pd.DataFrame(rows), t


results, ring_tabs = {}, {}
for name, tab in PRIMARY.items():
    j, pg, rt = joint_and_per_galaxy(tab)
    results[name] = (j, pg)
    ring_tabs[name] = rt
    print(f"[PRIMARY] {name:18s} N={len(rt):5d} ngal={pg.shape[0]:4d} "
          f"joint dlnB={j['dlnB']:+9.4f}  sum(per-gal dlnB)={pg.dlnB_locked_minus_MOND.sum():+9.4f}"
          f"  sum(ring)={rt.dlnB_ring.sum():+9.4f}")

alt_pg = {}
for name, tab in ALT.items():
    j, pg, _ = joint_and_per_galaxy(tab)
    alt_pg[name] = pg
    print(f"[ALT]     {name:18s} joint dlnB={j['dlnB']:+9.4f}")
    print("   per-gal:", {r.galaxy: round(r.dlnB_locked_minus_MOND, 3)
                          for r in pg.itertuples()})
for name in PRIMARY:
    print(f"[PRIMARY per-gal] {name}:",
          {r.galaxy: round(r.dlnB_locked_minus_MOND, 3)
           for r in results[name][1].itertuples()} if name != "sparc" else "(163 rows)")

# ------------------------------------------------------------- covariates
G_KPC = 4.300917270e-6            # kpc Msun^-1 (km/s)^2
HE_SPARC = 1.33                   # SPARC MHI -> gas mass convention


def sparc_cov():
    t = sp_t1.copy()
    t["Mstar_Msun"] = Y_DISK * t["L36"] * 1e9
    t["Mgas_Msun"] = HE_SPARC * t["MHI"] * 1e9
    t["Mbar_Msun"] = t["Mstar_Msun"] + t["Mgas_Msun"]
    t["gas_fraction"] = t["Mgas_Msun"] / t["Mbar_Msun"]
    out = pd.DataFrame(dict(
        galaxy=t["Galaxy"], morph_type_T=t["T"], distance_Mpc=t["D"],
        e_distance_Mpc=t["e_D"], distance_method_code=t["f_D"],
        inclination_deg=t["Inc"], e_inclination_deg=t["e_Inc"],
        Vflat_kms=t["Vflat"], e_Vflat_kms=t["e_Vflat"],
        Mstar_Msun=t["Mstar_Msun"], Mgas_Msun=t["Mgas_Msun"],
        Mbar_Msun=t["Mbar_Msun"], gas_fraction=t["gas_fraction"],
        central_SB_disk_Lsun_pc2=t["SBdisk"], SB_eff_Lsun_pc2=t["SBeff"],
        Rdisk_kpc=t["Rdisk"], Reff_kpc=t["Reff"], RHI_kpc=t["RHI"],
        quality_flag=t["Q"]))
    return out


def lt_cov():
    oh1 = pd.read_csv(os.path.join(SRC_B, "oh2015_table1_galaxy_properties.csv"))
    oh2 = pd.read_csv(os.path.join(SRC_B, "oh2015_table2_massmodel_results.csv"))
    def norm(s):
        return (str(s).upper().replace("_", "").replace(" ", "")
                .replace("CVNIDWA", "CVNLDWA"))
    oh1["_k"] = oh1["Name"].map(norm)
    oh2["_k"] = oh2["Name"].map(norm)
    rows = []
    for gal, m in lt_meta.items():
        k = norm(gal)
        r1 = oh1[oh1._k == k]
        r2 = oh2[oh2._k == k]
        mg, ms = m["m_gas_Msun"], m["m_stars_Msun"]
        rows.append(dict(
            galaxy=gal, morph_type_T=np.nan,
            distance_Mpc=m["distance_Mpc"], e_distance_Mpc=m["e_distance_Mpc"],
            distance_method_code="LT_sample_yaml",
            inclination_deg=m["inc_deg"], e_inclination_deg=m["e_inc_deg"],
            Vflat_kms=(float(r2["V_Rmax_kms"].iloc[0]) if len(r2) else np.nan),
            e_Vflat_kms=np.nan,
            Mstar_Msun=ms, Mgas_Msun=mg, Mbar_Msun=ms + mg,
            gas_fraction=mg / (ms + mg),
            central_SB_disk_Lsun_pc2=np.nan, SB_eff_Lsun_pc2=np.nan,
            Rdisk_kpc=np.nan, Reff_kpc=np.nan,
            RHI_kpc=(float(r2["Rmax_kpc"].iloc[0]) if len(r2) else np.nan),
            quality_flag="LT_regular_rotation",
            abs_Vmag=(float(r1["VMag_mag"].iloc[0]) if len(r1) else np.nan),
            metallicity_12logOH=(float(r1["Ab_OH_12plogOH"].iloc[0]) if len(r1) else np.nan),
            y_star_fit=m["y_fit"]))
    return pd.DataFrame(rows)


def things_cov():
    w = pd.read_csv(os.path.join(SRC_C, "walter2008_table1_things_sample.csv"))
    w["_k"] = w["Name"].astype(str).str.replace(" ", "", regex=False).str.upper()
    rows = []
    for gal in ["NGC925", "NGC3031", "NGC3621", "NGC4736"]:
        r = w[w._k == gal]
        sub = th_wb[th_wb.Galaxy == gal]
        # baryonic masses from the model curves themselves (V^2 R / G at last ring)
        last = sub.iloc[-1]
        ms = Y_DISK * last["Vdisk"] ** 2 * last["R"] / G_KPC
        mb_bulge = Y_BULGE * last["Vbul"] ** 2 * last["R"] / G_KPC
        mg = abs(last["Vgas"]) * last["Vgas"] * last["R"] / G_KPC
        rows.append(dict(
            galaxy=gal, morph_type_T=(float(r["TT_type"].iloc[0]) if len(r) else np.nan),
            distance_Mpc=(float(r["Dist_Mpc"].iloc[0]) if len(r) else np.nan),
            e_distance_Mpc=np.nan,
            distance_method_code=(str(r["r_Dist"].iloc[0]) if len(r) else "NOT_RECORDED"),
            inclination_deg=(float(r["incl_deg"].iloc[0]) if len(r) else np.nan),
            e_inclination_deg=np.nan,
            Vflat_kms=float(sub["Vobs"].iloc[-5:].mean()), e_Vflat_kms=np.nan,
            Mstar_Msun=ms + mb_bulge, Mgas_Msun=mg, Mbar_Msun=ms + mb_bulge + mg,
            gas_fraction=mg / (ms + mb_bulge + mg),
            central_SB_disk_Lsun_pc2=np.nan, SB_eff_Lsun_pc2=np.nan,
            Rdisk_kpc=np.nan, Reff_kpc=np.nan, RHI_kpc=np.nan,
            quality_flag="deBlok2008_massmodel_sample",
            abs_Bmag=(float(r["BMAG_abs"].iloc[0]) if len(r) else np.nan),
            metallicity_12logOH=(float(r["Metal_12plogOH"].iloc[0]) if len(r) else np.nan)))
    return pd.DataFrame(rows)


COV = {"sparc": sparc_cov(), "little_things_12": lt_cov(), "things_4": things_cov()}

# ------------------------------------------------------- assemble per-galaxy
pg_all = []
for name in PRIMARY:
    pg = results[name][1].copy()
    pg["sample"] = name
    cov = COV[name]
    m = pg.merge(cov, on="galaxy", how="left")
    rt = ring_tabs[name]
    agg = rt.groupby("Galaxy").agg(R_min_kpc=("R", "min"), R_max_kpc=("R", "max"),
                                   gbar_median=("gbar", "median"),
                                   gobs_median=("gobs", "median")).reset_index()
    agg = agg.rename(columns={"Galaxy": "galaxy"})
    m = m.merge(agg, on="galaxy", how="left")
    m["R_min_over_Rd"] = m["R_min_kpc"] / m["Rdisk_kpc"]
    m["R_max_over_Rd"] = m["R_max_kpc"] / m["Rdisk_kpc"]
    # mean baryonic surface density inside R_max  (Msun / pc^2)
    m["mean_Sigma_bar_Msun_pc2"] = m["Mbar_Msun"] / (
        math.pi * (m["R_max_kpc"] * 1000.0) ** 2)
    if name in alt_pg:
        a = alt_pg[name][["galaxy", "dlnB_locked_minus_MOND"]].rename(
            columns={"dlnB_locked_minus_MOND": "dlnB_alt_ML_convention"})
        m = m.merge(a, on="galaxy", how="left")
    else:
        m["dlnB_alt_ML_convention"] = np.nan
    pg_all.append(m)
pg_all = pd.concat(pg_all, ignore_index=True)

# class flags from the catalogues' own definitions
_T = pd.to_numeric(pg_all["morph_type_T"], errors="coerce").to_numpy(float)
pg_all["morph_type_T"] = _T
pg_all["class_dwarf_or_spiral"] = np.where(
    pg_all["sample"].to_numpy() == "little_things_12", "dwarf_irregular_LT_sample",
    np.where(~np.isfinite(_T), "NOT_RECORDED",
             np.where(_T >= 8, "dwarf_irregular_T>=8", "spiral_T<8")))
# SPARC HSB/LSB by the SPARC central disk SB (Lelli+2016 uses 100 Lsun/pc2)
pg_all["class_HSB_LSB"] = np.where(
    pg_all["central_SB_disk_Lsun_pc2"].isna(), "NOT_RECORDED",
    np.where(pg_all["central_SB_disk_Lsun_pc2"] >= 100.0, "HSB", "LSB"))

cols = ["sample", "galaxy", "n_rings", "dlnB_locked_minus_MOND",
        "dlnB_alt_ML_convention", "dlnL_sum_at_joint_sigma",
        "lnZ_gate", "lnZ_mond", "sigma_int_gate_dex", "sigma_int_mond_dex",
        "morph_type_T", "class_dwarf_or_spiral", "class_HSB_LSB",
        "distance_Mpc", "e_distance_Mpc", "distance_method_code",
        "inclination_deg", "e_inclination_deg", "Vflat_kms", "e_Vflat_kms",
        "Mbar_Msun", "Mstar_Msun", "Mgas_Msun", "gas_fraction",
        "central_SB_disk_Lsun_pc2", "SB_eff_Lsun_pc2", "mean_Sigma_bar_Msun_pc2",
        "Rdisk_kpc", "Reff_kpc", "RHI_kpc", "R_min_kpc", "R_max_kpc",
        "R_min_over_Rd", "R_max_over_Rd", "gbar_median", "gobs_median",
        "quality_flag", "abs_Vmag", "abs_Bmag", "metallicity_12logOH", "y_star_fit"]
for c in cols:
    if c not in pg_all.columns:
        pg_all[c] = np.nan
pg_all = pg_all[cols].sort_values(["sample", "galaxy"]).reset_index(drop=True)
pg_all.to_csv(os.path.join(OUT, "per_galaxy.csv"), index=False)
print("per_galaxy rows:", len(pg_all),
      dict(pg_all.groupby("sample").size()))

# ------------------------------------------------------------- per-ring file
rd = pg_all.set_index(["sample", "galaxy"])["Rdisk_kpc"].to_dict()
ring_out = []
for name, rt in ring_tabs.items():
    r = pd.DataFrame(dict(
        sample=name, galaxy=rt["Galaxy"].values, R_kpc=rt["R"].values,
        V_obs_kms=rt["Vobs"].values,
        V_bar_kms=np.sign(rt["Vb2"].values if "Vb2" in rt else rt["gbar"].values)
        * np.sqrt(np.abs(rt["Vb2"].values)) if "Vb2" in rt else np.nan,
        g_obs=rt["gobs"].values, g_bar=rt["gbar"].values,
        e_gobs=rt["e_gobs"].values,
        g_pred_gate=rt["g_pred_gate"].values, g_pred_mond=rt["g_pred_mond"].values,
        dlnB_ring=rt["dlnB_ring"].values))
    r["R_over_Rd"] = [ (row.R_kpc / rd.get((name, row.galaxy), np.nan))
                       if rd.get((name, row.galaxy), np.nan) == rd.get((name, row.galaxy), np.nan)
                       else np.nan for row in r.itertuples() ]
    ring_out.append(r)
ring_out = pd.concat(ring_out, ignore_index=True)
ring_out = ring_out[["sample", "galaxy", "R_kpc", "R_over_Rd", "V_obs_kms",
                     "V_bar_kms", "g_obs", "g_bar", "e_gobs",
                     "g_pred_gate", "g_pred_mond", "dlnB_ring"]]
ring_out.to_csv(os.path.join(OUT, "per_ring_FULL.csv"), index=False)
print("per_ring rows:", len(ring_out), dict(ring_out.groupby("sample").size()))

# ------------------------------------------------------------- correlations
from scipy import stats
COVARS = ["morph_type_T", "distance_Mpc", "e_distance_Mpc", "inclination_deg",
          "Vflat_kms", "Mbar_Msun", "Mstar_Msun", "Mgas_Msun", "gas_fraction",
          "central_SB_disk_Lsun_pc2", "SB_eff_Lsun_pc2",
          "mean_Sigma_bar_Msun_pc2", "Rdisk_kpc", "Reff_kpc", "RHI_kpc",
          "R_min_kpc", "R_max_kpc", "R_min_over_Rd", "R_max_over_Rd",
          "gbar_median", "gobs_median", "n_rings", "metallicity_12logOH"]
LOGCOV = {"Mbar_Msun", "Mstar_Msun", "Mgas_Msun", "central_SB_disk_Lsun_pc2",
          "SB_eff_Lsun_pc2", "mean_Sigma_bar_Msun_pc2", "gbar_median",
          "gobs_median"}

def corr_block(df, label):
    out = []
    y = df["dlnB_locked_minus_MOND"].to_numpy(float)
    for c in COVARS:
        x = pd.to_numeric(df[c], errors="coerce").to_numpy(float)
        if c in LOGCOV:
            x = np.where(x > 0, np.log10(np.where(x > 0, x, np.nan)), np.nan)
        ok = np.isfinite(x) & np.isfinite(y)
        n = int(ok.sum())
        if n < 4:
            out.append(dict(subset=label, covariate=c, transform=("log10" if c in LOGCOV else "linear"),
                            n=n, spearman_rho=np.nan, spearman_p=np.nan,
                            pearson_r=np.nan, pearson_p=np.nan)); continue
        rho, pr = stats.spearmanr(x[ok], y[ok])
        r, pp = stats.pearsonr(x[ok], y[ok])
        out.append(dict(subset=label, covariate=c,
                        transform=("log10" if c in LOGCOV else "linear"),
                        n=n, spearman_rho=float(rho), spearman_p=float(pr),
                        pearson_r=float(r), pearson_p=float(pp)))
    return pd.DataFrame(out)

ext = pg_all[pg_all["sample"] != "sparc"]
blocks = [corr_block(pg_all, "all_three_samples_pooled"),
          corr_block(ext, "external_heldout_pooled_LT12_plus_THINGS4"),
          corr_block(pg_all[pg_all["sample"] == "sparc"], "sparc_only")]
corr = pd.concat(blocks, ignore_index=True)
corr.to_csv(os.path.join(OUT, "correlations.csv"), index=False)
print("\n=== EXTERNAL-POOLED CORRELATIONS (n=16) ===")
print(blocks[1].to_string(index=False))
print("\n=== ALL POOLED (n<=179) top by |spearman| ===")
b0 = blocks[0].dropna(subset=["spearman_rho"]).reindex(
    blocks[0].dropna(subset=["spearman_rho"]).spearman_rho.abs().sort_values(ascending=False).index)
print(b0.to_string(index=False))

json.dump({k: results[k][0] for k in results}, open(os.path.join(OUT, "joint_evidence.json"), "w"), indent=1)
print("\nJOINT:", {k: round(results[k][0]["dlnB"], 4) for k in results})
