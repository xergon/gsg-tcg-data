# J1004_PITD0_STAGE_1 -- result bundle

Frozen procedure specified by ChatGPT research thread **T8**; executed by Cat (compute arm).
**This document reports numbers only.** Steps 7-8 (M0/M1/M2/M3 fits, null farm, and any
KILLED / SURVIVES / PIVOT call) are T8's and are deliberately absent.

UTC of run: 2026-07-24T22:08:25Z

## STEP 1 -- data verification

- `j1004_lightcurves_long.csv` sha256 **6c476e4b829da9de61bfe91675aae1f07b546d1e8d34c4ed3e2e439cff38407e** -- matches the expected value: **True**
- rows: **4072** (expected 4072): **True**
- columns exactly `image, mjd, jd_minus_2450000, mag, magerr, band, telescope, in_paper_fit`: **True**
- 1018 rows per image for A, B, C, D; **1017** unique MJD; MJD range 52993.023 to 58290.152
- single band (`SDSS r`), single telescope (`FLWO 1.2m Keplercam`)
- `in_paper_fit==1` per image: {'A': 1018, 'B': 1018, 'C': 919, 'D': 518}

Cat note (fact, not a judgement call): `in_paper_fit` is an **overlap mask, not a quality mask**.
The 499 excluded D rows are all MJD < 54599 and the 99 excluded C rows are all MJD > 57665 --
exactly the epochs with no counterpart in another image under the published delays.

## STEP 2 -- J1004_DUPLICATE_MJD_53663P501_MERGE_IN_FLUX

MJD 53663.50100 appears twice per image (8 rows). Merged in relative flux
`f = 10^(-0.4 m)`, `sigma_f = 0.4 ln10 f sigma_m`, inverse-variance combined, returned to magnitude.
Inflation rule: `chi2_red > 1 -> sigma *= sqrt(chi2_red)`. Rows 4072 -> **4068** (expected 4068: **True**).

| image | inputs (mag +/- err) | merged mag | merged err | chi2_red (1 dof) | inflation |
|---|---|---|---|---|---|
| A | 19.486+/-0.034, 19.555+/-0.012 | **19.5480** | 0.0211 | 3.484 | YES x1.8666 |
| B | 19.919+/-0.040, 19.905+/-0.014 | **19.9066** | 0.0132 | 0.110 | no |
| C | 20.023+/-0.051, 19.954+/-0.029 | **19.9721** | 0.0301 | 1.427 | YES x1.1947 |
| D | 20.520+/-0.107, 20.421+/-0.038 | **20.4335** | 0.0358 | 0.815 | no |

Inflation triggered for **A** and **C**; not for B or D.

## STEP 3 -- constant-delay reproduction (calibration check)

`in_paper_fit == 1` rows only, eps = 0. DRW/OU latent process fitted on **image C alone**
(sigma = 0.2758 mag, tau = 537.6 d, jitter = 0.0385 mag) -- independent of any trial delay.
Statistic = mean **held-out** predictive residual, 5-fold, microlensing polynomial fitted on training folds only.

| pair | published Joint BIC | dispersion | difference-smoothing | latent process |
|---|---|---|---|---|
| DC | 2458.47 +/- 1.02 | 2454.12 (-4.35) | 2460.02 (+1.55) | 2454.12 (-4.35) |
| AC | 825.23 +/- 0.46 | 821.98 (-3.25) | 833.68 (+8.45) | 821.08 (-4.15) |
| BC | 782.20 +/- 0.43 | 782.80 (+0.60) | 783.85 (+1.65) | 782.40 (+0.20) |

(value in brackets = recovered minus published Joint BIC, days)

Internal check, Delta_AC - Delta_BC vs published Delta_AB = 43.01 d: dispersion 39.18, difference 49.83, latent 38.68.

All three estimators land within a few days of the published Joint-BIC delays on all three pairs,
including Delta_DC. The calibration gate of step 3 is therefore passed and step 4 onward proceeded.

Cat note: a first pass reported +40 to +52 d offsets on DC/AC. That was a **Cat coding defect**, not a
data result: an admissibility floor requiring `N >= 0.8 * max(N)` over the delay scan excluded the true
minimum, because N varies strongly with Delta. It was replaced by an absolute floor `N >= 150` points.

## STEP 4 -- frozen C-only feature windows

Defined on image C alone (full merged curve, 1017 epochs). No A/B/D magnitude and no trial
delay entered this step. Candidates 51 -> **34 frozen windows**, ranked by C-only epoch:
**17 exploration (odd-ranked)** and **17 confirmation reserve (even-ranked)**.

**The even-ranked reserve was not touched in Stage 1**: reserve-window points are excluded from every
step-5 and step-6 fit in this bundle. The reserve list is in `feature_windows.json` for T8's inspection only.

