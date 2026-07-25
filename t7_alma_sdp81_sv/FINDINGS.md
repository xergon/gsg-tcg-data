# SDP.81 SV — FINDINGS (read before computing)

`ADS/JAO.ALMA#2011.0.00016.SV` — enumerated 2026-07-25 from the ALMA Science Archive's own
TAP (`ivoa.obscore`), DataLink, and request-handler JSON. Nothing here is guessed.

---

## 1. THE IDENTIFIERS YOU ASKED FOR

There is exactly **ONE** Member OUS covering **all three bands**. This is unusual and it matters:
Bands 4, 6 and 7 are not separate MOUSs you can request independently.

```
PROJECT   2011.0.00016.SV
SGOUS     uid://A002/X8fa7af/X10
GOUS      uid://A002/X8fa7af/X11
MOUS      uid://A002/X8fa7af/X12          <-- the only MOUS; covers B4 + B6 + B7
SCHEDBLOCKS  SDP.81_B4 , SDP.81_B6 , SDP.81_B7
```

- `data_rights = Public`, `obs_release_date = 2016-06-24T14:02:08`, `calib_level = 2`.
- QA2 state of every raw EB tarball is **`ASDM_SEMIPASS`**, not full pass.
- Total published volume: **540.84 GiB** via the ASA package/ASDM route,
  **402.19 GiB** via the SV portal route (the two overlap heavily — see section 5).

### 32 execution blocks — Band 4 = 12, Band 6 = 9, Band 7 = 11

The EB->band assignment below is taken from the three official ALMA READMEs and cross-checked
against the 32 `.asdm.sdm.tar` names in the archive: the two sets match **exactly and bijectively**
(0 unmatched either way).

| Band | n EB | raw ASDM total | execution blocks |
|---|---|---|---|
| 4 | 12 | 137.97 GiB | X91068d/Xa1e, X91068d/Xc50, X91068d/Xead, X915f1c/X5d0, X924c91/X12c, X924c91/X34f, X924c91/X572, X924c91/X847, X924c91/Xa47, X93514d/X1634, X93514d/X1857, X93514d/Xfc6 |
| 6 | 9 | 59.20 GiB | X8fd70d/X1484, X8fd70d/X188b, X907514/X11d6, X915f1c/X8be, X916b15/X1716, X923b56/X43c, X923b56/X65f, X92c694/X1099, X92ec61/X1f23 |
| 7 | 11 | 107.37 GiB | X91dc9f/X2eb, X91dc9f/X517, X91dc9f/Xb6, X91f01f/X5e6, X91f01f/X812, X920302/X1059, X920302/X1336, X920302/X1562, X920302/Xe29, X925649/Xa99, X925649/Xcc5 |

(all prefixed `uid://A002/`). Per-EB byte counts and URLs are in `MANIFEST.tsv`.

**DO NOT enumerate the EBs from ObsCore.** `ivoa.obscore` exposes only **5** of the 32
`asdm_uid` values for this project. Querying obscore and concluding "5 execution blocks" is wrong
by a factor of 6. The authoritative enumeration is the request-handler tree
(`https://almascience.eso.org/rh/data/expand/uid___A002_X8fa7af_X12`) plus the READMEs.

### Calibrators present (from obscore `target_name`)
`J1058+0133`, `J0909+0121`, `J0854+2006`, `J0914+0245`, `J0750+1231`, `J0808-0751`, `J0825+0309`
— science target is `SDP.81`. Calibrator visibilities are **inside the same EB tarballs**, not
separate products; there is no `sdp81_calibrator_visibilities/` split published by ALMA. Splitting
target from calibrator is your step, after `scriptForCalibration.py`.

---

## 2. THE SPECTRAL WINDOW MAP (this is what defines your replication arms)

Recovered from the four official CASA imaging scripts, all four of which are included in
`scripts/imaging/`. Redshift is `z = 3.042` and is consistent to 4 decimal places across all
four lines.

| Band | Line | SPW | rest freq (GHz) | sky freq (GHz) | ALMA's own detection verdict |
|---|---|---|---|---|---|
| 4 | CO(5-4)   | `3,7,11,15,19,23,27,31,35,39,43,47` (4th spw of each of 12 EBs) | 576.26793 | 142.5700 | detection |
| 6 | CO(8-7)   | `2` | 921.79970 | 228.05534 | detection |
| 6 | H2O 2(0,2)-1(1,1) | `3,4` | 987.92676 | 244.415 | **weak detection** |
| 7 | CO(10-9)  | `3` | 1151.98544 | 285.00382 | detection |

