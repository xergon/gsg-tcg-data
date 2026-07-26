# T2 — MHONGOOSE outer-H I roughness inputs (derived), 2026-07-26

## Provenance
MHONGOOSE Deep Data Release 1+2+3, moment maps, distributed via Google Drive only
(no ASTRON/Zenodo mirror of the deep releases exists). Survey paper: de Blok et al. 2024, A&A 688, A109.
252 source FITS files pulled auth-free from `drive.usercontent.google.com`, **every file magic-byte gated
as `SIMPLE` FITS** (252/252 OK, 0 failures). Products used per galaxy: `mom0_pb` (primary-beam corrected
moment-0) and `mask-2d` (SoFiA 2.5.1 2-D detection mask), at weightings `r05_t00`, `r10_t00`, `r10_t90`.

## 🔴 THE HEADLINE NUMBER
**The public MHONGOOSE deep release covers 28 galaxies, not 19** — measured from the 1,749-file release index,
not from a paper's sample table. **All 28 carry the identical complete 47-file moment set** (6 angular
weightings x 8 products). Zero are partial. DR1=8, DR2=9, DR3=11.

## Units and conversion (stated so it can be checked, not trusted)
`mom0_pb` BUNIT is `Jy/beam*m/s`.
  N_HI [cm^-2] = 1.104e24 * S[Jy/beam*km/s] / (bmaj_arcsec * bmin_arcsec)
  (= 1.823e18 * 1.222e6 / nu_GHz^2, nu = 1.42041 GHz)
  Sigma_HI [Msun/pc^2] = 8.0e-21 * N_HI   (atomic H only, no He)
  Sigma_faceon = Sigma_obs * cos(i), i from MHONGOOSE_TARGETS.csv.
Sanity anchor: NGC 5068 (J1318-21) at r10_t90 gives Sigma_max = 11.48 Msun/pc^2 — correct for a 94" beam.

## Geometry
Centre = flux-weighted centroid of the SoFiA mask. PA = weighted second moments of the mask (`pa_pix_deg`,
pixel frame, 0-180). Deprojected radius uses PA and the catalogue inclination. Azimuth binned into 72 bins
of 5 deg; R(theta) = outermost radius along each ray at which Sigma_faceon >= level.
A contour is called CLOSED only if >= 75% of the 72 azimuthal bins are filled (`nth_filled_R*`).

## Files
- `T2_MHONGOOSE_OUTER_HI_PERGAL.csv` — 84 rows = 28 galaxies x 3 weightings.
  Per contour level L in {0.01, 0.03, 0.1, 0.3, 1, 3, 10} Msun/pc^2 (tag `0p01`…`10`):
  `R<L>_kpc` mean contour radius; `nbeam_R<L>` radius in bmaj units; `nth_filled_R<L>` azimuthal
  completeness /72; `A1_R<L>`…`A8_R<L>` Fourier amplitudes of R(theta)/<R> - 1; `A345_R<L>` = sqrt(A3^2+A4^2+A5^2).
  Also: distance_mpc, inclination_deg, log_mhi, log_mstar_wise, pix/beam scales, kpc_per_arcsec,
  sigma_max_Msun_pc2, and the PUBLISHED per-weighting sensitivity `pub_log_NHI_3sig_16kms`,
  `pub_Sigma_3sig_Msun_pc2`, `pub_noise_mJy_beam` (de Blok 2024 Table 4).
  `eligible_L0p1 / L0p3 / L1` = contour closed AND radius >= 2 beams AND i <= 75 deg.
- `T2_MHONGOOSE_CONTOUR_RTHETA.part01/02.csv` — 26,568 rows, the raw R(theta) per
  (galaxy, weighting, level, 72 azimuths). **Ship this so any Fourier order or roughness estimator can be
  recomputed without re-fetching 1.5 GB of FITS.** `filled` = 1 if the ray genuinely reached the level.

## ⚠ NOISE — READ BEFORE DEBIASING
SoFiA moment-0 maps are **exactly zero outside the detection mask** (`frac_nonzero_offmask` = 0.0 on every
row). **You cannot estimate a noise floor from these maps.** Use the published `pub_Sigma_3sig_Msun_pc2`
column instead (3-sigma over 16 km/s, from Table 4, cos-i corrected). At r10_t90 that is ~0.004 Msun/pc^2,
so the 0.1 Msun/pc^2 contour sits ~24x above the 3-sigma floor and the 0.01 contour sits ~2.4x above it —
**the 0.01 level is NOT safely above noise; 0.1 and above are.**

## ELIGIBILITY (the decisive count)
| weighting | beam | Sigma>=0.1 | Sigma>=0.3 | Sigma>=1.0 |
|---|---|---|---|---|
| r10_t00 | 26.4" | **22 / 28** | 21 / 28 | 19 / 28 |
| r10_t90 | 94.2" | 12 / 28 | 9 / 28 | 8 / 28 |
**22 of 28 clear the composite N >= 10 requirement at r10_t00 / Sigma = 0.1 — over twice the gate.**
The r10_t90 count is lower purely because a 94" beam is only a few beams across these discs, not because
the data are missing. Both are shipped so resolution-selection is an explicit control, not a hidden choice.
