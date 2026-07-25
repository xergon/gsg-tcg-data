#!/usr/bin/env python3
"""Post-process the streamed KiDS-1000 aperture extract.

Pure selection + counting.  NO shear estimator, no Gamma_B, no profile, no stacked
contrast is computed anywhere in this file -- see the row's standing quarantine."""
import os, csv, math, numpy as np, time
from scipy.spatial import cKDTree
import pyarrow as pa, pyarrow.parquet as pq

BASE = os.path.dirname(os.path.abspath(__file__))
src  = np.load(os.path.join(BASE, "kids1000_sami_aperture_sources.npy"))
print("streamed rows:", len(src))

gal = list(csv.DictReader(open(os.path.join(BASE, "sami_gama_targets.csv"))))
gra = np.array([float(g["RA_OBJ"]) for g in gal])
gde = np.array([float(g["DEC_OBJ"]) for g in gal])
cid = np.array([g["CATID"] for g in gal])
print("lenses:", len(gal))

def xyz(ra, de):
    r = np.radians(ra); d = np.radians(de)
    return np.stack([np.cos(d)*np.cos(r), np.cos(d)*np.sin(r), np.sin(d)], axis=1)

gt = cKDTree(xyz(gra, gde))
sx = xyz(src["RAJ2000"].astype(np.float64), src["DECJ2000"].astype(np.float64))

R_KEEP = 15.0/60.0                                   # deg
chord  = 2.0*np.sin(np.radians(R_KEEP)/2.0)
d, i   = gt.query(sx, k=1, distance_upper_bound=chord)
inside = np.isfinite(d)
print("exact-radius survivors: %d of %d (%.3f)" % (inside.sum(), len(src), inside.mean()))
src = src[inside]; sx = sx[inside]

# ---- per-lens source counts (counting only) ----
RADII = [1.0, 2.0, 3.0, 5.0, 10.0, 15.0]             # arcmin
mask0 = (src["MASK"] == 0)
fit0  = (src["fitclass"] == 0)
counts = {}; counts_clean = {}
st = cKDTree(sx)
idx_clean = np.nonzero(mask0 & fit0 & (src["weight"] > 0))[0]
st_clean = cKDTree(sx[idx_clean])
gxyz = xyz(gra, gde)
for r in RADII:
    ch = 2.0*np.sin(np.radians(r/60.0)/2.0)
    counts[r]       = np.array([len(a) for a in st.query_ball_point(gxyz, ch)], dtype=np.int32)
    counts_clean[r] = np.array([len(a) for a in st_clean.query_ball_point(gxyz, ch)], dtype=np.int32)
    print("  r=%4.1f'  median all=%6.1f  median MASK==0 & fitclass==0 & w>0 = %6.1f" %
          (r, np.median(counts[r]), np.median(counts_clean[r])))

hdr = ["CATID","RA_OBJ","DEC_OBJ","z_spec","PA_GASKIN","PA_GASKIN_ERR","LAMBDAR_RE"] + \
      ["n_src_%gp"%r for r in RADII] + ["n_clean_%gp"%r for r in RADII]
with open(os.path.join(BASE, "per_lens_source_counts.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(hdr)
    for k, g in enumerate(gal):
        w.writerow([g["CATID"], g["RA_OBJ"], g["DEC_OBJ"], g["z_spec"], g["PA_GASKIN"],
                    g["PA_GASKIN_ERR"], g["LAMBDAR_RE"]] +
                   [int(counts[r][k]) for r in RADII] + [int(counts_clean[r][k]) for r in RADII])
print("wrote per_lens_source_counts.csv")

# ---- lenses with zero KiDS coverage: the EMPIRICAL footprint check ----
for r in (5.0, 15.0):
    z = int((counts[r] == 0).sum())
    print("lenses with ZERO KiDS gold sources within %4.1f arcmin: %d of %d" % (r, z, len(gal)))

# ---- MASK / fitclass tally over the whole extract (verification, not a lensing product) ----
import collections
mc = collections.Counter(src["MASK"].tolist())
print("MASK values over %d extracted sources:" % len(src))
for v, k in mc.most_common(10):
    print("   MASK=%6d  n=%9d  %6.2f%%  bits=%s" % (v, k, 100.0*k/len(src), bin(int(v))))
print("fitclass:", dict(collections.Counter(src["fitclass"].tolist())))
zb = src["Z_B"]
print("Z_B range %.4f .. %.4f ; fraction in (0.1,1.2] = %.6f" % (zb.min(), zb.max(), np.mean((zb>0.1)&(zb<=1.2))))

# ---- parquet: full 15' extract ----
tbl = pa.table({n: pa.array(src[n]) for n in src.dtype.names})
pq.write_table(tbl, os.path.join(BASE, "kids1000_sami_15arcmin_sources.parquet"),
               compression="zstd", compression_level=9)
print("full parquet:", os.path.getsize(os.path.join(BASE, "kids1000_sami_15arcmin_sources.parquet")), "B")

# ---- compact: 5' radius, essential columns, for a sandbox-sized load ----
ch5 = 2.0*np.sin(np.radians(5.0/60.0)/2.0)
d5, _ = gt.query(sx, k=1, distance_upper_bound=ch5)
m5 = np.isfinite(d5)
keep = ["RAJ2000","DECJ2000","e1","e2","weight","Z_B","MASK","fitclass",
        "PSF_e1","PSF_e2","THELI_INT","model_SNratio"]
sub = src[m5]
tbl5 = pa.table({n: pa.array(sub[n]) for n in keep})
pq.write_table(tbl5, os.path.join(BASE, "kids1000_sami_5arcmin_compact.parquet"),
               compression="zstd", compression_level=9)
print("5' compact rows:", len(sub), "bytes:",
      os.path.getsize(os.path.join(BASE, "kids1000_sami_5arcmin_compact.parquet")))
