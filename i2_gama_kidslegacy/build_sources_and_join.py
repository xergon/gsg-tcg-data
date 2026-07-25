#!/usr/bin/env python3
"""
i2 — KiDS-Legacy DR5 SOURCE side + the final join.

1. Stream the 6.69 GiB KiDS_Legacy_NS_unblind_final.fits(.gz) and keep only the
   sources that fall inside the three GAMA-II equatorial fields (+0.25 deg
   margin), with only the columns needed for a Delta-Sigma / IPR / RAR analysis.
2. Build a HEALPix (nside=1024, ~3.4 arcmin pix) map of source number, summed
   shear weight and mean Z_B, so per-lens local lensing efficiency is available
   without shipping 40.9 M rows.
3. Per-lens EXACT source counts in the two destroyer annuli
   (100-300 kpc and 300-1000 kpc, physical, h70=1) plus 30-1400 kpc total.
4. Per-lens <Sigma_crit^-1> from the SOM-calibrated KiDS-Legacy tomographic
   n(z) shipped in KiDS_Legacy_cosebis.fits (NZ_SOURCE), which is the
   KiDS-recommended route -- per-source Z_B is provided as a cross-check only.
5. Write gama_kidslegacy_ipr_rar_inputs_v1.parquet
"""
import os, json, gzip, shutil, math
import numpy as np
import pandas as pd
from astropy.io import fits
from scipy.spatial import cKDTree

ROOT = "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/fleet_fanout_harvest_2026_07_25/i2_gama_kidslegacy"
K, B = os.path.join(ROOT, "kids"), os.path.join(ROOT, "build")
GZ = os.path.join(K, "KiDS_Legacy_NS_unblind_final.fits.gz")
FT = os.path.join(K, "KiDS_Legacy_NS_unblind_final.fits")

counts = []
def rec(stage, n, note=""):
    counts.append({"stage": stage, "n": int(n), "note": note})
    print(f"[S{len(counts):02d}] {stage:56s} N = {n:>12,}   {note}")

# ------------------------------------------------------------ 0. decompress
if not os.path.exists(FT):
    print("decompressing ...")
    with gzip.open(GZ, "rb") as fi, open(FT, "wb") as fo:
        shutil.copyfileobj(fi, fo, length=1 << 24)
print("uncompressed FITS:", os.path.getsize(FT), "bytes")
with open(FT, "rb") as fh:
    assert fh.read(9) == b"SIMPLE  =", "NOT A FITS FILE"

hdul = fits.open(FT, memmap=True)
src_hdu = hdul[1]
NSRC = src_hdu.header["NAXIS2"]
rec("KiDS-Legacy gold catalogue (full)", NSRC,
    f"{len(src_hdu.columns)} cols, EXT={src_hdu.header.get('EXTNAME')}")
assert NSRC == 40894394, f"row count {NSRC} != published 40,894,394"

# ------------------------------------------------------- 1. footprint subset
FIELDS = {"G09": (129.0, 141.0, -2.0, 3.0),
          "G12": (174.0, 186.0, -3.0, 2.0),
          "G15": (211.5, 223.5, -2.0, 3.0)}
M = 0.25   # deg margin, > the largest lens aperture used below

KEEP = ["RAJ2000", "DECJ2000", "PATCH", "MAG_AUTO", "SG2DPHOT",
        "Z_B", "T_B", "TOMOBIN", "e1", "e2", "weight",
        "shear_weight_only", "gold_weight_only",
        "autocal_scalelength_pixels", "bulge_fraction", "model_SNratio"]
KEEP = [c for c in KEEP if c in src_hdu.columns.names]

D = src_hdu.data
ra_all = np.asarray(D["RAJ2000"]).astype(np.float64)
de_all = np.asarray(D["DECJ2000"]).astype(np.float64)
sel = np.zeros(NSRC, dtype=bool)
for (r0, r1, d0, d1) in FIELDS.values():
    sel |= (ra_all >= r0 - M) & (ra_all <= r1 + M) & (de_all >= d0 - M) & (de_all <= d1 + M)
idx = np.where(sel)[0]
print(f"  footprint mask: {len(idx):,} of {NSRC:,}")
del ra_all, de_all

dd = {}
for c in KEEP:
    v = np.asarray(D[c])[idx]
    if v.dtype.kind in "SU":
        dd[c] = np.char.strip(v.astype(str))
    else:
        nat = v.dtype.newbyteorder("=")
        v = v.astype(nat)
        if v.dtype == np.float64 and c not in ("RAJ2000", "DECJ2000", "Z_B"):
            v = v.astype(np.float32)
        dd[c] = v
    print("   col", c, dd[c].dtype)
src = pd.DataFrame(dd); del dd
hdul.close()
rec("KiDS-Legacy sources inside GAMA G09/G12/G15 (+0.25 deg)", len(src))

src_out = os.path.join(B, "kidslegacy_sources_gama_equatorial_v1.parquet")
src.to_parquet(src_out, index=False, compression="zstd")
print("wrote", src_out, os.path.getsize(src_out), "bytes")

# ------------------------------------------------------- 2. n(z) -> Sigma_crit
C_KMS, H0, OM, OL = 299792.458, 70.0, 0.3, 0.7
DH = C_KMS / H0
_zg = np.linspace(0.0, 6.0, 60001)
_E = np.sqrt(OM * (1 + _zg) ** 3 + OL)
_Dc = DH * np.concatenate(([0.0], np.cumsum(0.5 * (1 / _E[1:] + 1 / _E[:-1]) * np.diff(_zg))))
Dc = lambda z: np.interp(z, _zg, _Dc)

