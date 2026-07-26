# URL VERIFICATION — every URL below was curl'd and the bytes counted, 2026-07-25 (UTC)

Complete and verbatim, one per line. No `base + FILENAME` templates.

---

## 1. IceTracks-DR2 — ALREADY PUBLISHED, RE-VERIFIED LIVE, NOT RE-FETCHED

Publisher: **doi:10.7910/DVN/MMIIZA**, version 1.0 (RELEASED), 41 files, 2,612,528,359 bytes.
Landing page: `https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MMIIZA`

Our mirror, checked today: **HTTP 200, `content-length: 116163148`** — an exact match to the
published byte count. The zip's central directory was read back over an HTTP range request and
parsed: **44 members, 2,609,179,705 bytes uncompressed**, and all four
`irfs/IC{40,59,79,86}_smearing.csv` are present at their full 598,080,195-byte size.
**Nothing was re-downloaded.**

```
https://github.com/xergon/gsg-tcg-data/releases/download/t6-icetracks-dr2-v1.0/icetracks_dr2_full_release_v1.0.zip
```

## 2. NGC 1068 IceCube data release (Science 2022)

Dataset DOI **10.21234/03fq-rh11** → resolves to
`https://icecube.wisc.edu/data-releases/2022/11/evidence-for-neutrino-emission-from-the-nearby-active-galaxy-ngc-1068/`
Publication DOI **10.1126/science.abg3395**, arXiv:2211.09972.

🔴 **The publisher's own download link is dead.** See `README.md` §8. Re-hosted here:

```
https://github.com/xergon/gsg-tcg-data/releases/download/t6-ngc1068-seyfert-v1/20220913_Evidence_for_neutrino_emission_from_the_nearby_active_galaxy_NGC_1068_data.zip
```

Verified: **386,783,716 bytes**, `content-type: application/zip`, magic `PK\x03\x04`,
sha256 `23cdf378b31f6f35f71cf93144eeac70472900246ba3d745f1b84a3cef1d45f4`,
**CRC32 OK on all 214 members**, 1,108,725,015 bytes uncompressed. The publisher's page states
"369 MB" — 386,783,716 B = 368.9 MiB, an exact match.

The high-value small files are also unpacked as direct repo files:

```
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/event_list.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/FULL_RELEASE_FILELIST.tsv
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/psi_square.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/llh_contour_1D.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/ngc1068_spectrum_68.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/ngc1068_spectrum_95.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/txs0506+056_spectrum_68.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/diffuse_numu_spectrum.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/diffuse_nue_nutau_spectrum.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/electromagnetic_observations.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/gammaray_0.1_to_100_GeV.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/gammaray_above_200_GeV.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/model_inoue_et_al.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/model_murase_et_al.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/aeff_spline.pkl
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/likelihood_sbratio_2d.py
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/NGC_1068_Science_Analysis.ipynb
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/README.pdf
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/ngc1068_science2022/LICENSE
```

⚠ The 1,037,407,680-byte `sig_E_psi_photospline_v006_4D.fits` — the energy-dependent signal PSF —
is **only** inside the release zip at
`ps_data_release/analysis_scripts/kdes/sig_E_psi_photospline_v006_4D.fits`. It is too large to
re-host separately and too large for a sandbox; ask for a specific slice of it if you need one.

## 3–5. Catalogue tables (repo files, direct raw URLs)

```
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/README.md
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/MANIFEST.txt
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icecube_seyfert_tables/icecube_2510.13403_tab_xray_47sources.csv
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icecube_seyfert_tables/icecube_2510.13403_tab_gammaray_110sources.csv
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icecube_seyfert_tables/icecube_2510.13403_tab_summary_of_results.csv
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icecube_seyfert_tables/icecube_2602.10208_tab_candidate_sources_14.csv
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icecube_seyfert_tables/icecube_2602.10208_tab_individual_results_14.csv
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icecube_seyfert_tables/icecube_2602.10208_tab_stacking_and_brightest.csv
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icecube_seyfert_tables/extract_tables.py
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr2_koss2022/ReadMe
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr2_koss2022/table8.dat
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr2_koss2022/table9.dat
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr2_koss2022/table11.dat
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr1_xray_ricci2017/ReadMe
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr1_xray_ricci2017/table1.dat
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr1_xray_ricci2017/table5.dat
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr1_xray_ricci2017/table12.dat
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr1_xray_ricci2017/table13.dat
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr1_xray_ricci2017/table14.dat
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/bass_dr2_lines_oh2022/BASS_DR2_tables.zip.gz
```

