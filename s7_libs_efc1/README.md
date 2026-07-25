# S7 / EFC-1 — LIBS + atomic-line data stage

Machine-readable index of everything here: `SUMMARY.json` (DOIs, verified MD5s, byte counts,
row counts, and the exact NIST ASD query URLs).

## A. NASA PDS SuperLIBS — per-shot  (DOI 10.17189/b2aj-cz96)
Bundle `urn:nasa:pds:libs_reference_database::1.1`, collection
`urn:nasa:pds:libs_reference_database:data_superlibs::1.0`.
Archive root: https://pds-geosciences.wustl.edu/speclib/urn-nasa-pds-libs_reference_database/data_superlibs/

**Per-shot confirmed.** Each product CSV = one target/location: 24 header rows, then 8767
wavelength rows; columns = wavelength + 24 *individual shot* intensity integrations
(PDS4 label: `Un-Normalized intensity, integration N`). Not averages.

- `pds/pds_superlibs_file_manifest.csv.gz` — all **314,300** files with direct URL + byte size
  (17 leaf dirs: 10k/{earth,mars,vacuum}, 18k/mars × 3–9 mJ). **Full collection = 600.6 GB.**
- `pds/collection_data_superlibs_inventory.csv` — official PDS inventory, 157,150 products (LIDVIDs)
- `pds/bundle_readme.txt` — bundle README

The full 600.6 GB is **not** mirrored. A matched per-shot sample is in the release (see below);
anything else is directly fetchable using the URLs in the manifest.

## B. Zenodo SuperLIBS 10K Mars, 4 laser energies  (DOI 10.5281/zenodo.7566042)
All four CSVs, **MD5-verified against the published checksums**, in release `s7-libs-efc1-v1`.
Each: 2,435 rows × 16,088 cols — 8 oxide wt% + `Pellet Name` + 16,078 wavelength channels
from 233.1524722 nm; 2,433 spectra. CC-BY-4.0.

> Note: the Zenodo energies (2.4 / 4.0 / 5.6 / 7.2 mJ) are **not** the PDS energies (3 / 5 / 7 / 9 mJ).

## C. NIST ASD v5.12  (DOI 10.18434/T4W30F)
`nist/nist_asd_<EL>_I-III_240-870nm.tsv` for Si, Al, Fe, Mg, Ca, Na, K, Ti — **20,592 lines total**.
Air wavelengths, energies in eV. Columns include `obs_wl_air(nm)`, `ritz_wl_air(nm)` and their
uncertainties, `Aki(s^-1)`, `Ei(eV)`/`Ek(eV)`, `conf_i`/`term_i`/`J_i`, `conf_k`/`term_k`/`J_k`,
`g_i`/`g_k`. Exact reproducible query URLs are in `SUMMARY.json` → `C_nist_asd.per_element[].query_url`.
