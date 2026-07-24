# T4 HOJD — CMS 2011A CORE3 (SIM leg) + CMS real-data v0.2 correction

Higher-Order Jet-Distribution (HOJD) feature tables built from the MIT **MOD HDF5**
release of the CMS 2011A Open Data, under the **PtYPhiM** four-vector convention.

## The convention (T4 ruling, 2026-07-24)

> "Choose (B): PtYPhiM is canonical — the MOD field is y, and EnergyFlow's hadronic
> coordinate convention uses rapidity y, not pseudorapidity; rebuild the CMS
> `pfc_mass_GeV` column with the new extractor (n=1 → raw PFC mass, n=0 → 0), keep all
> other parity-passing columns unchanged, and stream SIM with the identical convention."

Particle four-vectors are therefore built from the MOD `(pt, y, phi, m)` fields as

```
mT = sqrt(pt^2 + m^2)
E  = mT * cosh(y)      px = pt * cos(phi)
pz = mT * sinh(y)      py = pt * sin(phi)
```

`pfc_mass_GeV` is the invariant mass of the summed four-vector of the selected PFCs.

**PFC selection:** `vertex == 0` and `pt >= 0.5 GeV`. No JEC is applied to individual
PFCs. `weight_nb` is the raw MOD `jets_f['weight']` in nanobarns, with no EnergyFlow
k-factor.

**Edge behavior:** `n_pfc_selected == 1` → the raw PFC mass; `n_pfc_selected == 0` → `0.0`.
Both are algebraically exact in the formula above. Neither is reachable in this data —
the minimum `n_pfc_selected` over the pT > 375 GeV selection is 4.

## Releases

| release | contents | rows |
|---|---|---|
| `t4-cms2011a-core3-v1` | `T4_HOJD_CMS2011A_CORE3_v1_features_SIM.parquet` — detector-level Pythia 6 QCD SIM | see `SUMMARY_sim.json` |
| `t4-cms2011a-v0.2` | `T4_HOJD_CMS2011_v0_2_features_CMS.parquet` — CMS real data, `pfc_mass_GeV` corrected | 1,785,625 |
| `t4-cms2011a-v0.1` | superseded by v0.2 (`pfc_mass_GeV` used the wrong coordinate convention) | 1,785,625 |

**v0.2 is v0.1 with `pfc_mass_GeV` replaced and nothing else.** The other 32 columns were
independently recomputed from the source HDF5 and verified to still match v0.1 at the
original tolerances (integer/id exact; raw `jets_f`-derived bit-exact; `corr_jet_pt_GeV`
rtol ≤ 1e-14; `pfc_pt_sum_GeV` and the `e2`/`e3`/`D2` family rtol ≤ 1e-10). See
`SUMMARY_cms_v0_2.json`.

## Sources

| record | DOI | leg |
|---|---|---|
| 3341498 | `10.5281/zenodo.3341498` | Pythia 6 QCD 300–470 (`QCD300to470`) |
| 3341500 | `10.5281/zenodo.3341500` | Pythia 6 QCD 170–300 (`QCD170to300`) |
| 3340205 | `10.5281/zenodo.3340205` | CMS 2011A Jet Primary Dataset (real data) |

Every raw `.h5` was verified against its Zenodo-published MD5 before parsing; the CMS
containers were additionally verified against the `source_file_sha256` recorded in v0.1.

Only the `SIM*` files of records 3341498/3341500 are used. The `GEN*` files in those
records carry no `pfcs` dataset and lack `jec`/`jet_area`/`jet_max_nef`/`npv`/`quality`,
so the frozen HOJD schema is not computable from them.

License: **CC-BY-4.0**, inherited from the source records.

## Files here

- `t4_hojd_extractor.py` — T4's canonical extractor, used **verbatim and unmodified**
- `stage1_stream_sim.py` — SIM streaming pipeline (zero accumulation: each raw `.h5` is
  deleted as soon as its part table is written)
- `stage2_rebuild_cms.py`, `stage2_verify_and_build.py` — real-data re-stream, the
  32-column equality check, and the v0.2 build
- `SUMMARY_sim.json`, `SUMMARY_cms_v0_2.json` — provenance, checksums, column lists
- `parse_log_sim.txt`, `parse_log_cms_v0_2.txt` — per-file parse logs
- `STAGE0_unit_check.json` — the edge-behavior unit check for the ruling