Continuum: Band 4 spws `0~2,4~6,...,44~46`; Band 6 = `calavg` with the CO(8-7) channels flagged out
of spw 2 *inside each* `scriptForCalibration.py`; Band 7 = 4-spw `calavg`.

Channelisation as delivered: B6 CO(8-7) -> 128 ch x ~20.5 km/s. B6 H2O -> 960 ch x 2.5 km/s.
B7 CO(10-9) -> spw3 split, 960 ch.

### Two traps inside the SPW map

- **B6 H2O is not homogeneous across EBs.** SPW 3 in the **first 5** EBs has a different spectral
  resolution from SPW 4 in the **latter 4** EBs; ALMA resamples them with `width=[2,1]` to force a
  common 2.5 km/s grid. Any H2O-vs-CO differential inherits a resolution discontinuity that splits
  the Band 6 EB set 5/4. Treat "H2O arm" as two sub-arms unless you re-derive from raw.
- **B7 spw 3 channel 1 is flagged in the CONTINUUM `calavg` MS** (`flagdata(vis=...calavg, spw='3:1')`).
  ALMA's stated reason, verbatim: *230/240 channels in the parent datasets that contribute to this
  channel were flagged due to the presence of the CO 10-9 line*, and CASA 4.2.2 cannot produce
  channelized weights for a proper weighted sum. ALMA calls the sensitivity loss negligible. This is
  line contamination of the continuum, **not** corrupt data, and it does not affect the line MS.

---

## 3. THE UV-TAPER PROBLEM — THIS DIRECTLY CONFRONTS YOUR BRIEF

You specified **"no uv-taper, all baselines retained, uv <= 2Mlambda carried as a FLAG only, not a cut."**

**Every published SDP.81 reference LINE image violates that**, and by more than you assumed:

```
clean(..., uvtaper=True, outertaper=['1000klambda'], weighting='briggs', robust=1.0)
```

`1000 klambda = 1 Mlambda` — **half** the 2 Mlambda you were treating as the outer flag. Applied to
CO(5-4), CO(8-7), H2O, CO(10-9) and the B6+7 combined continuum alike. All three READMEs state
flatly: *"It was necessary to uv-taper the spectral line data."*

This is **not** a property of the uv data. The taper is applied at imaging time. The calibrated
visibilities retain all baselines, so your untapered requirement is satisfiable — but you must
re-image, and you should read ALMA's "necessary" as a measured statement that untapered line SNR
is inadequate.

### Resolutions actually achieved — against your 2.0 mas kill threshold

| Band | continuum beam | line beam |
|---|---|---|
| 4 | 60 x 54 mas | up to ~169-170 mas |
| 6 | 39 x 30 mas | up to ~169-170 mas |
| 7 | 31 x 23 mas | up to ~169-170 mas |

Your kill is `D_coherent,95% < 2.0 mas => abandon`. The **line** beam is ~85x that threshold; the
best **continuum** beam (B7, 31x23 mas) is ~12x. Centroid precision goes as beam/(2*SNR), so 2 mas
off a 170 mas line beam demands per-tracer positional SNR >~ 40 *in the differential*. Continuum
imaging cells are `0.005"` = 5 mas (B6/B7) and `0.01"` = 10 mas (B4); **line** imaging cells are
`0.02"` = 20 mas. A 2.0 mas effect is a **sub-cell, sub-tenth-beam** measurement in every published
line product. Decide explicitly whether that is reachable before spending the pull.

### ONE EXCEPTION — Band 4 ships an UNTAPERED CO(5-4) cube

`SDP.81_Band4_Imaging.py` runs the line clean **twice**: once tapered, and once at
`imsize=1500, cell='0.01arcsec'` under the comment *"Imaging target - robust=1 weighting and no
uvtapering"*. Both cubes are in the Band 4 reference-image tarball:

- `SDP.81.Band4.CO_z3.042.fits`        <- **untapered**, 10 mas cells
  (produced with `interactive=True` and a hand-drawn `prior.mask` — it is not a blind product)
- `SDP.81.Band4.CO_smooth_z3.042.fits` <- tapered

Band 4 CO(5-4) is therefore the **only** arm where your no-taper condition is already met by an
official ALMA product, at 2x finer cells than any other line image.

---

## 4. THE ARM THAT KILLS YOUR STATED ADVERSARY

