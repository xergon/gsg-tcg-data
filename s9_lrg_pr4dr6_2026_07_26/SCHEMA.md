# S9 delivery — DESI LRG x PR4/DR6 tomography + Fig-4 PPD  (cut 2026-07-26 UTC)

## PART A — Zenodo 10.5281/zenodo.12613408 (Sailer et al. + Kim et al.)
Archive `zenodo_LRGxPR4-DR6.tar`, 1,309,163,026 B, md5 `7055fb98a70381292b18a9b0e06bd0c2`
VERIFIED byte-for-byte against the value published in the Zenodo record metadata. Source member used:
`zenodo_LRGxPR4-DR6/data/lrg_cross_pr4+dr6.json` (20,110,262 B) = the fiducial measurement + covariance.

### Binning (identical for every spectrum)
12 bandpowers. ledges = 20,44,79,124,178,243,317,401,495,600,713,837,971
ell_eff  = 32, 61.5, 101.5, 151, 210.5, 280, 359, 448, 547.5, 656.5, 775, 904

### `lrg_pr4dr6_bandpowers_144.csv` — the data vector, 144 rows
Spectrum order (12 spectra x 12 bands, band fastest):
 0 DR6xLRGz1, 1 DR6xLRGz2, 2 DR6xLRGz3, 3 DR6xLRGz4,
 4 PR4xLRGz1, 5 PR4xLRGz2, 6 PR4xLRGz3, 7 PR4xLRGz4,
 8 LRGz1xLRGz1, 9 LRGz2xLRGz2, 10 LRGz3xLRGz3, 11 LRGz4xLRGz4