Sources of the above, for citation:
- BASS DR2 catalogue: doi:10.3847/1538-4365/ac6c05, arXiv:2207.12432, CDS `J/ApJS/261/2`
  (`https://cdsarc.cds.unistra.fr/ftp/J/ApJS/261/2/`)
- BASS DR1 X-ray: Ricci+ 2017 ApJS 233, 17, CDS `J/ApJS/233/17`
  (`https://cdsarc.cds.unistra.fr/ftp/J/ApJS/233/17/`)
- BASS DR2 line measurements: `https://www.bass-survey.com/DR2_data/BASS_DR2_tables.zip.gz`
- arXiv LaTeX sources: `https://arxiv.org/e-print/2510.13403` and
  `https://arxiv.org/e-print/2602.10208`

## 6. IceTracks-DR2 IRF products (repo files, direct raw URLs)

```
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/IRF_NOTES.md
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/smearing_declination_bins.csv
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/source_to_smearing_decbin.csv
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/IC40_effectiveArea.tab
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/IC59_effectiveArea.tab
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/IC79_effectiveArea.tab
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/IC86_effectiveArea.tab
```

Per-declination smearing slices follow the pattern below with `CFG ∈ {IC40, IC59, IC79, IC86}` and
`NN` = the two-digit bin index from `smearing_declination_bins.csv` (00–29). The four that matter
most are spelled out complete; the rest are enumerated in `MANIFEST.txt`.

```
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/smearing_dec_slices/IC86_smearing_decbin19.csv.gz
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/smearing_dec_slices/IC86_smearing_decbin20.csv.gz
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/smearing_dec_slices/IC79_smearing_decbin19.csv.gz
https://raw.githubusercontent.com/xergon/gsg-tcg-data/main/t6_seyfert_neutrino/icetracks_dr2_irfs/smearing_dec_slices/IC79_smearing_decbin20.csv.gz
```

(bin 19 = Dec ∈ [−1.432544°, 0.000000°] — contains NGC 1068 at Dec = −0.01°;
 bin 20 = Dec ∈ [0.000000°, +5.739170°] — contains the northern-sky hottest spot at Dec = +0.02°.)

## 7. The full bundle the thread asked for

```
https://github.com/xergon/gsg-tcg-data/releases/download/t6-ngc1068-seyfert-v1/T6_NGC1068_Seyfert_Eminus2_extension_v1.tar.zst
```

## ⛔ BLOCKED — needs a human

**ANTARES Public Data 2007–2017** (11-yr point-source track sample, 8,754 events, 3,125 days
livetime; columns: declination, right ascension, number of hits, estimated angular resolution, MJD).

```
https://antares.in2p3.fr/data/data-set-for-the-2007-2017-antares-search-for-cosmic-neutrino-point-sources/
```

The ASCII table is not linked on the page. It is released only through a **Contact Form 7 form**
(`_wpcf7 = 2267`, `_wpcf7_unit_tag = wpcf7-f2267-p2266-o1`) whose required fields are
`your-name`, `your-email` (plus a confirm-email field), `your-subject`, and a free-text
**"Intended use of the data"**, with submit button id `download-data-form-2007-2010`.
Entering personal data into a form is outside what an agent may do here, so **no submission was
attempted**.

The same gate covers the 2007–2010 and 2007–2012 releases and the legacy mirror
`https://antares-old.in2p3.fr/publicdata/form-page2017.html` (HTTP 200, same form). There is **no
DOI** for this dataset and no Zenodo, VizieR or CDS mirror was found. The page also asks that
anyone using the data e-mail `antares.spokesperson@in2p3.fr`.

⇒ **A human must fill the form once.** Everything else in this bundle is unaffected.
