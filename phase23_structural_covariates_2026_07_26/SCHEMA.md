# Phase-23 external held-out sample — disk scale length `R_d` and central surface brightness `mu_0`

Fetched by Cat (orchestrator), TRUE UTC `2026-07-28T21:23:31Z` (`date -u`; the local clock is UTC+4
and was not used).

**This is a FETCH product. Nothing here was analysed, correlated, interpreted, fitted or estimated.**
Every number is a literal catalogue or published-text value, or an explicitly-labelled unit conversion
of one. No value was inferred, no colour transformation was applied, and no gap was filled.

Fills the `n = 0` gap in
`implementation_lanes/phase23_transfer_diagnostic_2026_07_26/` — that diagnostic has 16 external
galaxies (12 LITTLE THINGS + 4 THINGS) with `Rdisk_kpc` and `central_SB_disk_Lsun_pc2` empty for
every row.

---

## 🔴 THE THREE THINGS THAT WILL BITE YOU IF YOU IGNORE THEM

1. **`mu_0` IS DISTANCE-INDEPENDENT. `R_d` IN kpc IS NOT.** A surface brightness in mag/arcsec² needs
   no rescaling ever. An `R_d` in kpc is only valid at the distance its source assumed. Every row
   therefore carries **`Rd_arcsec`**, **`distance_assumed_Mpc`** and **`distance_diagnostic_Mpc`**.
   To move an `R_d` onto the diagnostic's own distance scale:
   `Rd_kpc_diag = Rd_arcsec * distance_diagnostic_Mpc / 206.264806`.

2. **THE BANDS ARE NOT INTERCHANGEABLE AND NO CONVERSION WAS APPLIED.** This table mixes **V**, **J**,
   **3.6 µm (IRAC, de Blok photometric scale)** and **3.6 µm AB (S4G)**. A V-band `mu_0` of 23.7 and a
   3.6 µm `mu_0` of 16.6 are not comparable numbers. **All 12 LITTLE THINGS rows are V (plus 4 extra J
   rows); all 4 THINGS rows are 3.6 µm.** Any statistic computed across the full n=16 therefore mixes
   two bands by construction. That is a property of the literature, not a defect of this fetch.

3. **THE `mu_0` CONVENTIONS DIFFER AND ARE RECORDED PER ROW** in `mu0_convention`:
   - Hunter & Elmegreen 2006: extrapolated central SB of the fitted exponential, **reddening-corrected**,
     **NOT inclination-corrected**.
   - de Blok+2008: extrapolated central SB, **NOT inclination-corrected** (stated explicitly in the paper).
   - S4G / Salo+2015: **corrected to FACE-ON**.
   ⇒ S4G and de Blok `mu_0` for the same galaxy are on **different conventions** and will not agree.

---

## Row model — LONG FORMAT, one row per (galaxy × source × component × band)

**38 rows, 16 distinct galaxies.** This is deliberately not one row per galaxy: several galaxies have
more than one published decomposition, and **no source was selected as "the" answer.** Choosing is a
downstream decision.

| column | meaning |
|---|---|
| `galaxy` | key matching `per_galaxy.csv` in the transfer diagnostic (verbatim) |
| `sample` | `little_things_12` or `things_4` |
| `source_id` | short source code (see table below) |
| `source_bibcode` | ADS bibcode |
| `source_table` | exact table / location the value was read from |
| `component` | which fitted component this row is (single disk, outer disk, inner component/bulge, …) |
| `band` | **load-bearing** — `V`, `J`, `3.6um_IRAC`, `3.6um_AB`, `3.6um_derived_stellar_surface_density` |
| `Rd_arcsec` | disk scale length in arcsec (distance-free) |
| `Rd_kpc` | disk scale length in kpc, **valid only at `distance_assumed_Mpc`** |
| `e_Rd_kpc` | published 1σ uncertainty, blank where the source publishes none |
| `Rd_kpc_provenance` | `as_published` or `converted_at_diagnostic_distance` |
| `mu0_mag_arcsec2` | central surface brightness |
| `e_mu0_mag_arcsec2` | published 1σ uncertainty, blank where none published |
| `mu0_convention` | extrapolated/observed, reddening-corrected?, inclination-corrected? |
| `distance_assumed_Mpc` | distance the SOURCE assumed (blank where the source is arcsec-native) |
| `distance_diagnostic_Mpc` | distance the transfer diagnostic uses |
| `status` | `FOUND`, `FOUND_Rd_only`, `NOT_AVAILABLE` |
| `notes` | per-row caveats |

### Which numbers were computed here, and how

