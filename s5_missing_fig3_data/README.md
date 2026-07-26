# S5 follow-up fetch — the two load-bearing defects in Dryad `10.5061/dryad.4xgxd25rg`

Fetched / verified 2026-07-26 (UTC). Parent delivery: `s5_dryad_4xgxd25rg/`, commit
`c02629a6cd83b0fb205169629114dc5a3666280a`.

## Identity of the deposit — established from the artifact, not the label

- Dryad title: *"Data from: In-orbit test of the weak equivalence principle with atom interferometry"*
- Preprint: **arXiv:2603.22981v1** (submitted 2026-03-24, 22 pages, 6 figures) — **China Space Station
  ⁸⁵Rb/⁸⁷Rb dual-species atom interferometer**, η = (−3.1 ± 4.6)×10⁻⁷. **This is NOT Cold Atom Lab.**
- Journal: Dryad records `relatedPublicationISSN = 1095-9203` (**Science**); the zip is named for
  Science manuscript **aeh0529**.
- Dryad DataCite record carries **`relatedIdentifiers: []`** — no article DOI is linked.

## 🔴 (a) `data_for_Figs3b / 3c / 3d / 3e` — NOT FOUND, AND NO PUBLIC SOURCE EXISTS YET

These are **supplementary** figures S3b–S3e (per-configuration differential-phase *histograms*), and the
supplementary materials have **not been published anywhere**. Routes checked and closed:

| Route | Result |
|---|---|
| Dryad archive itself | 21 zip entries = 13 data files + 8 dirs. Absent. Confirmed by full `unzip -l`. |
| Other Dryad versions | `/api/v2/datasets/.../versions` → **count 1** (v5 only). No other version. |
| arXiv `/e-print/2603.22981v1` | **PDF-only submission** (2,874,072 B, `%PDF-1.6`) — **no LaTeX source**. |
| arXiv `/format/` + abs page | **no ancillary files**. |
| arXiv v1 content | main text + Materials and Methods I–IV only. **No Fig S1/S3/S4/S6.** SM referenced, not included. |
| Crossref `10.1126/science.aeh0529` | **404**. `doi.org` → **DOI Not Found**. |
| Crossref journal search (ISSN 0036-8075 / 1095-9203) | no matching article. |
| OpenAlex | 3 records: arXiv preprint ×2 + this Dryad deposit. **No journal record.** |
| Europe PMC | 0 hits. |
| Zenodo API | 0 hits. Figshare API | 0 hits. |
| Dryad search (title / authors / "China Space Station") | only this one deposit. |
| `science.org/doi/10.1126/science.aeh0529` | **HTTP 403, Cloudflare "Just a moment…" challenge (5,743 B).** Not bypassed. |
| ScienceDB `scidb.cn` API | `{"code":20001,"message":"用户未登录"}` — **login wall.** Not bypassed. |

**⇒ The Science article is accepted but not yet published; the SM that contains Figs S3b–e does not exist
publicly. There is nothing to fetch. This is a HUMAN-ONLY BLOCKER (author contact, or wait for publication).**

**Structural note for the thread:** S3b–e are *histograms derived from per-shot Δφ*, and the per-shot Δφ for the
four configurations (>9,700 fringe pairs) is **also absent** from the archive — only `data_for_Fig2ef`
(3,223 samples, one round) and the 44 per-configuration *averages* in Fig4a exist. So even a full SM would give
binned counts, not the underlying shots. The first two moments per configuration **are** already recoverable
from `data_for_Fig4a.csv` (`pha1..pha4` + errors).

## ✅ (b) Fig4a's missing date column — SOLVED, and the ≥3-time-block test is RUNNABLE

The date column is not needed, and the epoch grid is recoverable from the archive's own two files.

1. **The 44 rows are in chronological order — proven, not assumed.** Recomputing the **non-overlapping Allan
   deviation** of `phaave` **in file order** reproduces **all 10 published Fig4b values exactly** at printed
   precision (max |diff| = 0.00000). Arbitrary-input control: **0 of 20,000 random permutations** come close
   (best permutation 0.00416). See `ALLAN_ORDER_PROOF.txt`.
2. **The epoch grid is fixed.** `t_published / m = 6.45455 d` for **every** cluster size m ⇒
   **τ = 284/44 = 6.4545454545 d exactly**; the 44 points tile **284.000 d** from the paper's stated start date
   **2024-08-27** → end **2025-06-07**.
3. ⚠ **4-day discrepancy flagged, not resolved:** the prose says *"over a period of 280 days"*, the Allan grid
   says 284.000 d.
4. ⚠ **The reconstructed epochs are the paper's own UNIFORM Allan time base, NOT true calendar timestamps.**
   The real campaign had gaps. Use for block labelling and ordering; **do not** use for gap/cadence analysis.

## Files

- `data_for_Fig4a_with_RECONSTRUCTED_epoch.csv` — the 44 Fig4a rows verbatim, prefixed with
  `k`, `t_mid/t_start/t_end_days_since_20240827_RECONSTRUCTED`, `date_mid_RECONSTRUCTED`.
  **Every reconstructed column is named `_RECONSTRUCTED` on purpose. It is derived, not measured.**
- `ALLAN_ORDER_PROOF.txt` — the reproduction table + the 20,000-permutation control.
