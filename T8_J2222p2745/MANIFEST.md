# T8 — SDSS J2222+2745 : published-data delivery (2026-07-25 UTC)

All files below are extracted from **public** journal / arXiv sources. Every number is traceable to a
published paper; nothing here is derived, fitted, or guessed.

## 🔴 FINDINGS THE THREAD MUST READ BEFORE IT COMPUTES

### F1 — The 36.4 ± 1.8 d anchor is a MODEL MEDIAN, not the CCF measurement, and its MEAN is 59.4 d
`36.4 (+1.8/-1.8)` is `\partaumedian` in **Williams et al. 2021b (ApJL 915, L9; arXiv 2103.10961)** —
the *dynamical-model* emissivity-weighted **median** rest-frame lag. In the same posterior:

| quantity | value |
|---|---|
| `tau_median` (the 36.4 ± 1.8 anchor) | 36.4 (+1.8/−1.8) rest-frame d |
| **`tau_mean`** | **59.4 (+2.7/−2.5) rest-frame d** |
| `r_median` | 33.0 (+2.4/−2.1) light days |
| `r_mean` | 48.3 (+3.5/−3.0) light days |
| `r_min` | 8.2 (+1.3/−1.1) light days |
| `beta` (radial shape) | 1.32 (+0.11/−0.09) |

The transfer function is strongly right-skewed: **mean/median = 1.63**. An injection test that injects a
delta-function lag at 36.4 d is NOT injecting this BLR's response — the first moment of the true
response is 59.4 d. Which moment the ΔBIC gate is defined on changes the answer materially.

The independent cross-correlation measurement (Williams et al. 2021a, ApJ 911, 64) is
**`tau_cen = 36.5 (+2.9/−3.9)`** rest-frame d — same central value, but **~2× wider and asymmetric**.
The ±1.8 is a *model posterior width*, not a measurement error bar. Using ±1.8 as if it were the
measurement uncertainty overstates the data's constraining power by roughly a factor of two.

### F2 — The macro-delay posterior in DOI 10.1088/0004-637X/813/1/67 is SUPERSEDED
That paper (Dahle et al. 2015 = arXiv 1505.06187) reports
`Δt_AB = 47.7 ± 6.0 d`, `Δt_AC = −722 ± 24 d` (95% CI).

**Current best values are Dyrland (2019):**
`Δt_AB = 42.44 (+1.36/−1.44) d`, `Δt_AC = −696.65 (+2.00/−2.10) d`
— quoted verbatim in Napier et al. 2023 (arXiv 2301.11240) Table `time_delays`, which states these are
"the most up-to-date values from the literature".

Shifts vs. the 2015 values: **AB moves 5.3 d, AC moves 25.4 d**; errors shrink ~4× and ~11×.
A 25-day error in the C-image macro delay is comparable to the *entire* 36.4 d BLR lag being tested.
**Using the 2015 posterior would put a systematic into the injection test larger than the signal.**
⚠ Dyrland (2019) is a **University of Oslo master's thesis**, not a journal article — the numbers are
public only via the Napier et al. 2023 quotation. No posterior samples are published, only the intervals.

### F3 — 4.5 yr, 5.3 yr and 6 yr are three different, all-correct baselines
- **4.5 yr** = the GMOS-N + NOT monitoring campaign itself (Williams 2021a abstract)
- **5.3 yr** = the effective baseline *after accounting for gravitational time delays* (Williams 2021b abstract) — this is the row's stated figure and it is correct
- **">6 yr"** = the light-curve duration built from the delay-shifted images (Williams 2021a abstract)

### F4 — The 2016–2020 campaign light curves are NOT published
Williams et al. 2021a ships exactly **three** machine-readable tables (standard stars, lags, line widths).
There is **no** table of the 47 spectroscopic epochs or the 86/49/41 NOT/ALFOSC photometric epochs, and
no Data Availability statement, Zenodo deposit, or GitHub link anywhere in the LaTeX source. The only
published epoch-level photometry for this system is Dahle et al. 2015 Table 1 (delivered here), which
**stops at MJD 57260 (2015 Aug)** — i.e. it ends *before* the reverberation campaign starts.
⇒ An "actual-cadence" injection test can use the delivered 2010–2015 cadence, or the campaign cadence
*descriptors* in F5, but the campaign epoch list itself does not exist in public form.

### F5 — Campaign cadence descriptors (verbatim, Williams et al. 2021a)
- 36 lunations, **June 2016 → September 2020**; 9 lunations split over 2 nights, 1 over 3 ⇒ **47 epochs**
- 6000 s exposure per lunation, queue mode, **April–December** visibility window
- **average spectroscopic cadence 10 d during the 8 months of visibility per season**
- NOT photometry from 2016 June 1: **86 (g), 49 (i), 41 (He I 5876 narrow band)** epochs
- Losses: one full lunation Aug 2017 (weather); 1/3 of the July 2019 allocation (weather);
  April 2020 lunation (COVID shutdown, recovered as an extra July 2020 epoch)

