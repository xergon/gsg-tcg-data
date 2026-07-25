# i5 — cross-survey replication package: SNLS · PS1 Medium Deep · SDSS-II SN

Extracted from **`SNDATA_ROOT for SNANA`**, Zenodo DOI **`10.5281/zenodo.19503606`**,
file `SNDATA_ROOT_2026-04-10.tar.gz`, **1,970,835,028 B**,
**md5 `0ff9100985903edf13887123564e5ebb` — matches the publisher's exactly**.
sha256 `d529d116386b7132e93c1ef6358e6bf4b13b78c1f8c042703b98ffc42a0c881f`. Magic bytes `1f8b` (real gzip).
Uncompressed: **13,404 files, 3,041,326,122 B**. Concept DOI `10.5281/zenodo.4001177`.
Fetched and verified 2026-07-25 (UTC).

---

## 1. THE NUMBER YOU ASKED FOR FIRST — per-survey recovered SN counts

| survey | dataset shipped in SNDATA_ROOT | light curves | epochs | with z | with peak epoch | with host logmass | with host surface brightness | epochs with PHOTFLAG | with SALT2 x1,c (JLA2014) | with SALT2 x1,c (Pantheon+) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **SNLS** | `SNLS3year_MEGACAM` (Guy+2010 / Conley+2011) | **281** | 23,837 | 281 | 281 | **0** | **0** | **0** | 239 | 160 |
| SNLS | `JLA2014_SNLS` (Betoule+2014 recal) | 239 | 21,206 | 239 | 239 | 0 | 0 | 0 | 239 | 160 |
| SNLS | `SNLS_Ast06` (Astier+2006, 1st year) | 71 | 2,983 | 71 | 71 | 0 | 0 | 0 | 58 | 36 |
| **PS1MD** | `PS1MD_Jones18` — **photometrically classified** | **1,169** | 434,024 | 1,169 | 1,169 | 1,158 | 1,166 | 434,024 | 0 | 253 |
| PS1MD | `Pantheon_PS1MD_FITS` — **spectroscopic** | 369 | 16,320 | 369 | 369 | 360 | 369 | 16,320 | 0 | 269 |
| **SDSS-II** | `SDSS_allCandidates+BOSS` (Sako+2018, SMPv8+BOSS) | **10,258** | 1,110,308 | 4,684 | 10,258 | 4,542 | 10,258 | 1,110,308 | 368 | 321 |
| SDSS-II | `SDSS_HOLTZ08` (Holtzman+2008) | 146 | — (not derived, see §5) | — | — | — | — | — | — | — |

Redshift ranges: SNLS 0.082–1.060 · PS1MD 0.026–0.941 · SDSS −0.004–6.47 (the SDSS upper tail is
AGN/SLSN in the all-transient table, not SNe).

**SDSS-II is an ALL-TRANSIENT table, not an SN Ia sample.** Type breakdown of the 10,258
(`counts/SDSS_SNTYPE_BREAKDOWN.csv`):

| subset | SNTYPE | n |
|---|---|---:|
| spectroscopically confirmed SNIa | 118 + 120 | **499** |
| SNIa? | 119 | 41 |
| photometric SNIa with host spec-z (zSNIa) | 106 | 824 |
| photometric SNIa with photo-z (pSNIa) | 103 | 624 |
| everything else (Variable 3,225 · Unknown 2,009 · AGN 906 · pSNII 1,628 · …) | — | 8,270 |

### The go/no-go number for a cross-survey replication with SALT2 shape/colour

| join | SNLS | SDSS-II | PS1MD | **total** |
|---|---:|---:|---:|---:|
| **homogeneous** — Pantheon+ (Brout+2022) params for all three | 160 | 321 | 269 | **750** |
| **maximal** — JLA2014 for SNLS+SDSS, Pantheon+ for PS1MD | 239 | 368 | 269 | **876** |

Photometry alone (no x1/c required): **281 + 499 + 369 = 1,149** spectroscopically confirmed SNe Ia
across the three surveys, or **281 + 1,988 + 1,169 = 3,438** if photometric SN Ia classifications
are admitted.

---

## 2. 🔴 STRUCTURAL FACTS THAT CHANGE WHAT YOU CAN COMPUTE

**(a) SNDATA_ROOT contains NO SALT2 `x1` / `c` for any of the three surveys.**
`x1` and `c` are light-curve *fit outputs*; SNANA HEAD tables carry none. The only `.FITRES`
files in the entire 13,404-file archive are `lcmerge/CFA3_4SHOOTER2/CFA3_4SHOOTER2.FITRES`,
`lcmerge/CFA3_KEPLERCAM/CFA3_KEPLERCAM.FITRES` and a DES template — **none for SNLS, PS1MD or
SDSS**. They are supplied here from two external public tables (§4); nothing else in SNDATA_ROOT
can give them to you.