| rank | set | MJD start | MJD end | dur (d) | amp (mag) | n_C | max gap (d) | kind |
|---|---|---|---|---|---|---|---|---|
| 1 | EXPL | 52996.84 | 53195.15 | 198.3 | 0.549 | 107 | 25.3 | multi_reversal |
| 2 | reserve | 53313.51 | 53398.52 | 85.0 | 0.389 | 20 | 18.0 | monotonic_sharp |
| 3 | EXPL | 53398.52 | 53462.34 | 63.8 | 0.194 | 15 | 20.1 | monotonic_sharp |
| 4 | reserve | 53462.34 | 53516.18 | 53.8 | 0.405 | 31 | 7.0 | monotonic_sharp |
| 5 | EXPL | 53516.18 | 53549.15 | 33.0 | 0.311 | 14 | 6.0 | monotonic_sharp |
| 6 | reserve | 53654.53 | 53694.36 | 39.8 | 0.429 | 31 | 8.0 | monotonic_sharp |
| 7 | EXPL | 53694.36 | 53742.49 | 48.1 | 0.265 | 28 | 7.2 | monotonic_sharp |
| 8 | reserve | 53770.29 | 53907.18 | 136.9 | 0.342 | 55 | 19.9 | monotonic_sharp |
| 9 | EXPL | 54018.51 | 54110.52 | 92.0 | 0.335 | 43 | 10.0 | monotonic_sharp |
| 10 | reserve | 54110.52 | 54233.24 | 122.7 | 0.399 | 37 | 14.1 | multi_reversal |
| 11 | EXPL | 54233.24 | 54278.17 | 44.9 | 0.366 | 25 | 5.0 | monotonic_sharp |
| 12 | reserve | 54393.46 | 54557.29 | 163.8 | 0.897 | 55 | 14.0 | monotonic_sharp |
| 13 | EXPL | 54557.29 | 54592.15 | 34.9 | 0.375 | 20 | 7.1 | monotonic_sharp |
| 14 | reserve | 54592.15 | 54629.15 | 37.0 | 0.396 | 17 | 8.0 | monotonic_sharp |
| 15 | EXPL | 54769.41 | 54822.41 | 53.0 | 0.332 | 17 | 14.0 | monotonic_sharp |
| 16 | reserve | 54822.41 | 55006.17 | 183.8 | 0.518 | 50 | 17.0 | monotonic_sharp |
| 17 | EXPL | 55134.50 | 55191.51 | 57.0 | 0.311 | 12 | 16.1 | monotonic_sharp |
| 18 | reserve | 55191.51 | 55338.17 | 146.7 | 0.301 | 25 | 28.8 | monotonic_sharp |
| 19 | EXPL | 55508.49 | 55688.21 | 179.7 | 0.543 | 27 | 22.2 | monotonic_sharp |
| 20 | reserve | 55688.21 | 55732.19 | 44.0 | 0.202 | 9 | 18.0 | monotonic_sharp |
| 21 | EXPL | 55887.48 | 56014.34 | 126.9 | 0.374 | 23 | 34.0 | multi_reversal |
| 22 | reserve | 56014.34 | 56086.16 | 71.8 | 0.285 | 20 | 11.0 | monotonic_sharp |
| 23 | EXPL | 56331.31 | 56442.18 | 110.9 | 0.289 | 33 | 14.0 | monotonic_sharp |
| 24 | reserve | 56590.43 | 56640.30 | 49.9 | 0.208 | 17 | 9.0 | monotonic_sharp |
| 25 | EXPL | 56640.30 | 56691.33 | 51.0 | 0.142 | 30 | 6.2 | monotonic_sharp |
| 26 | reserve | 56691.33 | 56838.15 | 146.8 | 0.573 | 73 | 8.0 | monotonic_sharp |
| 27 | EXPL | 57304.50 | 57390.45 | 86.0 | 0.185 | 13 | 20.0 | monotonic_sharp |
| 28 | reserve | 57390.45 | 57462.17 | 71.7 | 0.428 | 20 | 14.1 | monotonic_sharp |
| 29 | EXPL | 57462.17 | 57556.16 | 94.0 | 0.254 | 29 | 23.0 | monotonic_sharp |
| 30 | reserve | 57715.47 | 57759.44 | 44.0 | 0.260 | 11 | 11.0 | monotonic_sharp |
| 31 | EXPL | 57759.44 | 57808.49 | 49.0 | 0.125 | 16 | 12.0 | monotonic_sharp |
| 32 | reserve | 57808.49 | 57884.15 | 75.7 | 0.130 | 25 | 12.2 | monotonic_sharp |
| 33 | EXPL | 57884.15 | 57921.15 | 37.0 | 0.140 | 9 | 15.0 | monotonic_sharp |
| 34 | reserve | 58070.49 | 58290.15 | 219.7 | 0.614 | 25 | 34.0 | monotonic_sharp |

Windows 1-20 are testable against D, A and B; 21-28 against A and B only; 29-34 against none
(their source epochs fall past the end of the campaign once the delay is added).

## STEP 5 -- affine-delay maps

Grid: Delta over published +/- 15 d in 0.25 d steps; eps over +/- 5e-03 in 1e-04 steps
(121 x 101 = 12221 nodes per map).
Map: `u = t - Delta - eps (t - T0)`, T0 = 55641.5875 MJD (campaign midpoint; eps and every ratio of eps are T0-independent,
only the quoted Delta shifts with T0).
Frozen maximum interpolation gap: **45 d** (never interpolate across a seasonal gap; the
15 observing seasons are separated by 105-332 d, so this confines interpolation inside a season).
Slow differential microlensing: polynomial of order 3 in (t-T0)/1000 d, fitted on training folds only.
Held-out scheme: **5-fold**, fold = (time rank of the image-i point) mod 5; every nuisance parameter is
estimated on 4/5 of the points and the statistic accumulated on the withheld 1/5, so each quoted number is a
pairwise **predictive** residual, image i predicted from image C.

