# Calibration version and cadence-library identifier — VERBATIM, per survey

Source: `SNDATA_ROOT_2026-04-10.tar.gz`, Zenodo DOI `10.5281/zenodo.19503606`
(md5 `0ff9100985903edf13887123564e5ebb`, verified against publisher).
Every string below is copied verbatim from the shipped file named in each row.

> **Read this first.** SNDATA_ROOT ships **two different calibration vintages** for all three
> surveys: the *native* per-survey kcor set, and the *Pantheon "supercal"* re-calibration under
> `kcor/PS1/Pantheon/`. They use **byte-identical filter throughput curves** but **different
> AB zero-point offsets and a different primary-standard SED**. Mixing them is exactly the
> mislabelling risk flagged in the dispatch.

---

## 1. SNLS

### Calibration — NATIVE vintage
| field | verbatim value |
|---|---|
| kcor directory | `$SNDATA_ROOT/kcor/SNLS/SNLS_C11` |
| kcor input | `kcor_EFFMEGACAM_AB.input` |
| kcor output table | `kcor_EFFMEGACAM_AB.fits` |
| SN SED | `SN_SED: Hsiao07.dat` |
| mag system | `MAGSYSTEM: AB` / `FILTSYSTEM: COUNT` |
| filter path | `FILTPATH: SNLS3year/SNLS3-Megacam` |
| filters + AB offsets | `FILTER: SNLS-g effMEGACAM-g.dat   0.0`<br>`FILTER: SNLS-r effMEGACAM-r.dat   0.0`<br>`FILTER: SNLS-i effMEGACAM-i.dat   0.0`<br>`FILTER: SNLS-z effMEGACAM-z.dat   0.0` |
| lambda range | `LAMBDA_RANGE: 2100 11300` |
| redshift grid | `REDSHIFT_RANGE: 0.0 1.20` / `REDSHIFT_BINSIZE: 0.05` |
| dataset README pointer | `SNANA calib files in $SNDATA_ROOT/kcor/SNLS` |

A companion BD17-primary variant also ships: `kcor_EFFMEGACAM_BD17.input`.
An older 1st-year vintage exists at `kcor/SNLS/SNLS_A05/kcor_SNLS.input` (Astier 2006 era).

### Calibration — PANTHEON "supercal" vintage
| field | verbatim value |
|---|---|
| kcor input | `$SNDATA_ROOT/kcor/PS1/Pantheon/kcor_SNLS.input` |
| primary standard | `BD17_SED:    bd17_stisnic_005.dat` |
| filter path | `FILTPATH:   PS1/Pantheon/SNLS3-Megacam` |
| filters + AB offsets | `FILTER: SNLS-g effMEGACAM-g.dat -0.0067+ 0.0076605430`<br>`FILTER: SNLS-r effMEGACAM-r.dat -0.0081-0.0012669564`<br>`FILTER: SNLS-i effMEGACAM-i.dat -0.0073-0.0057157707`<br>`FILTER: SNLS-z effMEGACAM-z.dat -0.0078+0.0024809218` |
| extra key | `DUPLICATE_LAMSHIFT_GLOBAL: 10` |

**Verified by md5:** `effMEGACAM-{g,r,i,z}.dat` are **byte-identical** between
`filters/SNLS/SNLS_C11/SNLS3-Megacam/` and `filters/PS1/Pantheon/SNLS3-Megacam/`.
The entire native-vs-Pantheon calibration difference for SNLS is therefore carried by the
**zero-point offset strings above**, not by the passband shapes.

