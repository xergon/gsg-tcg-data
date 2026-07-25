# C-Triangle — KiDS-1000 × SAMI DR3 stage-1 delivery

Row: **C-Triangle**. Successor target: PA-free local-aperture cross-shear `Γ_B` with an externally supplied
signed spin-parity label. Stage-1 ask ~30–70 GB, hard ceiling 100 GB. **This delivery is 46 MB of
catalogue + a manifest; the ceiling was never approached, because the two numbers that could kill the lane
cost nothing to obtain and neither of them required the 16 GB pull.**

Fetched 2026-07-25 (UTC, `date -u`).

---

## 1. 🔴 `N_qualified` — THE KILL DOES NOT FIRE. **N_qualified = 2075**, margin 2.1×.

Falsifier: `N_qualified < 1,000 ⇒ PIVOT`.

**Every SAMI DR3 GAMA-region galaxy — all 2,100 of them — falls inside the KiDS-1000 footprint. Zero
outside.** KiDS-N was built to cover GAMA G09/G12/G15, so the overlap is complete by construction, not by
luck.

| rung | cut | N |
|---|---|---|
| L0 | SAMI DR3 GAMA-region galaxy with a cube, inside KiDS-1000 | **2100** |
| L1 | + finite `PA_GASKIN` | 2099 |
| L2 | + `PA_GASKIN_ERR ≤ 10°` | 2075 |
| L3 | + `PA_GASKIN_ERR ≤ 5°` | 2033 |
| L4 | + finite `PA_STELKIN` | 1808 |
| L5 | gas **and** stellar PA both present | 1808 |
| L6 | + finite `LAMBDAR_RE` (the spin-*magnitude* proxy — see below, **not** needed for parity) | 1155 |
| L7 | **STRICT**: `PA_GASKIN_ERR ≤ 10°` + `LAMBDAR_RE` + `WARNMULT=WARNFILL=WARNZ=0` | **1120** |

By GAMA field: **G09 657, G12 702, G15 741**.

### 🔴 The operative rung is L2 = 2075, not L7 — `PA_GASKIN` is ALREADY a signed label

`PA_GASKIN` spans **0.5° → 360.0°**, with **50.13% of values above 180°** and a flat octant histogram. It is
measured with **`fit_kinematic_pa`** (Krajnović et al. 2006, Appendix C), applied to the 1-component gas
kinematic maps — a routine that returns the PA of the **receding** half of the velocity field over the full
circle. **⇒ The rotation sense is encoded in the PA itself. `PA_GASKIN` *is* the externally supplied signed
spin-parity label C-Triangle asked for, with no extra ingredient.**

`PA_STELKIN` behaves identically (1.0° → 359.5°, 49.88% above 180°).

**So `N_qualified` = 2099 (finite `PA_GASKIN`) or 2075 (`err ≤ 10°`) — a 2.1× margin, not 1.12×.**
`LAMBDAR_RE` (N = 1155) constrains spin **magnitude**, not parity; it is finite for only 1930 of 3426 cubes
and it is **not** the binding cut unless the estimator specifically needs fast/slow-rotator classification.
**If the row confirms it needs parity only, the footprint question is closed with a 2× margin.**

`PA_GASKIN_ERR` is excellent: median **0.167°**, p90 1.25°, p95 3.9°, p99 11.3°.

⚠ **`PA_STELKIN_ERR` saturates.** Median 3.17°, but p90 = p95 = p99 = **29.9167°** — 336 rows sit exactly on
that cap, i.e. those stellar PAs are unconstrained, not merely noisy. SAMI themselves fall back to the *gas*
PA whenever the stellar PA error exceeds 20°. **Do not treat `PA_STELKIN` as an independent label of equal
quality.**

⭐ **A free internal sign control the row did not ask for.** Joining the two PA tables on `CUBEID`
(identical key sets, 2815 galaxies with both finite): median |PA_gas − PA_stel| = **19.0°**, 46% within 15°
— and **9.0% exceed 150°, i.e. gas–star counter-rotators** (7.8% with both errors < 10°). For roughly one
galaxy in eleven the spin-parity label **flips between tracers**. `Γ_B` must flip sign with it. That is a
built-in, zero-cost falsification test on the estimator itself, and it is far sharper than a random-sign
null because the flip is physically real and externally labelled.

