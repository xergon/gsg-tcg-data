#!/usr/bin/env python3
"""
i2 — Brouwer(2021)/Mistele(2024) ISOLATION RADIUS for every GAMA lens.

R_isol == 3D comoving distance to the nearest neighbouring galaxy having at
least 10% of the lens' stellar mass  (Brouwer et al. 2021 criterion, adopted
verbatim by Mistele et al. 2024 §3 with R_isol = 4 Mpc/h70).

Neighbour pool: EVERY GAMA-II equatorial galaxy with NQ>=3 and a stellar mass,
NOT only the r<19.8 main-survey lens sample -- being stricter about the pool
makes the isolation criterion harder to pass, which is the conservative choice.

Also computes:
  * R_isol_proj  : projected (transverse comoving) analogue
  * d_edge_deg   : angular distance to the nearest GAMA field boundary, so that
                   edge-inflated isolation can be flagged (GAMA is 3 x 12x5 deg
                   rectangles; a lens 1 deg from an edge has no neighbours
                   beyond it and looks spuriously isolated).
"""
import os, json
import numpy as np
import pandas as pd
from astropy.io import fits
from scipy.spatial import cKDTree

G = "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/fleet_fanout_harvest_2026_07_25/i2_gama_kidslegacy/gama"
B = "/Users/resorb/Documents/My Papers/Research Program Management/implementation_lanes/fleet_fanout_harvest_2026_07_25/i2_gama_kidslegacy/build"

C_KMS, H0, OM, OL = 299792.458, 70.0, 0.3, 0.7
DH = C_KMS / H0
_zg = np.linspace(0.0, 1.5, 30001)
_E = np.sqrt(OM * (1 + _zg) ** 3 + OL)
_Dc = DH * np.concatenate(([0.0], np.cumsum(0.5 * (1 / _E[1:] + 1 / _E[:-1]) * np.diff(_zg))))
comoving = lambda z: np.interp(z, _zg, _Dc)

lens = pd.read_parquet(os.path.join(B, "gama_lens_stage_pre_isolation.parquet"))
print(f"lens rows: {len(lens):,}")

# ------------------------------------------------- neighbour pool
h = fits.open(os.path.join(G, "TilingCatv46.fits"), memmap=True); t = h[1].data
pool = pd.DataFrame({"CATAID": np.asarray(t["CATAID"], dtype=np.int64),
                     "RA": np.asarray(t["RA"], dtype=np.float64),
                     "DEC": np.asarray(t["DEC"], dtype=np.float64),
                     "NQ": np.asarray(t["NQ"], dtype=np.int16),
                     "SC": np.asarray(t["SURVEY_CLASS"], dtype=np.int16)})
h.close()
h = fits.open(os.path.join(G, "DistancesFramesv14.fits"), memmap=True); d = h[1].data
dfr = pd.DataFrame({"CATAID": np.asarray(d["CATAID"], dtype=np.int64),
                    "Z_CMB": np.asarray(d["Z_CMB"], dtype=np.float64)})
h.close()
h = fits.open(os.path.join(G, "StellarMassesLambdarv24.fits"), memmap=True); m = h[1].data
sm = pd.DataFrame({"CATAID": np.asarray(m["CATAID"], dtype=np.int64),
                   "logmstar": np.asarray(m["logmstar"], dtype=np.float64)})
h.close()

pool = pool.merge(dfr, on="CATAID").merge(sm, on="CATAID")
pool = pool[(pool.NQ >= 3) & (pool.Z_CMB > 0.002) & (pool.Z_CMB < 0.6)
            & np.isfinite(pool.logmstar) & (pool.logmstar > 5) & (pool.logmstar < 13)]
pool = pool.reset_index(drop=True)
print(f"neighbour pool: {len(pool):,} GAMA galaxies (all SURVEY_CLASS, NQ>=3, has logmstar)")

def xyz(ra, dec, dc):
    r = np.radians(ra); dd = np.radians(dec)
    return np.column_stack([dc * np.cos(dd) * np.cos(r),
                            dc * np.cos(dd) * np.sin(r),
                            dc * np.sin(dd)])

pool_dc = comoving(pool.Z_CMB.to_numpy())
P = xyz(pool.RA.to_numpy(), pool.DEC.to_numpy(), pool_dc)
pool_lm = pool.logmstar.to_numpy()
pool_id = pool.CATAID.to_numpy()

# mass-sorted pool so that "mass >= thr" is a contiguous prefix
order = np.argsort(-pool_lm)
P_s, lm_s, id_s = P[order], pool_lm[order], pool_id[order]

lens_lm = lens["logmstar"].to_numpy(dtype=float)
lens_dc = comoving(lens["Z_CMB"].to_numpy())
L = xyz(lens.RA.to_numpy(), lens.DEC.to_numpy(), lens_dc)
lens_id = lens.CATAID.to_numpy()

