# S5 — Dryad `10.5061/dryad.4xgxd25rg` (China Space Station dual-species atom-interferometer WEP test)

Fetched and verified 2026-07-26 UTC. Delivered as **plain CSV and plain text only** (no parquet).
Total directory size ~5.2 MB; largest single file 1.47 MB.

## What this dataset actually is

| field | value |
|---|---|
| Title | *Data from: In-orbit test of the weak equivalence principle with atom interferometry* |
| Dryad DOI | `10.5061/dryad.4xgxd25rg` (published 2026-07-16, version 5) |
| Preprint | `arXiv:2603.22981` — **same paper**, "In-orbit Test of the Weak Equivalence Principle with Atom Interferometry", 2026-03-24 |
| Journal | Science (ISSN 1095-9203); manuscript number **aeh0529** |
| Licence | CC0-1.0 |
| Apparatus | Dual-species **⁸⁵Rb / ⁸⁷Rb** atom interferometer aboard the **China Space Station** |
| Headline result | test uncertainty 2.8×10⁻⁸ from 280 days; Eötvös parameter η = (−3.1 ± 4.6)×10⁻⁷ |

### ⚠ This is NOT the NASA Cold Atom Lab

The second companion identifier, `10.1038/s41467-026-75230-2`, is a **different experiment**:
Meister et al., *"Magnetometry with a space-based differential atom interferometer"*, Nature Communications,
published 2026-07-11. That is the CAL/ISS paper whose supplementary already lives in
`s5_cal_cuas_psi_v3/`. The Dryad record here is an **independent second space platform (CSS)** —
useful precisely because it is independent, but it must not be merged with CAL as if it were the same
instrument.

## 🔴 Structural findings — read before computing

1. **The Dryad README describes 24 files. The archive contains 13.** The README is a description of the
   *paper's figure panels*, not of the shipped archive. `DRYAD_README_verbatim.md` is included verbatim so
   the discrepancy is auditable.
2. **These requested files DO NOT EXIST in the archive**, under any name:
   `data_for_Figs3b.txt`, `data_for_Figs3c.txt`, `data_for_Figs3d.txt`, `data_for_Figs3e.txt`
   (the four per-configuration differential-phase distributions of Fig. S3b–e). Also absent: all Fig. S1,
   S4, S6 files, and all Fig. 6a–d simulation files. **The per-configuration Δφ histograms are not public.**
   The nearest available substitute is `data_for_Fig4a.csv`, which carries the four configurations'
   long-term *averaged* phases with errors (`pha1..pha4`), i.e. the summary of what Fig. S3b–e histogram.
3. **Filenames in the archive differ from the README's names.** Mapping is in the table below.
4. **`vval1.txt` is written in Mathematica scientific notation** (`9.039469629240084*^-6`, 1424 occurrences
   out of 50 845 tokens). `numpy.loadtxt` / `pandas.read_csv` **fail on the raw file**. The CSV in `csv/`
   has this normalised to standard `e` notation. Use the CSV, not the raw file, unless you handle `*^`.
5. **Fig. 3b has no `y₀` column and Fig. 4a has no date column**, contrary to the README. Fig. 3b ships 6
   columns (`phi1 phi1err phi2 phi2err phiave phiaveerr`), Fig. 4a ships 10 (`pha1..pha4` + errors +
   `phaave phaaveerr`). The abscissae of those two panels are not in the data.
6. **`pha1dif = (pha185 − pha187) mod 2π` to 1.1×10⁻¹⁴** — verified over all 3223 samples. `pha1dif` is the
   *wrapped* differential phase, so a naive `pha185 − pha187` differs from it by exactly 2π on some rows.
7. All files are CRLF-terminated; the last line carries no newline.

## File mapping and contents

| CSV in `csv/` | archive source | rows | cols | contents |
|---|---|---|---|---|
| `data_for_Fig2a_Rb87_PCA_2D.csv` | `data for Fig 2a-d/fri1.dat` | 52 | 1+52 | ⁸⁷Rb 2D PCA shearing-fringe map (52×52 grid, arb. units) |
| `data_for_Fig2b_Rb85_PCA_2D.csv` | `data for Fig 2a-d/fri2.dat` | 52 | 1+52 | ⁸⁵Rb 2D PCA shearing-fringe map |
| `data_for_Fig2c_Rb87_fringe_1D.csv` | `data for Fig 2a-d/cur1.txt` | 38 | 2 | ⁸⁷Rb 1D fringe (value only; no position column shipped) |
| `data_for_Fig2d_Rb85_fringe_1D.csv` | `data for Fig 2a-d/cur2.txt` | 43 | 2 | ⁸⁵Rb 1D fringe (value only) |
| `data_for_Fig2ef.csv` | `pha187.txt`, `pha185.txt`, `pha1dif.txt` | 3223 | 4 | `experiment_index, phi_Rb87_rad, phi_Rb85_rad, dphi_rad` |
| `data_for_Fig2g_accel_phase.csv` | `data for Fig 2g/vpha1.txt` | 5084 | 2 | acceleration-induced interference phase (rad) |
| `data_for_Fig2g_accel_raw.csv` | `data for Fig 2g/vval1.txt` | 50845 | 2 | raw residual acceleration a_z (m/s²) — notation normalised |
| `data_for_Fig3b.csv` | `data for Fig 3b/fig 3b.txt` | 11 | 6 | Δφ₁, Δφ₂, Δφ_avg with errors vs fitting-position offset (offset column absent) |
| `data_for_Fig3d.csv` | `data for Fig 3d/fig 3d.txt` | 11 | 4 | `zvelocity, phi(delta>0), phi(delta<0), phiave` — residual phase vs v_z0 |
| `data_for_Fig4a.csv` | `data for Fig 4a/data for fig 4a.txt` | 44 | 10 | four configurations' averaged Δφ + errors, and overall average (date column absent) |
| `data_for_Fig4b.csv` | `data for Fig 4b/data for Fig 4b.txt` | 10 | 3 | `time(day), Allandeviation, error` |

`raw_original/` holds the 13 archive files byte-for-byte (flattened names, `*^` notation untouched).
`data_for_aeh0529.zip` is the publisher's archive, **sha256 `42c2e2be…4973` — matches Dryad's published digest exactly.**
`MANIFEST.csv` lists every file with bytes, rows, columns and sha256.

## Provenance

- Public download route used: `https://datadryad.org/api/v2/versions/453064/download` (HTTP 200, `application/zip`, PK magic).
- ⚠ **Dryad's per-file routes are gated and return HTTP 200 shells.** `/api/v2/files/<id>/download` returns a
  56-byte `{"error":"Unauthorized…"}` with HTTP 401; `/downloads/file_stream/<id>` returns either a 118-byte
  AWS-ELB 403 page or a 4344-byte Anubis proof-of-work "Validating…" HTML page **with HTTP 200**. Neither was
  bypassed; the version-level bundle route is public and needs no credential.
- Both publisher SHA-256 digests (`data_for_aeh0529.zip`, `README.md`) reproduce exactly from the download.
