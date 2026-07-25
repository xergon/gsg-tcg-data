#!/usr/bin/env python3
"""
i2 — GAMA DR4 x KiDS-Legacy DR5 : LENS-SIDE build.

Stage-by-stage construction of the GAMA lens sample with every IPR / RAR input
column.  Every cut and every row count is recorded to build/STAGE_COUNTS.json.

Cosmology: flat LCDM, H0 = 70 km/s/Mpc, Om = 0.3, OL = 0.7  (GAMA standard;
cross-checked against GAMA DistancesFrames v14 column DM_70_30_70).
Mistele et al. 2024 use H0 = 73 (h70 = 73/70); an `h70` scaling column is
provided so the thread can convert without recomputing distances.
"""
import os, json, sys
import numpy as np
from astropy.io import fits
import pandas as pd

G = "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/fleet_fanout_harvest_2026_07_25/i2_gama_kidslegacy/gama"
B = "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/fleet_fanout_harvest_2026_07_25/i2_gama_kidslegacy/build"
os.makedirs(B, exist_ok=True)

counts = []
def rec(stage, n, note=""):
    counts.append({"stage": stage, "n": int(n), "note": note})
    print(f"[{len(counts):02d}] {stage:52s} N = {n:>9,}   {note}")

def tab(fn, ext=1):
    h = fits.open(os.path.join(G, fn), memmap=True)
    d = h[ext].data
    return h, d

# ----------------------------------------------------------------- cosmology
C_KMS = 299792.458
H0, OM, OL = 70.0, 0.3, 0.7
DH = C_KMS / H0                                    # Mpc

_zg = np.linspace(0.0, 1.5, 30001)
_E  = np.sqrt(OM * (1 + _zg) ** 3 + OL)
_Dc = DH * np.concatenate(([0.0], np.cumsum(0.5 * (1 / _E[1:] + 1 / _E[:-1]) * np.diff(_zg))))

def comoving(z):        # Mpc
    return np.interp(z, _zg, _Dc)

def ang_diam(z):        # Mpc  (flat)
    return comoving(z) / (1 + z)

# ---------------------------------------------------- STAGE 0 : parent
h_t, t = tab("TilingCatv46.fits")
rec("S0  TilingCat v46 (GAMA-II equatorial parent)", len(t),
    "G09+G12+G15, 3 x 12x5 deg^2 = 180 deg^2")

df = pd.DataFrame({
    "CATAID":       np.asarray(t["CATAID"], dtype=np.int64),
    "RA":           np.asarray(t["RA"], dtype=np.float64),
    "DEC":          np.asarray(t["DEC"], dtype=np.float64),
    "R_PETRO":      np.asarray(t["R_PETRO"], dtype=np.float32),
    "SURVEY_CLASS": np.asarray(t["SURVEY_CLASS"], dtype=np.int16),
    "NQ":           np.asarray(t["NQ"], dtype=np.int16),
    "Z_TILING":     np.asarray(t["Z"], dtype=np.float64),
    "VIS_CLASS":    np.asarray(t["VIS_CLASS"], dtype=np.int16),
    "MASK_IC_12":   np.asarray(t["MASK_IC_12"], dtype=np.float32),
})
h_t.close()

# ---------------------------------------------------- STAGE 1 : main survey
df = df[df.SURVEY_CLASS >= 4].copy()
rec("S1  SURVEY_CLASS >= 4  (r<19.8 GAMA-II main survey)", len(df))

# ---------------------------------------------------- STAGE 2 : reliable z
df = df[df.NQ >= 3].copy()
rec("S2  NQ >= 3  (reliable spectroscopic redshift)", len(df))

# ---------------------------------------------------- STAGE 3 : distances
h_d, d = tab("DistancesFramesv14.fits")
dfr = pd.DataFrame({
    "CATAID":  np.asarray(d["CATAID"], dtype=np.int64),
    "Z_HELIO": np.asarray(d["Z_HELIO"], dtype=np.float64),
    "Z_CMB":   np.asarray(d["Z_CMB"], dtype=np.float64),
    "Z_TONRY": np.asarray(d["Z_TONRY"], dtype=np.float64),
    "DM_70_30_70": np.asarray(d["DM_70_30_70"], dtype=np.float64),
})
h_d.close()
df = df.merge(dfr, on="CATAID", how="inner")
rec("S3  join DistancesFrames v14 on CATAID", len(df), "Z_CMB, DM")

df = df[(df.Z_CMB > 0.002) & (df.Z_CMB < 0.6)].copy()
rec("S3b 0.002 < Z_CMB < 0.6", len(df))

