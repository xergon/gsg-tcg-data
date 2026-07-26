# T9 — Querejeta CANFAR directory listing, LITERAL BASENAMES
Retrieved 2026-07-26T06:30Z (TRUE UTC). Cohort: NGC 628, NGC 3351, NGC 3627, NGC 1566, NGC 1672.

## 🔴 FINDING 0 — THERE IS NO AUTHENTICATION. THE THREAD'S PREMISE WAS WRONG.
The thread wrote: *"The authenticated directory listing must determine the literal basenames."*
**No login, no account, no certificate, no terms-acceptance is involved.** Both containers list
**anonymously** over plain HTTP GET and every file downloads anonymously.
`www.canfar.net/storage/vault/list/...` is a JavaScript shell and returns nothing useful — that is
what has made this look walled. The real IVOA VOSpace endpoints are:

- **listing**  `https://cadc-west-01.canfar.net/vault/nodes/<path>`   (returns VOSpace XML)
- **download** `https://ws-cadc.canfar.net/vault/files/<path>`        (supports HTTP Range / 206)

## 🔴 FINDING 1 — NGC 3351 HAS NO SPIRAL ARMS AT ALL. THE 5-GALAXY ARM COHORT IS REALLY 4.
`Querejeta_etal_2024/` contains **28 galaxies × 2 files + 1 README = 57 nodes. NGC3351 IS NOT ONE OF THEM.**
This is not an omission. Three independent products agree:

1. `table_components.csv` — NGC3351 row has `Spiral arms = 0` (it has Disk, Bulge, Bar, Lens_1, Ring_1, Ring_2).
2. `table_spiral_arms.csv` — **zero rows for NGC3351.** Its header states the table
   *"lists only galaxies where at least one spiral arm segment was retained after Quality Assurance"*.
3. `NGC3351_env_mask_simple.fits.gz` pixel values are exactly `{0, 1, 2, 9, 10}` =
   centre / bar / **interbar-for-galaxies-WITHOUT-spiral-mask** / **disc-where-no-spiral-arms-identified**.
   Classes 5, 6, 7 (spiral arms, interarm) are **entirely absent**.

**⇒ An arm-crossing / arm-phase hysteresis test is STRUCTURALLY IMPOSSIBLE on NGC 3351.**
The "4 of 5 galaxies" sub-gate can at best be evaluated on **4 spiral-capable galaxies (max 4/4)**,
which makes an already ~6%-power gate strictly worse. Either drop NGC 3351 from the arm test and
re-derive the gate on N=4, or replace it with a spiral-bearing PHANGS galaxy. **Do not fetch a
NGC3351 spiral mask — none exists.**

Retained spiral-arm segment counts (from `table_spiral_arms.csv`), which match the mask encoding exactly:
`NGC0628 = 7`, `NGC1672 = 6`, `NGC1566 = 4`, `NGC3627 = 4`, `NGC3351 = 0`.

## 🔴 FINDING 2 — MASK ENCODING (from `README.pdf`, verbatim semantics)
**`env_masks_simple`** — one environment per pixel:
`1` centre · `2` bar (excl. bar ends) · `3` bar ends (bar∩spiral) · `4` interbar (R<R_bar, outside bar,
for galaxies WITH a spiral mask) · `5` spiral arms inside interbar (R<R_bar) · `6` spiral arms (R>R_bar) ·
`7` interarm (only over the R spanned by spiral arms, R>R_bar) · `8` outer disc (R>spiral arms, only for
galaxies with identified spirals) · `9` interbar for galaxies WITHOUT a spiral mask · `10` disc (R>R_bar)
where **no spiral arms were identified** (e.g. flocculent spirals).
Collapsed 5-class scheme used in Querejeta+2021: `1`=centre, `2&3`=bar, `4&7&8`=interarm, `5&6`=spiral arms,
`9&10`=disc in galaxies without spirals.

**`env_masks_full`** — ADDITIVE, environments may overlap:
`Disc +1` (second disc, e.g. nuclear disc, `+2`) · `Bulge +10` · `Bar +100` (second/nuclear bar `+200`) ·
`Lens +1000` (second `+2000`) · `Ring +10000` (second `+20000`, third `+30000`) ·
**`Spiral arms +100000` for the FIRST segment, `+200000` for the SECOND, etc.** · `Centre +1000000`.
⚠ **The spiral digit is a SEGMENT INDEX, not a flag.** e.g. `700001` = spiral segment 7 + disc.
Verified against the data: NGC0628 max value `700001` (7 arms), NGC1672 `600001` (6), NGC1566 `400002` (4),
NGC3627 `400001` (4). `101` = bar+disc; `10101` = ring+bar+disc.
All masks: `BITPIX = -32` (float32 — cast before bitmask arithmetic), `CDELT1 = -0.00020833333333333` deg
(**0.75″/px**), Spitzer/IRAC 3.6 µm astrometric grid.

