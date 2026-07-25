# KiDS-1000 (DR4.1 SOM-gold) shear calibration — the published numbers, against C-Triangle's σ(c_×,s) > 4.0e-4 kill

Source: **Giblin, Heymans, Asgari et al. 2021, A&A 645, A105** — arXiv `2007.01845`.
All numbers below were read out of the **arXiv `/e-print/` LaTeX source**, not a rendered page, and the
column definitions were read out of the **actual FITS header of the 17.7 GB catalogue**, not the web table.

---

## 0. THE HEADLINE — the shipped catalogue FAILS the gate; the corrected catalogue passes it by 1.46×

| quantity | published value | vs the 4.0e-4 kill |
|---|---|---|
| `c₂`, survey-wide, on the **raw shipped `e1`/`e2`** | **(6 ± 1) × 10⁻⁴** | **EXCEEDS 4.0e-4** |
| `c₁`, survey-wide | consistent with zero (significant only in tomographic bins 3 and 5) | passes |
| residual after KiDS's own empirical correction, **quadrature** `√(c₁²+c₂²)` | **2.739 × 10⁻⁴** | passes, margin **1.46×** |
| the same, **per component** (`/√2`) | **1.937 × 10⁻⁴** | passes, margin **2.06×** |
| chip-dependent PSF-residual model `c₁`, exposure-weighted rms | **7.43 × 10⁻⁴** (mean +9.70e-4, max +4.95e-3) | **EXCEEDS at unit amplitude** |
| chip-dependent PSF-residual model `c₂`, exposure-weighted rms | 1.10 × 10⁻⁴ (mean −1.13e-4, max −4.29e-4) | passes |
| PSF leakage `α`, bins 1–3 and full survey | consistent with zero at 2σ | — |
| PSF leakage `α`, bins 4–5 | \|α\| ≈ 0.04 ± 0.01 | — |
| mean PSF ellipticity, **KiDS-N equatorial** (where every SAMI lens is) | ε̄₁ = 0.005 ± 0.001, ε̄₂ = −0.005 ± 0.001 | `α·ε̄` ≈ 2.0e-4 in bins 4–5 |
| mean PSF ellipticity, KiDS-S | ε̄₁ = 0.003 ± 0.001, ε̄₂ = 0.001 ± 0.001 | — |

**⇒ The lane does not die for free on the published residuals — but only because the c-subtraction is
applied, and the surviving margin is 1.46× on the quantity that matters.** If the estimator is run on the
`e1`/`e2` columns as they come off disk, the additive term is 6 × 10⁻⁴ and C-Triangle's own falsifier fires
on the first pass.

### Where 2.739e-4 comes from — quoted verbatim in substance from §3.4.1
KiDS-1000 corrects empirically: `ε_corr = ε_obs − ⟨ε_obs⟩`, with `⟨ε_obs⟩` the **weighted average ellipticity
of the relevant tomographic bin** — one survey-wide number per bin, not per patch and not per tile. The
accuracy of that correction is carried into the cosmology as a nuisance parameter `δε̄²` with a **zero-mean
Gaussian prior of width σ = 7.5 × 10⁻⁸**, defined as the largest variance measured from any tomographic bin
across **300 bootstrap sample measurements** of `⟨ε₁−ε̄₁⟩² + ⟨ε₂−ε̄₂⟩²`.

`√(7.5e-8) = 2.7386e-4` → residual quadrature additive amplitude.
`√(7.5e-8/2) = 1.9365e-4` → per component.

That bootstrap scatter is the closest published analogue to what C-Triangle calls `σ(c_×,s)`: it is the
*patch-to-patch* residual left after the survey-wide subtraction, which is exactly what a local-aperture
estimator sees.

### The one that should worry the row most
`PSFRES_CORRMAP/c1_map.fits`, `c2_map.fits` in the KiDS team's own open-source repo
`github.com/KiDS-WL/Cat_to_Obs_K1000_P1` are the **chip-dependent PSF-residual model, extrapolated to faint
magnitudes and dithered into the co-add frame** (2100 × 2100 pixels, plus `exposure_map.fits`). Statistics
computed here over the `exposure > 0.5` footprint (3,240,059 of 4,410,000 pixels):

```
c1 : exposure-weighted mean +9.6992e-04   rms 7.4271e-04   range +2.193e-04 .. +4.945e-03
     84.21 % of the footprint has |c1| > 4.0e-4
c2 : exposure-weighted mean -1.1268e-04   rms 1.1044e-04   range -4.287e-04 .. +1.510e-04
      2.95 % of the footprint has |c2| > 4.0e-4
|c|: mean 9.6408e-04   median 8.5084e-04   max 4.9450e-03
     90.86 % of the footprint has |c| > 4.0e-4
```

