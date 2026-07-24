# GSG-TCG research data staging

Public staging for **derived products of already-public open datasets**, so that ChatGPT Pro research
threads can fetch them directly with their own browsing. No unpublished research results are hosted here.

## T4_HOJD_CMS2011_v0_1_features_CMS.parquet

Per-jet feature table built from the **CMS 2011A Open Data Jet Primary Dataset**
(Zenodo `10.5281/zenodo.3340205`, MOD HDF5 format, 18 files, 1.98 GB), reprocessed by CMS from data
released under the CMS open-data policy. See also arXiv:1908.08542.

- **1,785,625 rows** — matches the publisher's stated jet count exactly.
- **33 columns**, exactly the requested schema.
- **Event cuts are deliberately NOT applied**, so boundary rows remain auditable.

Per jet, particle-flow candidates with `vertex == 0` and `pt >= 0.5 GeV` are retained. With
`z_i = pT_i / sum(pT)` and `dR_ij = sqrt((y_i-y_j)^2 + dphi_ij^2)`, for `beta` in {0.5, 1, 2}:

```
e2 = sum_{i<j}   z_i z_j       dR_ij^beta
e3 = sum_{i<j<k} z_i z_j z_k  (dR_ij dR_ik dR_jk)^beta
D2 = e3 / e2^3
```

`e3` is evaluated as `trace(M^3)/6` with `M_ij = sqrt(z_i z_j) * dR_ij^beta`. Since `M` has a zero
diagonal, every term with a repeated index vanishes, so the trace equals 6x the strictly-ordered triple
sum. This was **validated to 1e-10 relative tolerance against explicit combinatorial triple sums** on
real jets for all three beta values before the full run.

Notes: 3,056 rows have non-finite `e3` because fewer than 2 PFCs survive selection — physical, not a
defect. 1,072,660 rows fall inside the window `400 <= corr_jet_pt < 600 GeV`, `|eta| < 1.9`,
`quality >= 2`, `n_pfc_selected >= 8`.

`source_file_sha256` records the SHA-256 of the source HDF5 each row came from; all 18 source files were
verified against the publisher's published MD5 checksums.
