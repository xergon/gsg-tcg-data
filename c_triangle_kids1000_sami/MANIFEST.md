# C-Triangle — MANIFEST: every source URL, complete and verbatim

One URL per line. **No `base + FILENAME` templates anywhere** — the thread's browsing safety layer rejects
those and it costs a whole pulse.

---

## 1. KiDS-1000 — the 16 GB shear catalogue (MANIFESTED, NOT RE-HOSTED)

Over the 2 GiB GitHub release-asset cap; cannot be mirrored intact. Verified by header read, not assumed.

```
https://kids.strw.leidenuniv.nl/DR4/data_files/KiDS_DR4.1_ugriZYJHKs_SOM_gold_WL_cat.fits
```
* `Content-Length: 17712469440` (17,712,469,440 B)
* `Last-Modified: Mon, 07 Dec 2020 21:10:05 GMT`
* `Content-Type: image/fits`, `Accept-Ranges: bytes` (HTTP 206 confirmed on a 50 MB range read)
* magic `SIMPLE  =` — real FITS, not an HTML shell
* EXT 1 `OBJECTS`: `NAXIS1=833  NAXIS2=21262011  TFIELDS=193` — the row count matches the publisher's
  stated 21,262,011 **exactly**
* the publisher provides **no checksum**; the byte count and the row count are the verification
* single-stream rate from this egress 4.1–7.5 MB/s; **6 parallel range streams gave 7 MB/s aggregate — the
  server is rate-capped and parallelism does not help.** Budget ~45–70 min for a full pull.

### n(z) — ALREADY PUBLISHED, VERIFIED IDENTICAL, REUSE IT
```
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/s9_deflection_closure/kids1000/KiDS1000_SOM_N_of_Z.tar.gz
https://kids.strw.leidenuniv.nl/DR4/data_files/KiDS1000_SOM_N_of_Z.tar.gz
```
4,360 B, sha256 `1962a9117413f7fbb8adb863e4a85e250998257572cfffcbe2834e61c7d1704a`.
The repo copy was `cmp`-compared byte-for-byte against a fresh download of the publisher original today:
**identical**. 5 members, `SOM_N_of_Z/K1000_NS_V1.0.0A_ugriZYJHKs_photoz_SG_mask_LF_svn_309c_2Dbins_v2_
SOMcols_Fid_blindC_TOMO{1..5}_Nz.asc`, 6,022 B each, 121 lines (`# # binstart, density` + 120 bins of
Δz = 0.05 spanning z = 0 → 6.0). Blind C only — blind C is the true unblinded catalogue.

### Tile lists (footprint definition)
```
https://kids.strw.leidenuniv.nl/DR4/kids_dr4.0_cat_wget.sh
https://kids.strw.leidenuniv.nl/DR4/kids_dr4.1_cat_wget.sh
```
1,006 and 196 lines respectively. All 196 DR4.1 tiles are a strict subset of the DR4.0 1,006. Parsed into
`KiDS1000_tile_footprint.csv` with the complete per-tile FITS URL on every row.

### Systematics products (small, public, on GitHub — fetch these for the null tests)
```
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/PSFRES_CORRMAP/c1_map.fits
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/PSFRES_CORRMAP/c2_map.fits
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/PSFRES_CORRMAP/exposure_map.fits
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/PSFRES_CORRMAP/create_c12_mock.py
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/PSFRES_CORRMAP/README.md
https://raw.githubusercontent.com/KiDS-WL/Cat_to_Obs_K1000_P1/master/Calc_2pt_Stats/2D_GGL/KiDS_Patches.dat
```
17,642,880 B each for the three maps (2100 × 2100 float); 85,738 B for the patch file. All four fetched and
opened here — statistics in `KIDS1000_SHEAR_CALIBRATION.md` §0.

### Paper source (where every published number in this delivery came from)
```
https://arxiv.org/e-print/2007.01845
```
1,511,190 B gzip. `K1000_ShearStats_Paper.tex` plus `Section_PSF.tex`, `Section_ShearTests.tex`,
`Section_Data.tex`, and `stats_table_blindC.txt` (the per-tomographic-bin `n_eff`/`σ_ε`/`δ_z`/`m` table,
copied into this lane as `giblin2021_stats_table_blindC.txt`).

### ESO archive — alternate host for the *survey* products (not the SOM-gold WL catalogue)
ESO archive identifier **10.18727/archive/37**. Programme IDs **177.A-3016, 177.A-3017, 177.A-3018,
179.A-2004**. Cite Kuijken et al. 2019, Wright et al. 2020, Hildebrandt et al. 2021, Giblin et al. 2021.

The ESO TAP service is up and does serve the KiDS collection:
```
http://archive.eso.org/tap_obs/sync
```
`SELECT obs_collection,dataproduct_type,access_url,access_estsize FROM ivoa.ObsCore WHERE
obs_collection='KIDS'` returns per-tile `image` and `measurements` products behind `datalink/links?ID=...`.
⚠ **This is the ESO Phase-3 survey release — coadded tiles and multi-band source lists. It is NOT the
KiDS-1000 SOM-gold weak-lensing catalogue**, which is a consortium value-added product distributed only
from the Leiden server. Useful as a fallback for imaging and photometry, useless as a substitute for
`e1`/`e2`/`weight`. Note the ESO endpoint is `/tap_obs/sync`; `/programmatic/TAP` returns 404.

---

## 2. SAMI Galaxy Survey DR3 — catalogues (DELIVERED, anonymous VO TAP)

