# S5 — CAL-CUAS (NASA PSI PSI-32) per-shot epoch index + Meister 2026 supplementary

Retrieved **2026-07-26T04:26:34Z** (TRUE UTC, `date -u`).

## 1. Is PSI V3 public? YES — no account, no registration, no access control

- DOI `10.60555/6cnc-re60` → HTTP 302 → `https://psi.nasa.gov/physci/repo/data/investigations/PSI-32`
- Investigation metadata (`PSI-32_investigation_metadata.json`, fetched anonymously):
  - `"accession": "PSI-32"`, `"title": "Cold Atom Lab - Consortium for Ultracold Atoms in Space"`,
    `"doi": "10.60555/6cnc-re60"`
  - **`"public": true`**, **`"restricted": false`**
  - `"licenseName": "Creative Commons Zero v1.0 Universal"` (CC0-1.0)
  - `"version": 4` is CURRENT; V3 is retrievable via `?version=3` and via the `/versions` delta endpoint.
  - `"totalFileSize": 326782385724` (326.8 GB at V4; **284.36 GB at V3**)
- Nature Communications data-availability statement (Meister et al. 2026,
  `10.1038/s41467-026-75230-2`, Nat. Commun. **17**, 6089, published 2026-07-11):
  *"All NASA CAL raw data used in this study is publicly available through the NASA Physical
  Sciences Informatics (PSI) website"* — reference 84 is exactly
  `Bigelow, N. P. & Williams, J. R., CAL-CUAS, NASA PSI Data Repository, Version 3,
  https://doi.org/10.60555/6cnc-re60 (2025)`.
- Every file downloaded here came back over anonymous HTTPS with **no credentials of any kind**.
  Nothing was bypassed; the repository simply is open.

**⇒ The 2026-07-03 park ("segment-level data not publicly recoverable via quick probe") is superseded.**

### Public API route (documented so anyone can re-fetch)

The PSI landing page is an Angular SPA (954-byte shell). Its public JSON backend is:

```
https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-32              # metadata (V4)
https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-32?version=3    # metadata (V3)
https://psi.nasa.gov/geode-py/ws/repo/investigations/PSI-32/versions     # 3.6 MB full per-version file deltas
https://psi.nasa.gov/geode-py/ws/studies/PSI-32/download?redirect=false&file=<FILENAME>
```

The last endpoint returns a **plain-text presigned `psi-curation-prod.s3.amazonaws.com` URL**
(no auth header required); `GET` that URL to obtain the bytes.

## 2. What is in PSI-32 V3 — the real manifest

`PSI-32_v3_manifest.csv` — **2249 rows, 284,357,827,141 bytes total**:

| kind | count | note |
|---|---|---|
| `.zip` | 1804 | L1 / raw per-run image archives, typically **240–260 MB each** |
| `.csv` | 444 | the per-shot index files (see §3) — **33.5 MB in total** |
| `.pdf` | 1 | Williams/Chiow/Yu/Müller NJP 18 (2016) |

Interferometry runs present by name (from the manifest): **112 `*MZI*` L1 zips** —
`DiffMZI` (differential), `SoloMZI`, `FullMZI` — spanning 2021-061 … 2023-121, with
`mf0` explicitly in the run name for the magnetically-insensitive campaigns
(e.g. `2022_194_220711_V40_3740426714_DiffMZI_mf0_30sep_T1p0ms_Phase_1_L1.zip`), and no `mf0`
tag on the mF = 2 campaigns (e.g. `2022_118_220427_V40_3733933153_DiffMZI_30sep_T1p0ms_Phase_1_L1.zip`).
Also 183 `AI_`/`DiffAI`/`PAI` run names.

⚠ The 240–260 MB L1 zips were **NOT** re-hosted here: 112 MZI zips alone are ~25 GB and the whole
V3 is 284 GB. They are individually fetchable from the download endpoint above using the
`file_name` column of `PSI-32_v3_manifest.csv`. Ask and a named subset will be pulled.

## 3. THE PER-SHOT EPOCH INDEX — `cal_cuas_v3_epoch_index.csv`

All **444** index CSVs were downloaded, opened and normalised into one table.

- **109,495 shot rows**, **2018-DOY297T19:06:47Z → 2023-DOY222T23:43:06.720Z**
- **846 distinct L1 run folders**
- 38,258,670 bytes plain / 4,392,526 bytes gzipped (`.csv.gz`)
- Columns: `day_key, schema_variant, time, utc_iso, tab_name, start, stop,
  image0..3_time, image0..3_name, image0..3_human_time, new_path, found`
- `utc_iso` was **added by us** — ISO-8601 UTC parsed from the archive's DOY `time` field.

### 🔴 Timestamp convention — VERIFIED, not assumed

The numeric `image*_time` / `start` / `stop` fields are **seconds since the LabVIEW epoch
1904-01-01T00:00:00 UTC**. Verified against the archive's own human-readable companion columns
on **42,227 independent pairs**: median deviation **0.0005 s**, maximum deviation **0.001 s**
(i.e. exactly the printing precision). Conversion:
`utc = 1904-01-01T00:00:00Z + image0_time seconds`.