Rows 0..95 are the eight kappa-g cross-spectra; rows 96..143 are the four galaxy auto-spectra.
Values are PSEUDO-C_ell (the archive's own README: "cl_X_Y is the pseudo Cell C^{XY}").
Z-BIN LABELS ARE EXPLICIT in the source keys — no inference was needed.

### 🔴 COVARIANCE CONVENTION — READ BEFORE USING
The publisher does NOT ship a matrix. It ships **90 separately named DENSE 12x12 blocks**,
key `cov_X_Y_M_N` = Cov(C^{XY}, C^{MN}).
- Every block is a FULL dense 12x12. Verified: 0 of 90 blocks has an all-zero upper triangle,
  so NO block is lower-triangle-only. Diagonal blocks are symmetric to 3.9e-31 on a 7.7e-14 scale.
- ⚠ THE TRUNCATION IS AT THE **BLOCK** LEVEL, AND IT IS INCONSISTENT:
    * kappa-g x kappa-g, same lens map -> BOTH orderings stored, exactly redundant (A - B^T = 0.0).
    * kappa-g x kappa-g, across maps  -> only `cov_DR6_*_PR4_*`; `cov_PR4_*_DR6_*` ABSENT.
    * kappa-g x gg                    -> only `cov_<MAP>_LRGzi_LRGzj_LRGzj`; reverse ABSENT.
    * gg x gg                         -> only i<=j, e.g. `cov_LRGz1_LRGz1_LRGz2_LRGz2`; reverse ABSENT.
  ⇒ Assembling the full matrix required filling **54 of 144 blocks by transpose**. A diagonal-only
  sanity check PASSES on the wrong reading — this is exactly the trap that was flagged.
- HOW VERIFIED: (1) per-block upper-triangle emptiness test on all 90 blocks; (2) explicit
  A vs B^T comparison on a redundantly stored off-diagonal pair (max abs diff 0.0);
  (3) diagonal-block symmetry; (4) post-assembly symmetry 2.02e-28 and eigen-decomposition.

### `lrg_pr4dr6_covariance_144x144.csv` and `lrg_pr4dr6_kappag_covariance_96x96.csv`
**FULL SYMMETRIC SQUARE MATRICES, ROW-MAJOR, one row per line, comma separated, %.17e.**
NOT triangular. Row/column order is exactly the `index` column of the bandpower file.
144x144: symmetric to 2.02e-28, POSITIVE DEFINITE, eig 1.733455e-17 .. 1.687291e-11, cond 9.734e5.
 96x96  (kappa-g only): POSITIVE DEFINITE, eig min 1.733847e-17, cond 6329.
For S9's gate, K_LRG = A_z1 - (A_z2+A_z3+A_z4)/3 is a linear functional of rows 0..95;
propagate with v^T C_96 v using the 96x96 block.

### NOT SHIPPED (explicit)
The 28 bandpower window functions `wl_*`, each (12, 5725) ~1.7 MB of numbers, ~20 MB total —
past the 900 kB shard budget. They live in `data/lrg_cross_pr4+dr6.json` inside the tar.
The likelihood code is NOT in the archive; it is at https://github.com/NoahSailer/MaPar/ .

## PART B — Figure-4 Posterior Predictive Distribution (arXiv 2505.20656 / Zenodo 17636841)
⭐ THE 500-DRAW PPD IS **PRECOMPUTED BY THE AUTHORS** — it did not need to be regenerated.
Member: `Zenodo_data_chains/Fig4/specz_CkgCggPkXi_PPD_nsplanck_N500_BGSLRG_fixedDNDZ.json`
(144,333,862 B) inside `RSD_kxg_Zenodo_chains_data.tar.gz` (1,918,687,654 B,
md5 `d47491ba713051e7d830d70c06b5c9ae`, re-verified this run).
Contents: `Ckg` (4, 500, 1001), `Cgg`/`Cgg_alt` (4, 500, 1001), `Pks` (4, 500, 72),
`xis` (4 x (500, 10)), `ells` 0..1000, `kvec` (36), `rvec` (10).
The filename encodes the requested chain: Ckg+Cgg from the **PkXi** (P_ell + post-recon xi_ell)
fit, **N500**, **BGSLRG**, fixed dN/dz, Planck n_s prior. Paper caption confirms: "500 samples are
randomly drawn from the 1-sigma region of the 3D analysis chains".

### `ppd_mean_bandpower_18.csv` and `ppd_covariance_18x18.csv`
Binned onto the SAME 18 rows as the earlier `s9_data_rows_18.csv` cut:
(PR4,BGS),(PR4,LRG1),(PR4,LRG2),(DR6,BGS),(DR6,LRG1),(DR6,LRG2) x cov bands 1,2,3
([44,79) [79,124) [124,178), ell_eff 61.0 101.0 150.5), band fastest.
Binning operator = the publisher's own bandpower windows `w_<MAP>_<TRACER>` from
`Fig3_9_10/cl_ggkg_*_v1.5.json`, rows 2,3,4 (those files' ledges start at 10, the covariance file's
start at 20 — a ONE-INDEX OFFSET that is easy to get wrong). Alignment PROVEN: re-binning the
published cl_ arrays with the same indices reproduces `s9_data_rows_18.csv` with max rel diff **0.0**.
The PPD Ckg is tabulated only to ell=1000 while the windows run to 6143; the discarded window mass
is at most **6.7e-06** of the total, so the truncation is negligible.
`ppd_covariance_18x18.csv` = **FULL SYMMETRIC 18x18, ROW-MAJOR, %.17e**, the sample covariance
(ddof=1 mean, np.cov default) of the 500 binned realisations. Symmetric to 0.0 exactly,
positive definite, eig min 3.6166e-27. It is the PPD *spread*, ~4 orders of magnitude smaller in
eigenvalue than the data covariance — do not mistake it for a measurement error.
`ppd_realisations_500x18.csv` = the raw 500 x 18 draws, so any other statistic can be re-derived.

### 🔴 REPORTED, NOT GUESSED — an axis-ordering ambiguity
`Ckg` axis 0 has length 4 and the file carries NO label for it. The canonical reading (filename
`BGSLRG`, and the four full-shape spectroscopic samples) is index 0=BGS, 1=LRG1, 2=LRG2, 3=LRG3,
and that is what the two headline products use. **The data CANNOT confirm it**: over all 24
assignments of three indices to (BGS,LRG1,LRG2) the chi2 against the measured 18-vector spans only
30.6 to 37.9 (canonical = 35.83 for 18 rows). ⇒ `ppd_ambiguity_all_tracer_indices.csv` ships the
binned mean and sigma for ALL FOUR axis-0 indices against every one of the 18 window rows, so the
correct column can be chosen on physical grounds rather than assumed.
