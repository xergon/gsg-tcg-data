# Brody Lab Poisson-Clicks parsed distillation

Per-trial parquet distillation of the Brody Lab Poisson-Clicks Task dataset (rats, 2009–2024).

**Source:** Zenodo record [13352119](https://zenodo.org/records/13352119) — "Brody Lab Poisson Clicks Task Dataset, Rats 2009-2024, Parsed" (515 `.mat` files, 8,104,686,746 bytes zipped, MD5 `9bac21f991137ead56a0bc83ae62c49c`).

**License:** CC-BY-4.0 (inherited from source).

## Scale

| Field | Value |
|---|---|
| Rats parsed | 515 (0 failed) |
| Total trials | 25,562,353 |
| Trials/rat (min / median / max) | 9,170 / 32,585 / 286,535 |
| Parquet size | 2,131,341,109 bytes (2.13 GB, zstd-9) |
| Parquet sha256 | `86b51a3e5747fd44ce2e02fd4178faf2acea4e393a9b50b1d3ec7b9c9520bd99` |
| Parse date (UTC) | 2026-07-24T17:07:12Z |

## Schema (one row per trial)

| Column | Type | Meaning |
|---|---|---|
| `rat_id` | string | Filename stem of the source `.mat` (e.g. `A059`) |
| `trial_idx` | int32 | Zero-based trial index within the rat |
| `n_clicks_L` | int16 | Number of left clicks (from source `parsed.nL`) |
| `n_clicks_R` | int16 | Number of right clicks (from source `parsed.nR`) |
| `click_times_L` | list<float32> | Left click times, seconds (from `parsed.bt.left`) |
| `click_times_R` | list<float32> | Right click times, seconds (from `parsed.bt.right`) |
| `choice_R` | int8 | Response: 0 = left, 1 = right (from `parsed.gr`) |
| `correct` | int8 | Rewarded outcome: 0 or 1 (from `parsed.hh`) |
| `stim_duration_s` | float32 | Stimulus duration, seconds (from `parsed.sd`) |
| `gamma` | float32 | Difficulty parameter (from `parsed.ga`) |
| `reward_rule` | int16 | Reward rule tag (from `parsed.rg`) |

Extracted from `ratdata.parsed[0,0]` (the non-frozen, actually-delivered sequence). Not extracted here: `parsed_frozen`, `task_type`, RNG seeds — pull from the source `.mat` if needed.

## Files

- `brody_poisson_clicks_trials.parquet` — the distillation (2.13 GB)
- `SUMMARY.json` — machine-readable summary
- `parse_log.txt` — per-rat progress log

## Provenance

Stream-parsed from the source zip via Python `zipfile` + `inflate64` (source uses DEFLATE64, method 9 — Python stdlib and macOS `unzip`/`bsdtar` do not decompress it). Zip was never fully extracted to disk. Full pipeline is deterministic given the same source and produces the same sha256.