Only unit conversions, all reversible, all labelled:
- `Rd_arcsec = Rd_kpc / distance_assumed_Mpc * 206.264806` — for Hunter+2012, Hunter & Elmegreen 2006,
  de Blok+2008, Leroy+2008 (all publish kpc).
- `Rd_kpc = Rd_arcsec * distance_diagnostic_Mpc / 206.264806` — for S4G only, which publishes arcsec and
  **no distance in table7**. These rows are flagged `converted_at_diagnostic_distance`.

Nothing else was calculated.

---

## Sources — what each one is, and what it does and does not carry

| `source_id` | reference | table | covers | band | carries |
|---|---|---|---|---|---|
| `Hunter2012_LT` | Hunter et al. 2012, AJ 144, 134 | VizieR `J/AJ/144/134` table1 | all 12 LITTLE THINGS | V | `Rd` + `e_Rd`, **no `mu_0`** |
| `HunterElmegreen2006` | Hunter & Elmegreen 2006, ApJS 162, 49 | VizieR `J/ApJS/162/49` table4 | all 12 LITTLE THINGS | V (+J for 4) | `RD1`,`e_RD1`,`mu1`,`e_mu1` |
| `deBlok2008` | de Blok et al. 2008, AJ 136, 2648 | **Sect. 7 running text** | NGC 3031, 3621, 4736 | 3.6 µm | `mu_0`,`h`, **no uncertainties** |
| `S4G_Salo2015` | Salo et al. 2015, ApJS 219, 4 | VizieR `J/ApJS/219/4` table7 | NGC 3031, 4736 | 3.6 µm AB | `hr3`,`mu03`, **no uncertainties** |
| `Leroy2008` | Leroy et al. 2008, AJ 136, 2782 | VizieR `J/AJ/136/2782` table4 | NGC 4736 only | Σ\* | `l*`, **different convention** |

### 🔴 `deBlok2008` is NOT a machine-readable table

de Blok+2008 has **no VizieR/CDS version** (`J/AJ/136/2648` returns 404). The `mu_0` and `h` values are
quoted **in the running prose of Section 7**, per galaxy, not in any table. They were read from the
arXiv `/e-print/` LaTeX source of `0810.2100` (`deblok_astroph.tex`), not from the rendered PDF and not
from the HTML. The exact sentences are quoted in `SOURCE_NOTES.md`.

### 🔴 `Leroy2008` `l*` is a DIFFERENT QUANTITY — do not pool it with the others

`l*` is fitted to the stellar **mass** surface density profile Σ\*, not to a surface-brightness profile.
It is shipped because it exists and is labelled, **not** because it is interchangeable with a photometric
`R_d`. It is the only row of its kind in the file.

### Assumed distances

- **LITTLE THINGS**: `Hunter2012_LT`'s assumed distance **equals the diagnostic's distance for all 12
  galaxies** (verified row by row: 3.6, 6.4, 3.5, 0.9, 1.1, 10.3, 3.6, 1.3, 9.3, 3.4, 4.9, 2.6 Mpc).
  No rescaling is needed for those rows. `HunterElmegreen2006` uses **older, different** distances
  (e.g. DDO 101 at 9.0 vs 6.4 Mpc; DDO 133 at 6.1 vs 3.5 Mpc) — those `Rd_kpc` values **must** be
  rescaled before use, or `Rd_arcsec` used instead.