**(b) SNLS has NO host mass, NO host surface brightness and NO PHOTFLAG — at all.**
`SNLS3year_MEGACAM` ships SNANA TERSE text with
`VARLIST: MJD FLT FIELD FLUXCAL FLUXCALERR SNR MAG MAGERR Zpt`. There is no photometry-flag
column and no host block in the header. **Four of your twelve retained columns are structurally
absent for one of your three surveys.** Host mass can be recovered for 239/281 via JLA `logMst`
or 160/281 via Pantheon+ `HOST_LOGMASS`; **host surface brightness and per-epoch photometry flags
cannot be recovered for SNLS from any file in this archive.** If the estimator needs either, SNLS
is not a valid third leg and the replication is effectively PS1MD-vs-SDSS.

**(c) The PS1 sample shipped as "PS1MD" is the PHOTOMETRIC one.**
`PS1MD_Jones18` has `SNTYPE == 0` and `REDSHIFT_QUALITYFLAG == 0` for **all 1,169** rows — these
are photometrically classified SNe Ia (Jones+2018), not spectroscopic. The spectroscopic PS1 set
is the separate `Pantheon_PS1MD_FITS` (369 rows: 337 `SNTYPE==1`, 31 `SNTYPE==0`, 1 `SNTYPE==2`;
its README states **"280 remain after cuts"**). Which one you use changes the sample by 3×.

**(d) The two PS1 datasets use DIFFERENT, NON-OVERLAPPING SNID NAMESPACES.**
`PS1MD_Jones18` uses `PSc000006` / `PS0909006`; `Pantheon_PS1MD_FITS` and `Pantheon+SH0ES.dat`
use bare integers (`6`, `000006`, `370356`). **A naive join returns exactly 0 matches.** Strip the
`PSc` prefix and zero-pad and you get 281 (Jones18 ∩ Pantheon-spec) and 253 (Jones18 ∩ Pantheon+).
1,165 of 1,169 are `PSc…`; the remaining 4 are `PS0909…`/`PS0910…` in a third scheme.
`crosswalk/SNID_CROSSWALK_saltparams.csv` does this for you.

**(e) SDSS and PS1MD SNIDs are both bare integers and COLLIDE.** Two SDSS SNIDs match Pantheon+
PS1MD CIDs by value. **Always join on `(survey, SNID)`, never on `SNID` alone.**

**(f) `HOSTGAL_SPECZ` is 0 for every row in both FITS HEAD tables.** The spectroscopic redshift
you want is in `REDSHIFT_HELIO` / `REDSHIFT_FINAL`. Do not read `HOSTGAL_SPECZ` as "no spec-z".

**(g) Only 4,684 of the 10,258 SDSS rows have any redshift at all** (`REDSHIFT_FINAL > -8`).
The other 5,574 are `-9`. `PEAKMJD` is populated for all 10,258, so a peak-epoch cut will *not*
filter them out.

**(h) The shipped SDSS SNTYPE counts DIFFER from the Sako+2014 Table 3 reproduced in the
dataset's own README.** README says SNIa 500 / SNIa? 36 / zSNIa 907 / pSNIa 677; the actual FITS
gives **499 / 41 / 824 / 624**, with `Unknown` up from 1,584 to 2,009. Both sum to 10,258. The
README table is the paper's, the FITS is what you will actually compute on. Use the FITS.

**(i) 🔴 EXTRACTING THIS TARBALL ON macOS OR WINDOWS SILENTLY DESTROYS 25 SDSS FILTER CURVES.**
The archive ships case-pairs (`u.dat` **and** `U.dat`, …) for the SDSS passbands — 44 colliding
groups, 88 files. On a case-insensitive filesystem `tar x` overwrites one member of each pair with
no error. **25 of the 44 pairs have genuinely different content** (all the per-CCD sets,
`SDSS_Doi2010/CCD1`…`CCD6`); the 19 `CCDAVG` pairs are byte-identical, so the survey-average
throughput is safe but every per-CCD curve is not. `kcor_SDSS.input` declares `SDSS-u u.dat` and
`SDSS-U U.dat` as *distinct filters*, so this is real. **This package ships them case-safe** under
`filters/SDSS_Doi2010_CASESAFE/` with the uppercase member renamed `UPPER_<B>.dat`.

**(j) SNLS filter throughputs are PER-SUPERNOVA, not one curve per band.**
`filters/SNLS/SNLS_C11/SNLS3-Megacam/` contains **285 entries**, of which ~281 are per-SN
directories `filters-<SNID>/` each holding its own effective MegaCam g/r/i/z transmission
(MegaCam response is focal-plane-position dependent). PS1 and SDSS ship one curve per band.
**A cross-survey systematic that assumes one passband per survey is wrong for SNLS.**