thr = lens_lm - 1.0                       # neighbour must have >= 10% of lens M*
thr_b = np.where(np.isfinite(thr), np.floor(thr * 10) / 10.0, np.nan)   # 0.1 dex groups

R_isol = np.full(len(lens), np.nan)
R_isol_proj = np.full(len(lens), np.nan)
nb_id = np.full(len(lens), -1, dtype=np.int64)

ubins = np.unique(thr_b[np.isfinite(thr_b)])
print(f"{len(ubins)} mass-threshold groups")
for k, tb in enumerate(ubins):
    sel = np.where(thr_b == tb)[0]
    # prefix of mass-sorted pool with logmstar >= tb  (tb <= true threshold => conservative superset)
    cut = np.searchsorted(-lm_s, -tb, side="right")
    if cut < 2:
        continue
    tree = cKDTree(P_s[:cut])
    dd, ii = tree.query(L[sel], k=4, workers=1)
    for j, li in enumerate(sel):
        for a in range(4):
            if ii[j, a] < cut and id_s[ii[j, a]] != lens_id[li]:
                R_isol[li] = dd[j, a]
                nb_id[li] = id_s[ii[j, a]]
                break
    if k % 5 == 0:
        print(f"  group {k+1}/{len(ubins)} thr>={tb:.1f} poolsize={cut:,} n_lens={len(sel):,}")

lens["R_isol_Mpc_h70"] = R_isol
lens["R_isol_neighbour_CATAID"] = nb_id

# ---- projected analogue (transverse comoving separation at the lens distance)
#      computed with the same mass condition, using a 2D tree on the tangent plane
for tb in ubins:
    sel = np.where(thr_b == tb)[0]
    cut = np.searchsorted(-lm_s, -tb, side="right")
    if cut < 2:
        continue
    # unit vectors
    u_p = P_s[:cut] / np.linalg.norm(P_s[:cut], axis=1)[:, None]
    tree = cKDTree(u_p)
    u_l = L[sel] / np.linalg.norm(L[sel], axis=1)[:, None]
    dd, ii = tree.query(u_l, k=4, workers=1)
    for j, li in enumerate(sel):
        for a in range(4):
            if ii[j, a] < cut and id_s[ii[j, a]] != lens_id[li]:
                chord = dd[j, a]
                theta = 2 * np.arcsin(np.clip(chord / 2, 0, 1))
                R_isol_proj[li] = theta * lens_dc[li]
                break
lens["R_isol_proj_Mpc_h70"] = R_isol_proj

# ---- distance to GAMA field edge (deg)
FIELDS = {"G09": (129.0, 141.0, -2.0, 3.0),
          "G12": (174.0, 186.0, -3.0, 2.0),
          "G15": (211.5, 223.5, -2.0, 3.0)}
ra, dec = lens.RA.to_numpy(), lens.DEC.to_numpy()
field = np.full(len(lens), "OUT", dtype=object)
d_edge = np.full(len(lens), np.nan)
for name, (r0, r1, d0, d1) in FIELDS.items():
    inn = (ra >= r0) & (ra <= r1) & (dec >= d0) & (dec <= d1)
    field[inn] = name
    d_edge[inn] = np.minimum.reduce([
        (ra[inn] - r0) * np.cos(np.radians(dec[inn])),
        (r1 - ra[inn]) * np.cos(np.radians(dec[inn])),
        dec[inn] - d0, d1 - dec[inn]])
lens["GAMA_FIELD"] = field
lens["d_edge_deg"] = d_edge

out = os.path.join(B, "gama_lens_with_isolation.parquet")
lens.to_parquet(out, index=False)

print("\n================ ISOLATION SUMMARY (H0=70) ================")
print(f"R_isol computed for {int(np.isfinite(R_isol).sum()):,} / {len(lens):,}")
for cut in [1.0, 2.0, 3.0, 4.0, 5.0]:
    n = int(np.nansum(R_isol > cut))
    print(f"  R_isol > {cut:.0f} Mpc/h70              : {n:>8,}")
for cut in [0.5, 1.0, 2.0]:
    n = int(np.nansum(R_isol_proj > cut))
    print(f"  R_isol_proj > {cut:.1f} Mpc/h70         : {n:>8,}")
zc = (lens.Z_CMB > 0.1) & (lens.Z_CMB < 0.5)
print(f"\n  0.1 < z_cmb < 0.5 (Mistele window)   : {int(zc.sum()):>8,}")
for cut in [2.0, 3.0, 4.0]:
    n = int(np.nansum((R_isol > cut) & zc))
    print(f"  + R_isol > {cut:.0f} Mpc/h70            : {n:>8,}")
print(f"\n  GroupID == 0 (GAMA G3C ungrouped)    : {int((lens.GroupID==0).sum()):>8,}")
print(f"  GroupID == 0 AND 0.1<z<0.5           : {int(((lens.GroupID==0)&zc).sum()):>8,}")
print("\nfield counts:", lens.GAMA_FIELD.value_counts().to_dict())
print("wrote", out)