### Cadence library
| field | verbatim value |
|---|---|
| file | `$SNDATA_ROOT/simlib/SNLS/SNLS_3year.SIMLIB` (599,250 B) |
| header | `SURVEY: SNLS   FILTERS: griz   TELESCOPE: CFHT` |
| DOCUMENTATION PURPOSE | `SNLS cadence for SNANA simulation` |
| REF | `AUTHOR: Kessler et al. 2013` / `https://ui.adsabs.harvard.edu/abs/2013ApJ...764...48K` |
| VERSIONS | `DATE: Mar 3 2012` / `AUTHORS: R. Kessler` |
| NOTES | `includes each exposure; need to run co-add program` |
| flux-error term | `FLUXERR_ADD:  griz  0.22  0.30  1.08  1.62` |
| LIBID count | 4 (`SNLS_3year.SIMLIB`); co-added twin `SNLS_3year.SIMLIB.COADD` also 4 |
| 1st-year variant | `simlib/SNLS/SNLS_Ast06.SIMLIB.COADD`, `SURVEY: SNLS FILTERS: griz TELESCOPE: CFHT`, 69 LIBIDs, `AUTHORS: R. Kessler, N. Regnault`, `DATE: 2008-05` |

---

## 2. PS1 Medium Deep

### Calibration
| field | verbatim value |
|---|---|
| kcor input | `$SNDATA_ROOT/kcor/PS1/Pantheon/kcor_PS1_PS1MD.input` |
| kcor output table | `kcor_PS1_PS1MD.fits` |
| SN SED | `SN_SED:    Hsiao07.dat` |
| mag system | `MAGSYSTEM:  AB` / `FILTSYSTEM: COUNT` |
| filter path | `FILTPATH: PS1/Pantheon/PS1` |
| filters + AB offsets | `FILTER: PS1-g   g_filt_tonry.txt   -0.023-0.0037`<br>`FILTER: PS1-r   r_filt_tonry.txt   -0.033-0.0066`<br>`FILTER: PS1-i   i_filt_tonry.txt   -0.024-0.0043`<br>`FILTER: PS1-z   z_filt_tonry.txt   -0.024+.008`<br>`FILTER: PS1-y   y_filt_tonry.txt   0.0` |
| extra key | `DUPLICATE_LAMSHIFT_GLOBAL: 10` |
| lambda range | `LAMBDA_RANGE: 1800 13300` |
| redshift grid | `REDSHIFT_RANGE: 0.0 0.46` / `REDSHIFT_BINSIZE: 0.02` |
| earlier vintage | `$SNDATA_ROOT/kcor/PS1/PS1s_RS14/PS1_gkcor_none.input` → `kcor_PS1_none.fits` (Rest+2014 era) |

⚠ **The PS1 kcor input carries NO `BD17_SED:` line** — unlike the Pantheon SNLS and SDSS inputs,
which both declare `bd17_stisnic_005.dat`. The primary-standard declaration is therefore **not
uniform across the three surveys inside the same Pantheon calibration directory.**

### Cadence library
| field | verbatim value |
|---|---|
| file | `$SNDATA_ROOT/simlib/PS1/PS1MD_RS14.SIMLIB` (222,679 B) |
| header | `TELESCOPE: PS1` / `SURVEY: PS1MD    FILTERS: grizy` |
| DOCUMENTATION PURPOSE | `PS1 1.5-year cadence for SNANA simulation` |
| REF | `AUTHOR: Scolnic et al, 2014 (PS1 cosmology systematics)` / `https://ui.adsabs.harvard.edu/abs/2014ApJ...795...45S` |
| VERSIONS | `DATE:  2010-10` / `AUTHORS: D. Scolnic, S. Rodney` |
| NOTES | `includes seasons 2010 & half of 2011`<br>`includes all 10 PS1 Medium Deep (MD) fields`<br>`cadence info from OTISDB (internal to PS1)`<br>`Exposure times: g=8x113s; r=8x113s; i=8x240s;  z=8x240s; y=8x240s` |
| LIBID count | 5 |
| Pantheon-era variant | `simlib/PS1/Pantheon/PS1MD_FULL_fluxcorr.simlib` (292,228 B, 10 LIBIDs) |
| field definitions | `SURVEY.DEF`: `SURVEY:  PS1MD     15  # Pan-STARRS 1 Medium Deep Survey`, fields `MD00`…`MD10` |