Point-set sizes (image-i epochs, `in_paper_fit==1`):

| pair | all | in exploration windows | excluding reserve windows | in reserve (EXCLUDED) |
|---|---|---|---|---|
| DC | 518 | 73 | 375 | 143 |
| AC | 1017 | 251 | 846 | 171 |
| BC | 1017 | 265 | 746 | 271 |

### STEP 6 -- common-kappa basin, D_DC, closure ratio

Two point-set treatments are reported for every window set and every STRICT/CHAINED mode:

- **frozen** (PRIMARY): image-i epochs eroded so that the ENTIRE source-time excursion the point can make anywhere on the (Delta,eps) grid stays inside one covered interval. The point set is therefore IDENTICAL at every grid node and a mean statistic cannot be biased by points entering or leaving. PRIMARY.
- **moving**: coverage re-evaluated at each node. More points, but N varies across the map (measured 64-120 for D/C), so map contrast is partly a changing-sample effect. Reported for completeness only.

Cat designates **`exploration_only__strict__frozen`** as the primary configuration: T8's literal odd-ranked exploration set,
STRICT overlap only, and a point set that cannot move across the map. T8 may prefer another row.

`ln lambda_i = kappa Delta_i`; `D_DC = (lambda_D - 1) L_DC`; predicted closure ratio
`(Delta_AC - Delta_BC)/Delta_DC = 0.017503`.
STRICT = image-i point used only if its source time u lies inside image C's observed coverage with bracketing C epochs <= 45 d apart. CHAINED = additionally allow u up to CORR_LEN = 30 d beyond the nearest C epoch, bridged by the latent process; never further
(frozen correlation length **30 d**).

#### exploration_only__strict__frozen

| estimator | pair | best Delta (d) | +/- | best eps | +/- | dchi2 at eps=0 | N |
|---|---|---|---|---|---|---|---|
| dispersion_spectrum | DC | 2451.97 | 0.88 | +5.000e-03 | 2.050e-03 | 1.76 | 60 |
| dispersion_spectrum | AC | 833.48 | 0.25 | +5.000e-03 | 5.000e-05 | 38.30 | 226 |
| dispersion_spectrum | BC | 782.45 | 0.38 | -4.200e-03 | 4.000e-04 | 5.48 | 244 |
| difference_smoothing | DC | 2457.47 | 2.38 | +5.000e-03 | 5.000e-04 | 10.04 | 60 |
| difference_smoothing | AC | 834.48 | 1.25 | +1.200e-03 | 1.150e-03 | 7.96 | 226 |
| difference_smoothing | BC | 790.95 | 1.50 | -2.000e-04 | 7.500e-04 | 0.02 | 244 |
| latent_process | DC | 2456.72 | 2.50 | +5.000e-03 | 7.500e-04 | 4.66 | 60 |
| latent_process | AC | 832.73 | 1.12 | +3.100e-03 | 1.000e-03 | 8.74 | 226 |
| latent_process | BC | 784.20 | 1.50 | -1.300e-03 | 1.650e-03 | 0.30 | 244 |

| estimator | kappa (/d) | 1sigma | dchi2(kappa=0) | L_DC (d) | D_DC (d) | closure (eps_A-eps_B)/eps_D |
|---|---|---|---|---|---|---|
| dispersion_spectrum | +1.679e-06 | [+6.71e-07, +2.01e-06] | 8.49 | 2652.9 | +13.264 +/- 5.438 | +2.636 [+1.498, +8.460] |
| difference_smoothing | +1.796e-06 | [+1.18e-06, +2.03e-06] | 14.04 | 2652.9 | +13.264 +/- 1.326 | +0.433 [-0.560, +1.086] |
| latent_process | +2.030e-06 | [+1.77e-06, +2.03e-06] | 10.70 | 2652.9 | +13.264 +/- 1.990 | +0.638 [-1.005, +1.582] |

#### exploration_only__strict__moving

| estimator | pair | best Delta (d) | +/- | best eps | +/- | dchi2 at eps=0 | N |
|---|---|---|---|---|---|---|---|
| dispersion_spectrum | DC | 2467.22 | 8.38 | -8.000e-04 | 3.300e-03 | 1.02 | 73 |
| dispersion_spectrum | AC | 836.48 | 1.88 | +5.000e-03 | 1.650e-03 | 11.78 | 251 |
| dispersion_spectrum | BC | 782.45 | 0.50 | -4.200e-03 | 4.500e-04 | 5.64 | 265 |
| difference_smoothing | DC | 2458.47 | 2.25 | +5.000e-03 | 5.500e-04 | 11.25 | 73 |
| difference_smoothing | AC | 838.23 | 0.00 | +2.200e-03 | 0.000e+00 | 8.04 | 251 |
| difference_smoothing | BC | 793.20 | 1.62 | -4.000e-04 | 4.500e-04 | 0.31 | 265 |
| latent_process | DC | 2460.47 | 2.75 | +5.000e-03 | 5.000e-04 | 4.57 | 73 |
| latent_process | AC | 836.23 | 1.12 | +3.600e-03 | 2.150e-03 | 0.66 | 251 |
| latent_process | BC | 784.45 | 1.25 | -1.700e-03 | 1.350e-03 | 0.87 | 265 |

