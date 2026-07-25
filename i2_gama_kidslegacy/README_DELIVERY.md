# i2 — `gama_kidslegacy_ipr_rar_inputs_v1.parquet`

GAMA DR4 lens sample × KiDS-Legacy (KiDS DR5) shear catalogue, assembled for the
kinematics–lensing transfer test on `log10(A_IPR / kpc²)`.

Cosmology throughout: **flat ΛCDM, H0 = 70 km/s/Mpc, Ωm = 0.3, ΩΛ = 0.7** (`h70 = 1` column
carried). Mistele et al. 2024 use H0 = 73; radii scale as 1/h70, areas as 1/h70².
Redshifts: **GAMA spectroscopic**, CMB-frame (`Z_CMB` from `DistancesFrames v14`).

---

## Join keys, in order

| step | left | right | key | cardinality |
|---|---|---|---|---|
| S3 | TilingCat v46 | DistancesFrames v14 | `CATAID` | inner, 1:1 |
| S4 | " | SersicCatSDSS v09 | `CATAID` | inner, **exactly 1:1** (both tables are 221,373 rows) |
| S6 | " | StellarMassesLambdar v24 | `CATAID` | LEFT (200,077 rows on the right) |
| S7 | " | G3CGal v10 → G3CFoFGroup v10 | `CATAID` → `GroupID` | LEFT (204,110 / 26,194) |
| S8 | " | EnvironmentMeasures v06 | `CATAID` | LEFT (92,513 rows — the DMU is z-limited) |
| S10 | " | KiDS-Legacy gold sources | **sky position only** | per-lens aggregation |

