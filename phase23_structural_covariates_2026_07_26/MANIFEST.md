# MANIFEST — phase23_structural_covariates_2026_07_26

TRUE UTC 2026-07-28T21:23:31Z (`date -u`).

## Delivered files

| file | bytes | rows | sha256 |
|---|---|---|---|
| `phase23_structural_covariates.csv` | 18171 | 38 | `00d73ccbc28c8be2efbad71931b50ad0a8d93b4e4143e6f7b5ce8febc0962ae0` |
| `SCHEMA.md` | 11594 | - | `bb19a32b2d9ea9de907153352da96107df235a5562dd6f4f0948169cab7e399b` |
| `SOURCE_NOTES.md` | 4054 | - | `7e2d5e4afdc2bbac1709576607c5cf39351ab182e42fc50b1e1bcab5011cebdf` |

## Upstream sources as downloaded (content-verified, not size-verified)

| local name | bytes | sha256 | URL | what |
|---|---|---|---|---|
| `he06_table1.dat` | 11920 | `caf5d158c890928baa43319aaaba47eca6c2fa7b6e5fb3b1a128d57a1c29ea4a` | https://cdsarc.cds.unistra.fr/ftp/J/ApJS/162/49/table1.dat | Hunter & Elmegreen 2006 galaxy sample (distances) |
| `he06_table4.dat` | 15966 | `bcea9853608f3021f8517a513f314a5310c4962efac7388518474e1c479b5243` | https://cdsarc.cds.unistra.fr/ftp/J/ApJS/162/49/table4.dat | Hunter & Elmegreen 2006 structural parameters (RD1,mu1) |
| `he06.readme` | 16604 | `f7c0a37fcab5733650e1d7fe180c171a687f989b2e9fba6d1240c3eae5f54011` | https://cdsarc.cds.unistra.fr/ftp/J/ApJS/162/49/ReadMe | byte-by-byte spec |
| `lt12_table1.dat` | 6519 | `f0ddc054471c932fd9b4fa3615f5c3d465df2ded02a8cbb71144e341b3963fff` | https://cdsarc.cds.unistra.fr/ftp/J/AJ/144/134/table1.dat | Hunter+2012 LITTLE THINGS table1 (Rd,e_Rd,Dist) |
| `lt12.readme` | 14594 | `7b62dd4167f11ab3a52d1bc25f905b9fbdd2495fcb0e62b5caa1a1abb1e59e75` | https://cdsarc.cds.unistra.fr/ftp/J/AJ/144/134/ReadMe | byte-by-byte spec |
| `s4g_t7.dat.gz` | 113380 | `4b35e6faec1bf43dcc67a6dce3e1d6f63d57ed02fc4793dfa85c00020db9a2b6` | https://cdsarc.cds.unistra.fr/ftp/J/ApJS/219/4/table7.dat.gz | Salo+2015 S4G multi-component decompositions (gz; the plain .dat path returns a 404 HTML shell) |
| `s4g.readme` | 12412 | `fbf4ba97d126820120febf6501b7bb02fe308a7763a3c6165ce85146d244e22d` | https://cdsarc.cds.unistra.fr/ftp/J/ApJS/219/4/ReadMe | byte-by-byte spec |
| `leroy_t4.dat` | 1863 | `938104d0289f93f9fed0843028555e92f63a61889d623ee5b5f132e9d6ea1f44` | https://cdsarc.cds.unistra.fr/ftp/J/AJ/136/2782/table4.dat | Leroy+2008 sample properties (l*); NOTE table1.dat does not exist, returns 404 HTML |
| `deblok.eprint` | 2963689 | `5f9d482231d6528a6c120c66fcd717551a633c5e974adbcf3716fb80d2a55427` | https://arxiv.org/e-print/0810.2100 | de Blok+2008 arXiv LaTeX source tarball |

## Assertions

- **38 data rows**, non-zero, asserted at build time.
- **16 distinct galaxies** = the full external held-out pool of the transfer diagnostic.
- **15 galaxies have `R_d`; 15 have `mu_0`.** NGC 925 has neither (see SCHEMA.md for the per-source reason).
- 3 downloads returned HTTP 200 carrying a `404 Not Found` HTML shell and were caught by content inspection.
- S4G table7 field indexing verified against the CDS byte-by-byte spec (31 fields = 31 documented columns).
- Hunter+2012 vs Hunter&Elmegreen2006 distance-rescaling identity reproduces for 11/12 (DDO 133 differs by +0.098 kpc; both shipped, neither corrected).