Other counts, for completeness:
* SAMI DR3 unique galaxies with `ISBEST` cube and `WARNSTAR=0`: **2996** (2100 GAMA + 896 cluster).
  Adding the 72 filler-catalogue galaxies that are in neither input catalogue reproduces the published
  **3068**, and the 177 `WARNSTAR=1` rows are calibration stars.
* Cluster-sample galaxies that happen to fall inside KiDS-1000: **212** — excluded per the brief, but they
  exist if the row ever wants them.

### 🔴 The structural fact that matters more than the count
`z_spec` for the 2100 GAMA lenses: min 0.0038, **median 0.0401**, max 0.1121. These are **very
low-redshift lenses.** Every KiDS source is behind them (the gold catalogue is cut to `0.1 < Z_B ≤ 1.2`,
verified), so the full `n_eff = 6.17 arcmin⁻²` is geometrically usable — but `Σ_crit` is correspondingly
large and a fixed *physical* aperture subtends a large *angle* (100 kpc ≈ 2.2′ at z = 0.04). Whatever the
row means by "local aperture", the angular scale and the `Σ_crit` weighting both follow from this median
redshift and it should fix them explicitly before computing.

---

## 2. 🔴 Published `c₁`/`c₂` — the shipped catalogue FAILS the gate; the corrected one passes by 1.46×

Falsifier: `σ(c_×,s) > 4.0e-4 ⇒ PIVOT`. Full detail and provenance in **`KIDS1000_SHEAR_CALIBRATION.md`**.

| quantity (Giblin, Heymans, Asgari et al. 2021, arXiv 2007.01845) | value | vs 4.0e-4 |
|---|---|---|
| `c₂` survey-wide, on the **raw shipped `e1`/`e2`** | **(6 ± 1) × 10⁻⁴** | **EXCEEDS** |
| `c₁` survey-wide | consistent with zero (significant only in bins 3, 5) | passes |
| residual after KiDS's own empirical correction, quadrature `√(7.5e-8)` | **2.739 × 10⁻⁴** | passes, **1.46×** |
| the same, per component | **1.937 × 10⁻⁴** | passes, 2.06× |
| chip-dependent PSF-residual model `c₁`, exposure-weighted rms | **7.43 × 10⁻⁴**, 84% of the focal plane over 4.0e-4 | **EXCEEDS at unit amplitude** |
| PSF leakage `α`, bins 1–3 | consistent with zero at 2σ | — |
| PSF leakage `α`, bins 4–5 | \|α\| ≈ 0.04 ± 0.01 | — |
| mean PSF ellipticity, **KiDS-N equatorial** — where every SAMI lens is | ε̄₁ = 0.005 ± 0.001, ε̄₂ = −0.005 ± 0.001 | `α·ε̄` ≈ 2.0e-4 in bins 4–5 |

**⇒ Neither kill fires on published numbers — but the c-margin is 1.46×, and it is entirely contingent on
applying a correction that is NOT applied on disk.** `e1`/`e2` ship with *no m and no c correction*
(publisher's own header comment). Run the estimator on the raw columns and the additive term is
6 × 10⁻⁴ and C-Triangle kills itself on the first pass for a reason that has nothing to do with gravity.

The 2.739e-4 figure is `√σ` of the KiDS-1000 nuisance prior on `δε̄²` — a zero-mean Gaussian of width
**σ = 7.5 × 10⁻⁸**, set as the largest variance in any tomographic bin across **300 bootstrap samples** of
`⟨ε₁−ε̄₁⟩² + ⟨ε₂−ε̄₂⟩²`. That bootstrap scatter is the published quantity closest to what the row calls
`σ(c_×,s)`: it is the patch-to-patch residual left over after a survey-wide subtraction, which is exactly
what a local-aperture estimator is exposed to.

**The systematic to null-test against** is the chip-dependent PSF residual, whose 2100² focal-plane maps
(`c1_map.fits`, `c2_map.fits`, `exposure_map.fits`) and mock-generator (`create_c12_mock.py`) are public and
tiny — URLs in `KIDS1000_SHEAR_CALIBRATION.md` §3. It is spatially coherent, chip-locked, and **survives the
survey-wide mean subtraction**. Its `c₁` amplitude exceeds 4.0e-4 over 84% of the focal plane.

Cutting the other way: Giblin's own 2D galaxy-galaxy-lensing null test in the OmegaCAM pixel frame (409 deg²
of BOSS LRGs, to 5′ and again to 30′) finds **featureless residuals and a featureless signal around random
points**, which is the strongest published evidence that a local-aperture estimator is not additive-
dominated. **That is also the exact arbitrary-input control C-Triangle should reproduce before trusting any
`Γ_B`.**

