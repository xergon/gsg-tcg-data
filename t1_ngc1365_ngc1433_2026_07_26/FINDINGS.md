# T1 FETCH — NGC 1365 / NGC 1433 — measured findings, 2026-07-26

## 1. NGC 1365 does NOT need a raw reduction. Reduced HI products exist. (thread premise WRONG)
The MeerKAT Fornax Survey (MFS) release table lists, for NGC 1365, `cube / mom0 / mom1 / mom2` at
**five angular resolutions: 11", 21", 41", 66", 98"** (velocity resolution 1.4 km/s). NGC 1365 is one of the
two galaxies with the most HI in the Fornax cluster. At 11" and D=19.57 Mpc that is ~1.04 kpc resolution --
about 8.6x finer than the ATCA mosaic, and enough for complete 8-sector azimuthal work.
Release table (public, no login): https://docs.google.com/spreadsheets/d/1VHPbfsd_FLdNvXyACPtRVRpGOkjGbR39wMmZ8Dnmh7g
Data page: https://sites.google.com/inaf.it/meerkatfornaxsurvey/data

## 2. BLOCKER (human, 2 minutes): the NGC 1365 row carries the product labels but NO hyperlinks in any export
Measured three independent ways -- `export?format=xlsx`, `export?format=ods`, `export?format=zip` (HTML) --
all three return **0 anchors on the NGC 1365 row** (row 30), and also on NGC 1351A, NGC 1386, NGC 1387,
NGC 1427, FCC 057, FCC 248, FCC 267, FCCB 0507, FCCB 1461, FDS14D011. Rows that do export carry 20, 5, 4 or 2
links (NGC 1427A and NGC 1436 export the full 20), so the export is lossy and the links very likely exist in
the live sheet. `pubhtml` returns HTTP 401; `htmlembed`, `preview` and `gviz/tq?tqx=out:html` return a
JavaScript shell with zero anchors. This negative is scoped to those five Google export/render endpoints.
**EXACT HUMAN STEP:** open the sheet in a browser, right-click each of the 20 cells on the NGC 1365 row and
copy the link (or contact Paolo Serra, paolo.serra@inaf.it, named on the data page as the retrieval contact).
File naming convention, read from a resolved sibling link: `t06_1kms_NGC1427A_image_mos.fits`
=> expect `t01..t06_1kms_NGC1365_{image,mom0,mom1,mom2}_mos.fits`.

## 3. What IS fetched and verified: the pre-MeerKAT ATCA Fornax mosaic covering NGC 1365
Three unrestricted direct links on the MFS data page (no login):
  ATCAmom0.fits  https://drive.usercontent.google.com/download?id=14rCEMbCL9D2TTZSGE-M5tHtDeH2yfXN0&export=download&confirm=t
  ATCAmom1.fits  https://drive.usercontent.google.com/download?id=1ubH-ITgRISjfNz2P0N0YEBqQWCatk1cL&export=download&confirm=t
  ATCAcube.fits  https://drive.usercontent.google.com/download?id=1BKmenCu00g0KLEXK-ZFE_3A7CqXuch8T&export=download&confirm=t  (not fetched this pass)

## 4. 🔴 AZIMUTHAL SECTOR COVERAGE, MEASURED -- ATCA gives 5/8, NOT 8/8
Criterion stated first: a sector counts if it has >=1 radial annulus with mean mom0 S/N >= 3 AND >= 1
independent beam. Result, from `T1_NGC1365_ATCA_HI_sector_profile.csv`:
  sector 1: 0 annuli | sector 2: 3 (to 570") | sector 3: 1 (to 510") | sector 4: 0
  sector 5: 1 (to 540") | sector 6: 2 (to 570") | sector 7: 2 (to 570") | sector 8: 0
  => **5 of 8 sectors.** All 8 sectors do contain some finite mom1 pixels (74-183 each).
Independent reason the ATCA product cannot deliver 8 sectors: at beam 94.9", a 45-deg sector arc only exceeds
one beam beyond r ~ 121", leaving ~3 independent radial rings before the HI runs out.
**=> NGC 1365 as a TWELFTH GALAXY is viable, but ONLY on the MFS 11"/21" products, not on the ATCA mosaic.**

## 5. NGC 1433 -- the thread's "ATCA" route is genuinely a RAW reduction, and NGC 1433 is NOT in LVHIS
The LVHIS ATCA database (159 entries, https://www.narrabri.atnf.csiro.au/research/LVHIS/LVHIS-database.html,
HTTP 200, 50,297 B) contains **no NGC 1433 row** -- so the prior queue entry "LVHIS DOI 10.1093/mnras/sty479"
does NOT supply NGC 1433. The only resolved HI is Ryder et al. 1996, ApJ 460, 665 (ATCA), which predates data
archives; no reduced public cube was located. Raw ATCA visibilities should be in ATOA
(https://atoa.atnf.csiro.au/) -- NOT confirmed this pass: `query.jsp?source=NGC1433&format=text` returned the
25,140-byte query FORM, not a result set (HTTP 200 is not the file). ATOA query syntax is the open resume point.
NGC 1433 is a PHANGS-ALMA target, so its CO side is public on CANFAR anonymously
(listing https://cadc-west-01.canfar.net/vault/nodes/<path>, download https://ws-cadc.canfar.net/vault/files/<path>).
=> **Recommendation to T1: spend the thirteenth-galaxy budget only after MFS NGC 1365 lands.**