**(k) The PS1 cadence library does not span the PS1 photometry.**
`PS1MD_RS14.SIMLIB` documents `includes seasons 2010 & half of 2011`, but `PS1MD_Jones18`
`PEAKMJD` runs 55,083–56,677 (≈2009-09 → 2014-01). Use `simlib/PS1/Pantheon/PS1MD_FULL_fluxcorr.simlib`
if the cadence must cover the sample.

**(l) `SDSS_3year.SIMLIB` was regenerated 2026-01-27** (`AUTHORS: C. Meldorf (Added NLIBID Key for
batch mode.)`). Documented as a key addition, not a cadence change — but the bytes are not those
used by JLA/Pantheon. Same class as the DES HEAD-regenerated-while-PHOT-stayed-identical finding.

**(m) 🔴 `lcparam_full_long.txt` from `dscolnic/Pantheon` is a TRAP — do not use it for x1/c.**
Its header names `x1 dx1 color dcolor 3rdvar d3rdvar … set ra dec`, but **every one of those
columns is exactly 0.0 in all 1,048 rows.** Only `zcmb zhel mb dmb` are populated. It is not
shipped here. The two tables in `salt2_lcparams/` are verified populated.

---

## 3. WHAT IS IN THIS DIRECTORY

```
README.md                        this file
SUMMARY.json                     machine-readable summary + checksums
CALIBRATION_AND_CADENCE.md       VERBATIM calibration versions and cadence-library identifiers
MANIFEST_SNDATA_ROOT.tsv.gz      all 13,404 archive members: bytes + path
counts/PER_SURVEY_COUNTS.csv     the table in §1
counts/SDSS_SNTYPE_BREAKDOWN.csv
counts/SDSS_SNIa_SUBSETS.json
derived/<tag>_HEAD.csv.gz        one row per SN
derived/<tag>_PHOT.csv.gz        one row per epoch
crosswalk/SNID_CROSSWALK_saltparams.csv   SNID ↔ join_key ↔ JLA/Pantheon+ x1,c,mass
crosswalk/SALT2_COVERAGE_BY_DATASET.csv
salt2_lcparams/                  external SALT2 fit parameters (§4)
filters/                         throughput curves (§3.2)
kcor_inputs/                     calibration .input files, copied verbatim
cadence_headers/                 first 40 lines of each SIMLIB
```

### 3.1 Column mapping to your request

| you asked for | HEAD/PHOT column | present for |
|---|---|---|
| survey | `survey` | all |
| SNID | `SNID` | all |
| MJD | PHOT `MJD` | all |
| band | PHOT `band` | all |
| flux, flux error | PHOT `FLUXCAL`, `FLUXCALERR` | all |
| photometry flags | PHOT `PHOTFLAG` (+`PHOTPROB`) | PS1MD, SDSS only — **absent for SNLS** |
| spectroscopic redshift | HEAD `REDSHIFT_HELIO`, `REDSHIFT_FINAL` (+errors) | all (`HOSTGAL_SPECZ` is 0 everywhere) |
| peak epoch | HEAD `PEAKMJD` | all |
| SALT `x1`, `c` | **not in SNDATA_ROOT** → `salt2_lcparams/` + `crosswalk/` | 750–876 of them |
| host mass | HEAD `HOSTGAL_LOGMASS` | PS1MD, SDSS — **absent for SNLS**, recoverable via crosswalk |
| host surface brightness | HEAD `HOSTGAL_SB_FLUXCAL_<band>` | PS1MD (griz), SDSS (ugriz + UGRIZ) — **absent for SNLS** |

SNLS PHOT additionally carries `SNR` and `ZEROPT`; SDSS/PS1MD PHOT carry `ZEROPT`, `ZEROPT_ERR`,
`MAG`, `MAGERR`, `FIELD`, `TELESCOPE`/`CCDNUM`.

⚠ **Read `SNID` as a string.** `PS1MD,000006,…` is written verbatim in the CSVs, but
`pd.read_csv` will silently turn it into `6`. Use `dtype={'SNID': str}`.

### 3.2 Filter throughputs shipped
`filters/SNLS_MEGACAM_C11/` (survey-level effMEGACAM g,r,i,z + `-wpsf` variant, `FILTER.INFO`) ·
`filters/SNLS_MEGACAM_Pantheon/` (same curves, Pantheon path) ·
`filters/SNLS_MEGACAM_C11_perSN/` (**285 per-SN directories**) ·
`filters/PS1_Pantheon/` (`{g,r,i,z,y}_filt_tonry.txt`) · `filters/PS1_RS14/` ·
`filters/SDSS_Doi2010_CASESAFE/` (CCDAVG + CCD1–CCD6, both letter cases preserved, `ZPOFF.DAT`).

