# IceTracks-DR2 IRFs — what exists, what it covers, and where it breaks

Source: **IceCube Second Track Data Release (IceTracks-DR2), doi:10.7910/DVN/MMIIZA**, version 1.0
(RELEASED), publisher readme last updated **13 March 2026**. Publisher record: **41 files,
2,612,528,359 bytes**. Our full mirror (published earlier, re-verified live 2026-07-25) is
**116,163,148 bytes / 44 zip members / 2,609,179,705 bytes uncompressed**.

Everything below was measured from the files, not read off a description.

---

## The configuration ↔ season map (the answer to "which detector configurations, at what energies")

| IRF set | applies to event seasons | # seasons | simulated events behind the smearing matrix |
|---|---|---|---|
| **IC40** | IC40 | 1 | **621,843** |
| **IC59** | IC59 | 1 | (between the two extremes — readme gives only the endpoints) |
| **IC79** | IC79 | 1 | (as above) |
| **IC86** | IC86_I, II, III, IV, V, VI, VII, VIII, IX, X, XI | **11** | **12,097,409** |

> "Because the detector configuration have been unified for all IC86 seasons, the effective area for
> IC86 should be used for IC86-2011 through IC86-2021." — `DR2_readme.txt`

⇒ **14 event seasons, 4 IRF sets.** A `season` axis carries at most 4 distinct IRFs and 11 of the
14 seasons are degenerate. Per-season IRFs do not exist and cannot be synthesised from this release.

⇒ The **19× spread in MC statistics** (621,843 → 12,097,409) is the dominant systematic on any
per-configuration PSF-tail comparison. IC40 has cells where **no** simulated events survive: those
rows appear with all six bin edges equal to `0.000000`.

## Energy and declination coverage — measured

### Effective areas (`*_effectiveArea.tab`, 152 KB each, byte-identical to publisher)

Grid: **40 energy bins × 50 declination bins = 2000 rows**, log₁₀(E_ν/GeV) from **2.00 to 10.00**
in 0.20-wide bins, declination −90° to +90°.

| config | highest bin with A_eff > 0 | rows with A_eff > 0 | max A_eff (cm²) |
|---|---|---|---|
| IC40 | log₁₀E = 10.00 | 1531 / 2000 | 2.628e+08 |
| IC59 | log₁₀E = 9.00  | 1465 / 2000 | 1.678e+08 |
| IC79 | log₁₀E = 9.00  | 1497 / 2000 | 1.600e+08 |
| IC86 | log₁₀E = 8.80  | 1465 / 2000 | 1.945e+08 |

⚠ The readme states the effective areas were built from simulation spanning **100 GeV – 100 PeV**
(log₁₀E 2 → 8). The tables carry non-zero entries **above** log₁₀E = 8 in all four configs. Do not
treat A_eff above log₁₀E = 8 as validated.
⚠ Azimuthal effective areas are **not released** (~10% variation; matters only below 1 day).

### Smearing matrices (`*_smearing.csv`, 598,080,195 B each at the publisher)

Grid per configuration:
- **14 true-energy bins**, log₁₀(E_ν/GeV) **2.00 → 9.00**, 0.50 wide.
- **30 declination bins** (sin-uniform; edges in `smearing_declination_bins.csv`).
  🔴 **This is a different declination grid from the effective areas' 50 bins.** They do not nest.
- **8000 sub-bins per (E_ν, Dec_ν) cell** = 20 × 20 × 20 over
  (log₁₀E_reco, PSF[deg], AngErr[deg]).
- ⇒ 112,000 rows per declination bin, **3,360,000 rows per configuration**.

**Normalisation verified, not assumed:** in the NGC 1068 declination slice of IC40, the
`Fractional_Counts` column sums to **13.999999999** over the 14 energy bins — i.e. exactly **1.0000
per (E_ν, Dec_ν) cell**, as the readme specifies. Only **10.69%** of rows are non-zero.

🔴 **The (E_reco, PSF, AngErr) sub-grid edges differ from cell to cell.** The readme is explicit —
"bins are selected in each (E_nu, Dec_nu) bin independently" — and inspection confirms it: the
first IC86 cell spans PSF ∈ [10.52°, 11.87°] while its last spans PSF ∈ [90.50°, 138.47°].
**Reshaping these files into a rectangular 5-D array silently produces garbage.** Read them as a
row list keyed on the six edge columns.

🔴 `Fractional_Counts` is **a fraction of the parent cell's events, not a density**. Do not divide
by bin width before renormalising.

🔴 `AngErr` has a **hard floor at 0.20°** — the smallest lower edge in the matrices is
`1.999999881e-01`, and the readme applies the same floor to the released events. Deconvolved
structure below 0.2° is an artefact of that floor.

🔴 **`AngErr` is calibrated for an E⁻² flux** ("The errors are calibrated using simulated events so
that they provide correct coverage for an E^{-2} power law flux"). NGC 1068's own fitted spectrum
is γ = 3.4 ± 0.2, so at the source the released angular errors are **not** guaranteed-coverage.
The PSF axis of the smearing matrix (true neutrino-to-muon angle) is the way around this.

## 🔴 NGC 1068 sits 0.01° from a smearing-matrix declination bin edge

Declination bin 19 spans **[−1.432544°, 0.000000°]**; bin 20 spans **[0.000000°, +5.739170°]**.

- NGC 1068's catalogue position, Dec = **−0.01°** (arXiv:2510.13403 Table), falls in **bin 19**.
- The northern-sky hottest spot, Dec = **+0.02°** (same paper, Table 1), falls in **bin 20**.

**The source and its own hotspot land in different PSF cells.** Both bins are delivered here
(`*_decbin19.csv.gz` and `*_decbin20.csv.gz`) precisely so the sensitivity to that choice can be
tested rather than inherited. `source_to_smearing_decbin.csv` flags every source in the delivered
catalogues that sits within 0.25° of a bin edge.

## What is in this directory

- `IC{40,59,79,86}_effectiveArea.tab` — the four effective areas, complete, unmodified.
- `smearing_declination_bins.csv` — the 30 declination bins, identical across all four configs.
- `source_to_smearing_decbin.csv` — every source in the three delivered catalogues mapped to its
  smearing declination bin, with an edge warning.
- `smearing_dec_slices/IC*_smearing_decbin<NN>.csv.gz` — the complete smearing matrix restricted to
  one declination bin, per configuration. Each inflates to ~19.9 MB / 112,000 rows and carries the
  full 14 × 20 × 20 × 20 response for that band. These exist because the full matrices are 598 MB
  each (2.4 GB for the four) and cannot be held in a sandbox; a single band can.
