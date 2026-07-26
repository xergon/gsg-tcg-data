# B1608+656 — VLA 8.5 GHz monitoring light curves (Fassnacht et al.)

Prepared 2026-07-26 (UTC) for GSG-TCG thread T8.

## 🔴 READ FIRST — SCOPE LIMIT (this is NOT the three-season product that was requested)

The request was for **all three VLA monitoring seasons, unshifted**, from
**Fassnacht et al. 2002, ApJ 581, 823 (DOI 10.1086/344368; arXiv astro-ph/0208420)**.

**That product does not exist in published numeric form.** Verified as follows:

* The arXiv e-print source of Fassnacht et al. 2002 (`https://arxiv.org/e-print/astro-ph/0208420`,
  224,065 B gzip tarball, single LaTeX file `Fassnacht.tex`) contains **exactly six tables**
  (`\tablenum{1}`…`\tablenum{6}`):
  1. Monitoring Observations (per-season summary only: start/end date, `N_obs`, `N_good`, mean spacing)
  2. Component Positions and Mean Flux Densities
  3. Results of Dispersion Analysis of Combined Data Set
  4. Measured Quantities (time delays, magnification ratios)
  5. Parameter Confidence Intervals from Combined Analysis
  6. Mass Model Parameters
  **None of them is a light curve.** The paper states the three-season light curves are *"shown in
  Figure 2"* (`f2.eps`) — normalised by each component's three-season mean and additionally shifted
  vertically by arbitrary offsets (+0.3, +0.08, −0.08, −0.30) for clarity. Figure 3 is the
  delay-*aligned* composite, i.e. explicitly shifted.
* Paper III contains **no** data-availability footnote, URL, or acknowledgement pointing to a
  light-curve file (grepped for `electronic`, `machine-readable`, `available`, `ftp`, `http`,
  `request`, `nrao`, `cfassnac`).
* **VizieR / CDS has no catalogue `J/ApJ/581/823`** (query returns a VizieR error page, not a table).
* The IOP article page exposes no supplementary / machine-readable table; the PDF is behind IOP's
  bot wall and was **not** bypassed.
* Nothing was found in the Wayback Machine for any seasons-2/3 flux file.

⇒ **Seasons 2 and 3 (1998 Feb–Oct, 1999 Jun–2000 Feb; 78 + 88 good epochs) are a hard blocker.**
They appear to have been published only as a figure. Obtaining them requires contacting the authors
(C. D. Fassnacht, UC Davis) — a human action. **Do not treat any digitisation of Figure 2 as data;
none was performed here, and none should be substituted silently.**

## What IS delivered — season 1, exactly as published

`b1608_vla_8p5ghz_lightcurves_long_season1_only.csv`

Season 1 (1996 Oct – 1997 May) **is** published numerically, in the *previous* paper:

* **Fassnacht, C. D., Pearson, T. J., Readhead, A. C. S., et al. 1999, ApJ, 527, 498**
  (Paper I; DOI 10.1086/308118; arXiv astro-ph/9907257), **Table 3 "Final Component Light Curves"**.
* The same numbers are still served as the author's electronic table at
  `http://www.aoc.nrao.edu/~cfassnac/1608flux.tab` (3,906 B ASCII; the URL printed in Paper I was
  `http://www.nrao.edu/~cfassnac/1608flux.tab`, which is now dead (and has no Wayback capture) — the `aoc.` host still works).
  A verbatim copy is included here as `nrao_1608flux.tab`.

**Both sources were parsed independently and agree on all 62 epochs × 8 numbers with zero
mismatches.** That is the verification of this file.

### Rows and coverage

| quantity | value |
|---|---|
| rows | **248** (62 epochs × 4 images) |
| seasons present | **1 only** (62 good epochs) |
| seasons missing | **2 and 3** (see blocker above) |
| MJD range | **50366 – 50594** (= MJD−50000 of 366 – 594) |
| images | A, B, C, D — 62 rows each |
| frequency | 8.5 GHz |

**Unshifted, uncomposited, unaveraged, uninterpolated.** One row per (epoch, image), exactly the
published flux density and its published uncertainty.

### Columns