### F6 — Three of the row's named identifiers are a DIFFERENT lens system (SN Refsdal)
`10.3847/0004-637X/820/1/50` (Rodney et al. 2016), `10.3847/1538-4357/ac4ccb` and `arXiv 2305.06377`
(Kelly et al. 2023 — these two are the same paper) are all **SN Refsdal in MACS J1149**, not
J2222+2745. This is self-consistent with the row's "HST visit/exposure IDs + MAST calibrated exposures
+ difference images" item, which fits Refsdal's WFC3/IR programme, not J2222. Treated as a second
target and delivered: Refsdal's full DOLPHOT difference-image photometry is public (828-line MRT).
Kelly et al. 2023 measures **Δt(SX−S1) = 376.0 (+5.6/−5.5) d — 1.5% precision**, blind, with
microlensing and millilensing included in the error budget. That is by far the tightest lensed-source
delay available and a much sharper injection-test lever than J2222.

### F7 — MJD trap in the delivered light curve
Dahle et al. 2015 Table 1 is headed "MJD" but the values are **MJD − 50000**. The delivered CSV carries
BOTH columns; use `MJD`, not `MJD_minus_50000`.

---

## GEMINI PROGRAMME IDs — recovered, NOT guessed

The row required these come from the archive, "do not guess". **The Gemini Observatory Archive is
returning HTTP 403 to this host** (see BLOCKED). I did **not** guess and did **not** attempt any
bypass. Instead the IDs are quoted **verbatim from the published acknowledgements** of
Williams et al. 2021a (arXiv 2011.02007, `vr_lags.tex` line 911) — a published, authoritative source:

> "The Gemini data were obtained from programs GN-2016B-Q-28, GN-2017A-FT-9, GN-2017B-Q-33,
> GN-2018A-Q-103, GN-2018B-Q-143, GN-2019A-Q-203, GN-2019B-Q-232, GN-2020A-Q-105, and GN-2020B-Q-132
> (PI Treu), and were processed using the Gemini IRAF package."

| # | Programme ID | Semester |
|---|---|---|
| 1 | GN-2016B-Q-28 | 2016B |
| 2 | GN-2017A-FT-9 | 2017A (Fast Turnaround) |
| 3 | GN-2017B-Q-33 | 2017B |
| 4 | GN-2018A-Q-103 | 2018A |
| 5 | GN-2018B-Q-143 | 2018B |
| 6 | GN-2019A-Q-203 | 2019A |
| 7 | GN-2019B-Q-232 | 2019B |
| 8 | GN-2020A-Q-105 | 2020A |
| 9 | GN-2020B-Q-132 | 2020B |

Plus, from Dahle et al. 2015 (3 GMOS g-band points in the delivered light curve): **GN-2015A-FT-16**.

ALFOSC provenance ("Archive IAA" in the row): ALFOSC "is provided by the Instituto de Astrofisica de
Andalucia (IAA) under a joint agreement with the University of Copenhagen and NOTSA"
(Williams et al. 2021a acknowledgements).

---

## FILES

| file | bytes | md5 | source |
|---|---|---|---|
| `J2222_gband_lightcurve_Dahle2015_Table1.csv` | 8127 | `dd3e7a9f4011dcf7b48e782a81187b07` | arXiv 1505.06187 LaTeX Table 1 |
| `R1_Williams2021a_Table1_standard_stars.txt` | 715 | `aa00c2c4f5aa09ca2b0f41bb3b6b6c6f` | IOP MRT, DOI 10.3847/1538-4357/abe943 |
| `R1_Williams2021a_Table2_CIV_lags.txt` | 780 | `481184bbe0f14fb998df9c0fe7db602c` | IOP MRT, same |
| `R1_Williams2021a_Table3_linewidths_MBH.txt` | 1705 | `20cd95468f0c05655527e5298d94762c` | IOP MRT, same |
| `R3_Williams2021b_BLR_model_posterior.csv` | 1090 | `f1479130bca0471d6cc5240d184a6076` | arXiv 2103.10961 LaTeX macros |
| `Refsdal_Kelly2023_Table3_photometry_mrt.txt` | 61840 | `d7ba6d652d349898dcfbc94c971fa58e` | IOP MRT, DOI 10.3847/1538-4357/ac4ccb |
| `MANIFEST_HST_GO13337_J2222.csv` | 5034 | `d1bf6bb946eea3361e5c6aff061da26a` | MAST CAOM API |
| `cadence_summary.json` | 413 | `9b0ddc88063b266f386be16c9592cf3a` | computed from the light curve |

