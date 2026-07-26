# T6 — NGC 1068 / X-ray-bright Seyfert neutrino extension: data bundle

Fetched, verified and published 2026-07-25 (UTC) for the T6 ChatGPT Pro thread, which parked its
4LAC-FSRQ angular-halo target and pivoted to an **energy-dependent, PSF-deconvolved** neutrino
extension around **NGC 1068 and X-ray-bright Seyferts**.

Everything below was verified by opening the file and reproducing a published number — never by
HTTP status alone.

---

## 🔴 FINDINGS THAT CHANGE WHAT CAN VALIDLY BE COMPUTED

Read these before designing anything. Each one is measured from the delivered files, not quoted
from a summary.

### 1. There are exactly FOUR IRF sets for FOURTEEN event seasons — and the readme says so verbatim

The IceTracks-DR2 publisher readme (`DR2_readme.txt`, doi:10.7910/DVN/MMIIZA, last updated
13 March 2026) states:

> "Because the detector configuration have been unified for all IC86 seasons, the effective area
> for IC86 should be used for IC86-2011 through IC86-2021."

The release ships **4** `*_smearing.csv` (IC40, IC59, IC79, IC86) and **4** `*_effectiveArea.tab`
(IC40, IC59, IC79, IC86) against **14** event files (IC40, IC59, IC79, IC86_I … IC86_XI).
**Eleven of the fourteen seasons share one single smearing matrix and one single effective area.**
A `season` axis in any PSF/IRF product is therefore **not separable** — it can only ever carry
4 distinct values, and 11 seasons are degenerate by construction.

### 2. 🔴 The angular-error calibration is tied to an E⁻² flux — the thread's own target spectrum

Publisher readme, on both the event `AngErr[deg]` column and the smearing-matrix `AngErr` axis:

> "The errors are calibrated using simulated events so that they provide correct coverage for an
> E^{-2} power law flux."

This cuts both ways and both directions matter for T6:

- The **E⁻² extension the thread is proposing is the matched case** — the per-event angular
  uncertainties are calibrated for exactly that spectrum.
- **NGC 1068's measured spectrum is not E⁻².** IceCube's 13.1-yr fit is
  **γ = 3.4 ± 0.2** (arXiv:2510.13403, ApJL 1000 L26 (2026)). At γ = 3.4 the released `AngErr`
  values do **not** carry guaranteed coverage, and a PSF deconvolution that treats them as
  calibrated will absorb that mismatch into the deconvolved width. The smearing matrix is the
  escape hatch: it gives the **true** PSF axis (`PSF_min/max[deg]`, the true angle between the
  neutrino origin and the reconstructed muon) jointly with `AngErr`, so the E⁻²-calibration
  assumption can be bypassed rather than inherited.

There is also a **hard floor of 0.20°** on `AngErr` — verified numerically in the matrices
(`1.999999881e-01` is the smallest lower bin edge). Any deconvolution that returns structure
below 0.2° is reading the floor, not the detector.

### 3. 🔴 The smearing matrices are NOT a regular 5-D array — they cannot be reshaped

Publisher readme:

> "bins are selected in each (E_nu, Dec_nu) bin independently. The bin edges are given in the
> smearing matrix files. All locations not given have a Fractional_Counts of 0."

Confirmed by inspection: the `(log10 E, PSF, AngErr)` sub-grid differs from one `(E_nu, Dec_nu)`
cell to the next — e.g. the first IC86 cell spans `PSF ∈ [10.52, 11.87]°`, while its last cell
spans `PSF ∈ [90.50, 138.47]°`. **`np.reshape` on these files silently produces garbage.**
Consume them as a row list keyed on the six bin-edge columns.

`Fractional_Counts` is a **fraction of events within the parent (E_nu, Dec_nu) cell** — it is
**not a density** and must not be divided by bin width before it is normalised.

### 4. 🔴 PSF-tail statistics are the weak point, and they are worst exactly where the thread said

Publisher readme:

> "The simulations statistics, while large enough for direct sampling, are limited when producing
> these tables, ranging from just 621,843 simulated events for IC40 to 12,097,409 simulated events
> for IC86."

That is a **19× spread in MC statistics across the four configurations**, spread over a 5-D table.
The thread nominated "energy- and season-dependent PSF-tail miscalibration" as its own worst
adversary; this is the quantitative form of it. IC40 rows in the lowest `(E_nu, Dec_nu)` cells are
literally degenerate (all bin edges `0.000000`), i.e. no simulated events survived there at all.
**Any per-configuration PSF-tail difference between IC40 and IC86 must first be checked against
this 19× statistics difference before it is read as physics.**

