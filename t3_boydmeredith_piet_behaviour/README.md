# T3 — Boyd-Meredith & Piet dynamic-clicks BEHAVIOUR (5 rats) + Dryad deferral manifest

Delivered 2026-07-26. Source: Figshare article **16695592** (`10.6084/m9.figshare.16695592.v2`),
"Rat FOF Recordings During Dynamic Clicks Task", Boyd-Meredith & Piet. **CC BY 4.0.**

## 1. SUBJECT COUNTS — the number T3 asked for first

| Source | Subjects | Species | Trials | Note |
|---|---|---|---|---|
| **Already on disk** — Zenodo 13352119 Poisson-clicks parquet | **515 rats** | rat | 25,562,353 | static-gamma clicks, **no state switches** |
| Figshare 16695592 (this delivery) | **5 rats** | rat | 540,629 | **dynamic** clicks, **has `genSwitchTimes`** |
| Dryad 02v6wwq6b — main EEG analysis sample | **24 humans** | human | — | continuous RDK + EEG |
| Dryad — subjects present in `behav_data_all_subjs_all3.mat` | **28 humans** | human | — | `nS = 28` hardcoded in the analysis code |
| Dryad — total tested | 33 humans | human | — | 3 failed training, 1 asleep, 5 EEG-technical ⇒ 24 |
| Dryad — vertical-motion control (Fig 8) | +6 humans | human | — | **different stimulus condition, not poolable** |

Dryad counts are sourced from the eLife paper (`10.7554/eLife.82823`, Methods) and from
`CCNHuntLab/ruesseler-eeg-analysis`, whose `subjectList` is exactly the 24-subject main sample
`[16, 18:21, 24, 26:29, 31, 33:35, 42, 43, 47, 50:52, 54, 55, 57, 58]` and whose control-experiment
list is exactly `[62:64, 66, 68, 70]` (6 subjects).

## 2. What is in this delivery

`data` in each `H###.mat` is a `1 × nTrials` MATLAB struct array — **one entry per trial**, 14 fields.
Converted to Parquet, one row per trial, sharded by rat.

| Shard | Trials | Sessions | Parquet bytes | Uncompressed |
|---|---|---|---|---|
| H037 | 92,468 | 252 | 19,455,224 | 25,506,828 |
| H066 | 185,091 | 308 | 36,631,399 | 49,187,241 |
| H084 | 121,276 | 249 | 24,239,574 | 32,215,212 |
| H129 | 63,494 | 118 | 13,567,175 | 17,504,842 |
| H191 | 78,300 | 189 | 16,423,187 | 21,534,336 |
| **all5rats (combined)** | **540,629** | **1,116** | **104,820,115** | **149,715,322** |

**Spec compliance:** T3's cap is ≤500 MB uncompressed per shard (preferred 250–400 MB). The *entire*
Figshare behaviour corpus is **149.7 MB uncompressed**, so the combined single file already sits well
inside the cap — it is below the preferred band only because the corpus is smaller than that band.
Per-rat shards are provided as well.

### Parquet schema (19 columns)

| Column | Type | From MATLAB field | Meaning |
|---|---|---|---|
| `rat_id` | string | filename | H037 / H066 / H084 / H129 / H191 |
| `trial_idx` | int32 | position | zero-based index within rat |
| `sessid` | int32 | `sessid` | session identifier |
| `sessiondate` | string | `sessiondate` | YYYY-MM-DD |
| `T` | float32 | `T` | trial / stimulus duration (s) |
| `leftbups` | list\<float32\> | `leftbups` | left click times (s, rel. stimulus onset) |
| `rightbups` | list\<float32\> | `rightbups` | right click times (s) |
| `n_clicks_L` / `n_clicks_R` | int16 | derived | click counts |
| `Delta` | int16 | `Delta` | |
| `hit` | int8 | `hit` | rewarded outcome |
| `gamma` | float32 | `gamma` | difficulty parameter |
| `pokedR` | int8 | `pokedR` | 1 = went right |
| `Hazard` | int8 | `Hazard` | state-switch hazard rate |
| `genEndState` | int8 | `genEndState` | generative state at trial end |
| `genSwitchTimes` | list\<float32\> | `genSwitchTimes` | **state-switch times (s)** |
| `n_switches` | int16 | derived | number of switches on the trial |
| `correctAnswer` | int8 | `correctAnswer` | |
| `evidenceRatio` | float32 | `evidenceRatio` | |