## 🔴 FINDING 3 — `Querejeta_etal_2024` masks are NARROW RIDGE masks, a SUBSET of Querejeta+2021
From `README_Querejeta2024.txt`: the `_narrow` masks dilate the ridge of peak CO/Hα intensity along the
log-spiral backbone, smoothed with a **FWHM = 7.5″ Gaussian** and thresholded at **0.01**; the final narrow
mask is the **union of the CO and Hα versions** and is **by construction a subset of the original mask**,
typically covering **~50% of its area**. `<GAL>_spiral_mask.fits` is the Querejeta+2021 constant-width mask;
`<GAL>_spiral_mask_narrow.fits` is the thin 2024 variant. **Halving the arm footprint halves the aperture
count inside arms — this directly attacks T9's already-marginal N ≥ 50 independent-aperture requirement.**

---
# LITERAL BASENAMES — verbatim, cohort only

## A. `vos://cadc.nrc.ca~vault/phangs/RELEASES/Querejeta_etal_2024/`  (57 nodes; 4 of 5 cohort present)
```
NGC0628_spiral_mask.fits                 11517120 B
NGC0628_spiral_mask_narrow.fits          11517120 B
NGC1566_spiral_mask.fits                 13144320 B
NGC1566_spiral_mask_narrow.fits          13144320 B
NGC1672_spiral_mask.fits                  5777280 B
NGC1672_spiral_mask_narrow.fits           5777280 B
NGC3627_spiral_mask.fits                 12487680 B
NGC3627_spiral_mask_narrow.fits          12487680 B
README_Querejeta2024.txt                     1619 B
NGC3351 — ABSENT (no spiral arms; see FINDING 1)
```
Cohort subtotal 8 files = 85,853,760 B (81.9 MiB). Magic bytes verified `SIMPLE  =` by HTTP 206 range read.
Full 28-galaxy listing: `RAW_LISTING_Querejeta_etal_2024.txt`.

## B. `vos://cadc.nrc.ca~vault/phangs/RELEASES/PHANGS_env_masks/`  (74 galaxies, all 5 cohort present)
```
PHANGS_env_masks.bundle.tar.gz           24280576 B   (whole release, 74 galaxies)
README.pdf                                1695176 B
catalog.pdf                              19544547 B
table_components.csv                         2443 B
table_parameters.csv                        13997 B
table_spiral_arms.csv                       12325 B
env_masks_full/    NGC0628_env_mask_full.fits.gz     35235 B
env_masks_full/    NGC1566_env_mask_full.fits.gz     34593 B
env_masks_full/    NGC1672_env_mask_full.fits.gz     22787 B
env_masks_full/    NGC3351_env_mask_full.fits.gz     25533 B
env_masks_full/    NGC3627_env_mask_full.fits.gz     29814 B
env_masks_simple/  NGC0628_env_mask_simple.fits.gz   37036 B
env_masks_simple/  NGC1566_env_mask_simple.fits.gz   38894 B
env_masks_simple/  NGC1672_env_mask_simple.fits.gz   24992 B
env_masks_simple/  NGC3351_env_mask_simple.fits.gz   23799 B
env_masks_simple/  NGC3627_env_mask_simple.fits.gz   32648 B
```
⚠ **The on-disk basenames end `.fits.gz`. The README.pdf text writes them as `.fits` (uncompressed) — the
README is WRONG about the extension.** Do not construct URLs from the README.
⚠ **The README documents a `parameters/` subdirectory. IT DOES NOT EXIST.** The three CSVs sit at the
`PHANGS_env_masks/` top level. `RAW_LISTING_PHANGS_env_masks.txt` is the ground truth.