| estimator | kappa (/d) | 1sigma | dchi2(kappa=0) | L_DC (d) | D_DC (d) | closure (eps_A-eps_B)/eps_D |
|---|---|---|---|---|---|---|
| dispersion_spectrum | +1.658e-06 | [+5.08e-07, +1.95e-06] | 2.42 | 2652.9 | -2.122 +/- 8.754 | +0.954 [-8.359, +3.569] |
| difference_smoothing | +1.788e-06 | [+1.53e-06, +1.82e-06] | 8.46 | 2652.9 | +13.264 +/- 1.459 | -0.285 [-0.777, +0.591] |
| latent_process | +2.027e-06 | [+1.73e-06, +2.03e-06] | 2.60 | 2652.9 | +13.264 +/- 1.326 | +0.860 [-0.020, +1.941] |

#### exploration_only__chained__frozen

| estimator | pair | best Delta (d) | +/- | best eps | +/- | dchi2 at eps=0 | N |
|---|---|---|---|---|---|---|---|
| dispersion_spectrum | DC | 2467.22 | 8.38 | -8.000e-04 | 3.300e-03 | 1.02 | 73 |
| dispersion_spectrum | AC | 834.23 | 3.38 | +5.000e-03 | 1.700e-03 | 10.69 | 251 |
| dispersion_spectrum | BC | 782.45 | 0.50 | -4.200e-03 | 3.500e-04 | 6.48 | 265 |
| difference_smoothing | DC | 2458.47 | 2.25 | +5.000e-03 | 5.500e-04 | 11.25 | 73 |
| difference_smoothing | AC | 834.48 | 0.62 | +1.200e-03 | 5.500e-04 | 7.30 | 251 |
| difference_smoothing | BC | 790.45 | 0.50 | +2.000e-04 | 3.500e-04 | 0.25 | 265 |
| latent_process | DC | 2460.47 | 2.75 | +5.000e-03 | 5.000e-04 | 4.57 | 73 |
| latent_process | AC | 839.98 | 2.00 | +1.100e-03 | 1.650e-03 | 0.85 | 251 |
| latent_process | BC | 784.45 | 1.00 | -1.600e-03 | 1.150e-03 | 1.33 | 265 |

| estimator | kappa (/d) | 1sigma | dchi2(kappa=0) | L_DC (d) | D_DC (d) | closure (eps_A-eps_B)/eps_D |
|---|---|---|---|---|---|---|
| dispersion_spectrum | +7.190e-07 | [+5.08e-07, +1.77e-06] | 2.31 | 2652.9 | -2.122 +/- 8.754 | +1.009 [-8.346, +3.566] |
| difference_smoothing | +1.198e-06 | [+1.17e-06, +1.80e-06] | 14.47 | 2652.9 | +13.264 +/- 1.459 | +0.188 [-0.341, +0.662] |
| latent_process | +1.147e-06 | [+5.43e-07, +2.03e-06] | 2.78 | 2652.9 | +13.264 +/- 1.326 | +0.488 [-0.802, +1.559] |

#### exploration_only__chained__moving

| estimator | pair | best Delta (d) | +/- | best eps | +/- | dchi2 at eps=0 | N |
|---|---|---|---|---|---|---|---|
| dispersion_spectrum | DC | 2467.22 | 8.38 | -8.000e-04 | 3.300e-03 | 1.02 | 73 |
| dispersion_spectrum | AC | 834.23 | 3.38 | +5.000e-03 | 1.700e-03 | 10.69 | 251 |
| dispersion_spectrum | BC | 782.45 | 0.50 | -4.200e-03 | 3.500e-04 | 6.48 | 265 |
| difference_smoothing | DC | 2458.47 | 2.25 | +5.000e-03 | 5.500e-04 | 11.25 | 73 |
| difference_smoothing | AC | 834.48 | 0.62 | +1.200e-03 | 5.500e-04 | 7.30 | 251 |
| difference_smoothing | BC | 790.45 | 0.50 | +2.000e-04 | 3.500e-04 | 0.25 | 265 |
| latent_process | DC | 2460.47 | 2.75 | +5.000e-03 | 5.000e-04 | 4.57 | 73 |
| latent_process | AC | 839.98 | 2.00 | +1.100e-03 | 1.650e-03 | 0.85 | 251 |
| latent_process | BC | 784.45 | 1.00 | -1.600e-03 | 1.150e-03 | 1.33 | 265 |

| estimator | kappa (/d) | 1sigma | dchi2(kappa=0) | L_DC (d) | D_DC (d) | closure (eps_A-eps_B)/eps_D |
|---|---|---|---|---|---|---|
| dispersion_spectrum | +7.190e-07 | [+5.08e-07, +1.77e-06] | 2.31 | 2652.9 | -2.122 +/- 8.754 | +1.007 [-8.400, +3.558] |
| difference_smoothing | +1.198e-06 | [+1.17e-06, +1.80e-06] | 14.47 | 2652.9 | +13.264 +/- 1.459 | +0.190 [-0.338, +0.664] |
| latent_process | +1.147e-06 | [+5.43e-07, +2.03e-06] | 2.78 | 2652.9 | +13.264 +/- 1.326 | +0.486 [-0.799, +1.555] |