You wrote: *"calibration is the dominant adversary."* There is one arm where calibration
**cancels by construction**:

> **Band 6 CO(8-7) vs Band 6 H2O.** Same 9 execution blocks, same antennas, same weather, same
> bandpass/phase/flux calibrators, same `scriptForCalibration.py`, same CASA 4.2.2 run — two
> *different spectral windows of the same measurement set*: spw 2 vs spw 3/4.

A tracer-dependent deflection field surviving that comparison cannot be a calibration artefact,
because both tracers were calibrated by the identical solution. Cross-band comparisons
(B4 vs B6 vs B7) do **not** have this property: different EBs, different epochs, different
calibrators, separately derived solutions. ALMA published the two Band 6 tracers as separate
ready-made MSes, `SDP81_band6_9exec.ms.co87` and `SDP81_band6_9exec.ms.h2o`, both inside
`SDP81_Band6_CalibratedData.tgz`.

**Caveat that must be carried:** H2O is ALMA's own *"weak detection"*, and the 5/4 spectral-
resolution split of section 2 lands inside exactly this arm. The calibration-free comparison is the
strongest one available and is also the noisiest. That tension is the real state of the data.

---

## 5. ARCHIVE PACKAGING DEFECTS — MEASURED, NOT INFERRED

The ASA "download-all" package set (`2011.0.00016.SV_<date>_NNN_of_MMM.tar`) is **not** a faithful
copy of the SV portal. Verified by downloading the members and hashing them:

1. **Three members of the Band 7 group are byte-identical duplicates.**
   `2011-08-01_001_of_006`, `_004_of_006` and `_005_of_006` are each 1,721,222 bytes with
   md5 `6c552534ab37e193cf68999e05945994`, and each unpacks to the *same*
   `SDP81_Band6+7_ReferenceImages/` directory (3 FITS files).

2. **Consequently the ASA package set never delivers `SDP81_Band7_ReferenceImages.tgz`**
   (186,502,606 B — the CO(10-9) cube, its moment-0 and the Band 7 continuum image)
   **nor `SDP81_Band7_UncalibratedData.tgz`** (58,073,260,485 B). Anyone who pulls only the ASA
   packages silently ends up with **no Band 7 reference images at all**. Both files exist and are
   healthy on the SV portal. (Band 7 *raw* data is still reachable via the 11 per-EB
   `.asdm.sdm.tar` files, so raw coverage is complete — it is the packaged route that is broken.)

3. **Two package members are EMPTY.** `2011-06-01_005_of_005` and `2011-08-01_006_of_006` are
   10,240 bytes of **pure zero**, md5 `1276481102f218c981e0324180bafd9f`, which is exactly the md5
   of 10,240 NUL bytes — an empty tar with 0 entries, served as HTTP 200 with
   `Content-Type: application/tar`. Only Band 6's README survives packaging
   (`2011-07-01_005_of_005`); the Band 4 and Band 7 READMEs are the empty ones.

### The two routes are the SAME BYTES — verified

The ASA "package" members are the SV-portal files **renamed**, not repackaged. Proof: the SV portal's
`SDP81_Band6+7_ReferenceImages.tgz` and the ASA's `2011-08-01_001_of_006.tar` are both 1,721,222 bytes
with the identical md5 `6c552534ab37e193cf68999e05945994` — a gzip stream served under a `.tar` name.
So either route gives identical data, **except** for the Band 7 gap below. Full mapping:

| ASA package member | bytes | is actually |
|---|---|---|
| `2011-06-01_001_of_005` | 9,043,149,221 | `SDP81_Band4_CalibratedData.tgz` |
| `2011-06-01_002_of_005` | 17,910 | `SDP81_Band4_CalibrationScripts.tgz` |
| `2011-06-01_003_of_005` | 1,212,386,119 | `SDP81_Band4_ReferenceImages_z3.042.tgz` |
| `2011-06-01_004_of_005` | 77,538,234,020 | `SDP81_Band4_UncalibratedData.tgz` |
| `2011-06-01_005_of_005` | 10,240 | **EMPTY** (should hold `SDP81_Band4_Readme`) |
| `2011-07-01_001_of_005` | 44,965,898,587 | `SDP81_Band6_CalibratedData.tgz` |
| `2011-07-01_002_of_005` | 13,274 | `SDP81_Band6_CalibrationScripts.tgz` |
| `2011-07-01_003_of_005` | 386,715,687 | `SDP81_Band6_ReferenceImages.tgz` |
| `2011-07-01_004_of_005` | 34,501,182,039 | `SDP81_Band6_UncalibratedData.tgz` |
| `2011-07-01_005_of_005` | 10,240 | tar holding `SDP81_Band6_Readme` (the only README that survives) |
| `2011-08-01_001_of_006` | 1,721,222 | `SDP81_Band6+7_ReferenceImages.tgz` |
| `2011-08-01_002_of_006` | 86,078,616,365 | `SDP81_Band7_CalibratedData.tgz` |
| `2011-08-01_003_of_006` | 13,894 | `SDP81_Band7_CalibrationScripts.tgz` |
| `2011-08-01_004_of_006` | 1,721,222 | **duplicate** of `_001` |
| `2011-08-01_005_of_006` | 1,721,222 | **duplicate** of `_001` |
| `2011-08-01_006_of_006` | 10,240 | **EMPTY** (should hold `SDP81_Band7_Readme`) |

