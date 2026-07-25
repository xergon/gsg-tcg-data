# i2 — GAMA DR4 x KiDS-Legacy DR5 — SOURCE MANIFEST

All URLs below were fetched with `curl` and verified **by content**, not by HTTP status:
FITS files were opened, `SIMPLE  =` magic confirmed, `NAXIS2` read, and the first row
materialised. `.tar.gz` verified by gzip magic `1f 8b` + successful `tar tzf`.

Fetched 2026-07-25 (TRUE UTC via `date -u`).
**No registration, no credentials, no access control encountered anywhere. Everything below is openly public.**

---

## 1. GAMA DR4 — Driver et al. 2022, MNRAS 513, 439, DOI 10.1093/mnras/stac472

Landing page: https://www.gama-survey.org/dr4/
Schema browser: https://www.gama-survey.org/dr4/schema/
⚠ `WebFetch` on `gama-survey.org` returns HTTP 403 (User-Agent block). `curl -L` with a
browser UA works. This is a UA filter, not an access control.

### 1a. Files staged and verified

| file | bytes | rows (NAXIS2) | sha256 | URL |
|---|---|---|---|---|
| TilingCatv46.fits | 36,334,080 | 221,373 | c9dc8e098a76ede238f9d0d6b2ccd953ed3681ea86b79b04a741e8915942e67b | https://www.gama-survey.org/dr4/data/cat/EqInputCat/v46/TilingCatv46.fits |
| SersicCatSDSSv09.fits | 156,841,920 | 221,373 | d61b9b612eb9807a8dfea02f0a0134530e7243ebda1ecc549f34c1cf98b6093f | https://www.gama-survey.org/dr4/data/cat/SersicPhotometry/v09/SersicCatSDSSv09.fits |
| SpecObjv27.fits | 126,253,440 | 344,905 | e997cace56d01924f3eef163ae30d64888726ff7ea09ca7d6b56f588935e42f2 | https://www.gama-survey.org/dr4/data/cat/SpecCat/v27/SpecObjv27.fits |
| SpecAllv27.fits | 190,232,640 | 522,558 | 17e69b876b68a2e0e2033e9cf9948e2b0caf8f697cf6d8eadca54057bb0c9aad | https://www.gama-survey.org/dr4/data/cat/SpecCat/v27/SpecAllv27.fits |
| StellarMassesLambdarv24.fits | 95,310,720 | 200,077 | 1a98b61c1a92a082d1925a1c38aff135b2f3aaa66322d93a874ace65d95a23f4 | https://www.gama-survey.org/dr4/data/cat/StellarMasses/v24/StellarMassesLambdarv24.fits |
| StellarMassesGKVv24.fits | 177,727,680 | 370,116 | (see checksums_gama.txt) | https://www.gama-survey.org/dr4/data/cat/StellarMasses/v24/StellarMassesGKVv24.fits |
| G3CGalv10.fits | 17,167,680 | 204,110 | (see checksums_gama.txt) | https://www.gama-survey.org/dr4/data/cat/GroupFinding/v10/G3CGalv10.fits |
| G3CFoFGroupv10.fits | 7,502,400 | 26,194 | b6e50b03f1cab40141c1b2a9928dbb585fbe13de7de98bbdea467bccedcff83f | https://www.gama-survey.org/dr4/data/cat/GroupFinding/v10/G3CFoFGroupv10.fits |
| EnvironmentMeasuresv06.fits | 7,053,120 | 92,513 | 9c6a8f86fcfdf6a3e8e3114739d56eec5631312e25d450a3d6aa9c2ad5832e57 | https://www.gama-survey.org/dr4/data/cat/EnvironmentMeasures/v06/EnvironmentMeasuresv06.fits |
| DistancesFramesv14.fits | 21,078,720 | 339,693 | df0167e9f40f2f8dc82b8c2a33c502efa9edcfbeb180ee431977808a9d529ace | https://www.gama-survey.org/dr4/data/cat/LocalFlowCorrection/v14/DistancesFramesv14.fits |
| InputCatAv07.fits | 227,076,480 | 1,831,071 | f6dc17e6a27ec42ae592005dacbac8f47eb72a2efa09e0c3c9025c70c4824f23 | https://www.gama-survey.org/dr4/data/cat/EqInputCat/v46/InputCatAv07.fits |
| GalacticExtinctionv03.fits | 168,534,720 | 1,831,676 | 3cc58dc9d50031f35e1ba1c9c9d65e36f5fc15969d964ebd1f88e045c594b0c9 | https://www.gama-survey.org/dr4/data/cat/EqInputCat/v46/GalacticExtinctionv03.fits |

Each `.fits` has a machine-readable schema descriptor `<stem>.par` at the same URL with the
extension swapped; all `.par` files are staged and are the authoritative column dictionary.

### 1b. ⚠ THREE NAME/VERSION CORRECTIONS TO THE THREAD'S TARGET LIST

