# VizieR J/A+A/706/A40 — PHANGS-JWST PAH cloud catalog (Bazzi+ 2026)

Source: `https://cdsarc.cds.unistra.fr/ftp/J/A+A/706/A40/`
Paper: Astron. Astrophys. 706, A40 (2026), bibcode `2026A&A...706A..40B`
Fetched (TRUE UTC): 2026-07-26T04:55Z — 2026-07-26T05:08Z

---

## 1. WHAT IS HERE

| file | bytes | rows | sha256 |
|---|---|---|---|
| `ReadMe` | 18,784 | — | `b760d22b77579cccd5c6d8913cef9800fc06b5c06999d0e67ce488441db5d7aa` |
| `cat30pc.dat` (release asset) | 92,087,634 | 108,466 | `5672e85065dfa98ff1c309239aba941abb16fd88e8125b455992285c79411ea3` |
| `catnat.dat` (release asset) | 124,426,080 | 146,040 | `dad63f53976698cbbb6db8c29e86f3377d894546db675d0e909e849078bb14fe` |
| `cat30pc.dat.gz` (release asset, CDS-original bytes) | 40,780,143 | — | `53c344d4038918ae473c985673036e0feddc07aa2385fb0031ee89fe937d7f3c` |
| `catnat.dat.gz` (release asset, CDS-original bytes) | 55,294,953 | — | `f646b845dd65046f7ce58688c52a358bf3514849dd37870beecc4862dc78307b` |
| `reduced/cat30pc_allrows.csv.gz` | 19,060,610 (18.18 MiB) | 108,466 + header | see `SHA256SUMS.txt` |
| `reduced/catnat_allrows.csv.gz` | 25,649,204 (24.46 MiB) | 146,040 + header | see `SHA256SUMS.txt` |

**Completeness is proven, not assumed.** The ReadMe declares `Lrecl`/`Records`; the delivered files satisfy
the arithmetic exactly, with every line the declared width:

- `cat30pc.dat`: 108,466 × (848 + 1 newline) = **92,087,634 bytes** ✓ — all 108,466 lines are exactly 848 chars
- `catnat.dat`:  146,040 × (851 + 1 newline) = **124,426,080 bytes** ✓ — all 146,040 lines are exactly 851 chars

⚠ **`catnat.dat` is 124,426,080 bytes (118.7 MiB), NOT ~211 MB.** The 211 MB figure in the request is wrong.
124,426,080 is the complete table — the arithmetic above leaves no room for a truncation.

⚠ **CDS publishes these tables ONLY gzipped.** `.../A40/catnat.dat` and `.../A40/cat30pc.dat` return **HTTP 404**
(283-byte HTML). Only `catnat.dat.gz` / `cat30pc.dat.gz` exist on the FTP tree. Both gz files passed `gunzip -t`
and match the server's `Content-Length` byte-for-byte.

---

## 2. 🔴 THE `fall` COLUMN — THE ReadMe DEFINES IT TWO CONTRADICTORY WAYS

`fall` is an **A5 string** holding the literal text `True` / `False` (not 0/1). Both readings you asked for are
reproduced here, because **the ReadMe states both and they are mutually exclusive**:

> **Reading A — `True` SELECTS.** *Description* section: "Use `fall` set to 1 to select the subset analyzed in
> the paper." Repeated verbatim as Note (2) under `cat30pc.dat`.
>
> **Reading B — `True` EXCLUDES.** Byte-by-byte *Explanations* for the `fall` column itself, in **both** tables:
> "Flag to exclude clouds according to our method, **setting True excludes the clouds** (f_all)."

Measured counts (from the delivered files):

| table | `fall`=True | `fall`=False | total |
|---|---|---|---|
| `cat30pc.dat` | **77,884** | **30,582** | 108,466 |
| `catnat.dat`  | **108,019** | **38,021** | 146,040 |

⇒ Under **Reading A** the analysed subset is 77,884 / 108,019 clouds (72% / 74% kept).
⇒ Under **Reading B** the analysed subset is 30,582 / 38,021 clouds (28% / 26% kept).

**Neither reading is baked into any delivered file.** `fall` is carried through verbatim as the string
`True`/`False`, so you can switch readings with a one-line filter. The abstract's own framing — clouds in galaxy
*centers* are the ones flagged and omitted — is a datapoint you may want to weigh, but resolving the
contradiction is your call, not ours. Companion columns `overRatioAll` (velocity-space overlap fraction) and
`EdgeClouds` are also carried through untouched.

---