⚠ **There is no ID cross-match between GAMA and KiDS-Legacy.** The public KiDS-Legacy gold
catalogue ships no `SeqNr`/`SLID`/`ID` column at all — only `THELI_NAME` + `RAJ2000`/`DECJ2000`
(the KiDS DR5 release notes say external columns must be added "via a cross-match on-sky, with a
functionally zero matching radius"). The lens↔source relation is therefore **geometric**, which is
correct for lensing but means no per-object provenance link exists.

## Cuts, in order (full ladder with counts in `STAGE_COUNTS_lens.json`)

1. `SURVEY_CLASS >= 4` — GAMA-II main survey, r < 19.8, the GAMA-recommended science selection.
2. `NQ >= 3` — reliable spectroscopic redshift (GAMA `TilingCat` notes).
3. `0.002 < Z_CMB < 0.6`.
4. Valid r-band single-Sérsic fit: `0 < GALRE_r < 1000"`, `0.1 < GALINDEX_r < 20`,
   `0 ≤ GALELLIP_r < 1`, `0 < GALMAG_r < 30`.
   ⚠ `GALINDEX_r == 20` is the GALFIT **ceiling** (a non-convergence pile-up), and
   `GALMAG_r == 100` is the GALFIT failure sentinel — both are excluded by these bounds.
5. No isolation cut is applied in the delivered table — `R_isol_Mpc_h70` is provided so any
   threshold can be imposed downstream. **See `POWER_GO_NOGO.md`: this choice decides the test.**

## Derived columns

| column | definition |
|---|---|
| `axis_ratio_q_r` | `1 − GALELLIP_r` (GALELLIP **is** 1−b/a — see `GALELLIP_RESOLUTION.md`) |
| `Re_maj_arcsec_r` | `GALRE_r`, the **semi-major-axis** half-light radius |
| `Re_circ_arcsec_r` | `GALRE_r · sqrt(q)` |
| `Re_maj_kpc_r`, `Re_circ_kpc_r` | the above × `kpc_per_arcsec` (from `DA_Mpc`) |
| **`A_IPR_kpc2_ellip`** | `π · Re_maj_kpc² · q` = `π · Re_circ_kpc²` — half-light **ellipse** area |
| **`A_IPR_kpc2_major`** | `π · Re_maj_kpc²` — no inclination deprojection |
| `log10_A_IPR_ellip`, `log10_A_IPR_major` | log10 of the above — **the regressor X** |
| `log10_Re_circ_kpc`, `log10_Re_maj_kpc` | for the β_R = 2·β_A consistency check |
| `R_isol_Mpc_h70` | 3D comoving distance to nearest neighbour with ≥10% of the lens M* (Brouwer 2021 / Mistele 2024 criterion) |
| `R_isol_proj_Mpc_h70` | projected analogue |
| `R_isol_neighbour_CATAID` | which galaxy set `R_isol` (auditability) |
| `d_edge_deg`, `GAMA_FIELD` | angular distance to the GAMA field boundary — **edge lenses have artificially large R_isol; flag on this** |
| `sigma_crit_inv_bin1..6` | `<Σ_crit⁻¹>` per KiDS-Legacy tomographic bin, integrated over the SOM-calibrated `NZ_SOURCE` n(z), in **Mpc²/M⊙** |
| `sigma_crit_inv_neff_weighted` | the same, n_eff-weighted across the 6 bins |
| `sigma_crit_Msun_pc2` | `1/Σ_crit⁻¹` in M⊙/pc² (convenience) |
| `lensing_efficiency_sum_neff_scinv2` | `Σ_b n_eff,b · <Σ_crit⁻¹>_b²` — the S/N-relevant weight |
| `n_src_100_300kpc`, `n_src_300_1000kpc` | exact KiDS-Legacy source counts in the two **destroyer** annuli |
| `n_src_30_1400kpc` | total usable source count |
| `inside_kids_legacy` | `n_src_30_1400kpc > 0` |

`Σ_crit⁻¹` prefactor `4πG/c² = 6.013541559657027e-19 Mpc/M⊙`, cross-checked against
`c²/(4πG)·D_S/(D_L D_LS)`: both give **3455.8 M⊙/pc²** at (z_l, z_s) = (0.2, 0.8). ✔

## 🔴 THINGS THAT CHANGE WHAT CAN VALIDLY BE COMPUTED

1. **`e1`/`e2` in the public KiDS-Legacy catalogue carry NO multiplicative (m) correction.**
   The shipped readme says verbatim: *"c-corrected and recalibrated Lensfit ellipticity e1 —
   **no m corr**"*. The cosmic-shear tarball ships the n(z), the covariance and the chains but
   **no per-tomographic-bin m table**; m is marginalised inside the released covariance. Any ΔΣ
   amplitude built from this catalogue is therefore biased by (1+m) ≈ a few per cent per bin until
   m is applied from Wright et al. 2026 (A&A 703, A158). For **β_A specifically this is
   second-order** — m depends on source tomographic bin, not on lens A_IPR, so it scales the
   amplitude, not the slope — but it is not zero if the source-bin mix varies with lens redshift,
   and lens redshift correlates with A_IPR through the flux limit. **Test for that correlation
   before assuming m cancels.**
2. **`weight` already folds in the gold weight.** `weight = shear_weight_only × gold_weight_only`;
   using `weight` for shear stacking double-counts the N(z) gold weighting. Use
   `shear_weight_only` for ΔΣ and `gold_weight_only` only for n(z) work. Both columns are shipped.
3. **`GALINDEX_r` piles up at exactly 20.00** — the GALFIT upper bound. Excluded here; if any
   downstream re-selection loosens the Sérsic quality cut, that pile-up will re-enter and it is
   *not* a measurement.
4. **`EnvironmentMeasures v06` covers only 92,513 GAMA galaxies (67,740 of our lenses)** because
   the DMU is redshift- and edge-limited. `SurfaceDensity`/`CountInCyl`/`AGEDenPar` are NaN for
   the remaining 113,868 lenses. It is **not** a usable isolation variable for the full sample —
   `R_isol_Mpc_h70` (computed here for 181,536 of 181,608) is.
5. **GAMA edge bias in R_isol.** GAMA-II equatorial is three 12×5 deg rectangles. A lens near a
   boundary has no catalogued neighbours beyond it and its `R_isol` is inflated. At
   `R_isol > 4 Mpc/h70` (≈ 0.6 deg at z = 0.2) the effect is real. Cut on `d_edge_deg` before
   using any isolation threshold, or the isolated sample is preferentially an edge sample.
6. **Stellar-mass IMF mismatch with Mistele.** GAMA `StellarMassesLambdar v24` is
   Taylor et al. 2011 (BC03, Chabrier IMF, LAMBDAR matched-aperture photometry). Mistele et al.
   use Schombert et al. 2014 3.6 μm M/L. Applying Mistele Eqs 4.1–4.3 to GAMA `logmstar`
   inherits that offset (~0.1–0.2 dex, mass-dependent).
