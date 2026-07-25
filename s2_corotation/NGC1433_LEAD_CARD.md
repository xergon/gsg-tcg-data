# S2 corotation parity - Williams+2021 pattern speeds, read directly from FITS

Source: `pattern_speed_table_v1p0.fits`, upstream repo `thomaswilliamsastro/phangs_pattern_speeds`
at commit `33e814890d5ede0d46bd351c0f65a54443560538` (2021-03-08).
File: 97,920 bytes, MD5 `df7873cb74f06a12887e94ff6bc0f4c6`, magic `SIMPLE  =`.
Table: BinTableHDU, 83 rows x 101 columns. Pattern speeds in km/s/kpc, radii in kpc.

## !! THERE IS NO SINGLE `QUAL` FLAG PER GALAXY - THERE ARE THREE, ONE PER TRACER

The table carries `OM_P_ALMA_QUAL`, `OM_P_MUSE_MASS_QUAL` and `OM_P_MUSE_HA_QUAL`
as three independent columns. Any statement of the form "galaxy X is QUAL=1" is
underdetermined until the tracer is named.

### Quality-flag meaning (verbatim from `create_diagnostic_webpage.py`, classes are stored as index+1 by `make_table.py`)

- **1 = Single-well-definedP** - "Single, well defined pattern speeds: no issues (integrals have converged, reasonably stable with slit width, sufficiently high covering factor"
- **2 = ClearMultiplebutClean** - "Clear multiple pattern speeds visible in the <v><x> plot, but otherwise the fit would be a quality flag (1)"
- **3 = PoorFit** - "Poor fit: integral hasn't converged, or there is some issue in the data that causes us to distrust this pattern speed"
- **4 = InsuffQuality** - "Data of insufficient quality to calculate a reliable pattern speed. In this case, a more reliable pattern speed may be possible with higher resolution or deeper data."

The published flag is the **mode over three independent human classifiers** (`ee`, `es`, `tw`);
if all three disagree the **maximum** (worst) is taken. See `make_table.py` lines 192-278.

## LEAD GALAXY: NGC 1433

| quantity | value |
|---|---|
| GALAXY | NGC1433 |
| PGC | 13586 |
| DIST | 12.11 |
| INCL | 28.6 |
| PA | 199.7 |
| HAS_BAR | 1 |
| **OM_P_ALMA (CO 2-1)** | **105.553838  +4.617606 / -8.064562  km/s/kpc** |
| **OM_P_ALMA_QUAL** | **3.0** |
| **OM_P_MUSE_MASS (stellar)** | **19.988451  +2.447837 / -1.934184  km/s/kpc** |
| **OM_P_MUSE_MASS_QUAL** | **1.0** |
| **OM_P_MUSE_HA (ionised gas)** | **41.206559  +0.660323 / -0.737066  km/s/kpc** |
| **OM_P_MUSE_HA_QUAL** | **1.0** |
| R_CR_ALMA_1 | 0.07208333611488343 +/- 0.07208333611488343 kpc |
| R_CR_ALMA_2 | 0.3063541784882545 +/- 0.05406250208616259 kpc |
| R_CR_MUSE_MASS_1 | 6.275 +/- 0.375 kpc |
| R_CR_MUSE_HA_1 | 0.07208333611488343 +/- 0.07208333611488343 kpc |
| LITERATURE_OM_P | 17.21962462862518 (ref 2008AJ....136..300T) |

### What the numbers say about NGC 1433

- The three tracers do **not** agree: 105.554 (CO), 19.988 (stellar), 41.207 (Ha) km/s/kpc.
  CO is **5.28x** the stellar value and **2.56x** the Ha value.
- The CO pattern speed carries **OM_P_ALMA_QUAL = 3** = *PoorFit*, i.e. Williams+ themselves
  flag the ALMA integral as not converged / distrusted. Only the two MUSE tracers are QUAL = 1.
- `R_CR_ALMA_1 = 0.0721 kpc` with `R_CR_ALMA_1_ERR = 0.0721 kpc` - the error equals the value
  exactly, i.e. the innermost CO corotation is consistent with R = 0 and is **not resolved**.
  `R_CR_MUSE_HA_1` is the *identical* number (0.07208333611488343) with the identical error.
- The literature value (Treuthardt+2008, `2008AJ....136..300T`) is 17.220 km/s/kpc, close to the
  stellar MUSE value and nowhere near the CO value.

## The trio, and the two galaxies the static screen disagreed on

| galaxy | ALMA Om_p | ALMA QUAL | MUSE_MASS Om_p | MM QUAL | MUSE_HA Om_p | HA QUAL |
|---|---|---|---|---|---|---|
| NGC1433 | 105.554 | 3.0 | 19.988 | 1.0 | 41.207 | 1.0 |
| NGC3351 | 60.511 | 1.0 | 43.608 | 1.0 | 89.672 | 3.0 |
| NGC1672 | 32.471 | 2.0 | 22.733 | 1.0 | 28.071 | 1.0 |
| NGC3627 | 45.798 | 1.0 | 29.128 | 2.0 | 50.687 | 1.0 |
| NGC4303 | 46.674 | 1.0 | 43.518 | 1.0 | 48.409 | 1.0 |

### On the reported static-screen / QUAL disagreement

- **NGC 3627** is `QUAL = 1` on **ALMA** and on **MUSE_HA**, and `QUAL = 2` on **MUSE_MASS**.
  So it is not true without qualification that NGC 3627 "is not QUAL=1" - it is QUAL=1 in two
  of the three tracers, and QUAL=2 ("clear multiple pattern speeds, but otherwise would be a 1")
  in the stellar one.
