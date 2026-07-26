# T7 / JVAS B0218+357 · VLBA project BC214 — SCHEMA
Fetched 2026-07-26 UTC. Source archive: NRAO Data Archive, `https://data.nrao.edu/archive-service/restapi_get_paged_exec_blocks`
(`archive.nrao.edu` is RETIRED; `https://data-query.nrao.edu/tap` TIMES OUT on TCP 443 — do not use either).
Publication for the imaged products: Spingola et al. 2016, MNRAS 457, 2263 (arXiv:1601.03591), LaTeX e-print source.

## 1. bc214_archive_inventory.csv  (24 rows)
Every BC214 exec block held by the NRAO archive. One row per correlator output file.
- `vlba_segment` BC214A..BC214P · `obs_start`/`obs_stop` UTC ISO
- `obs_band` band label of THIS file · `segment_bands` bands of the parent segment
- `obs_id` IDIFITS filename · `sci_prod_locator` `uid://vlba/correlation/<uuid>` (the download handle)
- `dataproduct_type` = correlation for all 24 · `cal_status` = "Do Not Calibrate" for all 24
- `data_rights` = PUBLIC for all 24 · `num_antennas` (10, except 9 on BC214K and BC214N)
- `access_estsize_bytes` this file · `segment_size_bytes` whole segment
🔴 `obs_band`/`segment_bands` list only K and S. **The archive label UNDER-REPORTS the frequency setup:
the 8.4 GHz X band was recorded SIMULTANEOUSLY with 2.3 GHz** (Spingola+2016 §2.1: "The 2.3 and 8.4 GHz
observations were simultaneous"). The X-band IFs live inside the S-labelled IDIFITS on the 4 dual-band dates.
Do NOT conclude from this file that X band is absent.

## 2. b0218_bc214_epoch_fluxes_long.csv  (48 rows) — THE COMPUTABLE PRODUCT
Spingola+2016 Table 1, long form. One row per (epoch, lens image, band).
`epoch_date` (ISO, reconciled to the archive) · `vlba_segment` · `paper_epoch_label` (non-empty ONLY where the
paper's printed label disagrees with the archive — see FINDING 3) · `lens_image` A|B · `band` S|X|K ·
`freq_ghz` · `flux_mJy` · `flux_err_mJy` · `beam_maj_mas` · `beam_min_mas` (restoring beam for that band).
16 epochs at 22 GHz; 4 of those also carry 2.3 and 8.4 GHz ⇒ 16*2 + 4*2*2 = 48 rows.
Errors are dominated by the absolute flux scale (7–8% at S/X, 10% at K), NOT by image rms.

## 3. b0218_bc214_magnification_ratio.csv  (24 rows)
Derived here: `ratio_A_over_B` = S_A/S_B with `ratio_err` by quadrature of the fractional errors.
⚠ The two flux errors are dominated by a COMMON absolute-scale term, so quadrature OVERSTATES the ratio error.
Treat `ratio_err` as an upper bound; the epoch-to-epoch scatter is the better noise estimate.

## 4. b0218_bc214_gaussian_components_22ghz.csv  (7 rows)
Spingola+2016 Tables 2 and 3. Image-plane Gaussian fits at 22 GHz.
`lens_image` · `component` (A1–A4, B1–B3) · `peak_mJy_per_beam`(+err) · `total_flux_mJy`(+err) ·
`deconv_maj_mas` · `deconv_min_mas` · `pa_deg` · `pos_x_mas_rel_A1` · `pos_y_mas_rel_A1`.
Positions are relative to A1 and quoted to 0.01 mas. Deconvolved sizes reach 0.125 mas.
Single epoch only — the paper reports no significant morphological variation across epochs.

## 5. bc214_resolution_budget.csv  (3 rows) — HOW THE RESOLUTION WAS ESTABLISHED
Computed here from ITRF positions of all 10 VLBA stations. `max_baseline_km` = 8611.585 km (MK–SC),
`diffraction_limit_lambda_over_B_mas` = lambda/B_max, `published_beam_*` from Spingola+2016 §3.1,
`published_min_over_diffraction_limit` = the ratio that proves the published beam is NOT tapered down,
`meets_T7_2mas_threshold_on_{minor,major}_axis`.