Endpoint, anonymous, no registration:
```
https://datacentral.org.au/vo/tap/sync
https://datacentral.org.au/vo/tap/tables
```
`REQUEST=doQuery&LANG=ADQL&FORMAT=csv&QUERY=SELECT ... FROM sami_dr3.<table>`

| table | rows returned | delivered as |
|---|---|---|
| `sami_dr3.InputCatGAMADR3` | 5,536 | `sami/InputCatGAMADR3.csv` |
| `sami_dr3.InputCatClustersDR3` | 1,433 | `sami/InputCatClustersDR3.csv` |
| `sami_dr3.CubeObs` | 3,712 | `sami/CubeObs.csv` |
| `sami_dr3.samiDR3gaskinPA` | 3,426 | `sami/samiDR3gaskinPA.csv` — **the gas-kinematic PA catalogue** |
| `sami_dr3.samiDR3Stelkin` | 3,426 | `sami/samiDR3Stelkin.csv` |

`PA_GASKIN` and `PA_STELKIN` are both documented **"Anticlockwise, North = 0 degrees"** — same convention,
so the gas–stellar PA offset is directly differenceable without a frame conversion.

Paper: Croom et al. 2021, MNRAS 505, 991, DOI **10.1093/mnras/stab229**, arXiv `2101.12224`.

### ⛔ SAMI DR3 MAP PRODUCTS — BLOCKED, HUMAN NEEDED
```
https://datacentral.org.au/api/services/sov/?source=<CATID>
```
→ **HTTP 403** `{"detail":"Authentication credentials were not provided.","status_code":403}`

```
https://datacentral.org.au/services/download/
```
→ POST validates and returns **HTTP 400** with **`email: This field is required.`**
Form fields: `csrfmiddlewaretoken`, `source_list`, `data_releases`, `data_products_ifs`,
`loose_matching`, `email`. Delivery is by email; a personal address is mandatory.

**No account was created and no email address was submitted.** Product IDs, read out of the form:
* `180` — SAMI DR3 SAMI 1-component line emission map: **Hα** ← the one C-Triangle named
* `190` — Recommended-component Hα; `200` sectors-binned; `230` adaptively-binned; `220` 2-component annular
* `149` / `150` — stellar velocity / dispersion map (two moment) from default cube
* `157` / `158` / `159` / `160` — stellar velocity / dispersion / h3 / h4 (four moment) from default cube
* `248` — star-formation mask map from 1-component emission line ratios
* the eight line species span IDs 179–246 across all binning schemes

Croom et al. 2021 §data-access names Data Central as the **only** distribution route; there is no static
mirror and no arXiv-hosted supplement. A human must register at Data Central or authorise submitting an
address. The full DR3 archive is ~430 GB (confirmation-stage only per the brief); the Hα subset for the
2,100 GAMA lenses is a small fraction of that and is what should actually be requested.

---

## 3. DESI Legacy Imaging Surveys DR9 — primary host DOWN, substitute VERIFIED

### ⛔ Primary route, unreachable
```
https://www.legacysurvey.org/viewer/cutout.fits
https://portal.nersc.gov/cfs/cosmo/data/legacysurvey/dr9/
```
`www.legacysurvey.org` → CNAME **`lb.cosmo-viewer.production.svc.spin.nersc.org`**, A records
`128.55.206.106–113` — **it is hosted at NERSC.** Every endpoint times out (25 s, HTTP 000), from local curl
and from a second egress. Same **NERSC "Major Power Upgrade to Disrupt Services, July 22 – August 3"**
outage already recorded in this queue for DESI DR1. **Re-attempt after 2026-08-03.**

### ✅ Substitute — NOIRLab Astro Data Lab, NERSC-independent, verified
```
https://datalab.noirlab.edu/sia/ls_dr9
https://datalab.noirlab.edu/tap/sync
```
Brick grid pulled from `ls_dr9.bricks_s` via ADQL over the GAMA strip (4,988 bricks with exact
`ra1/ra2/dec1/dec2`) → `desi_dr9_bricks_gama_strip.csv`. **All 2,100 SAMI lenses matched a brick; 0
unmatched.** 31,500 complete cutout URLs in `DESI_LS_DR9_cutout_urls.txt` — 15 products × 2,100 galaxies,
`SIZE=0.03725,0.03725` deg = **512 px at 0.262″/px**. **10 of 10 randomly sampled URLs returned valid FITS**
(`SIMPLE  =`, 0.75–1.07 MB each). Full pull ≈ 30 GB — **deferred**, per the brief's ordering.

Products included: `image-g image-r invvar-g invvar-r invvar-z model-g model-r model-z maskbits chi2-g
chi2-r chi2-z psfsize-g psfsize-r psfsize-z`.

🔴 **`image-z` is MISSING from the Data Lab `ls_dr9` collection.** Reproduced at two independent positions
with `MAXREC=5000`: the SIA returns 38 product types per brick and `image-z` is not among them, while every
other z-band product is. `image-g`/`image-r` are complete. **The z-band science image is only obtainable
from NERSC, i.e. after 2026-08-03.**

🔴 **DR9 bricks ship no residual product.** There is no `resid-*` layer — residual = `image − model`. The
viewer's `ls-dr9-resid` layer computes it on the fly and is NERSC-hosted (down). Both `image-*` and
`model-*` are in the URL list, so the residual is constructible.

Survey paper DOI **10.3847/1538-3881/ab089d**.