- **NGC 4303** is `QUAL = 1` in **all three** tracers - it is the cleanest row of the five here.
- **NGC 1433**, the new lead galaxy, is the **only** one of the five carrying a `QUAL = 3`
  (*PoorFit*) on any tracer, and it carries it on **CO**, which is the tracer the fixed-annulus
  Pi_g statistic was built on.

## THE COROTATION RADIUS IS NOT A SINGLE NUMBER - READ THIS BEFORE FIXING ANY ANNULUS

Two published catalogues are already in this directory and **they disagree at the multi-sigma
level on two of the three trio galaxies**. Williams+2021 additionally lists **multiple**
corotation radii per tracer, not one.

| galaxy | Williams ALMA R_CR (kpc) | Williams stellar R_CR | Williams Ha R_CR | Ruiz-Garcia 2024 R_CR | stellar vs RG24 |
|---|---|---|---|---|---|
| NGC 1433 | 0.0721+/-0.0721, 0.3064+/-0.0541, 1.8201+/-0.8109 | 6.2750+/-0.3750 | 0.0721+/-0.0721, 3.7123+/-1.0813 | 4.8+/-0.3 (QF 2) | **3.07 sigma** |
| NGC 3351 | 2.9000+/-1.2000 | 3.3500+/-0.7500 | 2.4500+/-1.6500 | 2.2+/-0.1 (QF 1) | 1.52 sigma |
| NGC 1672 | 3.2605+/-0.9782 | 6.0727+/-1.5895 | 3.9941+/-0.4891 | 11.9+/-1.9 (QF 3^dagger) | 2.35 sigma |

For **NGC 1433** the published corotation candidates span **0.072 to 6.275 kpc** - a factor of ~87.
Neither catalogue's quoted uncertainty comes close to covering that spread. Ruiz-Garcia Table A.3
lists **no** pattern speed at all for any of the three trio galaxies (all cells are `...`).

Ruiz-Garcia has been tagged `SECONDARY_CO_TORQUE_COORDINATE / NOT_INDEPENDENT_PRIMARY`, which is
why it appears here only as a cross-check, not as a primary. The point stands regardless: the
*allowed* range of R_CR is set by catalogue-to-catalogue disagreement, not by either catalogue's
internal error bar.

## A REPRODUCIBILITY DEFECT IN THE CODE THAT BUILT THE PUBLISHED TABLE

`make_table.py`, the script that writes `pattern_speed_table_v1p0.fits`, contains a
copy-paste bug at line 266 (published, unfixed at HEAD `33e8148`):

```python
try:
    muse_mass_q, count = mode(quality_flags[galaxy + '_muse_mass'])
    if np.any(count == 1):
        alma_co_q = np.nanmax(quality_flags[galaxy + '_muse_mass'])   # <-- should be muse_mass_q
    else:
        muse_mass_q = muse_mass_q[0]
except KeyError:
    muse_mass_q = np.nan
```

Two consequences, both reaching the published columns (they are written out at lines 386-388):

1. When the three human classifiers **all disagree** on the MUSE-mass flag, `OM_P_ALMA_QUAL`
   is **overwritten by the MUSE-mass maximum**, destroying the ALMA flag computed just above.
2. In that same branch `muse_mass_q` is never subscripted, so it retains the raw `mode()`
   return rather than a scalar.

The equivalent ALMA (line 258) and Ha (line 274) branches are correct; only the MUSE-mass branch
is wrong. **Which rows are affected cannot be determined from the public repo**: the inputs
`pattern_speeds_output/quality_flags/batch{1,2}_{ee,es,tw}.txt` are **not shipped** with it, and
the bug only fires on unanimous three-way disagreement. `OM_P_ALMA_QUAL = 3` for NGC 1433 should
therefore be treated as *possibly* the MUSE-mass max rather than the ALMA modal flag, and cannot
be disambiguated from public data alone.

## THE MUSE DAP MAPS DO NOT CONTAIN A STELLAR FLUX MAP

`<GAL>_MAPS_native.fits` is a 54-extension file. It carries the stellar **kinematics**
(`V_STARS`, `FORM_ERR_V_STARS`, `SIGMA_STARS`, `FORM_ERR_SIGMA_STARS`) and full flux / velocity /
sigma sets for eight emission lines (HB4861, OIII4958, OIII5006, NII6548, HA6562, NII6583,
SII6716, SII6730), plus `BIN_ID` for the Voronoi binning.

There is **no stellar continuum flux extension**. A Tremaine-Weinberg integral needs a surface-
brightness weight, so the stellar TW **cannot be run from the MAPS file alone**. The weight comes
from the separate `IMAGES` product, which is why `phangs_muse_white_images/` is mirrored here:
white-light mosaics, native and copt, for all three galaxies (`DATA`, `STAT`, `DQ` extensions).

All MUSE products - MAPS and IMAGES, native and copt - are on the same 0.2000 arcsec/pix grid,
read from `CD2_2`. The copt PSF is **0.91 / 1.05 / 0.96 arcsec** for NGC1433 / NGC3351 / NGC1672,
and that value appears only in the **filename**; the trio's native PSFs are not equal to each
other and are not equal to the copt values. Per-galaxy pixel grids differ in size
(1480x915, 897x896, 1235x711) but not in scale.