### Direct CANFAR download URLs, complete and verbatim, one per line
```
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/Querejeta_etal_2024/README_Querejeta2024.txt
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/Querejeta_etal_2024/NGC0628_spiral_mask.fits
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/Querejeta_etal_2024/NGC0628_spiral_mask_narrow.fits
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/Querejeta_etal_2024/NGC1566_spiral_mask.fits
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/Querejeta_etal_2024/NGC1566_spiral_mask_narrow.fits
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/Querejeta_etal_2024/NGC1672_spiral_mask.fits
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/Querejeta_etal_2024/NGC1672_spiral_mask_narrow.fits
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/Querejeta_etal_2024/NGC3627_spiral_mask.fits
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/Querejeta_etal_2024/NGC3627_spiral_mask_narrow.fits
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/README.pdf
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/catalog.pdf
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/table_components.csv
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/table_parameters.csv
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/table_spiral_arms.csv
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/PHANGS_env_masks.bundle.tar.gz
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/env_masks_full/NGC0628_env_mask_full.fits.gz
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/env_masks_full/NGC1566_env_mask_full.fits.gz
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/env_masks_full/NGC1672_env_mask_full.fits.gz
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/env_masks_full/NGC3351_env_mask_full.fits.gz
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/env_masks_full/NGC3627_env_mask_full.fits.gz
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/env_masks_simple/NGC0628_env_mask_simple.fits.gz
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/env_masks_simple/NGC1566_env_mask_simple.fits.gz
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/env_masks_simple/NGC1672_env_mask_simple.fits.gz
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/env_masks_simple/NGC3351_env_mask_simple.fits.gz
https://ws-cadc.canfar.net/vault/files/phangs/RELEASES/PHANGS_env_masks/env_masks_simple/NGC3627_env_mask_simple.fits.gz
```

## Also present in the same vault, not requested but relevant
`phangs/RELEASES/` holds 28 containers, including `PHANGS-JWST/` (`v0p4`, `v1p0`, `v1p0p1`, `v1p1`,
`v1p1p1`), `PHANGS-MUSE/` (`DR1.0` only), `Querejeta_etal_2023/` (`ic342` only — not the cohort),
`Lang_etal_2020/`, `Sun_etal_2018/2020/2020b/2022/2023/`, `Watkins_etal_2022/2023b/`,
`Neumann_et_al_2024/`, `Neumann_etal_2024b/`, `Rosolowsky_etal_2021/`, `Leroy_etal_2025/`, `ALMOND/`, `SWAN/`.
⚠ `PHANGS-JWST/` on CANFAR carries a **`v1p1p1`** that is NEWER than the `v1p1` the thread pinned.

---
# SECONDARY — reachability of the rest of the T9 manifest (metadata only, no bulk pulled)

| target | status | evidence |
|---|---|---|
| Querejeta CANFAR (both dirs) | **PUBLIC, anonymous** | listed + magic bytes verified |
| PHANGS-JWST `10.17909/ew88-jt15` | **PUBLIC, anonymous** | DOI → `hlsp/phangs/phangs-jwst`; `v1p1/` has all 5 cohort dirs, all 8 filters |
| PHANGS-CAT DR5 `10.17909/jray-9798` | **PUBLIC, anonymous** | all 7 thread-named basenames exist verbatim in `dr5/` |
| Williams pattern speeds, commit `33e8148` | **PUBLIC** | commit resolves; table fetched + parsed |
| MHONGOOSE `10.5281/zenodo.10907080` | **PUBLIC, open** | `MHONGOOSE_singletrack.zip` 17,577,036 B, md5 `9f7f6a38ead801b69a45140000f0df50` |
| PHANGS-MUSE ESO `10.18727/archive/47` | DOI resolves; **per-file manifest NOT enumerated this pass** | see DEFERRED |
| THINGS | **NOT attempted this pass** | see DEFERRED |

### PHANGS-JWST — `https://archive.stsci.edu/hlsps/phangs-jwst/v1p1/`
Version dirs present: `v0p4`, `v1p0p1`, `v1p1` (**note: no `v1p0` on MAST, unlike CANFAR**), plus `footprints/`.
Release readme: `hlsp_phangs-jwst_jwst_miri-nircam_all_multi_v1p1_readme.txt`.
All 5 cohort galaxies present. Per-galaxy pattern, verified on `ngc0628/` — **all 8 filters present**:
```
hlsp_phangs-jwst_jwst_nircam_ngc0628_f200w_v1p1_img.fits
hlsp_phangs-jwst_jwst_nircam_ngc0628_f300m_v1p1_img.fits
hlsp_phangs-jwst_jwst_nircam_ngc0628_f335m_v1p1_img.fits
hlsp_phangs-jwst_jwst_nircam_ngc0628_f360m_v1p1_img.fits
hlsp_phangs-jwst_jwst_miri_ngc0628_f770w_v1p1_img.fits
hlsp_phangs-jwst_jwst_miri_ngc0628_f1000w_v1p1_img.fits
hlsp_phangs-jwst_jwst_miri_ngc0628_f1130w_v1p1_img.fits
hlsp_phangs-jwst_jwst_miri_ngc0628_f2100w_v1p1_img.fits
hlsp_phangs-jwst_jwst_miri-nircam_ngc0628_multi_v1p1_img.tar.gz
```
Substitute `ngc1566 / ngc1672 / ngc3351 / ngc3627` for `ngc0628` in both the path and the basename.
🔴 **The products are `_img.fits` only. There are NO separate `SCI / ERR / CON / WHT` files** — those are
**extensions inside the single `_img.fits`**, not filenames. A sibling `_tweakback.tar.gz` exists per filter.
(C-TripleKappa was told to expect four separate SCI/ERR/CON/WHT products — that expectation is wrong.)

