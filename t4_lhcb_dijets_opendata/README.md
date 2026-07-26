# T4 — LHCb DiJet open data: measured inventory, schema and entry counts

Derived tables for the two CERN Open Data archives T4 named. The archives themselves are far too large to
reach a sandbox (record 94000 alone is **136.92 GB**), so this directory carries only measured metadata.

## The two records

| record | DOI | title | files | total bytes |
|---|---|---|---|---|
| 94000 (+ children 94001–94006) | `10.7483/OPENDATA.LHCB.CGFF.E7X9` | DiJet Ntuples 6000 (**real collision data**, 2015–2017, magnet up + down) | 25 (22 `.dvntuple.root` + 3 config) | 136,917,130,023 |
| 4910 | `10.7483/OPENDATA.LHCB.N75T.TJPE` | Simulated jet samples for quark flavour identification studies | 26 (24 `.root` + 2 config) | 2,919,550,312 |

Every one of the 25 record-94000 sizes was confirmed by a real `curl -I` (`HEADCHECK_record94000.tsv`,
25/25 MATCH). Every downloaded file was confirmed by **adler32** against CERN's own checksum.

## The structural fact that matters

| | simulation (4910) | collision (94000) |
|---|---|---|
| tree | `DecayTreeTuple/tuple` | `dijets/DecayTree` |
| branches | **1000** | **350** |
| `TRUEJET{1,2}_PT/ETA/PHI/CHARGE/NBHAD` | **present** | **absent** |
| trigger-decision `bool` branches | 497 | 0 |

**Truth jet charge exists only in the simulated record.** Record 94000 provides reconstructed jets with no
truth labels, so any truth-labelled jet-charge study is confined to record 4910.

Sentinel for "no truth jet" is **`-99`** (not NaN). `jet_slots = 2 x events` (Jet0 + Jet1);
`truth_charge_valid_jets = count(TRUEJET*_CHARGE != -99)`.

## Scale

Measured on the one fully downloaded collision ntuple (`00392998_00000002_1.dvntuple.root`, 511,106,461 B,
adler32 `435d51fc`): **214,253 events**, i.e. ~2,387 bytes/event. Extrapolated over the 22 collision ntuples,
record 94000 holds an estimated **~57 million dijet events**.

## Files here

- `MANIFEST_record94000_collision.tsv` — recid, filename, bytes, adler32, HTTPS URL, xrootd URI
- `MANIFEST_record4910_simulation.tsv` — same for the simulation record
- `HEADCHECK_record94000.tsv` — metadata size vs real HTTP `content-length`, 25/25 MATCH
- `SCHEMA_record4910_branches.tsv` — all 1000 simulation branches + typenames
- `SCHEMA_record94001_branches.tsv` — all 352 collision branches (2 trees) + typenames
- `ROWCOUNTS_measured_record4910.tsv` — per-file events / jet slots / valid truth jets / daughters
- `ROWCOUNTS_measured_record94001.tsv` — collision tree entry counts
- `CHECKSUMS_record4910.tsv` — measured vs expected adler32 for every local simulation file

## Reproduction note / trap

`opendata.cern.ch` **does not serve HTTP range requests** — `curl -r 0-99` returns `200` with the *full*
content-length. Remote TTree-metadata reads therefore fail (`uproot` raises "responded with status 200,
rather than 206", or silently pulls the whole file and times out). Entry counts require whole-file downloads.
The `eospublic.cern.ch` HTTPS door is not a workaround — self-signed certificate chain. Rate limit: 60 req/min.