Also delivered: `fit_analytical_H###.mat` (8-parameter accumulation-model fits, param_names
`\lambda, \sigma_a, \sigma_s, \sigma_i, \phi, \tau, bias, lapse`, with `auto_se`, `hessian`, and a
per-trial posterior vector `pr` whose length equals that rat's trial count) and `group_analysis.mat`.
These are shipped as the original `.mat` — they are small and their struct layout is not tabular.

## 3. FILE FORMAT

**Every `.mat` in the Figshare archive is MATLAB 5.0 (v5/v6), NOT HDF5 v7.3.**
`scipy.io.loadmat` reads them. `h5py` does **not** — there is no `\x89HDF` signature at offset 512.

## 4. Verification

- Publisher MD5 for the source zip: `24445f41ec41a592bad63e3d53f66d5d` (Figshare `supplied_md5` == `computed_md5`).
- Never downloaded the 3.72 GB zip whole: read the zip **central directory** (830 entries, 111,186 B)
  by HTTP-206 range read, then range-read and inflated only the 11 needed members.
- **Every extracted member was CRC-32 verified against the zip central directory** and its
  uncompressed length checked. 11/11 passed.
- **Independent content check:** 540,629 trials / 5 rats = **108,126 trials per rat**, which reproduces
  the publisher's stated "an average of 108,126 trials" exactly.
- Read-back of the combined Parquet: 540,629 rows, 5 rats, 1,116 sessions, `pokedR` mean 0.4981
  (no side bias), accuracy 0.7590, `T` ∈ [0.151, 2.000] s, 67.00% of trials carry ≥1 state switch.

## 5. DEFERRED — Dryad `10.5061/dryad.02v6wwq6b` (58.24 GB)

**Not fetched. All documented routes are walled** — see `DRYAD_DEFERRED_MANIFEST.json` for exact URLs,
per-file byte counts and the publisher's own sha-256 digests.

| Route | Result |
|---|---|
| `/api/v2/files/<id>/download` | **HTTP 401** `{"error":"Unauthorized, must have current bearer token"}` |
| `/api/v2/versions/257980/download` | **HTTP 405** "The dataset is too large for zip file generation. Please download each file individually." |
| `/downloads/file_stream/<id>` | **HTTP 200 but not the file** — 4,340 B of **Anubis proof-of-work** HTML, `<title>Validating...</title>` |
| `/api/v2/datasets/<doi>/download` | **HTTP 401** |

The two routes contradict each other: the bulk route says fetch files individually, and the individual
route returns 401. Metadata endpoints are **not** walled, which is how the digests below were obtained.
No gate was bypassed. **A human must retrieve these through a browser session.**

| File | Bytes | sha-256 (publisher) |
|---|---|---|
| `preprocessedData.zip` | 6,344,650,009 | `5572f972a44efcd004186b06355b7571cbd2cf996cdf3a1e5cea393b887c9cb4` |
| `convGLM.zip` | 26,080,285,545 | `b46644595d199dce1d9c6e9c289af5bf109ae2662a558f89c7aa58a421ddbcd1` |
| `conventionalEEGAnalysis.zip` | 25,816,675,748 | `80f3938c96a98f8b4067e2a455996e439556bfde529cf602891fe4f10a318215` |
| `participantInfo.xlsx` | 10,952 | `429d8493076d719525736bddec56d4dd8a2e9b4f2e6f5197848180d226f360d6` |
| `README.md` | 12,091 | `c89d2a4e483ef431299a3822015690e4df6553b4d627083e62258cf9a219ee22` |

`behav_data_all_subjs_all3.mat` lives **inside** `preprocessedData.zip` (6.34 GB), under
`preprocessedData/behaviour/`. Its in-memory variable is `all_responses`, an N×12 double matrix; the
column meanings, read out of `read_in_behav_data_with_new_response_matrix.m`, are:
cols 1–7 from the per-block response matrix, **8** = trials in block, **9** = block, **10** = session,
**11** = subject *index* (`nS = max(all_responses(:,11))` ⇒ **28**), **12** = subject *ID*.
Companion variables saved alongside: `trigger_streams`, `stim_streams`, `mean_stim_streams`,
`mean_stim_streams_org`, `stim_streams_org`, `noise_streams`, `sample_rate` (and `vertical_stim_streams`
in the vertical-motion variant, which is saved under the **different** name `behav_data_all_subjs_allVertical`).