### 5. Effective-area energy coverage does NOT match the readme's stated simulation range

Measured over all 2000 rows (40 energy bins × 50 declination bins) of each file:

| config | grid, log₁₀(E_ν/GeV) | highest bin with A_eff > 0 | max A_eff (cm²) |
|---|---|---|---|
| IC40 | 2.00 → 10.00, 0.20 wide | **10.00** | 2.628e+08 |
| IC59 | 2.00 → 10.00, 0.20 wide | **9.00**  | 1.678e+08 |
| IC79 | 2.00 → 10.00, 0.20 wide | **9.00**  | 1.600e+08 |
| IC86 | 2.00 → 10.00, 0.20 wide | **8.80**  | 1.945e+08 |

The readme says the effective areas are "averaged over bins using simulated muon neutrino events
ranging from 100 GeV to 100 PeV", i.e. log₁₀E 2 → **8**. The tables carry non-zero entries **above**
that. Treat A_eff above log₁₀E = 8 as outside the stated simulation range, and note that the
declination grid of the effective areas (50 bins) is **finer than** the declination grid of the
smearing matrices — they do not share a binning.

Azimuthal effective areas are **not** in the release ("may be made available upon request"); the
readme puts the azimuthal variation at ~10%, relevant only below 1-day timescales.

### 6. 🔴 The "47 X-ray-bright AGN" table has 48 rows — NGC 1068 is in it and is NOT one of the 47

`icecube_2510.13403_tab_xray_47sources.csv` reproduces the paper's own longtable, which lists
NGC 1068 first for reference. The abstract is explicit: the 3.3σ binomial excess comes from
"an ensemble of 11 sources, **with NGC 1068 excluded from the sample**". The delivered CSV carries
an `in_47_source_sample` column (`0` for NGC 1068, `1` for the other 47) so the cut is not left to
a name match. Row-count checks against the papers' own statements pass: 110 / 47 / 14.

### 7. 🔴 The named BASS DR2 paper does not contain the X-ray luminosities either IceCube paper uses

BASS DR2 (Koss+ 2022, ApJS 261, 2 = doi:10.3847/1538-4365/ac6c05 = arXiv:2207.12432) is the
**AGN counterpart / optical-spectroscopy** catalogue. Its machine-readable tables carry
coordinates, AGN type, redshift, distance, black-hole mass, L_bol and Eddington ratio — and
**no X-ray flux or X-ray luminosity column at all**.

But both IceCube papers weight on X-rays:

- arXiv:2510.13403 weights on **intrinsic 20–50 keV flux** "from the BASS catalog";
- arXiv:2602.10208 weights on **log₁₀(L^intr_2–10 keV)** "from BASS".

Those columns live in **BASS DR1 (Ricci+ 2017, ApJS 233, 17 = J/ApJS/233/17)**, whose `table13.dat`
carries exactly `logL2-10int` **and** `logL20-50int` for 801 sources. That table is therefore
included here — without it the X-ray leg of this hunt cannot be reconstructed from the DR2 paper
alone.

### 8. The primary IceCube download path for the NGC 1068 release is dead site-wide

`https://icecube.wisc.edu/data-releases/20220913_Evidence_for_neutrino_emission_from_the_nearby_active_galaxy_NGC_1068_data.zip`
— the link the DOI landing page itself serves — returns **HTTP 404**. So does every other
`icecube.wisc.edu/data-releases/*.zip` probed (Galactic Plane 2023, HESE 7.5-yr 2021): the whole
legacy direct-download path is broken, not just this file. A first attempt produced a
**153,393-byte HTML 404 shell delivered as `.zip`** — the exact "HTTP 200 is not the file" trap;
it was deleted, not published. The bytes here come from the Internet Archive capture of the
publisher's own URL (snapshot `20240722014823`), and the archive's recorded length matches.

---

## WHAT IS IN THIS DIRECTORY