### `J2222_gband_lightcurve_Dahle2015_Table1.csv` — the actual-cadence asset
115 rows, 48 unique nights, images A/B/C simultaneously.
Columns: `MJD, MJD_minus_50000, mag_A, err_A, mag_B, err_B, mag_C, err_C, observatory, detector`

- MJD 55122.200 → 57260.148, span 2137.9 d (5.85 yr)
- Provenance: 1× SDSS (2009 archival), 3× NOT/MOSCA, 108× NOT/ALFOSC, 3× Gemini/GMOS
- Dropping the 2009 SDSS point: monitoring runs MJD 55829 → 57260, **1431 d (3.92 yr)**
- **Median gap between observing nights = 15.5 d**, mean 31.1 d, **largest seasonal gap 354 d**
- Typical per-point photometric error 0.014–0.015 mag (A and B), 0.015–0.030 mag (C)
- Note the strong seasonal window function — the 354 d gap is the dominant aliasing structure and
  must be in any actual-cadence injection.

### `MANIFEST_HST_GO13337_J2222.csv` — HST holdings for J2222+2745
37 MAST observation records for **GO-13337 (PI Sharon)**, the only HST programme on this target
(Napier et al. 2023 §J2222: "WFC3/F160W, F110W (1 orbit) and ACS/F814W, F606W, F435W (6 orbits)").
Breakdown: ACS/WFC 24, WFC3/IR 13. Filters F435W, F606W, F814W, F110W, F160W (+ detection images
and 10 SkySurf HLSP level-4 products). Calibrated products fetch from MAST with no authentication:
`https://mast.stsci.edu/api/v0.1/Download/bundle.sh?obsid=<obsid>` or via `astroquery.mast`.

---

## SOURCE URLs (complete and verbatim)

https://arxiv.org/abs/2011.02007
https://arxiv.org/e-print/2011.02007
https://doi.org/10.3847/1538-4357/abe943
https://iopscience.iop.org/0004-637X/911/1/64/suppdata/apjabe943t1_ascii.txt?doi=10.3847/1538-4357/abe943
https://iopscience.iop.org/0004-637X/911/1/64/suppdata/apjabe943t2_ascii.txt?doi=10.3847/1538-4357/abe943
https://iopscience.iop.org/0004-637X/911/1/64/suppdata/apjabe943t3_ascii.txt?doi=10.3847/1538-4357/abe943
https://arxiv.org/abs/2103.10961
https://arxiv.org/e-print/2103.10961
https://doi.org/10.3847/2041-8213/ac081b
https://arxiv.org/abs/1505.06187
https://arxiv.org/e-print/1505.06187
https://doi.org/10.1088/0004-637X/813/1/67
https://arxiv.org/abs/2301.11240
https://arxiv.org/e-print/2301.11240
https://doi.org/10.3847/1538-4357/ac4ccb
https://arxiv.org/abs/2305.06377
https://content.cld.iop.org/journals/0004-637X/948/2/93/revision1/apjac4ccbt3_mrt.txt?doi=10.3847/1538-4357/ac4ccb
https://doi.org/10.3847/0004-637X/820/1/50

---

## BLOCKED — needs a human

**Gemini Observatory Archive returns HTTP 403 to this host.** Every endpoint tried
(`/jsonsummary/notengineering/SDSSJ2222+2745`, `/jsonsummary/object=...`, `/jsonqastate/GMOS-N/...`)
returns 403 with this body:

> "Login Required. Please visit https://archive.gemini.edu/login … the Gemini Observatory Archive has
> been subject to a massive increase in excessive and/or malicious requests, often associated with AI
> training robots and associated malware. Your IP address range or ISP has been the source of excessive
> or malicious requests to this server…"

This is an **IP/ISP-range block plus a login requirement** — an access control. Per standing rules I did
not create an account, authenticate, or look for a side door. **A human must run the archive query**, or
it must be run from a different network. The nine programme IDs above are published and are sufficient
to drive that query directly:
`https://archive.gemini.edu/searchform/GN-2016B-Q-28` (repeat per ID), or
`https://archive.gemini.edu/jsonsummary/GN-2016B-Q-28`.

## DEFERRED (explicitly, not silently)

1. **Raw GMOS-N frames** (R2) — blocked as above; volume unknown until the archive query runs.
   Estimate from the campaign description: 47 epochs × 6000 s in queue mode across 9 programmes.
2. **NOT/ALFOSC g / i / He I 5876 epoch photometry** (R4) — **not published**. Only the counts
   (86/49/41) and the ~18 d cadence appear in print. Would require a request to the authors (H. Dahle).
3. **2016–2020 campaign spectroscopic epoch list and light curves** — not published (F4).
4. **Dyrland (2019) posterior samples** — thesis only; intervals published via Napier et al. 2023.
5. **HST calibrated exposures and difference images** — enumerated (37 records for J2222/GO-13337),
   bulk pixels not staged. Refsdal difference-image *photometry* is delivered; the images themselves
   are not.
