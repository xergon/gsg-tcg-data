# S9 — DESI LRG x Planck PR4 / ACT DR6 bandpower WINDOW FUNCTIONS + LRG dN/dz

Source: Zenodo record **12613408**, `zenodo_LRGxPR4-DR6.tar`
(md5 `7055fb98a70381292b18a9b0e06bd0c2`, verified against the Zenodo API record).
Everything below is extracted verbatim from
`zenodo_LRGxPR4-DR6/data/lrg_cross_pr4+dr6.json` (20,110,262 B) and
`zenodo_LRGxPR4-DR6/data/dNdz/*.txt`. **No rounding anywhere** — every float is written
with Python `repr()` (shortest round-trip representation of the exact float64).

## 0. Count correction (reported, not silently fixed)

The dispatch said "28 `wl_*` windows". The record contains **12** `wl_*` arrays, each
exactly **(12, 5725) float64**, and **24** dN/dz files (not 25). Enumerated:

```
wl_DR6_LRGz1  wl_PR4_LRGz1  wl_DR6_LRGz2  wl_PR4_LRGz2
wl_DR6_LRGz3  wl_PR4_LRGz3  wl_DR6_LRGz4  wl_PR4_LRGz4
wl_LRGz1_LRGz1  wl_LRGz2_LRGz2  wl_LRGz3_LRGz3  wl_LRGz4_LRGz4
```

8 CMB-lensing x galaxy cross windows (DR6 or PR4 x LRGz1..4) + 4 galaxy auto windows.
Names are carried **verbatim**, and the archive's own convention is already **map-first**
(`wl_PR4_LRGz1`, never `wl_LRGz1_PR4`). The `map` / `tracer` columns split that same name;
for the auto spectra `map == tracer == LRGz<n>`.

## 1. Window CSVs — orientation, stated explicitly

The on-disk array is `W[band, ell]` with shape **(12 bands, 5725 multipoles)**.

**The CSV is NOT stored in that orientation.** It is stored **ell-major**:
one row per multipole, twelve value columns, one per band.

```
window_id, map, tracer, ell_index, band_00, band_01, ..., band_11
```

* `ell_index` — integer 0..5724, **strictly ascending**, no gaps. This is index 1 of the
  numpy array as released.
* `band_bb` — `W[bb, ell_index]`, i.e. **column `band_bb` is band `bb` of the original
  first axis**. There is no transpose hidden anywhere: the CSV row index is the array's
  *second* axis and the CSV column index is the array's *first* axis.

### `ell_index` is the multipole itself (verified, not assumed)

For each band we took `argmax` over `ell_index`. For `wl_PR4_LRGz1` the peaks land at
`[32, 61, 96, 160, 225, 299, 364, 448, 548, 657, 778, 904]` against the released band
centres `ell = [32.0, 61.5, 101.5, 151.0, 210.5, 280.0, 359.0, 448.0, 547.5, 656.5,
775.0, 904.0]`. The alignment is exact at both ends ⇒ **`ell_index` == multipole `ell`**,
integer, from 0 to 5724. (DR6 windows peak a few multipoles low, as expected for a
lensing-reconstruction window; the identification still holds.)

### Band edges and centres (from the same JSON, for the k-mapping)

```
ledges = [20, 44, 79, 124, 178, 243, 317, 401, 495, 600, 713, 837, 971]   # 13 edges
ell    = [32.0, 61.5, 101.5, 151.0, 210.5, 280.0, 359.0, 448.0, 547.5, 656.5, 775.0, 904.0]
nside  = 2048
```

Archive README, verbatim: *"cl_X_Y is the pseudo Cell C^{XY}. wl_X_Y is the window
function for C^{XY}."* So bandpower `b` of spectrum `X_Y` is
`Cb[b] = sum_ell W[b, ell] * C_ell^{XY}` — this is the released window, which is exactly
what S9 requires **instead of** an `ell_eff / chi(z_eff)` shortcut.

### Sharding and reconstruction

Each window is split into **2 shards**, `<window_id>.part01.csv` and `.part02.csv`, each
under 900,000 bytes. The split is on `ell_index` only; every shard repeats the full
header, and no row is duplicated or dropped (`2915 + 2810 == 5725`).

Worked reconstruction of one (12, 5725) array:

```python
import numpy as np, pandas as pd
df = pd.concat([pd.read_csv(f'wl_PR4_LRGz1.part{i:02d}.csv') for i in (1, 2)],
               ignore_index=True)
df = df.sort_values('ell_index')
assert len(df) == 5725 and (df.ell_index.values == np.arange(5725)).all()
cols = [f'band_{b:02d}' for b in range(12)]
W = df[cols].to_numpy().T          # <-- the .T restores (12, 5725)
assert W.shape == (12, 5725)
# W[b, l] is the weight of multipole l in bandpower b.
```

## 2. dN/dz CSVs

One CSV per original file, original basename preserved:
`<tracer>_dNdz[_<region>].csv`, 24 files.

```
file, tracer, region, z, dNdz
```

* `tracer` — `LRGz1`..`LRGz4`.
* `region` — `all` for the unsuffixed files, else `north`, `south`, `decals`, `des`, `act`.
  Files without the `_act` suffix have **149 rows** (dz = 0.01, z from 0.005);
  the `_act` files have **74 rows** (dz = 0.02, z from 0.01).
* Header comment from the source, verbatim: *"Angular number densities per z bin
  ('number per bin'), i.e., the number of galaxies per sq.deg. that have zmin<z<zmax.
  Both imaging and spectroscopic weights are included."* Columns were
  *"redshift, dNdz"*. 🔴 **The normalisation differs between the `_act` files and all the
  others** — measured, not assumed: `sum(dNdz)` is **81.92** for `LRGz1_dNdz.csv` and
  **83.27** for `LRGz1_dNdz_north.csv`, but **121,066** for `LRGz1_dNdz_act.csv` (the
  latter is in raw galaxies/sq.deg.). **Normalise to unit integral before use.**

## 3. Integrity

`MANIFEST.csv` lists `file, shard, rows, bytes, sha256` for all 48 data files. Every
file was asserted **non-empty (rows > 0)** at write time; the minimum row count in the
whole delivery is 74 and the maximum is 2918. No parquet, no compression, plain UTF-8 CSV.