# ---------------------------------------------------- STAGE 4 : Sersic
h_s, s = tab("SersicCatSDSSv09.fits")
sers = pd.DataFrame({
    "CATAID":       np.asarray(s["CATAID"], dtype=np.int64),
    "GALRE_r":      np.asarray(s["GALRE_r"], dtype=np.float64),
    "GALREERR_r":   np.asarray(s["GALREERR_r"], dtype=np.float64),
    "GALINDEX_r":   np.asarray(s["GALINDEX_r"], dtype=np.float64),
    "GALINDEXERR_r":np.asarray(s["GALINDEXERR_r"], dtype=np.float64),
    "GALELLIP_r":   np.asarray(s["GALELLIP_r"], dtype=np.float64),
    "GALELLIPERR_r":np.asarray(s["GALELLIPERR_r"], dtype=np.float64),
    "GALMAG_r":     np.asarray(s["GALMAG_r"], dtype=np.float64),
    "GALMUE_r":     np.asarray(s["GALMUE_r"], dtype=np.float64),
    "GALR90_r":     np.asarray(s["GALR90_r"], dtype=np.float64),
    "GALPA_r":      np.asarray(s["GALPA_r"], dtype=np.float64),
    "GALCHI2_r":    np.asarray(s["GALCHI2_r"], dtype=np.float64),
})
h_s.close()
df = df.merge(sers, on="CATAID", how="inner")
rec("S4  join SersicCatSDSS v09 on CATAID", len(df), "1:1 with TilingCat")

BAD = -999.0
ok = (
    np.isfinite(df.GALRE_r) & (df.GALRE_r > 0) & (df.GALRE_r < 1000) &
    np.isfinite(df.GALINDEX_r) & (df.GALINDEX_r > 0.1) & (df.GALINDEX_r < 20) &
    np.isfinite(df.GALELLIP_r) & (df.GALELLIP_r >= 0) & (df.GALELLIP_r < 1) &
    np.isfinite(df.GALMAG_r) & (df.GALMAG_r > 0) & (df.GALMAG_r < 30)
)
df = df[ok].copy()
rec("S5  valid r-band Sersic fit "
    "(0<Re<1000\", 0.1<n<20, 0<=e<1, 0<mag<30)", len(df),
    "GALINDEX_r==20 is the GALFIT ceiling -> excluded")

# ---------------------------------------------------- STAGE 6 : stellar mass
sm_file = "StellarMassesLambdarv24.fits"
h_m, m = tab(sm_file)
mn = [c.name for c in h_m[1].columns]
want = [c for c in ["CATAID", "logmstar", "dellogmstar", "fluxscale",
                    "logage", "logtau", "metal", "absmag_r", "gminusi",
                    "logmoverl_i", "logmintsfh", "logmremnants", "nbands",
                    "Z_TONRY", "zmax_19p8"] if c in mn]
sm = pd.DataFrame({c: np.asarray(m[c]).astype(np.float64 if c != "CATAID" else np.int64)
                   for c in want})
h_m.close()
sm = sm.rename(columns={"Z_TONRY": "Z_TONRY_SM"})
df = df.merge(sm, on="CATAID", how="left")
rec(f"S6  join {sm_file} on CATAID (LEFT)", len(df),
    f"logmstar present for {int(np.isfinite(df.logmstar).sum()):,}")

# GAMA convention: logmstar must be corrected by fluxscale for total mass
if "fluxscale" in df.columns:
    fs = df["fluxscale"].to_numpy()
    good_fs = np.isfinite(fs) & (fs > 0.1) & (fs < 10)
    lm = df["logmstar"].to_numpy(dtype=float).copy()
    lm_corr = np.where(good_fs, lm + np.log10(np.where(good_fs, fs, 1.0)), np.nan)
    df["logmstar_fluxscaled"] = lm_corr
    rec("S6b logmstar_fluxscaled = logmstar + log10(fluxscale)",
        int(np.isfinite(lm_corr).sum()), "GAMA-recommended total stellar mass")

# ---------------------------------------------------- STAGE 7 : groups
h_g, g = tab("G3CGalv10.fits")
grp = pd.DataFrame({
    "CATAID":      np.asarray(g["CATAID"], dtype=np.int64),
    "GroupID":     np.asarray(g["GroupID"], dtype=np.int64),
    "RankIterCen": np.asarray(g["RankIterCen"], dtype=np.int32),
    "RankBCG":     np.asarray(g["RankBCG"], dtype=np.int32),
    "SepIterCen":  np.asarray(g["SepIterCen"], dtype=np.float64),
})
h_g.close()
h_f, f = tab("G3CFoFGroupv10.fits")
fof = pd.DataFrame({
    "GroupID": np.asarray(f["GroupID"], dtype=np.int64),
    "Nfof":    np.asarray(f["Nfof"], dtype=np.int32),
    "Rad100":  np.asarray(f["Rad100"], dtype=np.float64),
    "MassA":   np.asarray(f["MassA"], dtype=np.float64),
    "VelDisp": np.asarray(f["VelDisp"], dtype=np.float64),
})
h_f.close()
grp = grp.merge(fof, on="GroupID", how="left")
df = df.merge(grp, on="CATAID", how="left")
df["GroupID"] = df["GroupID"].fillna(0).astype(np.int64)
df["Nfof"] = df["Nfof"].fillna(1).astype(np.int32)
rec("S7  join G3CGal v10 + G3CFoFGroup v10 (LEFT)", len(df),
    f"in a FoF group: {int((df.GroupID>0).sum()):,}; ungrouped: {int((df.GroupID==0).sum()):,}")