---

## 3. Column definitions — the standing KiDS-Legacy warning is HALF WRONG for DR4.1

Checked against the **actual FITS header** of the 17.7 GB file (`TFIELDS=193`, `NAXIS1=833`,
`NAXIS2=21262011` — matching the published 21,262,011 exactly), not the web page.

```
TTYPE191= 'e1      '  / Lensfit ellipticity e1 - no m or c corr
TTYPE192= 'e2      '  / Lensfit ellipticity e1 - no m or c corr    <-- says "e1"; publisher typo
TTYPE193= 'weight  '  / Recalibrated Lensfit inverse variance weight
```

* ✅ **Holds:** `e1`/`e2` carry **no m and no c correction**, same as KiDS-Legacy.
* ❌ **Does not hold:** DR4.1 has **no `shear_weight_only`, no `gold_weight_only`, no `Flag_SOM_*`, no
  `TOMOBIN`, and no per-object `m`** — all 193 column names were enumerated. In KiDS-1000 the SOM gold
  selection is a **binary cut already applied to the file**; the catalogue *is* the gold sample. So
  **`weight` is the pure recalibrated lensfit inverse-variance shear weight and using it directly is
  correct — there is nothing to double-count.** (Contrast `i2_gama_kidslegacy/COLUMNS.txt` in this repo,
  where KiDS-Legacy does carry all three weight columns.)

What the user must apply themselves: the **c-subtraction** (per tomographic bin) and the **m-correction**
(per tomographic bin, from the table in `KIDS1000_SHEAR_CALIBRATION.md` §1 — not per object). Tomographic
bin membership is not a column; assign it from `Z_B`.

---

## 4. What is delivered

| file | bytes | what |
|---|---|---|
| `N_QUALIFIED.json` | — | the ladder above, machine-readable |
| `KIDS1000_SHEAR_CALIBRATION.md` | — | every published calibration number + provenance |
| `sami_dr3_lens_table.csv` | — | **2,996** SAMI DR3 galaxies (GAMA + cluster), position, `z_spec`, `Mstar`, `r_e`, `ellip`, photometric `PA`, `PA_GASKIN(+err)`, `PA_STELKIN(+err)`, `LAMBDAR_RE`, `VSIGMA_RE`, `SIGMA_RE`, warn flags, `IN_KIDS1000` |
| `sami_gama_targets.csv` | — | the **2,100** GAMA-region rows only — the lens sample |
| `sami/InputCatGAMADR3.csv` | — | raw TAP export, 5,536 rows |
| `sami/InputCatClustersDR3.csv` | — | raw TAP export, 1,433 rows |
| `sami/CubeObs.csv` | — | raw TAP export, 3,712 cubes with all `WARN*` flags |
| `sami/samiDR3gaskinPA.csv` | — | **the gas-kinematic PA catalogue**, 3,426 rows |
| `sami/samiDR3Stelkin.csv` | — | stellar kinematics, 3,426 rows, 44 columns |
| `KiDS1000_tile_footprint.csv` | — | all 1,006 DR4.0 + 196 DR4.1 tile centres, patch label, complete per-tile URL |
| `DESI_LS_DR9_cutout_urls.txt` | — | **31,500 complete cutout URLs** = 15 products × 2,100 galaxies, NERSC-independent |
| `MANIFEST.md`, `SUMMARY.json`, `URL_VERIFICATION.txt` | — | provenance |
| *(release asset)* `kids1000_sami_aperture_sources` | ~0.7 GB | every KiDS-1000 gold source within **15′** of a SAMI GAMA lens, 27 columns |

**No `Γ_B`, no shear profile, no ESD, no stacked contrast was computed.** The aperture-source file is a
spatial row selection plus a column subset — nothing derived.

---

## 5. Deferred and blocked — stated explicitly, not truncated silently

