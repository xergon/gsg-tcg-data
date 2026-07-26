# SLD per-event table (1996-1997 mini-DSTs) — data dictionary

One row per event. 279,505 rows total, sharded across 21 CSV files, each < 900,000 bytes.
Source: `sld_minidsts_parquet_1996_1997.tar.gz` sha256 `de4b010a50b5d3a10680896cd6cba0286e1ddb350bdda505f747d92d15f70e10` (1,982,875,078 B), 28 parquet members.

## Files
- `sld_perevent_01.csv` … `sld_perevent_21.csv` — the data shards, identical header, concatenate in filename order to reconstruct the full table.
- `MANIFEST.csv` — shard, row_start, row_end (0-based, inclusive, over the concatenated table), rows, bytes, sha256.
- `FILES.csv` — file_id -> source parquet member filename.
- `SCHEMA.md` — this file.

## Columns
- `run` — SLD run number (from bank IEVENTH, field `run`).
- `event` — event number within run (IEVENTH.event).
- `evttype` — event type code (IEVENTH.evttype).
- `trigger` — trigger word (IEVENTH.trigger).
- `ecm` — centre-of-mass energy in GeV (PHBM.ecm, first PHBM entry), 4 dp.
- `pol` — signed electron beam longitudinal polarisation (PHBM.pol, first entry), 5 dp. THE SLD-UNIQUE HANDLE.
- `dpol` — uncertainty on `pol` (PHBM.dpol, first entry), 5 dp.
- `n_phchrg` — number of entries in bank PHCHRG (charged tracks).
- `n_phcrid` — number of entries in bank PHCRID (CRID particle ID). BLANK = bank absent for this row.
- `n_phkchrg` — entries in PHKCHRG (track-cluster matches).
- `n_phkelid` — entries in PHKELID (electron ID).
- `n_phklus` — entries in PHKLUS (calorimeter clusters).
- `n_phpoint` — entries in PHPOINT.
- `n_phpsum` — entries in PHPSUM.
- `n_phwic` — entries in PHWIC (warm iron calorimeter).
- `has_phcrid` — 1 if the source parquet member carries a PHCRID column at all, 0 if the whole member lacks it (9,994 rows, file_id 0). Distinguishes "no PID information recorded" from "empty bank".
- `file_id` — integer key into FILES.csv giving the source parquet member.

## Schema-variant note
Three parquet schema variants exist in the archive and columns were selected BY NAME, never by position:
24 members full; 3 members (36,996 rows) carry `PHCRID` in last position; 1 member (9,994 rows) has no `PHCRID` column at all.
A blank `n_*` cell means the bank was absent/null for that row; `0` means the bank was present and empty. These are different facts.