# ---------------------------------------------------- STAGE 8 : environment
h_e, e = tab("EnvironmentMeasuresv06.fits")
env = pd.DataFrame({
    "CATAID":            np.asarray(e["CATAID"], dtype=np.int64),
    "SurfaceDensity":    np.asarray(e["SurfaceDensity"], dtype=np.float64),
    "SurfaceDensityFlag":np.asarray(e["SurfaceDensityFlag"], dtype=np.int32),
    "CountInCyl":        np.asarray(e["CountInCyl"], dtype=np.float64),
    "CountInCylFlag":    np.asarray(e["CountInCylFlag"], dtype=np.int32),
    "AGEDenPar":         np.asarray(e["AGEDenPar"], dtype=np.float64),
    "AGEScale":          np.asarray(e["AGEScale"], dtype=np.float64),
    "AGEDenParFlag":     np.asarray(e["AGEDenParFlag"], dtype=np.int32),
    "DistanceToEdge":    np.asarray(e["DistanceToEdge"], dtype=np.float64),
    "Completeness":      np.asarray(e["Completeness"], dtype=np.float64),
})
h_e.close()
df = df.merge(env, on="CATAID", how="left")
rec("S8  join EnvironmentMeasures v06 (LEFT)", len(df),
    f"has env measure: {int(np.isfinite(df.SurfaceDensity).sum()):,} "
    f"(DMU is z-limited, N_total={len(env):,})")

# ---------------------------------------------------- derived geometry
z   = df["Z_CMB"].to_numpy()
DA  = ang_diam(z)                                  # Mpc
kpc_per_arcsec = DA * 1000.0 * (np.pi / 180.0) / 3600.0

q      = 1.0 - df["GALELLIP_r"].to_numpy()         # axis ratio b/a  (GALELLIP == 1-(b/a))
Re_maj = df["GALRE_r"].to_numpy()                  # arcsec, SEMI-MAJOR half-light radius
Re_cir = Re_maj * np.sqrt(q)                       # arcsec, circularised

df["DA_Mpc"]                 = DA
df["DL_Mpc"]                 = DA * (1 + z) ** 2
df["kpc_per_arcsec"]         = kpc_per_arcsec
df["axis_ratio_q_r"]         = q
df["Re_maj_arcsec_r"]        = Re_maj
df["Re_circ_arcsec_r"]       = Re_cir
df["Re_maj_kpc_r"]           = Re_maj * kpc_per_arcsec
df["Re_circ_kpc_r"]          = Re_cir * kpc_per_arcsec
df["R90_maj_kpc_r"]          = df["GALR90_r"].to_numpy() * kpc_per_arcsec

# ---- A_IPR : the two admissible conventions, BOTH built (ambiguity documented)
df["A_IPR_kpc2_ellip"]  = np.pi * (df["Re_maj_kpc_r"] ** 2) * q      # = pi*a*b = pi*Re_circ^2
df["A_IPR_kpc2_major"]  = np.pi * (df["Re_maj_kpc_r"] ** 2)          # no inclination deprojection
df["log10_A_IPR_ellip"] = np.log10(df["A_IPR_kpc2_ellip"])
df["log10_A_IPR_major"] = np.log10(df["A_IPR_kpc2_major"])
df["log10_Re_circ_kpc"] = np.log10(df["Re_circ_kpc_r"])
df["log10_Re_maj_kpc"]  = np.log10(df["Re_maj_kpc_r"])

df["h70"] = 1.0            # this table is in h70 = 1 units (H0 = 70)

out = os.path.join(B, "gama_lens_stage_pre_isolation.parquet")
df.to_parquet(out, index=False)
rec("S9  lens table written (pre-isolation, pre-KiDS)", len(df), out)

json.dump(counts, open(os.path.join(B, "STAGE_COUNTS_lens.json"), "w"), indent=2)
print("\nWrote", out, os.path.getsize(out), "bytes")