#### all_minus_reserve__strict__frozen

| estimator | pair | best Delta (d) | +/- | best eps | +/- | dchi2 at eps=0 | N |
|---|---|---|---|---|---|---|---|
| dispersion_spectrum | DC | 2451.97 | 0.88 | +5.000e-03 | 2.050e-03 | 1.76 | 60 |
| dispersion_spectrum | AC | 831.98 | 0.38 | +5.000e-03 | 5.000e-05 | 29.68 | 245 |
| dispersion_spectrum | BC | 780.95 | 0.12 | +4.000e-04 | 5.000e-04 | 0.64 | 260 |
| difference_smoothing | DC | 2457.47 | 2.38 | +5.000e-03 | 5.000e-04 | 10.04 | 60 |
| difference_smoothing | AC | 835.98 | 0.62 | +4.200e-03 | 5.500e-04 | 17.41 | 245 |
| difference_smoothing | BC | 790.70 | 0.75 | +1.301e-17 | 7.000e-04 | 0.00 | 260 |
| latent_process | DC | 2456.72 | 2.50 | +5.000e-03 | 7.500e-04 | 4.66 | 60 |
| latent_process | AC | 832.48 | 0.50 | +3.300e-03 | 6.000e-04 | 11.85 | 245 |
| latent_process | BC | 782.95 | 1.38 | +2.200e-03 | 1.800e-03 | 0.88 | 260 |

| estimator | kappa (/d) | 1sigma | dchi2(kappa=0) | L_DC (d) | D_DC (d) | closure (eps_A-eps_B)/eps_D |
|---|---|---|---|---|---|---|
| dispersion_spectrum | +6.400e-07 | [+3.93e-07, +9.38e-07] | 3.40 | 2652.9 | +13.264 +/- 5.438 | +1.453 [+0.843, +4.576] |
| difference_smoothing | +2.030e-06 | [+1.78e-06, +2.03e-06] | 20.01 | 2652.9 | +13.264 +/- 1.326 | +0.809 [-0.884, +1.355] |
| latent_process | +2.030e-06 | [+1.84e-06, +2.03e-06] | 14.19 | 2652.9 | +13.264 +/- 1.990 | +0.193 [-0.530, +0.928] |

#### all_minus_reserve__strict__moving

| estimator | pair | best Delta (d) | +/- | best eps | +/- | dchi2 at eps=0 | N |
|---|---|---|---|---|---|---|---|
| dispersion_spectrum | DC | 2451.97 | 0.50 | +5.000e-03 | 3.000e-04 | 4.92 | 120 |
| dispersion_spectrum | AC | 831.23 | 0.00 | +4.400e-03 | 3.000e-04 | 25.58 | 326 |
| dispersion_spectrum | BC | 780.95 | 0.00 | +5.000e-04 | 4.500e-04 | 0.70 | 349 |
| difference_smoothing | DC | 2459.22 | 2.38 | +4.100e-03 | 9.000e-04 | 23.08 | 120 |
| difference_smoothing | AC | 838.23 | 0.00 | +2.200e-03 | 2.200e-03 | 8.00 | 326 |
| difference_smoothing | BC | 789.70 | 0.00 | +1.000e-04 | 0.000e+00 | 1.55 | 349 |
| latent_process | DC | 2459.22 | 2.00 | +4.200e-03 | 7.500e-04 | 9.61 | 120 |
| latent_process | AC | 836.23 | 0.12 | -2.500e-03 | 8.000e-04 | 4.61 | 326 |
| latent_process | BC | 781.20 | 1.12 | +6.000e-04 | 1.000e-03 | 0.33 | 349 |

| estimator | kappa (/d) | 1sigma | dchi2(kappa=0) | L_DC (d) | D_DC (d) | closure (eps_A-eps_B)/eps_D |
|---|---|---|---|---|---|---|
| dispersion_spectrum | +6.403e-07 | [-3.69e-07, +8.91e-07] | 0.91 | 2652.9 | +13.264 +/- 0.796 | +0.947 [+0.708, +1.459] |
| difference_smoothing | +1.550e-06 | [+1.31e-06, +1.79e-06] | 19.49 | 2652.9 | +10.877 +/- 2.388 | -0.342 [-0.817, +0.521] |
| latent_process | +1.663e-06 | [+1.23e-06, +1.79e-06] | 8.67 | 2652.9 | +11.142 +/- 1.990 | -0.654 [-1.177, -0.230] |

#### all_minus_reserve__chained__frozen