### 🔴 FINDINGS — structural defects in the archive's own CSVs (read before computing)

1. **Four incompatible schemas, no version marker.** Of 444 files:
   - 229 files: **9 columns, some with NO header row at all** (4 files are entirely headerless)
   - 95 files: header declares **9** names but data rows have **10** fields (undeclared trailing `found`)
   - 118 files: **16** columns (4 images/shot — the differential-interferometer era)
   In the 9/10-column era the order is `…, image0_name, image1_name, image0_time, image1_time, …`
   whereas in the 16-column era it is `…, image0..3_time, image0..3_name, image0..3_human_time, …`
   — **names and times are swapped between eras.** A single `read_csv` across the set silently
   mixes filenames into time columns.
2. **17 files carry an 18-column header over 16-column data** (header declares `start, stop` which
   the rows do not contain). Naive header-based parsing misassigns every column in those files.
3. **685 header rows appear EMBEDDED mid-file, in 161 of the 444 files** — the files were appended
   across reprocessing passes. Any parse that only skips row 0 injects 685 literal `"time"` strings
   into the time column. All were stripped here.
4. **2 files (`2022_075`, `2022_076`) have a corrupted header row of 745 / 705 fields**
   (`image0_name,image1_name` repeated ~180×) over normal 10-field data rows.
5. **Duplicate filenames.** The V1 add-list has 4001 entries but only **2247 distinct
   `remote_path`s**: the same `*_tabs_to_pngs.csv` name is registered once per run subcategory
   (up to 20×), sometimes with **different byte sizes** (e.g. `2021_139_tabs_to_pngs.csv` at both
   84,548 B and 90,965 B). The `download?file=` endpoint takes only a bare filename and therefore
   resolves ONE variant. Our 444 downloads total **33,553,217 B** against a manifest sum of
   **36,275,648 B** for those names — the difference is exactly this variant ambiguity, not
   truncation. The full per-variant records (with distinct legacy `athena` ids) are in
   `PSI-32_investigation_metadata.json` / the `/versions` endpoint.
6. **The paper names no PSI filenames or run ids.** The Meister 2026 supplementary contains no
   run identifiers, so mapping paper campaigns → PSI runs must be done via the manifest's
   date/run-name encoding (`YYYY_DOY_YYMMDD_V##_<labviewtime>_<runname>_Phase_#_L1.zip`) joined
   on the epoch index. `cal_cuas_v3_run_summary.csv` gives `run_key, n_shots, utc_first, utc_last`
   for all 846 runs to make that join direct.

### Pre-cut subsets (same schema as the full index)

| file | rows | content |
|---|---|---|
| `cal_cuas_v3_mzi_shots.csv` | 2,306 | any `MZI` in `tab_name`/`new_path` |
| `cal_cuas_v3_diffmzi_shots.csv` | 1,615 | `DiffMZI` only |
| `cal_cuas_v3_atominterferometry_shots.csv` | 8,376 | `AI_` / `DiffAI` / `PAI` |
| `cal_cuas_v3_run_summary.csv` | 846 | per-run shot count + UTC first/last |
| `psi32_v3_raw_index_csvs.tar.gz` | 444 files | **unmodified** originals, for byte-level audit |

## 4. Meister et al. 2026 supplementary (Springer, public)

`springer_supplementary/`
- `41467_2026_75230_MOESM1_ESM.pdf` — 402,679 B, PDF 1.5 (Supplementary Information; **Supplementary
  Figure S2 = classical COM measurement of the residual trap frequency along the Bragg beam,
  ω_COM,z′ = 2π(0.965 ± 0.014) Hz**, angle α = (4.77 ± 0.04)°)
- `41467_2026_75230_MOESM2_ESM.pdf` — 489,855 B, PDF 1.6 (peer-review file)
- `41467_2026_75230_MOESM3_ESM.xlsx` — 89,321 B, Excel 2007+, **8 sheets**:
  `Figure 2, Figure 3, Figure 4, Figure 5, Supplementary Figure 1..4`

`source_data/` — every sheet extracted to CSV (`Supplementary_Figure_2.csv` = 43 rows × 21 cols).

## 5. Provenance

| item | value |
|---|---|
| DOI | `10.60555/6cnc-re60` |
| Accession | `PSI-32`, Version **3** (current on server is 4) |
| Repository | NASA Physical Sciences Informatics (PSI) Data Repository |
| Licence | CC0-1.0 |
| Paper | Meister et al., *Magnetometry with a space-based differential atom interferometer*, Nat. Commun. **17**, 6089 (2026), `10.1038/s41467-026-75230-2` |
| Retrieval time | **2026-07-26T04:26:34Z** |
| Verification | every file re-opened after download; 0/444 HTML shells or stubs; checksums in `CHECKSUMS.sha256` |

## 6. Not fetched (explicit)

- The **1804 L1/raw `.zip` archives (284 GB)**. Above GitHub's 2 GiB release-asset cap in aggregate
  and useless to a no-network sandbox. Manifest published instead — name a subset and it will be pulled.
- PSI-31 / PSI-33 / PSI-35 / PSI-36 (the `related_glds` siblings of PSI-32) were not enumerated.
