# Phase-23 locked-vector TRANSFER DIAGNOSTIC — per-galaxy and per-ring decomposition

Computed by Cat (orchestrator), TRUE UTC `2026-07-28T21:18:19Z` (`date -u`; the local clock is
UTC+4 and was not used).

**This is a COMPUTE product. No model was fitted, tuned, modified or proposed.** Every number below
comes from the frozen Phase-120 vector applied verbatim to three galaxy samples. The interpretation
belongs to the ChatGPT Pro thread that receives this file.

---

## 🔴 THE UNDERPOWERED CAVEAT — READ THIS BEFORE ANY CORRELATION IN `correlations.csv`

`correlations.csv` reports Spearman and Pearson coefficients between the per-galaxy
`dlnB_locked_minus_MOND` and each covariate. **These are DESCRIPTIVE STATISTICS ONLY.**

- The external held-out pool is **n = 16 galaxies** (12 LITTLE THINGS + 4 THINGS). With 23 covariates
  screened at n = 16, the expected number of |Spearman| > 0.5 hits under a pure null is of order one.
  **Nothing in the external block can support a model-selection claim.** Not one entry there reaches
  p < 0.05 even before any multiplicity correction.
- The pooled block (n = 179) is dominated 163/179 by SPARC, which is the *training* sample. A pooled
  correlation is therefore mostly a within-SPARC correlation, not a transfer diagnostic.
- No multiplicity correction of any kind has been applied. No covariate has been ranked by "promise",
  and no covariate is recommended.
- **Downstream: do not treat any coefficient here as evidence for or against anything.** Use them to
  decide which *larger* sample is worth sourcing, not to conclude.

---

## The frozen vector — used verbatim, never refitted

```
a0     = 1.1141506080465188e-10   m s^-2
L*     = 0.39992170918182096      kpc      (0.39992170918182096 * 3.0856775814913673e19 m)
q      = 0.6663695144357871
Y_disk = 0.5
Y_bulge= 0.7   (SPARC pipeline contract, src/tcg/data.py:220-221; see "bulge" note below)
```

Gate: `S(L_b) = 1 - exp(-(L_b/L*)^q)` with **`L_b = R` (galactocentric radius, metres)** — NOT a
gradient scale. Prediction: `g_pred = g_bar + S * (g_MOND(g_bar; a0) - g_bar)`,
`g_MOND = g_bar / (1 - exp(-sqrt(g_bar/a0)))`.
Likelihood: Gaussian in `log10 g`, `sigma^2 = (0.434 * e_gobs / g_obs)^2 + sigma_int^2`, unweighted
rings, no per-galaxy nuisance, **no distance term, no inclination term**.

All of the above is imported unchanged from
`implementation_lanes/phase23_locked_evaluator_spec_2026_07_22/phase23_locked_evaluator.py`
(sha256 `d8657ff4df80d0ef7a036fd899fd0d7bc9f3d56bea165ff3c00732b07a5e5336`). The evaluator module was
**imported and called**, not rewritten.

## The k=1 vs k=1 comparison and how `dlnB` is computed here

`dlnB_locked_minus_MOND = lnZ(gate at the locked vector) − lnZ(plain MOND at the SAME a0)`.
Both sides have exactly ONE free parameter, `log10 sigma_int`, uniform on `[-3, 0]`
(`BOUNDS_LOCKED_K1`, evaluator line 117).

The marginal likelihood is computed by **deterministic 1-D quadrature** over that prior box
(20 001-point trapezoid in `log10 sigma_int`), NOT by nested sampling. Reason: the per-galaxy
decomposition needs a *noiseless* estimator — dynesty's ±0.18 sampling error would swamp per-galaxy
differences of order 1. The quadrature is exact for a 1-D box prior and seed-independent.
**Calibration: it reproduces the recorded SPARC number.** See below.

## 🔴 PARSE CALIBRATION — reproduced before anything was trusted