**Verified by md5: `effMEGACAM-{g,r,i,z}.dat` are byte-identical between the C11 and Pantheon
vintages.** The whole native-vs-Pantheon calibration difference for SNLS is in the zero-point
offsets, not the passband shapes. See `CALIBRATION_AND_CADENCE.md`.

---

## 4. SALT2 x1 / c — sourced externally, since SNDATA_ROOT has none

**`salt2_lcparams/JLA2014_tablef3_SNLS_SDSS.csv`** — Betoule et al. 2014 (JLA), CDS
`J/A+A/568/A22`, `tablef3.dat` (143,560 B, HTTP 200, parsed on the published byte-by-byte ReadMe).
740 SNe total → **239 SNLS + 374 SDSS** shipped here. Columns `x1, e_x1, c, e_c, logMst, e_logMst,
tmax, e_tmax, mb, e_mb, cov_*`. All 740 rows have non-zero x1, c and logMst.
⚠ The ReadMe states `e_mb` **"includes contributions from redshift uncertainties, intrinsic SNe
dispersion and lensing"**, and `mb` is **already bias-corrected** (`bias` column). This is the same
class of quantity as the `LENSDMU` you ruled out on the DES side — **`e_mb` and `mb` are flagged,
not dropped**, because unlike LENSDMU they are not separable from the published table. `x1`, `c`,
`logMst` and `tmax` are unaffected.

**`salt2_lcparams/PantheonPlus_lcparams_SNLS_SDSS_PS1MD.csv`** — Brout et al. 2022,
`PantheonPlusSH0ES/DataRelease` → `Pantheon+SH0ES.dat` (579,283 B, HTTP 200), 1,701 rows →
**160 SNLS (IDSURVEY 4) + 321 SDSS (1) + 269 PS1MD (15)**. Columns kept: `c, cERR, x1, x1ERR,
mB, mBERR, x0, x0ERR, COV_*, HOST_LOGMASS, HOST_LOGMASS_ERR, PKMJD, PKMJDERR, zCMB, zHEL, VPEC,
MWEBV, NDOF, FITCHI2, FITPROB, RA, DEC, HOST_*`.
🔴 **Cosmology- and distance-derived columns were DROPPED, not shipped**, on the same principle as
your DES `4_DISTANCES_COVMAT` / `5_COSMOLOGY` exclusion:
`MU_SH0ES, MU_SH0ES_ERR_DIAG, CEPH_DIST, IS_CALIBRATOR, USED_IN_SH0ES_HF, m_b_corr,
m_b_corr_err_DIAG, m_b_corr_err_RAW, m_b_corr_err_VPEC, biasCor_m_b, biasCorErr_m_b,
biasCor_m_b_COVSCALE, biasCor_m_b_COVADD, zHD, zHDERR`.
No `LENSDMU`-equivalent column exists in either table; none was reintroduced.

⚠ These two tables are **different SALT2 trainings and different calibrations** (JLA/B14 vs
Pantheon+ B21 + Fragilistic supercal). Do not pool them into one x1/c column — pick one, or use
both as a systematic.

---

## 5. WHAT WAS DEFERRED, AND WHY

- **`SDSS_HOLTZ08` (146 SNe) — native files shipped in the release tarball, no derived CSV.**
  It uses SNANA's *verbose multi-band SDSS epoch* format (`EPOCH:` blocks with parallel `ugriz`
  rows), not the TERSE `OBS:` format, so it needs a separate parser. It is superseded in coverage
  by `SDSS_allCandidates+BOSS` (SMPv8 recalibration of the same Holtzman photometry, 2005–2007
  rather than 2005 only). Stated rather than silently omitted.
- **The rest of SNDATA_ROOT is not re-hosted** — 3.04 GB, 13,404 files. The full manifest with
  byte counts is `MANIFEST_SNDATA_ROOT.tsv.gz`; anything in it is one Zenodo fetch away.
  Not re-hosted: `models/` (1.22 GB), `MWDUST/` (320 MB), `snsed/` (58 MB), all non-target surveys
  (DES-SN3YR/5YR, CSPDR2/3, CFA3, LOWZ_JRK07, Pantheon LOWZ/HST, SALT3TRAIN_K21, Foundation),
  and the SDSS `.HOSTLIB` / `SIM/` trees.
- **Not attempted:** running SNANA light-curve fits to produce our own x1/c. That is a fit, not a
  fetch, and it belongs in your sandbox with the shipped kcor + filter files if you want it.