| estimator | pair | best Delta (d) | +/- | best eps | +/- | dchi2 at eps=0 | N |
|---|---|---|---|---|---|---|---|
| dispersion_spectrum | DC | 2451.97 | 0.62 | +5.000e-03 | 3.500e-04 | 3.36 | 98 |
| dispersion_spectrum | AC | 830.98 | 0.50 | +4.400e-03 | 3.000e-04 | 35.56 | 315 |
| dispersion_spectrum | BC | 780.95 | 0.00 | +4.000e-04 | 5.000e-04 | 0.35 | 312 |
| difference_smoothing | DC | 2448.22 | 1.38 | -5.000e-03 | 2.000e-04 | 11.79 | 98 |
| difference_smoothing | AC | 837.23 | 1.00 | +3.100e-03 | 9.000e-04 | 12.39 | 315 |
| difference_smoothing | BC | 791.95 | 0.00 | -1.200e-03 | 0.000e+00 | 9.32 | 312 |
| latent_process | DC | 2456.47 | 2.12 | +5.000e-03 | 5.500e-04 | 6.57 | 98 |
| latent_process | AC | 834.48 | 1.00 | +2.200e-03 | 7.500e-04 | 5.53 | 315 |
| latent_process | BC | 782.70 | 1.00 | -5.000e-04 | 1.000e-03 | 0.22 | 312 |

| estimator | kappa (/d) | 1sigma | dchi2(kappa=0) | L_DC (d) | D_DC (d) | closure (eps_A-eps_B)/eps_D |
|---|---|---|---|---|---|---|
| dispersion_spectrum | -1.633e-07 | [-4.21e-07, +1.88e-07] | 0.23 | 2652.9 | +13.264 +/- 0.929 | +0.961 [-2.543, +2.054] |
| difference_smoothing | +1.433e-06 | [-2.04e-06, +2.03e-06] | 16.97 | 2652.9 | -13.264 +/- 0.531 | -0.131 [-1.180, +1.344] |
| latent_process | +2.030e-06 | [+1.62e-06, +2.03e-06] | 10.00 | 2652.9 | +13.264 +/- 1.459 | +0.521 [-0.498, +1.289] |

#### all_minus_reserve__chained__moving

| estimator | pair | best Delta (d) | +/- | best eps | +/- | dchi2 at eps=0 | N |
|---|---|---|---|---|---|---|---|
| dispersion_spectrum | DC | 2451.97 | 0.50 | +4.900e-03 | 2.500e-04 | 10.61 | 171 |
| dispersion_spectrum | AC | 830.98 | 0.38 | +4.500e-03 | 2.000e-04 | 33.34 | 415 |
| dispersion_spectrum | BC | 780.95 | 0.00 | +4.000e-04 | 4.000e-04 | 0.51 | 434 |
| difference_smoothing | DC | 2457.22 | 1.00 | +5.000e-03 | 4.000e-04 | 21.64 | 171 |
| difference_smoothing | AC | 835.23 | 1.00 | +2.400e-03 | 9.000e-04 | 15.64 | 415 |
| difference_smoothing | BC | 791.95 | 0.00 | -1.200e-03 | 0.000e+00 | 12.96 | 434 |
| latent_process | DC | 2448.97 | 0.12 | +5.000e-03 | 1.500e-04 | 9.16 | 171 |
| latent_process | AC | 825.98 | 0.12 | +1.000e-03 | 6.000e-04 | 1.04 | 415 |
| latent_process | BC | 781.20 | 0.38 | +8.000e-04 | 4.000e-04 | 3.22 | 434 |

| estimator | kappa (/d) | 1sigma | dchi2(kappa=0) | L_DC (d) | D_DC (d) | closure (eps_A-eps_B)/eps_D |
|---|---|---|---|---|---|---|
| dispersion_spectrum | +6.113e-07 | [+3.14e-07, +1.86e-06] | 3.48 | 2796.6 | +13.704 +/- 0.699 | +0.962 [+0.817, +1.176] |
| difference_smoothing | +2.030e-06 | [+1.98e-06, +2.03e-06] | 31.03 | 2796.6 | +13.983 +/- 1.119 | +0.998 [+0.724, +1.290] |
| latent_process | +1.915e-06 | [+1.78e-06, +2.04e-06] | 9.00 | 2796.6 | +13.983 +/- 0.419 | -0.036 [-0.332, +0.313] |

### Wide-range eps diagnostic

Because several frozen maps put their minimum ON the +/-5e-3 eps boundary, a 6x wider scan
(eps in [-0.03, 0.03], step 5e-04, exploration windows, moving (N varies) -- DIAGNOSTIC ONLY)
was run to locate where each statistic finally turns over:

| pair | estimator | best eps (wide) | still at wide edge? | dchi2 at eps=0 (wide) |
|---|---|---|---|---|
| DC | dispersion_spectrum | +0.0125 | False | 4.2 |
| DC | difference_smoothing | +0.0060 | False | 11.6 |
| DC | latent_process | +0.0090 | False | 6.1 |
| AC | dispersion_spectrum | +0.0090 | False | 61.8 |
| AC | difference_smoothing | -0.0035 | False | 4.9 |
| AC | latent_process | +0.0035 | False | 0.4 |
| BC | dispersion_spectrum | -0.0040 | False | 5.2 |
| BC | difference_smoothing | +0.0000 | False | 0.0 |
| BC | latent_process | -0.0015 | False | 0.8 |

### L_DC, computed explicitly

Data-level spans (all `in_paper_fit==1` epochs of the image, before any window selection or grid erosion):