| anchor | recorded | this run | delta |
|---|---|---|---|
| SPARC row count after Phase-23 cuts | 3269 | **3269** | 0 |
| SPARC galaxy count (Q<=2) | 163 | **163** | 0 |
| SPARC joint `dlnB` (locked k=1 vs MOND k=1) | **+27.071 ± 0.183** | **+27.0908** | +0.020 (0.11 sigma) |
| THINGS-4 ring count | 418 | **418** | 0 |
| THINGS-4 per-galaxy NGC 3031 | −0.326 | **−0.3259** | 0.0001 |
| THINGS-4 per-galaxy NGC 3621 | −6.056 | **−6.0558** | 0.0002 |
| THINGS-4 per-galaxy NGC 925 | +2.954 | **+2.9505** | 0.0035 |
| THINGS-4 per-galaxy NGC 4736 | −1.512 | **−1.5024** | 0.0096 |

**The THINGS-4 per-galaxy decomposition is reproduced independently to ≤ 0.010 on all four galaxies.**
That is the strongest possible calibration of the THINGS parse and of the scorer.

**SPARC .mrt parse:** the repository's own loaders were used (`tcg.data.load_galaxies`,
`load_massmodels`, `build_rar_table(quality_max=2)`), which tokenise by whitespace and do **not**
honour the CDS byte offsets — this is the recorded convention and is what reproduces 3269/163/+27.09.
`Vflat = 0` rows are kept: that is a sample-definition fact, not a parse failure.

### Two joint numbers that did NOT reproduce, stated plainly

- **THINGS-4 joint.** Recorded (S5): **−3.2527** over 418 rings. This run's σ-marginalised joint is
  **−0.4815**. The per-galaxy values reproduce to ≤0.010 (above), so the difference is a *pooling /
  σ_int convention* difference, not a data or model difference. For reference, the joint ΔlnL at the
  **fixed** Phase-120 bulk σ_int (0.07115 dex) is **−3.1427**, and the sum of the four independently
  σ-marginalised per-galaxy values is **−4.9336**. All three poolings are reported; none is claimed
  to be "the" number. **Whatever the pooling, the sign is negative and the per-galaxy pattern is
  identical.**
- **LITTLE THINGS-12 joint.** Recorded (C-Pincer): **−12.221** over 182 rings. This run gets
  **185 rings** (every row in the 12 non-SPARC blocks of `little_things_sample.yaml` survives the
  `gbar>0 & gobs>0 & isfinite(e_gobs)` cut; C-Pincer's 182 implies three further rows were dropped by
  a rule that is not recorded) and **dlnB = −5.1158**. Not reproduced. Sign agrees, magnitude does not.
  See the M/L ambiguity immediately below — it is the most likely cause and it is large.

## The two convention choices that are genuinely ambiguous, and how they were handled

Both are reported as **two columns**, never silently resolved.

1. **LITTLE THINGS stellar M/L.** `little_things_sample.yaml` gives `v_stars` already decomposed
   (digitised from the Oh+2015 figures) plus a per-galaxy `y_fit` (0.26–0.56). There is no photometry
   in the file, so "apply Y_disk = 0.5" has two readings.
   - `dlnB_locked_minus_MOND` (**primary**) = `v_stars` used **as published**. Joint **−5.1158**, 185 rings.
   - `dlnB_alt_ML_convention` = `v_stars` rescaled by `sqrt(0.5 / y_fit)`. Joint **−0.7073**, 184 rings.
   The two differ by more than 4 lnB units jointly and flip the sign of individual galaxies
   (e.g. DDO 133: −6.469 → +2.212; DDO 70: −3.817 → +4.196). **Any downstream reading of the
   LITTLE THINGS per-galaxy pattern must state which column it used.**