### ⛔ DESI Legacy Imaging Surveys DR9 — the primary host is DOWN, but a full substitute route was found and verified
`www.legacysurvey.org` resolves to **`lb.cosmo-viewer.production.svc.spin.nersc.org` (128.55.206.x)** — it is
hosted **at NERSC**. Both it and `portal.nersc.gov` time out from every endpoint tried, including a second
egress. This is the same **NERSC "Major Power Upgrade to Disrupt Services, July 22 – August 3"** outage
already on record in this queue for DESI DR1. Re-attempt after 2026-08-03.

✅ **Substitute, NERSC-independent, verified working: the NOIRLab Astro Data Lab SIA collection `ls_dr9`.**
All 2,100 SAMI lenses were matched to a DR9 brick (from `ls_dr9.bricks_s` via Data Lab TAP — 4,988 bricks
over the GAMA strip, exact `ra1/ra2/dec1/dec2` bounds, **0 galaxies unmatched**), and 31,500 complete
cutout URLs were generated. **10 of 10 randomly sampled URLs returned valid FITS** (`SIMPLE  =`,
~0.75–1.07 MB each). Full pull ≈ 30 GB — deferred as the brief directs, since imaging is the cheapest
thing to re-fetch and the two kill numbers did not need it.

🔴 **FINDING — `image-z` is MISSING from the Data Lab `ls_dr9` collection.** Reproduced at two independent
sky positions with `MAXREC=5000`: the SIA returns **38 product types per brick** and `image-z` is not one of
them, while `invvar-z`, `model-z`, `blobmodel-z`, `chi2-z`, `nexp-z`, `depth-z`, `galdepth-z` and
`psfsize-z` all **are** present. `image-g` and `image-r` are complete. **⇒ The z-band science image cannot
be obtained by the NERSC-independent route; g and r can.** C-Triangle asked for "g, r, z" — it gets g and r
now, z only after NERSC returns.

🔴 **FINDING — DR9 bricks ship no residual product.** There is no `resid-*` layer: residual = `image − model`,
computed by the user. The viewer's `ls-dr9-resid` layer computes it on the fly and is NERSC-hosted, i.e.
currently down. Both `image-*` and `model-*` are delivered in the URL list, so the residual is constructible.

### ⛔ SAMI DR3 **map products** (Hα velocity / velocity error / flux / flux error / dispersion / masks / WCS) — HUMAN NEEDED
The **catalogues** are all delivered (anonymous VO TAP at `https://datacentral.org.au/vo/tap/sync` works
fine, and that is where every number in §1 comes from). The **map products** are not, and there are exactly
two routes, both of which are stops under the brief's hard limits:

1. `https://datacentral.org.au/api/services/sov/?source=<CATID>` →
   **HTTP 403 `{"detail":"Authentication credentials were not provided."}`**
2. `https://datacentral.org.au/services/download/` (bulk download, POST) → validates and returns
   **HTTP 400 with `email: This field is required.`** The service is delivery-by-email and mandates a
   personal email address. Field names are `source_list`, `data_releases`, `data_products_ifs`,
   `loose_matching`, `email`; the Hα product the row named is **`data_products_ifs=180`, "SAMI DR3 SAMI
   1-component line emission map: Hα"**. Stellar velocity maps are `149` (two-moment) and `157`
   (four-moment); the 8 line species and all binning schemes are IDs 179–246.

**No account was created and no email address was submitted.** Croom et al. 2021 (arXiv `2101.12224`, §data
access) documents Data Central as the *only* route — there is no static mirror to fall back on. A human
must either register at Data Central or authorise submitting an address to that form. The full SAMI DR3
archive is ~430 GB and is confirmation-stage only per the brief; the Hα subset for 2,100 galaxies is far
smaller and is what should be requested.

### Not fetched, deliberately
* **`KiDS_DR4.1_ugriZYJHKs_SOM_gold_WL_cat.fits`, 17,712,469,440 B** — **over the 2 GiB GitHub release-asset
  cap, cannot be re-hosted intact.** Manifested with byte count, `Last-Modified`, verified FITS magic and
  verified row count. What is delivered instead is the 15′ aperture extract, which is what the estimator
  actually reads.
* The full 30 GB DESI cutout set — URL list delivered, 10/10 spot-verified.
