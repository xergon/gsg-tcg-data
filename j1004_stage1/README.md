# j1004_stage1 — J1004_PITD0_STAGE_1 result bundle

Execution of the frozen procedure `J1004_PITD0_STAGE_1` specified by ChatGPT research
thread **T8**, run by Cat (compute arm) on the published J1004 light-curve archive.

**Steps 1–6 only.** T8's steps 7–8 — the M0/M1/M2/M3 model fits, the null farm, and any
TARGET KILLED / SURVIVES / PIVOT call — are deliberately **not** performed here. Nothing in
this bundle is a verdict; every file reports numbers and the procedure that produced them.

Start with **`RESULTS.md`**.

| file | contents |
|---|---|
| `RESULTS.md` | full narrative of what was computed, every number, and every Cat judgement call |
| `SUMMARY.json` | sha256 of every input and output file + all run parameters |
| `duplicate_merge.json` | step 2 — the MJD 53663.501 in-flux merge, per image |
| `delay_reproduction.json` | step 3 — constant-delay reproduction vs Munoz+2022 Table 2 |
| `feature_windows.json` | step 4 — the 34 frozen C-only windows, exploration vs untouched reserve |
| `estimator_outputs.json` | steps 5–6 — best (Δ, ε) per pair per estimator, κ, D_DC, closure ratio |
| `eps_wide_diagnostic.json` | wide-range ε scan used to locate where each statistic turns over |
| `affine_maps/*.csv.gz` | full (Δ, ε) grids for the primary *frozen* point-set family: statistic and Δχ² for each of the three estimators (the contributing-epoch count N is constant across a frozen map and is recorded in the file header) |
| `affine_maps/*.png` | 3×3 heatmaps, rows = pairs (D/C, A/C, B/C), columns = estimators |
| `delay_reproduction_scan.png` | step-3 coarse delay scans |

Input data (same repo): `j1004_lensed_quasar/j1004_lightcurves_long.csv`,
sha256 `6c476e4b829da9de61bfe91675aae1f07b546d1e8d34c4ed3e2e439cff38407e`.

**The even-ranked confirmation-reserve windows were not used in any fit in this bundle.**
They are listed in `feature_windows.json` only so that T8 can see what is being held back
for a Stage-2 confirmation.
