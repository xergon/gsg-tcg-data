# i5 — DES Supernova 5-Year Data Release (DES-SN5YR)

Public mirror staged for fleet row **i5** (residual cosmic phase de-sharpening in Type Ia supernovae).

## 🔴 Deliberate exclusion

`4_DISTANCES_COVMAT` and `5_COSMOLOGY` are **excluded from every artefact here**, on i5's explicit
instruction, so the test stays independent of distance-modulus cosmology, H₀ and a₀. Nothing in this
directory or in the release assets contains a Hubble diagram, a distance-modulus vector, a covariance
matrix, a likelihood or a cosmology chain. If you need them, they are upstream — they were not omitted
by accident.

## Provenance

| | |
|---|---|
| Zenodo record | `10.5281/zenodo.12720778` (concept DOI `10.5281/zenodo.12720777`) |
| Zenodo file | `DES-SN5YR-1.2.zip`, 1,534,568,826 B, publisher md5 `9019a6ddc569553bc323e9e1b68a55bf` |
| GitHub upstream | `des-science/DES-SN5YR` |
| Snapshot commit | `c9a4fcafc4cbd19bd750dee47fc76194a45c181f` (2026-01-28) |
| Legacy tag | `1.3` — "Vincenzi et al. 2024 Legacy Release" |
| Data paper | Sánchez et al. 2024, ApJ **975**, 5 — `10.3847/1538-4357/ad739a` |

### Two versions, and why both are here

The upstream repo **HEAD is no longer the Vincenzi et al. 2024 release**. It was replaced by the
**DES-Dovekie reanalysis** (Popovic et al. 2026); the upstream README states it "supercedes the original
DES-SN5YR results". The Zenodo zip and tag `1.3` are the original Vincenzi 2024 version.

- `github_dovekie_c9a4fca/` — current HEAD (Dovekie). SALT3.DOVEKIE + SALT3.DOVEKIE-SYS models.
- `zenodo_v1.2/` — small comparison files from the md5-verified Zenodo zip (Vincenzi 2024). The **full**
  v1.2 tree is the `DES-SN5YR-zenodo-v1.2-EXCL45.tar.gz` release asset.

**What actually differs between HEAD and the Vincenzi version, checked by git blob SHA — not assumed:**

- **Every PHOT file is identical.** `DES-SN5YR_DES_PHOT.FITS.gz`, `..._LOWZ_PHOT`, `..._Foundation_PHOT`
  and `DES5YR_SALT3_LCFIT.LCPLOT.gz` all match bit-for-bit. **The light curves themselves did not
  change between the Vincenzi and Dovekie versions.**
- **`DES-SN5YR_DES_HEAD.FITS.gz` DIFFERS.** The per-SN metadata table was regenerated: its internal gzip
  timestamp is 2025-12-02, against 2024-06-14 for the untouched PHOT file. The upstream README's
  `UPDATES` block gives the reasons — 2025-04 renamed the filters `g,r,i,z` → `DES-g,DES-r,DES-i,DES-z`,
  and 2025-12 corrected `HOSTGAL_MAG_[band]` / `HOSTGAL_MAGERR_[band]`.
  **If you touch host magnitudes or filter names, the version you pick matters.**
- Also differing: `0_DATA/README.md`, `0_DATA/DES-SN5YR_DES/DES-SN5YR_DES.README` (doc text), and the
  simulations + SALT3 model, which are a different production entirely.

Tag `1.3` vs Zenodo `v1.2` over the six kept directories: 725 files identical, 3 differ — all three are
pippin configs (`7_PIPPIN_FILES/D5yr_analysis.yml`, `D5yr_biascor.yml`, `D5yr_sim_nominal.yml`).
Tag `1.3` is therefore a near-exact stand-in for the zip's contents, **but not a byte-exact one.**

## Contents verified

| Quantity | Value | Where checked |
|---|---|---|
| High-quality SMP light curves | **19,706** | `NEVT_ALL` in `DES-SN5YR_DES.README`; HEAD FITS row count |
| SMP photometry epochs | **1,798,736** | `DES-SN5YR_DES_PHOT.FITS.gz` row count |
| Photometrically classified SNe | **1,635** | `3_CLASSIFICATION/DES_classification.csv` |
| Host spec-z available | 8,302 | `NEVT_HOSTGAL_SPECZ` |
| LOWZ / Foundation light curves | 342 / 185 | HEAD FITS row counts |
| Redshift range | 0.1 < z < 1.13 (cosmology sample) | Sánchez et al. 2024 |