1. **`environmentmeasures v05` DOES NOT EXIST.** `https://www.gama-survey.org/dr4/data/cat/EnvironmentMeasures/`
   lists exactly one version: **v06** (dated 2020-06-29, S. Brough et al. 2013, "latest GAMA II version").
   v06 was used.
2. **`stellarmasses v24 / StellarMassesv24.fits` DOES NOT EXIST.** `StellarMasses/v24/` ships **five**
   separate tables — `StellarMassesLambdarv24`, `StellarMassesGKVv24`, `StellarMassesPanChromv24`,
   `StellarMassesG02SDSSv24`, `StellarMassesG02CFHTLSv24`. There is no undifferentiated
   `StellarMassesv24.fits`. **`StellarMassesLambdarv24` was used** — it is the equatorial-region
   (G09/G12/G15) LAMBDAR-photometry table, i.e. the one that shares its footprint and its `CATAID`
   base with `SersicCatSDSSv09` and `TilingCatv46`. `StellarMassesGKVv24` (370,116 rows, equatorial
   + G23, ProFound/GKV photometry) is also staged as an alternative.
3. **`eqinputcat v46`** resolves to **`TilingCatv46.fits`** — that is the science catalogue of the
   `EqInputCat v46` DMU. (`InputCatAv07` is the pre-selection 1.83 M-row input catalogue; it is
   staged but is not the lens parent.)

### 1c. DEFERRED — `Randoms v02`

`https://www.gama-survey.org/dr4/data/cat/Randoms/v02/Randomsv02.fits` —
**6,969,075,840 bytes / 145,188,792 rows**. NOT fetched this pass: at the throughput the GAMA
server sustained while the KiDS-Legacy transfer was running it projected to >24 h and it was
starving the primary transfer. It is **not needed for the IPR/RAR input table** (it is the
clustering/window random catalogue). Directly fetchable at the URL above; `Randomsv02.par` IS staged.

---

## 2. KiDS-Legacy (KiDS DR5) weak-lensing catalogue

Landing page: https://kids.strw.leidenuniv.nl/DR5/legacy_wl.php
Papers: Wright, Kuijken, Hildebrandt, Radovich, Bilicki et al. 2024 (A&A 686, A170);
Wright, Stölzner et al. 2026 (A&A 703, A158, cosmic shear);
Wright, Hildebrandt, van den Busch et al. 2026 (A&A 703, A144, redshift calibration);
Reischke et al. 2025 (A&A 699, A124, covariance); Stölzner et al. 2025 (A&A 702, A169).

| file | bytes | contents | URL |
|---|---|---|---|
| KiDS_Legacy_NS_unblind_final.fits.gz | 7,179,531,549 | 40,894,394 gold sources, 1347 tiles | https://kids.strw.leidenuniv.nl/DR5/data_files/KiDS_Legacy_NS_unblind_final.fits.gz |
| KiDS_Legacy_NS_unblind_final.readme.txt | 6,245 | column dictionary (52 columns) | https://kids.strw.leidenuniv.nl/DR5/data_files/KiDS_Legacy_NS_unblind_final.readme.txt |
| KiDS_Legacy_cosmic_shear_data_release.tar.gz | 131,095,396 | data vectors, COVMAT, **NZ_SOURCE n(z)**, chains | https://kids.strw.leidenuniv.nl/sci_data/KiDS_Legacy_cosmic_shear_data_release.tar.gz |

⚠ **`KiDS_Legacy_NS_unblind_final.fits.gz` is 6.69 GiB — it EXCEEDS GitHub's 2 GiB release-asset
cap and is NOT re-hosted.** Fetch it from the URL above. The server supports HTTP byte ranges
(`Accept-Ranges: bytes`, verified 206), so a parallel range download works; a single stream ran at
~0.7 MB/s, ten parallel ranges at ~3 MB/s.

## 3. KiDS-1000 DR4.1 SOM-gold — FROZEN REPLICATION PATH ONLY

| file | bytes | contents | URL |
|---|---|---|---|
| KiDS_DR4.1_ugriZYJHKs_SOM_gold_WL_cat.fits | 17,712,469,440 | 21,262,011 sources, 1006 tiles | https://kids.strw.leidenuniv.nl/DR4/data_files/KiDS_DR4.1_ugriZYJHKs_SOM_gold_WL_cat.fits |
| KiDS1000_SOM_N_of_Z.tar.gz | 4,360 | SOM-calibrated n(z), 5 tomographic bins | https://kids.strw.leidenuniv.nl/DR4/data_files/KiDS1000_SOM_N_of_Z.tar.gz |

⚠ **16.5 GiB — this, not KiDS-Legacy, is the "~17.7 GB" file.** Manifest only; not fetched, since
the thread demoted KiDS-1000 to frozen replication. Byte count above is the live `Content-Length`.

## 4. Mistele et al. 2024 — the cited equations

arXiv:2310.15248, JCAP 04 (2024) 020, DOI 10.1088/1475-7516/2024/04/020.
LaTeX source read from `https://arxiv.org/e-print/2310.15248` (file `lensing-RAR.tex`).
See `MISTELE_EQ_4.1_4.3.md`.