## 3. THE REDUCTION — SELECTION RULE (deterministic, one sentence)

**Every row and every column of the source table is kept; the ONLY transformation is that each fixed-width field
is cut at its exact ReadMe byte offset, whitespace-trimmed, and re-emitted as CSV with floats rounded to 8
significant figures (`%.8g`) — except `RAdeg`/`DEdeg` at 10 significant figures (`%.10g`), and `Galaxy`, `Env`,
`fall`, `EdgeClouds` copied verbatim as strings — then gzipped.**

**There is NO row subsetting and NO column dropping**, so the reduction carries zero selection bias and both
`fall` readings survive intact. Sizes: 24.46 MiB and 18.18 MiB — both under your 32 MiB per-file ceiling,
42.64 MiB under your 64 MiB total.

Byte-exact compression was tried first and rejected: `xz -9e` on `catnat.dat` extrapolates to ~46.7 MiB, over
your ceiling. Precision reduction was the cheapest way under it. 8 significant figures is far beyond the
measurement precision of any quantity in this catalogue.

### Reduction fidelity — verified against the source, not assumed
- `fall` counts recomputed from the CSV reproduce the raw-file counts exactly (both tables, both values)
- Σ`MassCST` over all 146,040 catnat rows: raw `3.0541025665e10` vs CSV `3.0541025672e10` → **rel. diff 2.3e-10**
- `RAdeg` min/max: raw `24.14553262 / 347.47128426` vs CSV `24.14553262 / 347.47128430` (agree to ~0.04 mas)
- All 41 fields present on every row of both CSVs
- The 5,106 null `RadEqDec` values in `cat30pc` are preserved as **empty cells**, never as 0

### Byte-offset alignment was validated on all 254,506 rows
For every declared field on every row: no trimmed field contains an internal space (which would mean two fields
had merged), no field contains a comma, and every inter-field gap byte is a space. Zero violations in either
table. The only blank field anywhere is `cat30pc.RadEqDec` (5,106 rows), exactly matching its `?` nullable marker
in the ReadMe.

CSV column order is the ReadMe order, 41 columns:
`Cluster, Galaxy, Env, Xpos, Ypos, RAdeg, DEdeg, LPAH, LCO, MassCST, MassSL, MassS, MassB, MassT, RadEq,
RadEqDec, Rad, SDCST, SDSL, SDS, SDB, SDT, Dist, DistRe, fall, overRatioAll, EdgeClouds, e_LPAH, e_LCO,
e_RadDeFin, e_RadFin, e_MassfinCST, e_MassfinSL, e_MassfinS, e_MassfinB, e_MassfinT, e_SDfinCST, e_SDfinSL,
e_SDfinS, e_SDfinB, e_SDfinT`

Load with: `pandas.read_csv("catnat_allrows.csv.gz")` — no network needed, gzip is handled natively.

---

## 4. 🔴 STRUCTURAL FACTS THAT CHANGE WHAT IS VALIDLY COMPUTABLE

1. **`catnat.dat` covers 65 galaxies, `cat30pc.dat` covers 66. `IC5332` is present at 30 pc and ABSENT at native
   resolution.** The abstract and Description say "66 galaxies" for both. Any 30pc-vs-native comparison must drop
   IC5332 or it is comparing different samples.

2. **`catnat.dat` contains `Env = 0.0` on 3,163 rows — a code that does not exist in the ReadMe legend.**
   Note (G1) defines only 1.0–10.0 (Center/Bar/Spiral Arm/Interarm/Disc). `cat30pc.dat` carries the range
   constraint `[1/10]` and has **no** Env=0.0 rows; the `catnat` byte-by-byte description silently drops that
   constraint. Env=0.0 is unclassified/outside the environment mask. **Any environment-binned statistic on
   `catnat` will silently swallow 3,163 unclassified clouds unless they are cut explicitly.**

3. `EdgeClouds=1` on 3,633 / 108,466 (cat30pc) and 4,534 / 146,040 (catnat) rows.

4. The five mass and five surface-density columns are **the same measurement under five different α_CO
   prescriptions** (constant MW, Schinnerer & Leroy 2024, Sun+2020, Bolatto+2013, Teng+2023), not independent
   observables. They are ~perfectly correlated by construction — do not treat them as independent evidence.

5. Masses derive from PAH 7.7 µm via a **linear PAH→CO conversion**, not from CO detections. Only 41% of PAH
   clouds have an ALMA CO counterpart (paper's own cross-match, 27 galaxies at 90 pc).