⚠ **`PS1MD_RS14.SIMLIB` covers "seasons 2010 & half of 2011" only.** The Jones+2018 photometric
sample spans `PEAKMJD` 55083–56677 (≈ 2009-09 to 2014-01). **The shipped cadence library does not
span the shipped photometry.** `PS1MD_FULL_fluxcorr.simlib` is the fuller one (10 LIBIDs = the 10 MD fields).

---

## 3. SDSS-II SN

### Calibration — NATIVE vintage
| field | verbatim value |
|---|---|
| kcor directory | `$SNDATA_ROOT/kcor/SDSS/SDSS_Doi2010` |
| kcor input | `kcor_SDSS.input` → `OUTFILE:  kcor_SDSS_Bessell90_BD17.fits` |
| DOCUMENTATION PURPOSE | `Collect calibration info and make kcor tables for SDSS` |
| REF | `AUTHOR:  Kessler et al., 2009` / `https://ui.adsabs.harvard.edu/abs/2009ApJS..185...32K` |
| PRIMARY_REF | `AB for SDSS, BD17 for Bessell` |
| VALIDATE_SCIENCE | `used in SDSS 1st-year cosmology analyses` |
| NOTES | `add SURVEY keys (Apr 2022) so that snlc_fit.exe works with calib-shift keys` |
| SN SED | `SN_SED:    Hsiao07.dat` |
| primary standard | `BD17_SED:  bd_17d4708_stisnic_003.dat` |
| filter path | `FILTPATH:    $SNDATA_ROOT/filters/SDSS/SDSS_Doi2010/CCDAVG` |
| survey key | `SURVEY:  SDSS  # Apr 6 2022` |
| filters + AB offsets | `FILTER:  SDSS-u   u.dat   0.0`<br>`FILTER:  SDSS-g   g.dat   0.0`<br>`FILTER:  SDSS-r   r.dat   0.0`<br>`FILTER:  SDSS-i   i.dat   0.0`<br>`FILTER:  SDSS-z   z.dat   0.0`<br>`FILTER:  SDSS-U   U.dat   0.0     # overlap CCD1`<br>`FILTER:  SDSS-G   G.dat   0.0     # overlap CCD1`<br>`FILTER:  SDSS-R   R.dat   0.0     # overlap CCD1`<br>`FILTER:  SDSS-I   I.dat   0.0     # overlap CCD1`<br>`FILTER:  SDSS-Z   Z.dat   0.0     # overlap CCD1` |
| lambda range | `LAMBDA_RANGE: 2100 11300` |
| older vintage | `kcor/SDSS/SDSS_web2001/kcor_SDSS.input` |

### Calibration — PANTHEON "supercal" vintage
| field | verbatim value |
|---|---|
| kcor input | `$SNDATA_ROOT/kcor/PS1/Pantheon/kcor_SDSS.input` |
| primary standard | `BD17_SED:    bd17_stisnic_005.dat` |
| filter path | `FILTPATH:   PS1/Pantheon//SDSS_Doi2010/CCDAVG` (double slash is verbatim) |
| filters + AB offsets | `FILTER: SDSS-u U.dat 0.00000`<br>`FILTER: SDSS-g G.dat -0.0073-0.0029473880`<br>`FILTER: SDSS-r R.dat -0.0088+0.0044133478`<br>`FILTER: SDSS-i I.dat -0.0090+0.00072395845`<br>`FILTER: SDSS-z Z.dat -0.0094-0.0083579659` |

⚠ Note the two vintages differ in **primary standard** (`bd_17d4708_stisnic_003.dat` vs
`bd17_stisnic_005.dat`), in **zero-point offsets** (0.0 vs the strings above), and in **which
case of the filter file** the lowercase band is mapped to (`SDSS-u u.dat` vs `SDSS-u U.dat`).