### PHANGS-CAT DR5 — `https://archive.stsci.edu/hlsps/phangs-cat/dr5/`
All 7 thread-named basenames confirmed present **verbatim**:
```
hlsp_phangs-cat_hst_acs-uvis_dr5-targets_v1_human-class1+2-primary.fits
hlsp_phangs-cat_hst_acs-uvis_dr5-targets_v1_human-class3-primary.fits
hlsp_phangs-cat_hst_acs-uvis_dr5-targets_v1_machine-class1+2-primary.fits
hlsp_phangs-cat_hst_acs-uvis_dr5-targets_v1_machine-class3-primary.fits
hlsp_phangs-cat_hst_acs-uvis_dr5-targets_v1_supplemental.fits
hlsp_phangs-cat_dr5-targets_v1_primary-readme.txt
hlsp_phangs-cat_dr5-targets_v1_supplemental-readme.txt
```
plus `bundles/`. Per-galaxy dirs exist one level up at `/hlsps/phangs-cat/` (incl. `ngc1566/`, `ngc3351/`,
`ngc3627/`), alongside `dr4/`, `anc/`, `bundles/`.

### Williams stellar pattern speeds
🔴 **PATH CORRECTION — the thread's path is wrong.** It asked for
`pattern_speeds_output/pattern_speed_table_v1p0.fits`. At commit `33e8148` there is **no
`pattern_speeds_output/` directory**; the file sits at the **repository root**:
```
https://raw.githubusercontent.com/thomaswilliamsastro/phangs_pattern_speeds/33e814890d5ede0d46bd351c0f65a54443560538/pattern_speed_table_v1p0.fits
```
Commit `33e814890d5ede0d46bd351c0f65a54443560538`, dated **2021-03-08T09:51:12Z**, message
*"Included fits table for pattern speeds"*. Fetched: **97,920 B**, starts `SIMPLE  =`,
sha256 `f3284c78fe7da6bd04e7ae0b662e2c9b824303c1cca60f259834ea6895538528`.
**83 rows.** Every column the thread required is present. **All 5 cohort galaxies present** (NGC3351 IS in
this table — it has a bar and a pattern speed, it simply has no spiral arms).

Cohort values, straight from the table (Ω_p in km/s/kpc, R_CR in kpc; `QUAL` 1 = best, 3 = worst):

| GALAXY | HAS_BAR | OM_P_MUSE_MASS | QUAL | R_CR_MUSE_MASS_1 | OM_P_ALMA | QUAL | OM_P_MUSE_HA | QUAL |
|---|---|---|---|---|---|---|---|---|
| NGC0628 | 0 | 31.071 | 1 | 4.507 | 32.941 | 1 | 35.418 | 1 |
| NGC1566 | 1 | 29.399 | **3** | 6.757 | 58.467 | 1 | 64.655 | 1 |
| NGC1672 | 1 | 22.733 | 1 | 6.073 | 32.471 | 2 | 28.071 | 1 |
| NGC3351 | 1 | 43.608 | 1 | 3.350 | 60.511 | 1 | 89.672 | **3** |
| NGC3627 | 1 | 29.128 | **2** | 1.901 | 45.798 | 1 | 50.687 | 1 |

🔴 **FINDING 4 — THE PRIMARY CLOCK IS THE WEAKEST ONE, AND THE TRACERS DISAGREE VIOLENTLY.**
The thread declared `OM_P_MUSE_MASS` PRIMARY and the CO/Hα speeds "adversarial tracer clocks". But
`OM_P_MUSE_MASS` carries the **worst** quality flags of the three (NGC1566 = 3, NGC3627 = 2), and the
tracers do not agree at the level a phase clock needs: **NGC1566 stellar 29.4 vs CO 58.5 vs Hα 64.7
(a factor ≈ 2)**, NGC3351 stellar 43.6 vs Hα 89.7 (also ≈ 2). NGC0628 is the only galaxy where all three
agree (31.1 / 32.9 / 35.4) — and NGC0628 is **unbarred** (`HAS_BAR = 0`), so its pattern speed is the
least well-posed physically. **A ×2 ambiguity in Ω_p is a ×2 ambiguity in arm-crossing time, i.e. the
hysteresis lag T9 is trying to detect is smaller than the uncertainty in its own clock.** This is a
wrong-target signal on the clock itself, independent of the aperture-count problem — flag it to T9 before
any survey is staged.