- **THINGS**: `deBlok2008` adopts Walter+2008 distances (its Sect. 4: *"We adopt luminosities and
  distances as given in \[Walter+2008\]"*) = 9.2 / 3.6 / 6.6 / 4.7 Mpc, **identical to the diagnostic's**.
- **S4G table7 publishes no distance** — hence arcsec-native, hence the explicit conversion flag.

---

## ⚠ ONE INTERNAL INCONSISTENCY, FOUND AND NOT SMOOTHED OVER

Hunter+2012 states its `Rd` is measured from the Hunter & Elmegreen 2006 V-band images, so
`Rd(2012)` should equal `Rd(2006) × D(2012)/D(2006)` exactly. **It does, to ≤ 0.010 kpc, for 11 of the
12 galaxies.** The exception:

| galaxy | HE2006 `RD1` | HE2006 `D` | pure rescaling ⇒ | Hunter+2012 `Rd` | delta |
|---|---|---|---|---|---|
| **DDO 133** | 1.99 kpc | 6.1 Mpc | **1.142 kpc** | **1.24 kpc** | **+0.098 kpc** |

Both values are shipped as published. **Neither was corrected.** The discrepancy is either a refit or a
typo in one of the two papers; this fetch does not adjudicate it. DDO 133 is one of the galaxies whose
sign flips between the diagnostic's two M/L conventions (−6.469 → +2.212), so anything resting on it
should carry this flag.

---

## Per-galaxy result

### LITTLE THINGS (12/12 complete — `R_d` **and** `mu_0` for every galaxy)

`R_d`: Hunter+2012 (V, at the diagnostic's own distances) **and** Hunter & Elmegreen 2006 (V, at HE06
distances). `mu_0`: Hunter & Elmegreen 2006 (V, reddening-corrected, extrapolated).
Four galaxies (DDO 53, DDO 133, NGC 1569, NGC 3738, UGC 8508) additionally have a **J-band** row —
shipped labelled, **not** converted to V.

### THINGS (3/4 complete)

| galaxy | `R_d` | `mu_0` | sources |
|---|---|---|---|
| NGC 3031 | **FOUND** | **FOUND** | S4G outer disk (153.170″, 19.833 AB) + de Blok inner component (0.25 kpc, 12.2) |
| NGC 3621 | **FOUND** | **FOUND** | de Blok outer disk only (2.61 kpc, 16.6) — not in S4G |
| NGC 4736 | **FOUND** | **FOUND** | S4G **two** expdisks + de Blok inner & outer + Leroy `l*` — 5 rows, none selected |
| **NGC 925** | **NOT AVAILABLE** | **NOT AVAILABLE** | — see below |

### 🔴 NGC 925 — genuinely absent, with the reason each source fails

Not an unsearched gap. Six sources were checked and each fails for a stated, verifiable reason:

- **de Blok+2008** quotes no exponential parameters for NGC 925. Sect. 7 states the 3.6 µm profile is
  traced over the full extent of the HI disk and the galaxy *"shows no evidence for a bright central
  component"* — so no extrapolation fit was needed and none was published.
- **S4G / Salo+2015**: **zero** matches in table7. NGC 925 sits at galactic latitude ≈ −25° and fails
  S4G's |b| > 30° selection. **NGC 3621 is excluded for the same reason** — this is why S4G covers only
  2 of the 4 THINGS galaxies.
- **Leroy+2008** table4 contains only NGC 4736 of the four (23-galaxy sample).
- **Muñoz-Mateos+2007** (`J/ApJ/658/1006`) and **+2009** (`J/ApJ/703/1569`) publish azimuthally averaged
  *profiles* only — no exponential fit parameters in any table.
- **Hunter & Elmegreen 2006** is an Im/BCD/Sm sample; NGC 925 (SABd) is not in it.
- **Fisher & Drory 2008** (`J/AJ/136/773`) publishes bulge parameters only; its tables carry no disk `h`
  or `mu_0`.
- **HyperLEDA** was unreachable (**expired TLS certificate**, verified twice — this is a measured
  blocker, not an assumption). Independently, HyperLEDA publishes `mu25` — the mean surface brightness
  *inside the B = 25 mag/arcsec² isophote* — which is a **different quantity** from an extrapolated
  exponential `mu_0` and was deliberately **not** substituted for one.

**No value was invented for NGC 925 and no citation was fabricated.**

---

## Verification performed

- Every download was checked **by content**, not by HTTP status or byte count. **Three files returned
  HTTP 200 with a `404 Not Found` HTML shell** (`J/AJ/136/2782/table1.dat`, `J/ApJS/219/4/table7.dat`,
  and the un-gzipped S4G path) and were caught and replaced — the S4G table via its `.gz`, Leroy via the
  correct filename `table4.dat`. Any pipeline trusting size alone would have shipped 283-byte HTML.
- S4G field indexing was verified programmatically against the CDS byte-by-byte spec: **31 pipe-separated
  fields = 31 documented columns**, and `hr3`/`mu03` land on the documented `expdisk` slots.
- Hunter & Elmegreen table4 has **184 records for 143 galaxies**; the second line per galaxy is the
  **J band**, confirmed against ReadMe Note 1 and by duplicate-name detection. All 12 target galaxies
  were located; **0 missing**.
- The Hunter+2012 ↔ HE2006 distance-rescaling identity reproduces for **11/12** galaxies to ≤0.010 kpc
  (see the DDO 133 exception above).
- Row count asserted non-zero: **38 rows, 16 distinct galaxies, 15 with `R_d`, 15 with `mu_0`.**

## What was deliberately NOT done

No correlation, no interpretation, no ranking of covariates, no selection of a preferred source per
galaxy, no colour transformation between bands, no inclination correction applied or removed, and no
estimate substituted for a missing value.
