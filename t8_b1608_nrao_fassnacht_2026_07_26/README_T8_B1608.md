# T8 / CLASS B1608+656 — NRAO project-code recovery + Fassnacht Paper I/III tables
Harvested 2026-07-26 (UTC). Source of truth: NRAO Science Data Archive REST search
(https://data.nrao.edu/archive-service/restapi_get_paged_exec_blocks) and the arXiv /e-print/
LaTeX sources of Fassnacht et al. 1999 (astro-ph/9907257) and Fassnacht et al. 2002 (astro-ph/0208420).

## 1. THE BLOCKER IS CLEARED — season-1 VLA project code = AF310
The code is absent from the printed text of both papers. It survives ONLY in the LaTeX figure
labels of the Paper III e-print: `fig_compos_af310` (season 1), `fig_compos_af340` (season 2),
`fig_compos_ab922` (season 3). Each was then independently confirmed against the live NRAO archive.

| season | project code | PI (archive) | archive project window (UTC) | EBs | paper Table 1 window | N_obs |
|---|---|---|---|---|---|---|
| 1 | **AF310** | C. Fassnacht | 1996-10-10 -> 1997-05-26 | 60 | 1996 Oct 10 -> 1997 May 26 | 66 |
| 2 | **AX4** + **AF340** | E. Xanthopoulos / C. Fassnacht | 1998-02-13 -> 1998-06-09 / 1998-06-11 -> 1998-10-19 | 39 + 41 = 80 | 1998 Feb 13 -> 1998 Oct 19 | 81 |
| 3 | **AB922** | I. Browne | 1999-06-15 -> 2000-02-14 | 95 | 1999 Jun 15 -> 2000 Feb 14 | 92 |

All AF310 exec blocks: instrument VLA, band X (8.5 GHz), dataproduct visibility, data_rights PUBLIC,
configurations D->A(2) / A(26) / A->BnA(2) / BnA(4) / B(26), 910,135,296 bytes total.

Two seasons NOT in Paper III but present in the archive for this field:
**AF377** (C. Fassnacht, 76 EBs, 2000-10-13 -> 2001-05-29) and **AW576** (J. Winn, 55 EBs, 2002-01-24 -> 2002-08-01).

## 2. STRUCTURAL FINDINGS THAT CHANGE WHAT CAN BE COMPUTED
- **No covariance matrix for the three delays exists in the published record.** Paper III Table 5
  gives only marginal, asymmetric 68% and 95% intervals per parameter, from **1000** MC realizations
  (not 10,000-100,000). The MC chain is not published and is not on any archive/CDS mirror.
  The nearest thing to joint information is Paper III Table 3 (19 dispersion-statistic settings x
  the three delays jointly) plus the two published delay RATIOS with their own CIs.
- **The Paper III "recalibrated season 1" light curve is NOT tabulated anywhere.** Paper III recalibrates
  season 1 (S 2.1) but publishes only figures (f4.eps) and per-season MEAN flux densities (Table 2).
- **Row-count conflict, real and unexplained:** Paper I's published season-1 curve has **62 epochs**
  ("the final edited light curves contain 62 epochs"); Paper III reports season 1 as **66 observed / 64 good**;
  the NRAO archive holds **60** AF310 exec blocks. Three different numbers for the same season.
- The legacy electronic table URL quoted in Paper I, `http://www.nrao.edu/~cfassnac/1608flux.tab`,
  is **HTTP 404** and has **no Wayback snapshot**. The LaTeX source is now the only machine-readable copy.
- The legacy archive `archive.nrao.edu` is **retired** (serves a "Service Decommissioned" page).
  The documented VO/TAP endpoint `https://data-query.nrao.edu/tap` **did not connect** (TCP 443 timeout,
  three attempts). The working public route is the portal's own REST search, used here.

## 3. FILES
- `b1608_season1_epoch_calibration_null.csv` — 62 rows. Paper I Table 3 season-1 fluxes joined
  1:1 (unique, |dt| < 1 d) to AF310 archive exec blocks. 57/62 epochs matched; 5 unmatched
  (MJD-50000 = 387, 394, 398, 440, 464); 3 AF310 EBs carry no Paper I epoch
  (1996-10-20, 1996-10-26, 1996-11-01). `nrao_matched` flags this per row — do not drop it silently.
- `b1608_season1_epoch_calibration_null_long.csv` — 248 rows, same content melted to one row per (epoch, component).
- `b1608_af310_season1_nrao_epochs.csv` — 60 AF310 exec blocks, full archive metadata.
- `b1608_field_nrao_project_census.csv` — all 424 exec blocks within 0.05 deg of B1608+656 (VLA/EVLA/VLBA), 24 project codes.
- `b1608_field_project_summary.csv` — one row per project code.
- `b1608_paperI_table3_season1_lightcurve.csv` — 62 epochs x (A,B,C,D flux + error), Paper I calibration.
- `b1608_paperIII_table1_seasons.csv`, `..._table2_positions_meanflux.csv`, `..._table3_dispersion_grid.csv`,
  `..._table4_delays_magnifications.csv` (31.5 / 36.0 / 77.0 d), `..._table5_confidence_intervals.csv`.

`num_antennas` is 0 for every legacy-VLA exec block — the archive does not carry it for pre-EVLA data.