| column | populated? | source |
|---|---|---|
| `season` | yes — always `1` | Paper III Table 1 season definition |
| `MJD` | yes | Paper I Table 3 `MJD−50000` column, **+50000**. Integer day; no sub-day timestamp is published. |
| `image` | yes (`A`/`B`/`C`/`D`) | Paper I Table 3 column headers |
| `frequency_GHz` | yes — always `8.5` | Paper I (Observations): *"carried out at 8.5 GHz"* |
| `flux_mJy` | yes | Paper I Table 3 |
| `flux_error_mJy` | yes | Paper I Table 3 (the `±` value) |
| `array_configuration` | yes | joined on MJD from Paper I **Table 1 "Observations"**, `Array Configuration` column. Values: `A`, `B`, `BnA`, `D->A`, `A->BnA`, `BnA->B` (arrows = configuration-move epochs, verbatim from the paper's `$\rightarrow$`). All 62 epochs matched. |
| `phase_calibrator` | yes — always `1642+689` | Paper I §2 |
| `amplitude_calibrator` | yes — always `3C286_or_3C48` | Paper I (Observations): *"an absolute flux calibrator (3C 286 or 3C 48)"*. ⚠ **The paper does not state which of the two was used at which epoch**, so this is the published pair, not a per-epoch identification. Secondary flux calibrators (used for the systematic-error correction, not for the absolute scale) were **1634+627 and 1633+741**; they are not per-epoch either and are therefore not encoded as a column. |
| `quality_flag` | **partially** — 48 of 248 rows | verbatim `Comments` text from Paper I Table 1 (e.g. `Wind >= 10 m/s`, `Rain`, `Snow storms.`, `Elev. <= 30deg`). **Empty means Paper I Table 1 carried no comment for that epoch — not "unflagged good" in any formal sense.** Every epoch in this file already passed the paper's own good-epoch cut (epochs the authors rejected, e.g. MJD−50000 = 376 and 382, are absent from Table 3 and therefore absent here). |
| `original_table_or_epoch_id` | yes | `Fassnacht1999_ApJ527_498_Table3_MJDm50000=<n>` — audit key back to the exact published row |

**No column was interpolated, inferred, or invented.** Where the publication does not resolve a
quantity per epoch, that is stated above rather than filled in.

## ⚠ Structural findings the analysis must account for

1. **The season-1 numbers here are Paper I's calibration, NOT Paper III's.** Paper III (Data Reduction) states
   *"the season 1 data were recalibrated"* — the whole three-season set was retied to the primary
   flux calibrator **3C 343 (1634+628)** instead of 3C 286/3C 48, and in its final-light-curve section the authors **dropped
   1633+741** as a secondary calibrator, leaving season 1 with *no* secondary flux calibrator in the
   Paper III reduction. So the Paper III season-1 curve is a *different* reduction of the same
   visibilities. The recalibrated version was never tabulated.
2. **Epoch-count discrepancy — verified by cross-tabulation.** Paper III Table 1 lists season 1 as
   `N_obs = 66, N_good = 64`. Paper I's own observation table lists **64** epochs, and its published
   light-curve table has **62**: MJD−50000 = **376** (*"Elev. ≤ 30°. Thunderstorms"*) and **382**
   (*"T_sys > 100 K"*) are observed but carry no published flux densities. So Paper I's usable
   season-1 sample is 62, not the 64 that Paper III's `N_good` column implies.
3. Paper III normalises every light curve by its **three-season** mean, so its Figure 2 ordinate is
   not convertible to mJy without those means (its Table 2) — another reason not to digitise it.
4. Season 2 is described by the authors as having *"nearly a constant slope"* (featureless);
   season 3 carries the strong structure. Any three-season requirement is really a season-3 requirement.

## Provenance

| file | origin |
|---|---|
| `b1608_vla_8p5ghz_lightcurves_long_season1_only.csv` | built from Paper I `Fassnacht.tex` Tables 1 + 3 (arXiv astro-ph/9907257 e-print source), cross-checked against `nrao_1608flux.tab` |
| `nrao_1608flux.tab` | verbatim byte copy of `http://www.aoc.nrao.edu/~cfassnac/1608flux.tab` (fetched 2026-07-26 UTC, 3,906 B) |
| `CHECKSUMS.sha256` | sha256 of both files |

Papers:
* Paper I — Fassnacht et al. 1999, ApJ 527, 498 — DOI 10.1086/308118 — arXiv astro-ph/9907257
* Paper III — Fassnacht et al. 2002, ApJ 581, 823 — DOI 10.1086/344368 — arXiv astro-ph/0208420