### ⚠ The 31,636 DIFFIMG light curves are NOT here

Sánchez et al. 2024 describes **31,636 DIFFIMG** and **19,706 SMP** light curves. Only the **SMP** set is
in the public release. The docs list a `DES-SN5YR_DES_DIFFIMG` directory, and `0_DATA/README.md` still
says the full light-curve set "will be released after acceptance of Sanchez et al. 2024" — but that
directory exists in **no** public version (HEAD, tag `1.3`, tag `v1.2`, or the Zenodo zip). The paper's
own data-availability statement points at exactly the two sources mirrored here. This is an upstream gap,
not a fetch failure.

## Per-epoch quantities available for a de-sharpening test

`0_DATA/DES-SN5YR_DES/DES-SN5YR_DES_PHOT.FITS.gz` (and the CSV export) carry, per epoch:

`MJD, BAND, CCDNUM, IMGNUM, FIELD, PHOTFLAG, PHOTPROB, FLUXCAL, FLUXCALERR, PSF_SIG1, PSF_SIG2,`
`PSF_RATIO, SKY_SIG, SKY_SIG_T, RDNOISE, ZEROPT, ZEROPT_ERR, GAIN, XPIX, YPIX`

The HEAD table adds 99 per-SN columns including `PEAKMJD`, `MJD_TRIGGER`, `MJD_DETECT_FIRST/LAST`,
`REDSHIFT_HELIO`, `REDSHIFT_FINAL`, `VPEC`, `MWEBV`, `SNTYPE` and the full host-galaxy block.
Rows link via `SNID` and the `PTROBS_MIN`/`PTROBS_MAX` pointers into the PHOT table
(`MJD = -777` terminates each light curve).

## Layout

```
i5_des_sn5yr/
├── README.md                  this file
├── SUMMARY.json               machine-readable provenance, checksums, counts
├── MANIFEST.sha256            sha256 + byte count for every file tracked on main
├── derived_csv/               plain CSV exports of the FITS header tables (format conversion only)
├── github_dovekie_c9a4fca/    upstream HEAD, dirs 0/1/2/3/6/7  (~175 MB, 431 files)
└── zenodo_v1.2/               small v1.2 comparison files (HEAD table, classification, pippin)
```

### Release assets — tag `i5-des-sn5yr-v1`

| Asset | Bytes | What it is |
|---|---|---|
| `DES-SN5YR-zenodo-v1.2-EXCL45.tar.gz` | 1,170,147,464 | Full Vincenzi 2024 tree from the md5-verified zip, dirs 0/1/2/3/6/7. **Contains the 25 real DES mocks.** |
| `DES-SN5YR-github-c9a4fca-EXCL45.tar.gz` | 135,547,317 | Full Dovekie snapshot, dirs 0/1/2/3/6/7 |
| `DES-SN5YR_DES_PHOT.csv.gz` | 87,414,696 | All 1,798,736 SMP epochs as plain CSV |

### ⚠ Two upstream gaps you should know about

1. **The Dovekie simulations are not retrievable.** The 250 `*.FITS.gz` under `1_SIMULATIONS` at HEAD are
   git-LFS tracked and GitHub answers `Git LFS is disabled for this repository`.
   `raw.githubusercontent` returns a **131-byte pointer stub with HTTP 200** — a silent-corruption trap.
   Those stubs were **deleted** from what is published here rather than passed off as data.
   Use the 25 Vincenzi-era mocks in the v1.2 tarball instead; they are complete real files.
2. **`LENSDMU` / `LENSDMU_ERR` live in `0_DATA`, not in the excluded directories.** They are a lensing
   magnification *distance-modulus* correction sitting in the per-SN HEAD table of the Dovekie version.
   They are not part of `4_`/`5_`, so the exclusion did not remove them — flagged here so i5 can drop
   them if the test must stay clear of distance-modulus quantities. The v1.2 HEAD table has no such
   columns.

`derived_csv/` is a pure format conversion (astropy `Table.read` → CSV → gzip). No rows were filtered,
no columns dropped, no values altered. It exists because the FITS files are awkward to pull over a URL.

## Verification

Every file on `main` is listed in `MANIFEST.sha256` as `<sha256>  <bytes>  <path>`. The Zenodo zip was
checked against the publisher's md5 before anything was derived from it; the result is recorded in
`SUMMARY.json`. Every published file was checked for the two silent-corruption modes that have bitten
this programme before: HTML shells returned with HTTP 200, and git-LFS pointer stubs standing in for
real binaries.