⚠ **Read this correctly.** This is the residual *model* at unit amplitude — it enters the systematics model
as `β·δε^PSF` with `β` a free amplitude (Zuntz et al. argue `β ~ −1`), and Giblin show its impact on
cosmic shear is negligible. It is **not** the fitted additive `c`. But it is a **spatially coherent,
chip-locked pattern that the survey-wide per-tomographic-bin mean subtraction does not remove**, and its
amplitude in `c₁` sits an order of magnitude above C-Triangle's threshold at the worst focal-plane
positions. A local-aperture cross-shear evaluated in the OmegaCAM frame is precisely the statistic that
does not average it away. **This is the systematic to null-test against, and the map to do it with is
public and small.**

### Giblin's own remark that cuts the other way
§4.2: azimuthal averaging in galaxy-galaxy lensing "results in a cancellation of additive systematics", and
they verify it — 2D galaxy-galaxy lensing in the OmegaCAM pixel frame around 409 deg² of BOSS LRGs, out to
5′ and again to 30′, shows **featureless residuals and a featureless signal around random points**. They
conclude the constant-`c` approximation holds even near bright galaxies. That test is the strongest
published evidence that a local aperture estimator is not additive-dominated — and it is also the exact
null-test C-Triangle should reproduce with random points before trusting any Γ_B.

---

## 1. Column definitions — read from the FITS header, not the web page

`KiDS_DR4.1_ugriZYJHKs_SOM_gold_WL_cat.fits`, EXT 1 `OBJECTS`, `BITPIX=8 NAXIS1=833 NAXIS2=21262011
TFIELDS=193`. Row count matches the published 21,262,011 exactly.

```
TTYPE191= 'e1      '  / Lensfit ellipticity e1 - no m or c corr
TTYPE192= 'e2      '  / Lensfit ellipticity e1 - no m or c corr      <-- comment says "e1"; publisher typo
TTYPE193= 'weight  '  / Recalibrated Lensfit inverse variance weight
```