| pair / mode | L (days) | source-time range (MJD) | usable image epochs |
|---|---|---|---|
| DC_strict | **2688.9** | 53035.0 - 55723.9 | 226 |
| DC_chained | **2796.6** | 53035.0 - 55831.7 | 290 |
| AC_strict | **4471.8** | 52993.1 - 57464.9 | 459 |
| AC_chained | **4501.8** | 52963.1 - 57464.9 | 564 |
| BC_strict | **4514.7** | 52993.3 - 57508.0 | 568 |
| BC_chained | **4544.7** | 52963.2 - 57508.0 | 657 |

Per-configuration effective spans (what the fits actually used):


| config | L_DC (d) | u range (MJD) | usable D epochs | max lever arm abs(t-T0) (d) |
|---|---|---|---|---|
| exploration_only__strict__frozen | **2652.9** | 53035.0 - 55687.9 | 60 | 2505 |
| exploration_only__strict__moving | **2652.9** | 53035.0 - 55687.9 | 73 | 2505 |
| exploration_only__chained__frozen | **2652.9** | 53035.0 - 55687.9 | 73 | 2505 |
| exploration_only__chained__moving | **2652.9** | 53035.0 - 55687.9 | 73 | 2505 |
| all_minus_reserve__strict__frozen | **2652.9** | 53035.0 - 55687.9 | 60 | 2505 |
| all_minus_reserve__strict__moving | **2652.9** | 53035.0 - 55687.9 | 83 | 2505 |
| all_minus_reserve__chained__frozen | **2652.9** | 53035.0 - 55687.9 | 98 | 2505 |
| all_minus_reserve__chained__moving | **2796.6** | 53035.0 - 55831.7 | 147 | 2649 |

### Do the three estimators land in the same (Delta, eps) basin?

T8's criterion: a genuine shear must land in the same basin in all three estimators.
Machine-readable check, per configuration and pair -- sign agreement on eps, whether any
estimator's minimum sits ON the scanned eps boundary (which means its true minimum is outside
the scanned range and its 'best eps' is not a measurement), and the spread of the three eps values:

| config | pair | eps (disp / diffsm / latent) | same sign? | any at boundary? | spread / mean sigma |
|---|---|---|---|---|---|
| exploration_only__strict__frozen | DC | +5.00e-03 / +5.00e-03 / +5.00e-03 | YES | YES | 0.0 |
| exploration_only__strict__frozen | AC | +5.00e-03 / +1.20e-03 / +3.10e-03 | YES | YES | 5.2 |
| exploration_only__strict__frozen | BC | -4.20e-03 / -2.00e-04 / -1.30e-03 | YES | no | 4.3 |
| exploration_only__strict__moving | DC | -8.00e-04 / +5.00e-03 / +5.00e-03 | NO | YES | 4.0 |
| exploration_only__strict__moving | AC | +5.00e-03 / +2.20e-03 / +3.60e-03 | YES | YES | 2.2 |
| exploration_only__strict__moving | BC | -4.20e-03 / -4.00e-04 / -1.70e-03 | YES | no | 5.1 |
| exploration_only__chained__frozen | DC | -8.00e-04 / +5.00e-03 / +5.00e-03 | NO | YES | 4.0 |
| exploration_only__chained__frozen | AC | +5.00e-03 / +1.20e-03 / +1.10e-03 | YES | YES | 3.0 |
| exploration_only__chained__frozen | BC | -4.20e-03 / +2.00e-04 / -1.60e-03 | NO | no | 7.1 |
| exploration_only__chained__moving | DC | -8.00e-04 / +5.00e-03 / +5.00e-03 | NO | YES | 4.0 |
| exploration_only__chained__moving | AC | +5.00e-03 / +1.20e-03 / +1.10e-03 | YES | YES | 3.0 |
| exploration_only__chained__moving | BC | -4.20e-03 / +2.00e-04 / -1.60e-03 | NO | no | 7.1 |
| all_minus_reserve__strict__frozen | DC | +5.00e-03 / +5.00e-03 / +5.00e-03 | YES | YES | 0.0 |
| all_minus_reserve__strict__frozen | AC | +5.00e-03 / +4.20e-03 / +3.30e-03 | YES | YES | 4.2 |
| all_minus_reserve__strict__frozen | BC | +4.00e-04 / +1.30e-17 / +2.20e-03 | YES | no | 2.2 |
| all_minus_reserve__strict__moving | DC | +5.00e-03 / +4.10e-03 / +4.20e-03 | YES | YES | 1.4 |
| all_minus_reserve__strict__moving | AC | +4.40e-03 / +2.20e-03 / -2.50e-03 | NO | no | 6.3 |
| all_minus_reserve__strict__moving | BC | +5.00e-04 / +1.00e-04 / +6.00e-04 | YES | no | 1.0 |
| all_minus_reserve__chained__frozen | DC | +5.00e-03 / -5.00e-03 / +5.00e-03 | NO | YES | 27.3 |
| all_minus_reserve__chained__frozen | AC | +4.40e-03 / +3.10e-03 / +2.20e-03 | YES | no | 3.4 |
| all_minus_reserve__chained__frozen | BC | +4.00e-04 / -1.20e-03 / -5.00e-04 | NO | no | 3.2 |
| all_minus_reserve__chained__moving | DC | +4.90e-03 / +5.00e-03 / +5.00e-03 | YES | YES | 0.4 |
| all_minus_reserve__chained__moving | AC | +4.50e-03 / +2.40e-03 / +1.00e-03 | YES | no | 6.2 |
| all_minus_reserve__chained__moving | BC | +4.00e-04 / -1.20e-03 / +8.00e-04 | NO | no | 7.5 |