| path | what it is | verification |
|---|---|---|
| `icecube_seyfert_tables/` | the six published source-list and results tables of arXiv:2510.13403 and arXiv:2602.10208, extracted verbatim from the arXiv LaTeX into CSV | row counts 110 / 47 / 14 reproduce the papers' own statements |
| `icecube_seyfert_tables/extract_tables.py` | the extractor, so every cell is traceable to the LaTeX | re-runs from `arxiv.org/e-print/<id>` |
| `bass_dr2_koss2022/` | BASS DR2 AGN catalogue, CDS machine-readable form of Koss+ 2022 (ApJS 261, 2) | 1449 / 858 / 47 records — exact match to the CDS `ReadMe` file summary |
| `bass_dr1_xray_ricci2017/` | BASS DR1 X-ray catalogue, Ricci+ 2017 (ApJS 233, 17) — **the X-ray luminosities both IceCube papers weight on** | 838 / 836 / 836 / 801 / 56 records — exact match to its `ReadMe` |
| `bass_dr2_lines_oh2022/` | BASS DR2 spectroscopic line measurements (Oh+ 2022, BASS XXIV) as published on bass-survey.com | gzip magic + 9 machine-readable tables unpack cleanly |
| `icetracks_dr2_irfs/` | the four IceTracks-DR2 effective areas, and per-source declination slices of the four smearing matrices | byte counts identical to the publisher's; see `IRF_NOTES.md` |

Bulk binaries are release assets, not repo files — see `URL_VERIFICATION.md` for every complete URL.

---

## 🔴 FINDINGS 9–11 — the NGC 1068 Science-2022 release, opened and measured

### 9. The energy-dependent PSF the thread is asking for already exists, as a photospline

`ps_data_release/analysis_scripts/kdes/sig_E_psi_photospline_v006_4D.fits` —
**1,037,407,680 bytes**, a 4-D photospline of the **signal (E, ψ) PDF**: the analysis's own
energy-dependent angular response for NGC 1068. Alongside it:

| file | bytes | what |
|---|---|---|
| `kdes/sig_E_psi_photospline_v006_4D.fits` | 1,037,407,680 | signal (E, ψ) PDF, 4-D photospline |
| `kdes/E_dec_photospline_v006_3D.fits` | 7,225,920 | signal energy-vs-declination PDF |
| `kdes/bg_2d_photospline.fits` | 112,320 | background 2-D PDF |
| `kdes/bg_2d.pkl` / `bg_2d_values.pkl` | 182,751 / 180,179 | the same background KDE, pickled |
| `lib/aeff_spline.pkl` | 2,394 | effective-area spline |
| `lib/likelihood_sbratio_2d.py` | 8,465 | the S/B likelihood actually used |
| `NGC_1068_Science_Analysis.ipynb` | 97,571 | the notebook that reproduces the result |

The 1.04 GB photospline is inside the release zip only — it will not fit a Pro sandbox. Ask for a
specific slice and it can be cut out here.

### 10. 🔴 The Science-2022 event list is in RADIANS and has a 0.1° angular-error floor — IceTracks-DR2 is in DEGREES with a 0.2° floor

`resources/event_list.txt`, **19,452 events**, columns `logE,ra,dec,angErr`, measured:

| column | min | median | max |
|---|---|---|---|
| `logE` (reconstructed muon, GeV) | 2.000022 | 2.722887 | 5.140889 |
| `ra` (**radians**) | 0.448216 | 0.711639 | 0.971085 |
| `dec` (**radians**) | −0.087138 | 0.071771 | 0.261357 |
| `angErr` (**radians**) | 0.001745 | 0.009413 | 0.118697 |

- `ra` never exceeds 0.97 and `dec` spans −4.99° to +14.98° — **these are radians, not degrees.**
- `angErr` minimum is 0.001745 rad = **exactly 0.1000°**. IceTracks-DR2's floor is **0.2°**.
  **The two datasets have different angular-error floors, in different units.** A PSF-tail
  comparison across them is a units-and-floor artefact unless both are handled explicitly.
- The events cover a **~30° × 20° box around NGC 1068 only** (RA 25.7°–55.6°, Dec −5.0°–+15.0°) —
  it is **not** an all-sky sample and cannot serve the 47-source Seyfert list.
- Reconstructed energy tops out at log₁₀(E/GeV) = 5.14, i.e. **138 TeV**.

The IceTracks-DR2 readme also says outright: *"Events from this release should not be combined with
any other releases."*

### 11. A "completed, exit code 0" background job produced a truncated artefact

The first pass that wrote the per-declination smearing slices reported success, but all 30 IC86
files were cut off mid-stream with no gzip end-of-stream marker. It was caught only because every
slice was re-opened and its rows counted. After a clean re-run, all **120 slices verified at
exactly 112,000 rows each — 13,440,000 rows total, matching 4 × 3,360,000.**
Exit status is not evidence that a file is complete.