### 🔴 The KiDS-Legacy double-counting hazard does **NOT** exist in DR4.1
The standing warning — *"KiDS-Legacy `e1`/`e2` carry no m-correction and `weight = shear_weight_only ×
gold_weight_only`, so using `weight` for a shear estimator double-counts the gold weighting"* — was checked
directly against the DR4.1 header. Result:

* **Half of it holds.** `e1`/`e2` in DR4.1 carry **no m and no c correction**, same as KiDS-Legacy.
* **Half of it does not.** DR4.1 has **no `shear_weight_only`, no `gold_weight_only`, no `Flag_SOM_*`,
  no `TOMOBIN`, and no per-object `m` column** — the full 193-name list was enumerated and none exist.
  In KiDS-1000 the SOM gold selection is a **binary cut already applied to the file**, not a weight: the
  catalogue *is* the gold sample. `weight` is therefore the pure recalibrated *lens*fit inverse-variance
  shear weight, and **using it directly is correct — there is nothing to double-count.**
  (For contrast, `i2_gama_kidslegacy/COLUMNS.txt` in this same repo shows the KiDS-Legacy product does carry
  `weight`, `shear_weight_only` and `gold_weight_only` as three separate columns.)

### What the user must therefore apply themselves
1. **c-correction** — subtract the weighted mean ellipticity of the tomographic bin. Not applied on disk.
2. **m-correction** — per tomographic bin, **not** per object. From Giblin's Table (blind C, the true
   unblinded catalogue):

| bin | z_B range | n_eff^gold [arcmin⁻²] | σ_ε | z_SOM median | ⟨z_SOM⟩ | δ_z | m |
|---|---|---|---|---|---|---|---|
| 1 | 0.1 < z_B ≤ 0.3 | 0.62 | 0.270 | 0.2073 | 0.2571 | +0.0001 ± 0.0106 | −0.009 ± 0.019 |
| 2 | 0.3 < z_B ≤ 0.5 | 1.18 | 0.258 | 0.3590 | 0.4027 | +0.0021 ± 0.0113 | −0.011 ± 0.020 |
| 3 | 0.5 < z_B ≤ 0.7 | 1.85 | 0.273 | 0.5421 | 0.5636 | +0.0129 ± 0.0118 | −0.015 ± 0.017 |
| 4 | 0.7 < z_B ≤ 0.9 | 1.26 | 0.254 | 0.7460 | 0.7918 | +0.0110 ± 0.0087 | +0.002 ± 0.012 |
| 5 | 0.9 < z_B ≤ 1.2 | 1.31 | 0.270 | 0.9336 | 0.9838 | −0.0060 ± 0.0097 | +0.007 ± 0.010 |

Sum of `n_eff` over the five bins = **6.22 arcmin⁻²**; the abstract quotes **6.17** for the gold sample
(the small difference is rounding across bins — use 6.17 for area budgets).
Tomographic bin membership is **not** a column: assign it from `Z_B`.

3. `Z_B` in the shipped gold catalogue is already restricted to **(0.1, 1.2]** — verified on 62,735 rows,
   fraction inside the range = 1.000. There is no need to re-cut, and no sources exist outside it.

---

## 2. Verified file facts

| item | value |
|---|---|
| URL | `https://kids.strw.leidenuniv.nl/DR4/data_files/KiDS_DR4.1_ugriZYJHKs_SOM_gold_WL_cat.fits` |
| Content-Length | **17,712,469,440 B** (16.5 GiB) |
| Last-Modified | Mon, 07 Dec 2020 21:10:05 GMT |
| Accept-Ranges | bytes (HTTP 206 confirmed) |
| magic | `SIMPLE  =` — real FITS, not an HTML shell |
| rows | 21,262,011 (header `NAXIS2`, matches publisher's stated count exactly) |
| columns | 193 |
| sustained rate from this egress | 4.3–7.5 MB/s single stream; **6 parallel range streams gave 7 MB/s aggregate — the server is rate-capped, parallelism does not help** |

⚠ **Over the 2 GiB GitHub release-asset cap — cannot be re-hosted intact.** It is manifested, not mirrored.

### n(z) — already published, verified, reuse it
`https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/s9_deflection_closure/kids1000/KiDS1000_SOM_N_of_Z.tar.gz`
* 4,360 B, sha256 `1962a9117413f7fbb8adb863e4a85e250998257572cfffcbe2834e61c7d1704a`
* **`cmp`-identical to the publisher's original** freshly re-downloaded from
  `https://kids.strw.leidenuniv.nl/DR4/data_files/KiDS1000_SOM_N_of_Z.tar.gz` today.
* 5 members, `SOM_N_of_Z/K1000_NS_V1.0.0A_..._Fid_blindC_TOMO{1..5}_Nz.asc`, 6,022 B each, 121 lines
  (header `# # binstart, density` + 120 bins of Δz = 0.05, z = 0 → 6.0). **Blind C only** — blind C is the
  true unblinded catalogue, so this is the right one; blinds A and B are not distributed.

### The "DR4.1" in the filename does not mean 196 tiles
`kids_dr4.0_cat_wget.sh` lists **1006** tiles; `kids_dr4.1_cat_wget.sh` lists **196**, and all 196 were
checked to be a strict subset of the 1006. DR4.1 is a partial re-release of 196 tiles, but the SOM-gold WL
catalogue named `DR4.1` is the **full 1006-tile KiDS-1000** — confirmed independently by `NAXIS2` =
21,262,011.

---

## 3. Files to fetch for the systematics nulls (small, public, already on GitHub)

```
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/PSFRES_CORRMAP/c1_map.fits
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/PSFRES_CORRMAP/c2_map.fits
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/PSFRES_CORRMAP/exposure_map.fits
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/PSFRES_CORRMAP/create_c12_mock.py
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/PSFRES_CORRMAP/README.md
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/Calc_2pt_Stats/2D_GGL/KiDS_Patches.dat
```
Each map is 17,642,880 B. `create_c12_mock.py` builds a mock KiDS catalogue of the residual model at the
position of every KiDS galaxy — i.e. it generates the **arbitrary-input control** for this systematic
directly. `KiDS_Patches.dat` (85,738 B) is the patch definition used for the bootstrap that produced the
7.5 × 10⁻⁸ prior.

---

## 4. What "DR4.1" actually is, and what the `MASK` column already had done to it

From `https://kids.strw.leidenuniv.nl/DR4/release-description-KiDS-ESO-DR4.1.pdf` (1,466,895 B), quoted in
substance:

> DR4.1 fixes a bug in the production of the DR4.0 catalogues which produced **erroneous `MASK` values for
> the VIKING NIR photometry**. On **196 of the 1006 tiles**, up to **~5 % of sources** were affected. DR4.1
> ships new multi-band catalogues and updated masks for those tiles. **The ugri images and single-band
> catalogues are byte-identical to DR4.0.** With the corrected masks the total unmasked area with valid
> 9-band photometry rises by **0.5 %** relative to DR4.

⇒ **The thing DR4.1 fixes is exactly the `MASK` column.** If any downstream step reaches for a DR4.0
product, masking is wrong for up to 5 % of sources on 196 tiles. Everything delivered and manifested here
is DR4.1.

**Checked for this row specifically: 0 of the 2,100 SAMI GAMA lenses sits on a bug-affected tile.** The 139
re-released KiDS-N tiles span RA 157.0–171.5, 187.5–210.0, 220.6/221.6, 225.0–237.7 at
dec ∈ {−3.5, −2.5, −1.5, +1.5, +2.5}. Only RA 220.6 and 221.6 fall inside the G15 RA window and both sit at
dec −3.5, outside G15's declination range. **The mask bug does not touch this lens sample at all.**

### `MASK` bit meanings (Table 8 of the release description), bit 0 upward
```
0  THELI manual mask (very conservative)
1  THELI automatic large star halo mask (faint)
2  THELI automatic large star halo mask (bright), or bright star mask
3  Manual mask around globular clusters, Fornax dwarf, ISS passage
4  THELI void mask, or asteroids, or weight = 0
5..9   VIKING Z / Y / J / H / Ks band image masked
10..13 Astro-WISE u / g / r / i band halo+stellar PULECENELLA mask, or weight = 0
14 Object outside the RA/DEC cut for its tile
15 not used (reserved as the sign bit of a 2-byte FITS integer)
```

### 🔴 A bitmask selection has **already been applied** to the gold catalogue — do not re-cut on `MASK == 0`
Across 62,735 real rows read from the head of the file, `MASK` takes **only four values**:

```
MASK =    0   56,074 rows   89.38 %   (no bits)
MASK =    2    3,262 rows    5.20 %   (bit 1  — THELI automatic large star halo mask, faint)
MASK = 4098    1,993 rows    3.18 %   (bits 1 and 12)
MASK = 4096    1,406 rows    2.24 %   (bit 12 — Astro-WISE r-band halo+stellar PULECENELLA mask)
```

**Only bits 1 and 12 ever survive; every one of the other fourteen bits is absent from all 62,735 rows.**
That is the signature of a bitmask selection having already been applied at build time, retaining exactly
the two bits KiDS tolerates for lensing. (The constant is not stated in the DR4.1 release description and
is not asserted here — the empirical bit pattern is.)

**⇒ Re-cutting the gold catalogue on `MASK == 0` would discard 10.62 % of the sources, and not at random:
bit 1 is the faint star-halo mask and bit 12 the r-band stellar-halo mask, so the loss is concentrated
around bright stars — exactly where a local-aperture estimator is already most exposed to a spatially
coherent additive.** Use the catalogue as delivered. `fitclass` is `0` for 62,616 rows and `−9` for 119
(0.19 %); the `−9` rows all carry `weight ≈ 15.44–15.56`, i.e. they are not zero-weighted.

Other selections already applied on disk, verified on the same sample:
* `Z_B` strictly within **(0.1, 1.2]** — fraction inside = 1.000
* `weight > 0` — fraction = 1.000
* `|e| ≤ 1` — fraction = 1.000
* `fitclass ∈ {0, −9}`, `SG_FLAG ∈ {0, 1}`

### One open item the row should settle before publishing
KiDS's own analysis code (`Cat_to_Obs_K1000_P1/Calc_2pt_Stats/create_tomocats.py`) reads
`autocal_e1_<blind>` / `autocal_e2_<blind>` from the internal catalogue, with plain `e1_<blind>` commented
out. The public DR4.1 file ships a single unblinded `e1`/`e2` pair and the header does not say which of the
two it corresponds to. The fiducial KiDS-1000 figures are all labelled `KAll.autocal.BlindC...`, so `e1`/`e2`
are **most likely** the autocal ellipticities with the blinding removed — but that is an inference, not a
documented statement, and it is flagged rather than asserted. **It does not change the c-subtraction
procedure either way**; it would only matter if the row compares its own recovered `c` against Giblin's
published value at the 10 % level.

### Confirmation that the c-recipe here is the one KiDS actually ran
`create_tomocats.py` computes, per tomographic bin, `c1 = weighted mean of e1`, `c2 = weighted mean of e2`,
then `e1_corr = e1 − c1`. Its `Bootstrap_Error_csq` returns `std((bt_e1 − c1)² + (bt_e2 − c2)²)` over
`nboot` resamples — **which is exactly the `δε̄²` quantity whose largest per-bin value gives the
σ = 7.5 × 10⁻⁸ prior.** The 2.739 × 10⁻⁴ figure in §0 is therefore not a paraphrase of the paper; it is the
square root of the number their own published code produces.

Also worth knowing: their code passes `e1`/`e2` straight into TreeCorr as `g1`/`g2` with
`ra_col='ALPHA_J2000'`, `dec_col='DELTA_J2000'`, `w_col='weight'` and **no sign flip anywhere**. For a
parity-odd estimator that is the load-bearing convention statement — ⚠ but note that the *photometric*
angles in the same catalogue use the opposite handedness (`THETA_J2000` is documented "**West of North**"
and `PAgaap` "North of West"), whereas SAMI's `PA_GASKIN` is "Anticlockwise, North = 0" i.e. **East of
North**. **Do not cross-wire a photometric PA from the KiDS catalogue with a SAMI kinematic PA without
fixing the handedness first — that is a silent sign flip straight into a parity-odd statistic.**