Never delivered by the ASA package route: `SDP81_Band7_ReferenceImages.tgz`,
`SDP81_Band7_UncalibratedData.tgz`, `SDP81_Band4_Readme`, `SDP81_Band7_Readme`.

**=> Use the SV portal URLs (the "SV PORTAL" section of `URLS.md`) as the entry point, not the ASA packages.**

### NO PUBLISHER CHECKSUM EXISTS
ALMA publishes **no** checksum for any of these 74 files. Not in DataLink (`content_qualifier` is
empty), not in the request-handler JSON, not in HTTP headers — there is no `Content-MD5` and no
`Digest`. The Apache `ETag` on the SV portal encodes inode/size/mtime, **not** content. The only
integrity gates available are byte count, gzip/tar magic, and re-download comparison. Every byte
count in `MANIFEST.tsv` was independently confirmed by HTTP HEAD (74/74, zero mismatches against
the archive's own declared sizes).

---

## 6. WHAT IS AND IS NOT RE-HOSTABLE

GitHub's release-asset cap is **2 GiB**. Measured against it:

- **Nothing in the uv-data path fits.** Smallest raw ASDM = 3.40 GiB (`X8fd70d/X188b`, Band 6).
  Smallest per-EB *calibrated* split MS = 6.16 GiB (`X8fd70d_X188b.ms.split.cal.tar`). Smallest
  whole-band calibrated bundle = 8.42 GiB (Band 4). Your requested ~1 GiB shards keyed by
  band/EB **do not exist upstream** and cannot be produced without downloading and re-splitting
  hundreds of GiB, which is deferred (section 7).
- **All four reference-image tarballs fit** (1.13 GiB, 369 MB, 178 MB, 1.6 MB) and are staged.
- Band 6 is the **only** band offering per-EB calibrated MSes individually
  (`SDP81Band6/extras/`, 9 files, 6.16-19.4 GiB). Bands 4 and 7 have **no** `extras/` directory
  (both return HTTP 404) — for those bands the calibrated data is only available as one
  monolithic 8.42 GiB / 80.2 GiB tarball.

---

## 7. REDUCTION PROVENANCE

CASA **4.2.2** for all calibration and imaging. Imaging scripts are *not* on the science portal;
they live on the CASA guide `ALMA2014_LBC_SVDATA` and are included here in `scripts/imaging/`.
All 32 `scriptForCalibration.py` are in `scripts/calibration/`.

Note on the Rybak et al. reduction you cited (20 s averaging, uv <= 2 Mlambda): that is **Rybak's own
re-reduction**, not ALMA's. ALMA's published products use `robust=1.0` Briggs and a 1 Mlambda outer
taper, with no 20 s time-average step in the delivered line MSes. The two reductions are not
interchangeable and their uv coverage differs by a factor of 2 in outer radius.

### Two documentation errors in ALMA's own READMEs (do not chase these filenames)
- Band 6 README lists `SDP81_band6_9exec.ms.calavg` in its file list but then calls it
  `SDP81_band6_11exec.ms.calavg` in the prose. Band 6 has **9** executions; "11exec" is a
  copy-paste from Band 7. The file is the `9exec` one.
- Band 4 README says *"SDP.81_Band4.ms is the spectrally averaged continuum dataset"*. The imaging
  script contradicts it: `SDP.81_Band4.ms` is the **full** dataset, and the continuum is split out
  of it into `SDP.81_Band4_continuum.ms` (with `SDP.81_Band4_COline.ms` for the line).