### Cadence library
| field | verbatim value |
|---|---|
| file | `$SNDATA_ROOT/simlib/SDSS/SDSS_3year.SIMLIB` (18,307,866 B) |
| header | `SURVEY: SDSS     FILTERS: ugriz   TELESCOPE:  SDSS` / `NLIBID: 1998` |
| DOCUMENTATION PURPOSE | `SDSS 3-year cadence for SNANA simulation` |
| REF | `AUTHOR: Kessler et al. 2013` / `https://ui.adsabs.harvard.edu/abs/2013ApJ...764...48K` |
| VALIDATE_SCIENCE | `used in JLA & Pantheon cosmology analyses` |
| NOTES | `includes seasons 2005+2006+2007` |
| VERSIONS | `DATE:  2012-03-12` / `AUTHORS: R. Kessler`<br>`DATE: 2026-01-27` / `AUTHORS: C. Meldorf (Added NLIBID Key for batch mode.)` |
| LIBID count | 1,998 |
| per-season variants | `SDSS2005_ugriz.SIMLIB` (1,000 LIBIDs), `SDSS2006_ugriz.SIMLIB.gz`, `SDSS2007_ugriz_NO6930.SIMLIB.gz` |
| 2005 flux-error terms | `FLUXERR_ADD:  ugriz  28  10  15  23  60` with `COMMENT: Error correction needed to match SMP errors.` |
| flux-error model | `simlib/SDSS/SDSS_fluxErrModel.DAT` |
| field definitions | `SURVEY.DEF`: `SURVEY:  SDSS      1`, fields `82N  89  SDSS  # (Nine => North)` and `82S  86  SDSS  # (Six  => South)` |

⚠ **`SDSS_3year.SIMLIB` was regenerated on 2026-01-27** (NLIBID key added). This is the only one of
the six cadence libraries here with a 2026 modification. The change is documented as a batch-mode
key addition, not a cadence change, but the file bytes are not those used by JLA/Pantheon.

---

## Cross-survey summary — the one table i5 asked for

| survey | calibration version (native) | calibration version (Pantheon supercal) | cadence library identifier | LIBIDs |
|---|---|---|---|---|
| **SNLS** | `kcor/SNLS/SNLS_C11/kcor_EFFMEGACAM_AB.input`, AB offsets **all 0.0**, `FILTPATH: SNLS3year/SNLS3-Megacam` | `kcor/PS1/Pantheon/kcor_SNLS.input`, primary `bd17_stisnic_005.dat`, offsets `-0.0067+0.0076605430` … | `simlib/SNLS/SNLS_3year.SIMLIB`, `SURVEY: SNLS FILTERS: griz TELESCOPE: CFHT`, Kessler+2013, Mar 3 2012 | 4 |
| **PS1MD** | `kcor/PS1/PS1s_RS14/PS1_gkcor_none.input` (Rest+2014) | `kcor/PS1/Pantheon/kcor_PS1_PS1MD.input`, offsets `-0.023-0.0037` …, **no BD17_SED line** | `simlib/PS1/PS1MD_RS14.SIMLIB`, `SURVEY: PS1MD FILTERS: grizy`, Scolnic+2014, 2010-10 | 5 |
| **SDSS** | `kcor/SDSS/SDSS_Doi2010/kcor_SDSS.input`, primary `bd_17d4708_stisnic_003.dat`, offsets **all 0.0** | `kcor/PS1/Pantheon/kcor_SDSS.input`, primary `bd17_stisnic_005.dat`, offsets `-0.0073-0.0029473880` … | `simlib/SDSS/SDSS_3year.SIMLIB`, `SURVEY: SDSS FILTERS: ugriz TELESCOPE: SDSS`, Kessler+2013, 2012-03-12 (**regenerated 2026-01-27**) | 1,998 |

**The calibration genuinely differs between the three surveys and between the two vintages.**
It differs in the zero-point offset strings, in the primary-standard SED, and (SNLS only) in
whether the throughput is a single survey curve or a per-SN curve. It does **not** differ in the
MegaCam passband shapes between vintages — those are byte-identical.
