# DELPHI per-event CSV — `delphi_perevent_2026_07_26`

Per-event summary quantities reconstructed from the **public CERN Open Data DELPHI short-DST**
records with a locally built, container-free DELPHI `dstana`/SKELANA reader (PHDST + SKELANA,
gfortran, CERNLIB 2023.08.14). No credentials, no CERN account, no private data.

## Three samples — NEVER pool the two MC sets

| `sample`  | CERN Open Data record | dataset | generator |
|-----------|----------------------|---------|-----------|
| `data`    | 81431 | `DELPHI_collision_short94_c2` | — (real 1994 collision data) |
| `mc_qqps` | 81437 | `DELPHI_sh_qqps_e91.25_c94_2l_c2` | PYTHIA/JETSET parton shower (CERN production) |
| `mc_kk2f` | 81344 | `DELPHI_sh_kk2f4146qqpy_e91.25_l94_2l_c2` | KK2f 4.14.6 + PYTHIA (Lyon production) |

`data` / `mc_qqps` / `mc_kk2f` are the exact literal values of the `sample` column.

## Files

* `<sample>_NNN.csv` — data shards, each **< 900,000 bytes**, each carrying the full header row.
* `MANIFEST.csv` — `shard, sample, row_start, row_end, rows, bytes, sha256`.
  `row_start`/`row_end` are 1-based row indices **within that sample**.
* `FILES.csv` — every input file used: `file_id, sample, cern_record, file_key, size_bytes,
  adler32, events, source_url`. Every input was verified byte-for-byte against the adler32
  published in the record metadata before being read.
* `SCHEMA.md` — this file.

## 🔴 NULL vs 0

A **missing bank and an empty bank are different facts.** Columns derived from a PA extra-module
are written as the literal string `NULL` when that module is **absent from the event**, and as a
number (possibly `0`) when the module is present but yields nothing. Presence is tested per event
by walking the PA chain from `LDTOP` and calling `LPHPA(<module>, LPA, 0)`.

* `EMNC` (extra-module 22) governs `nhpc, ehpc_sum, nemf, eemf_sum`
* `PHOT` (extra-module 30) governs `nphot, ephot_sum, ephot_min, ephot_max`
* `SSTC` (extra-module 33) governs `nstic, estic_sum`
* `ephot_min` / `ephot_max` are additionally `NULL` when `nphot == 0` (no minimum exists).
* ⚠ `nemclu, eemclu_sum` are **never NULL**: the electromagnetic-cluster bank is essentially never
  stored on these DSTs and SKELANA's `PSFECL` *reconstructs* the clusters, so the value is a
  derived quantity that is always defined.

Empirical sanity check on the presence flags (run Y13709.1, 14,957 records): events with
`ihad4 == 1` (mean 44.7 particles) have `EMNC` present in 3,470 of 3,471; events with
`ihad4 == 0` (mean 4.2 particles) mostly do not. The flag tracks event content, not a parse bug.

## Columns

| column | meaning |
|---|---|
| `run` | DELPHI run number (`IIIRUN`) |
| `evt` | event number within the run (`IIIEVT`) |
| `date` | date stamp, `YYMMDD` (`IIIDAT`) |
| `time` | time stamp, `HHMMSS` (`IIITIM`) |
| `dsttype` | DST type tag (`CDTYPE`), e.g. `94C2` |
| `ecm` | centre-of-mass energy, GeV (`ECMAS`) |
| `nctrk` | number of charged tracks |
| `nntrk` | number of neutral tracks |
| `nvecp` | number of reconstructed particles in `VECP` |
| `ncvecp` | number of charged particles in `VECP` |
| `nnvecp` | number of neutral particles in `VECP` |
| `sum_px_ch`,`sum_py_ch`,`sum_pz_ch` | vector momentum sum over charged particles, GeV |
| `sum_e_ch` | energy sum over charged particles, GeV |
| `sum_p_ch` | scalar momentum sum over charged particles, GeV |
| `mean_p_ch` | `sum_p_ch / (number of charged particles)`, GeV; `0` when there are none |
| `sum_px_all`,`sum_py_all`,`sum_pz_all` | vector momentum sum over all `VECP` particles, GeV |
| `sum_e_all` | energy sum over all `VECP` particles, GeV |
| `echar` | total charged energy (`ECHAR`), GeV |
| `emneu` | total electromagnetic neutral energy (`EMNEU`), GeV |
| `ehneu` | total hadronic neutral energy (`EHNEU`), GeV |
| `nhpc` | number of HPC showers (EMNC 22) |
| `ehpc_sum` | summed HPC shower energy, GeV |
| `nemf` | number of forward-EMC showers (EMNC 22) |
| `eemf_sum` | summed forward-EMC shower energy, GeV |
| `nemclu` | number of electromagnetic clusters (SKELANA `PSFECL`) |
| `eemclu_sum` | summed electromagnetic-cluster energy, GeV |
| `nphot` | number of `VECP` particles tagged as photons (PHOT 30) |
| `ephot_sum` | summed tagged-photon energy, GeV |
| `ephot_min` | minimum tagged-photon energy, GeV |
| `ephot_max` | maximum tagged-photon energy, GeV |
| `nstic` | number of STIC (forward ECAL) showers (SSTC 33) |
| `estic_sum` | summed STIC energy, GeV |
| `ihad4` | DELPHI team-4 hadronic-event tag from the DST pilot record: `1` = hadronic, `0` = not |
| `sample` | `data` \| `mc_qqps` \| `mc_kk2f` — **do not merge the two MC sets** |
| `file_id` | key into `FILES.csv` giving the exact source file |

Floats are written in Fortran `1PE13.6` form (7 significant digits) and may carry a leading space.

## Selection

**None beyond the reader's own record filter.** Every `DST`/`MINI` record in every file listed in
`FILES.csv` is present as one row, hadronic and non-hadronic alike. Use `ihad4 == 1` to select
hadronic events. Files were taken in deterministic sorted order by file key from each record; this
is a bounded first delivery, not the complete sample.

## Reproduction

Analysis source `myana.car` (SKELANA user routines `USER00/01/02/99`, `MYANA`, `MYPRES`) plus the
two decompressors the public build ships only as fatal stubs — `MMUZIP` (`+DECK, PHINFLAT`) for the
data `.al` files and `ZLUZIP` for the MC `.sdst` files — both recovered from
`dstana/src/car/phdstxx.car`. Without `ZLUZIP` every MC file yields **zero rows with exit code 0**,
a silent zero-yield rather than a crash.
