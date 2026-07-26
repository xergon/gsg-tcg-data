# S7 — NIST SRD 161 Th–Ar hollow-cathode FTS, window 7400–9510 cm⁻¹

Source: NIST Standard Reference Database 161, **DOI 10.18434/T4S01V**, version 1.2 (Aug 2017).
Nave, Shlosberg, Redman & Sansonetti. Landing page: https://www.nist.gov/pml/spectrum-th-ar-hollow-cathode-lamps

Retrieved 2026-07-26 from the atlas's only public data route, the CGI
`https://physics.nist.gov/cgi-bin/TH/site.cgi`
with `atlaschoice=Thorium&xscale=Wavenumber&medium=vacuum&units=1/cm&low=<lo>&high=<hi>&current=<mA>&convolve=none&state=init`.
**`convolve=none`** ⇒ native FTS samples, no smoothing, no resampling, no normalisation, no line fitting,
no baseline subtraction. Values are exactly the numbers the archive serves.

## Spectrum metadata (verbatim from Table 1 of the atlas, "Spectra Used in Atlas")

| shard prefix | filename | instrument | current (mA) | resolution (cm⁻¹) | archive range (cm⁻¹) | k_eff | reference |
|---|---|---|---|---|---|---|---|
| `th112805-002_20mA_` | th112805.002 | NIST 2-m FTS | 20 | 0.005 | 3000–15000 | 7.21e−7 | Kerber, Nave & Sansonetti 2008 |
| `790222-008_75mA_` | 790222.008 | NSO/KPNO FTS | 75 | 0.0145 | 7400–11000 | 6.585e−7 | Palmer & Engleman 1983 |
| `820519-001_320mA_` | 820519.001 | NSO/KPNO FTS | 320 | 0.0127 | 1591–9510 | −7.06e−7 | Engleman, Hinkle & Wallace 2003 |

Measured native sample spacing in this window (from the delivered data):
th112805.002 **0.0035763 cm⁻¹** · 790222.008 **0.0115427 cm⁻¹** · 820519.001 **0.0094771 cm⁻¹**.
Delivered rows: 589,998 / 182,801 / 222,642 (995,441 total).

## 🔴 MISSING SPECTRUM — read before designing the resolution test

`th110211.440` (NIST 2-m FTS, **20 mA, 0.020 cm⁻¹**, archive range 8530–27000 cm⁻¹) is **NOT included and
cannot be obtained**. The CGI has **no filename parameter**: `current=20` returns exactly one trace and the
server chooses which 20 mA file by wavenumber. Measured: at σ = 8500 and σ = 9000 the 20 mA trace has
Δσ = 0.0035763 cm⁻¹ (= th112805.002, 0.005 cm⁻¹); at σ = 14990 and σ = 16000 it has Δσ = 0.0143051 cm⁻¹
(= th110211.440, 0.020 cm⁻¹) — exactly 4× apart, as the two resolutions are.
⇒ Inside 8530–9510 cm⁻¹, where the 0.005 and 0.020 spectra overlap on paper, the archive serves **only** the
0.005 file. A same-current 0.005-vs-0.020 resolution comparison in this window is **not constructible** from
SRD 161's public interface. The 0.020 spectrum is reachable only above the crossover (≳ 11000–15000 cm⁻¹),
where the 75 mA and 320 mA spectra no longer overlap it in the same way.
`th112905.003` (20 mA, 0.005, 1750–3100 cm⁻¹) lies entirely outside the window.

## Spectrum shard columns
- `wavenumber_cm_inv` — vacuum wavenumber, cm⁻¹, native FTS sample grid, 6 decimals as served.
- `intensity` — intensity as served. **Plot intensities are scaled so the noise ≈ 1** and are NOT the
  calibrated relative intensities in the line list; they are not comparable in absolute terms between
  spectra. NIST's own caveat.

## `linelist_7400_9510.csv` — 1,398 rows
Columns: `ritz_wavenumber_cm_inv, ritz_unc_cm_inv, measured_wavenumber_cm_inv, measured_unc_cm_inv,
relative_intensity, species, lower_level_energy, lower_J, upper_level_energy, upper_J, reference`.
`-` means the archive gives no value (Ar I has no Ritz wavenumber — its levels were never optimised).
`_odd` replaces the archive's superscript `o` odd-parity marker on J values.
Ritz values come from Redman, Nave & Sansonetti 2014; other columns from the reference in the last column.

## MANIFEST.csv
`shard, spectrum, current_mA, resolution_cm_inv, sigma_min, sigma_max, rows, bytes, sha256`.
Every shard is < 900,000 bytes so the thread's GitHub reader (1,000,000 B/file cap) can open each one.