2. **THINGS bulges.** The frozen-vector brief says "no bulges"; the SPARC pipeline the vector was
   locked on uses `Y_bulge = 0.7`. NGC 3031 and NGC 4736 have bulges in de Blok+2008; NGC 925 and
   NGC 3621 do not.
   - `dlnB_locked_minus_MOND` (**primary**) = bulge included at `Y_bulge = 0.7` — this is the column
     that reproduces S5 to ≤0.010, so it is what S5 did.
   - `dlnB_alt_ML_convention` = bulge dropped. Only NGC 3031 (−0.326 → −0.336) and NGC 4736
     (−1.502 → −2.464) move; **the +2.951 / −6.056 contrast between NGC 925 and NGC 3621 is bulge-free
     in both conventions.**

THINGS disk velocities are taken from the `ISO.fix.REV` variant, whose header carries `par_MD = 1.0`
— i.e. `Vdisk` there is the M/L = 1 disk (verified: the `.Kr` variant's `Vdisk` is exactly
`sqrt(0.71)×` it, matching its `par_MD = 0.71`). `Y_disk = 0.5` is then applied by this code.
de Blok's `Vgas` is **signed**; the `V*|V|` rule is used, matching SPARC's own
`V_b^2 = |Vgas|Vgas + Y_disk|Vdisk|Vdisk + Y_bulge|Vbul|Vbul` (`src/tcg/data.py:238-239`).

---

## Files

| file | rows | what |
|---|---|---|
| `per_galaxy.csv` | **179** | one row per galaxy, all three samples, ΔlnB + covariates |
| `per_ring_shard01.csv` / `per_ring_shard02.csv` | **3872** | one row per ring |
| `correlations.csv` | 69 | 23 covariates × 3 subsets, Spearman + Pearson with n and p |
| `joint_evidence.json` | – | joint lnZ / ΔlnB / posterior-mean σ_int per sample |
| `SOURCE_CHECKSUMS.txt` | – | sha256 + byte size of every input file read |
| `INPUT_little_things_sample.yaml` | – | the Zenodo file, md5 `b5a8e1e971150f59060aec66190b35a6` verified |
| `CODE_build_tables.py`, `CODE_analyze.py`, `CODE_package.py` | – | the exact code that produced this |
| `MANIFEST.csv` | – | filename, bytes, rows, sha256 |

### Per-sample counts — asserted, non-zero, all three

| sample | galaxies | rings |
|---|---|---|
| `sparc` | **163** | **3269** |
| `little_things_12` | **12** | **185** |
| `things_4` | **4** | **418** |

### `per_galaxy.csv` columns

`sample, galaxy, n_rings, dlnB_locked_minus_MOND, dlnB_alt_ML_convention,
dlnL_sum_at_joint_sigma, lnZ_gate, lnZ_mond, sigma_int_gate_dex, sigma_int_mond_dex,
morph_type_T, class_dwarf_or_spiral, class_HSB_LSB, distance_Mpc, e_distance_Mpc,
distance_method_code, inclination_deg, e_inclination_deg, Vflat_kms, e_Vflat_kms,
Mbar_Msun, Mstar_Msun, Mgas_Msun, gas_fraction, central_SB_disk_Lsun_pc2, SB_eff_Lsun_pc2,
mean_Sigma_bar_Msun_pc2, Rdisk_kpc, Reff_kpc, RHI_kpc, R_min_kpc, R_max_kpc,
R_min_over_Rd, R_max_over_Rd, gbar_median, gobs_median, quality_flag, abs_Vmag,
abs_Bmag, metallicity_12logOH, y_star_fit`

`dlnL_sum_at_joint_sigma` is the additive per-galaxy share of the JOINT number: the sum of that
galaxy's `dlnB_ring` values. It sums exactly to the joint ΔlnL. `dlnB_locked_minus_MOND` is the
galaxy's own σ-marginalised evidence ratio and does **not** sum to the joint — that is correct, not a
bug: marginalising σ_int per galaxy is a different (and more informative-per-galaxy) quantity.

### `per_ring_*.csv` columns