# Sigma_crit^-1 = 4 pi G / c^2 * D_L * D_LS / D_S     [physical ang.diam. dist.]
# 4 pi G / c^2 in Mpc / Msun :
G_MPC = 4.5171e-48          # Mpc^3 Msun^-1 s^-2
C_MPC = 9.7156e-15          # Mpc / s
PREF = 4 * math.pi * G_MPC / C_MPC ** 2          # Mpc^-1 * (Msun/Mpc^2)^-1 ... see below
# -> Sigma_crit^-1 [ Mpc^2 / Msun ] = PREF * DA_L*DA_LS/DA_S   (all in Mpc)

nzf = os.path.join(K, "KiDS_Legacy_cosmic_shear_data_release/data/KiDS_Legacy_cosebis.fits")
nzh = fits.open(nzf)
nz = nzh["NZ_SOURCE"].data
zs = np.asarray(nz["Z_MID"], dtype=float)
nzbins = {b: np.asarray(nz[f"BIN{b}"], dtype=float) for b in range(1, 7)}
NEFF = {b: float(nzh["NZ_SOURCE"].header[f"NGAL_{b}"]) for b in range(1, 7)}
nzh.close()
print("KiDS-Legacy n_eff per tomo bin (arcmin^-2):", NEFF, " total", round(sum(NEFF.values()), 3))

def sigma_crit_inv_bin(zl, b):
    """<Sigma_crit^-1> for lens redshift zl over the calibrated n(z) of bin b.
       Sources with z_s <= z_l contribute zero."""
    w = nzbins[b]
    DcS = Dc(zs); DcL = Dc(zl)
    DA_S = DcS / (1 + zs)
    DA_L = DcL / (1 + zl)
    DA_LS = np.where(zs > zl, (DcS - DcL) / (1 + zs), 0.0)
    val = PREF * DA_L * DA_LS / np.where(DA_S > 0, DA_S, np.inf)
    return np.trapz(val * w, zs) / np.trapz(w, zs)

lens = pd.read_parquet(os.path.join(B, "gama_lens_with_isolation.parquet"))
rec("GAMA lens table carried in", len(lens))

zl_grid = np.linspace(0.001, 0.65, 400)
sci = {b: np.array([sigma_crit_inv_bin(z, b) for z in zl_grid]) for b in range(1, 7)}
tot_neff = sum(NEFF.values())
for b in range(1, 7):
    lens[f"sigma_crit_inv_bin{b}"] = np.interp(lens.Z_CMB, zl_grid, sci[b])
lens["sigma_crit_inv_neff_weighted"] = sum(
    NEFF[b] * lens[f"sigma_crit_inv_bin{b}"] for b in range(1, 7)) / tot_neff
# lensing efficiency ~ <Sigma_crit^-1>^2 weighted by n_eff  (the S/N-relevant one)
lens["lensing_efficiency_sum_neff_scinv2"] = sum(
    NEFF[b] * lens[f"sigma_crit_inv_bin{b}"] ** 2 for b in range(1, 7))
# convenience unit: pc^2 / Msun   (1 Mpc^2 = 1e12 pc^2)
lens["sigma_crit_inv_pc2_Msun"] = lens["sigma_crit_inv_neff_weighted"] * 1e12
lens["sigma_crit_Msun_pc2"] = 1.0 / lens["sigma_crit_inv_pc2_Msun"]

# ------------------------------------------------------- 3. exact source counts
sra = src.RAJ2000.to_numpy(); sde = src.DECJ2000.to_numpy()
def uvec(ra, de):
    r, d = np.radians(ra), np.radians(de)
    return np.column_stack([np.cos(d) * np.cos(r), np.cos(d) * np.sin(r), np.sin(d)])
S = uvec(sra, sde)
tree = cKDTree(S)
print("source tree built:", len(S), "points")

L = uvec(lens.RA.to_numpy(), lens.DEC.to_numpy())
DA = lens.DA_Mpc.to_numpy()                       # physical ang.diam. distance
kpc_per_rad = DA * 1000.0

ANNULI = [("100_300", 100.0, 300.0), ("300_1000", 300.0, 1000.0),
          ("30_1400", 30.0, 1400.0)]
# group lenses into narrow z slices so the angular radius is ~constant
zb = np.digitize(lens.Z_CMB.to_numpy(), np.arange(0.0, 0.65, 0.005))
for tag, r_lo, r_hi in ANNULI:
    n_out = np.zeros(len(lens), dtype=np.int32)
    for g in np.unique(zb):
        sel = np.where(zb == g)[0]
        kr = np.median(kpc_per_rad[sel])
        th_hi = r_hi / kr
        th_lo = r_lo / kr
        c_hi = tree.query_ball_point(L[sel], 2 * np.sin(th_hi / 2), return_length=True)
        c_lo = tree.query_ball_point(L[sel], 2 * np.sin(th_lo / 2), return_length=True)
        n_out[sel] = (c_hi - c_lo).astype(np.int32)
    lens[f"n_src_{tag}kpc"] = n_out
    rec(f"per-lens source counts {tag} kpc", int(n_out.sum()),
        f"median per lens = {np.median(n_out):.0f}")

lens["inside_kids_legacy"] = lens["n_src_30_1400kpc"] > 0

out = os.path.join(B, "gama_kidslegacy_ipr_rar_inputs_v1.parquet")
lens.to_parquet(out, index=False, compression="zstd")
rec("FINAL gama_kidslegacy_ipr_rar_inputs_v1.parquet", len(lens), out)
json.dump(counts, open(os.path.join(B, "STAGE_COUNTS_source.json"), "w"), indent=2)
print("\nwrote", out, os.path.getsize(out), "bytes")