Cat states the arithmetic, not the interpretation: T8 owns the basin call.

## Cat judgement calls (T8 may overrule any of these)

- **candidate_enumeration**: T8 specified the qualifying criteria but not how candidates are enumerated. Cat froze: per-season Gaussian smoothing (width 10 d) to define slopes, zig-zag turning points confirmed by a 0.04 mag retracement, Type-A windows spanning 4 consecutive turning points (2 internal reversals) and Type-B windows spanning 1 confirmed monotonic leg.
- **sharpness_definition**: 'sharp' monotonic excursion := amplitude/duration >= 8.00e-04 mag/day (i.e. >=0.08 mag in <=100 d equivalent rate). T8 did not define it.
- **deduplication**: candidates overlapping an already-accepted window by >50% of the shorter window are dropped; ties broken chronologically, never by amplitude.
- **window_basis**: windows enumerated on the FULL C curve rather than in_paper_fit==1 only. The 99 excluded C epochs are the LATEST (MJD 57665-58290); because ranking is chronological they can only append at the end of the rank list, so the odd/even split of every earlier window is unaffected by this choice.
- **t0 pivot**: T8 wrote `u = t - Delta - eps (t - t0)` without fixing t0. Cat froze t0 = 55641.5875 MJD, the campaign
  midpoint. Every eps, every ratio of eps and kappa are invariant to this choice; only the quoted Delta shifts.
- **which rows feed steps 5-6**: T8 specified `in_paper_fit == 1` for step 3 only. Cat used the same mask
  throughout. Because the mask is an overlap mask, no usable D/C, A/C or B/C epoch is lost by this.
- **exploration_only vs all_minus_reserve**: T8's odd/even split designates the odd-ranked windows as the
  Stage-1 working set, but that leaves only 73 D epochs for the discovery lever. Cat therefore computed BOTH
  `exploration_only` (T8's literal set) and `all_minus_reserve` (every non-reserve epoch, 375 for D). BOTH keep
  the even-ranked reserve completely untouched. Cat does not choose between them; T8 should.
- **error scaling**: each estimator's statistic is rescaled so that chi2_red = 1 at its own minimum before any
  Delta chi2 = 1 interval is read off. This is the standard conservative rescaling; it inflates the error bars
  wherever a model is imperfect rather than reporting an over-tight interval.
- **point-set freezing**: window membership is decided once at the published Joint-BIC delay with eps = 0 and
  then held fixed over the whole (Delta, eps) grid. On top of that the PRIMARY maps additionally erode the
  point set by the largest source-time excursion any epoch can make anywhere on the grid, so the number of
  contributing epochs is identical at every node. This was added after a first pass showed N swinging 64-120
  across the D/C map, which would have let a changing sample masquerade as map contrast. Both versions are
  reported; T8 can compare them directly.
- **admissibility floor**: a trial delay is admissible only with >= 150 usable image-i epochs (step 3 wide scan).

## Power / honesty notes

- The D/C lever is the thinnest arm of the whole test: 518 D epochs with `in_paper_fit==1`, of which only
  ~220 have valid STRICT source-time coverage against C at the published delay, and only 73 fall inside an
  odd-ranked exploration window. Every D/C number below is drawn from that.
- The dispersion, difference-smoothing and latent estimators are **not** statistically independent -- they read
  the same photons. Agreement between them tests method robustness, not evidence multiplication.
- (Delta, eps) are strongly correlated by construction: a change in eps can be partly absorbed by a shift in
  Delta. The maps show this as an inclined valley; the quoted eps errors are profiled over Delta, not conditional.
- The three pairs are NOT independent measurements: all three are referred to the same image C, so their
  residuals share whatever imperfection image C carries.
- Sensitivity arithmetic T8 will want: if eps_D were as large as the +5e-3 boundary, the common-kappa
  hypothesis would imply eps_A - eps_B = kappa (Delta_AC - Delta_BC) ~ 5e-3 x 43.0/2458.5 ~ 8.8e-5, which is
  about an order of magnitude below the per-pair eps resolution measured here (~1e-3). The closure arm is
  therefore intrinsically far below this dataset's noise, independent of what D/C does.
- The closure ratio is a ratio with eps_D in the denominator. Whenever eps_D is compatible with zero the ratio
  has no finite variance, which is why percentiles of the profile-likelihood sample are quoted, never mean+/-sigma.

## Files

- `duplicate_merge.json`, `delay_reproduction.json`, `feature_windows.json`, `estimator_outputs.json`, `eps_wide_diagnostic.json`, `SUMMARY.json`
- `affine_maps/affine_map_<pair>_<set>_<mode>.csv.gz` -- full (Delta, eps) grids, statistic + Delta chi2 + N per estimator
- `affine_maps/affine_maps_<set>_<mode>.png` -- 3x3 heatmaps (rows = pairs, columns = estimators)
- `delay_reproduction_scan.png` -- step-3 coarse delay scans