`sample, galaxy, R_kpc, R_over_Rd, V_obs_kms, V_bar_kms, g_obs, g_bar, e_gobs,
g_pred_gate, g_pred_mond, dlnB_ring`

`dlnB_ring` = that ring's contribution to the joint ΔlnL, evaluated at each model's own
posterior-mean σ_int from the joint fit of that sample. **Sums exactly to the joint ΔlnL** (SPARC
+27.0958, LT-12 −5.0954, THINGS-4 −0.4771), so the failure can be located in radius.

## NOT_RECORDED — covariates that could not be sourced from a catalogue, and were NOT invented

- **Disk scale length `Rdisk`, `Reff`, central surface brightness**: available for SPARC only
  (Lelli+2016 Table 1). No staged LITTLE THINGS or THINGS product carries them. `R_over_Rd`,
  `R_min_over_Rd`, `R_max_over_Rd`, `class_HSB_LSB` are therefore `NaN` / `NOT_RECORDED` for the two
  external samples — which is exactly why the external correlation block has n = 0 for those rows.
- **Morphological type** for the LITTLE THINGS 12: not in any staged product (`NaN`); they are
  labelled `dwarf_irregular_LT_sample` by sample membership.
- **`e_distance_Mpc`** for THINGS-4: not tabulated in Walter+2008 Table 1 (`NaN`); the distance
  *method* code is given (`r_Dist`: `F01`, `K04`).
- **LITTLE THINGS `Mstar` / `Mgas`** are the yaml's own `m_stars` / `m_gas` (the values consistent
  with the `v_stars`/`v_gas` curves actually scored). **THINGS-4** baryonic masses are
  `V^2 R / G` at the outermost ring of each component, i.e. derived from the same curves that were
  scored — flagged here because they are *not* independent catalogue scalars.
- Gas-mass scales are **not** harmonised across samples: SPARC `Mgas = 1.33 × MHI`; de Blok+2008
  `Vgas` already includes helium+metals (×1.4); the LT yaml `m_gas` is the source's own value. Any
  cross-sample gas-fraction comparison inherits that inconsistency.

## Provenance of every input

See `SOURCE_CHECKSUMS.txt`. Summary:

- SPARC: `data/sparc/SPARC_Lelli2016c.mrt`, `data/sparc/MassModels_Lelli2016c.mrt` (Lelli+2016c),
  read through the repository's own loaders.
- LITTLE THINGS: `little_things_sample.yaml`, Zenodo record **20397291**
  (DOI 10.5281/zenodo.20397291, "For modified gravity, it's the LITTLE THINGS that matter"),
  81 580 B, **md5 `b5a8e1e971150f59060aec66190b35a6` verified on download** (HTTP 200),
  sha256 `77f405d6f9d28f09dd8796bdfccd21cc51cc10a376a234942bf166434ceebd7b`.
  20 galaxies; the 12 scored = 20 − {WLM, IC 1613} − {DDO 126, DDO 154, DDO 168, DDO 50, DDO 87,
  NGC 2366}. Its baryonic curves are **digitised from the Oh+2015 figures**, not author-tabulated.
- THINGS: `things_deblok2008_massmodels_tidy.csv` (130 GIPSY ROTMAS files, de Blok+2008) and
  `walter2008_table1_things_sample.csv`, both from
  `implementation_lanes/phase23_external_heldout_sources_2026_07_22/C_things_littlethings/`.
  The 4 scored = the 17 de Blok mass-model galaxies minus the 13 with a SPARC `Rotmod_LTG` file.
- Covariates: SPARC Table 1 (Lelli+2016c); Oh+2015 Tables 1–2; Walter+2008 Table 1.

## What was deliberately NOT done

No model was modified. No parameter was refitted, profiled or tuned. No revised formula is proposed.
No covariate is ranked or recommended. No conclusion is drawn about why NGC 925 and NGC 3621 differ.
