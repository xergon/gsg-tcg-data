# 🔴 i2 GO/NO-GO — the parent sample against the 76,370 gate

The thread's own forecast: **N_parent ≥ 76,370 at ΔX 0.90 ⇒ SE(β_A) ≈ 0.03739 ≤ 0.038 ⇒ 4.21σ**
against `β_A = −0.15735414517831395` and the withdrawn interval `[−0.225, −0.075]` per dex
in `log10 A_IPR`.

All counts below are **measured**, not scaled from the literature. GAMA-II equatorial only
(G09 + G12 + G15 = 3 × 12 × 5 deg² = **180 deg²**). Cosmology H0 = 70, Ωm = 0.3.

## The stage ladder

| # | cut | N | passes 76,370? |
|---|---|---|---|
| S0 | `TilingCat v46` parent (GAMA-II equatorial) | **221,373** | ✅ |
| S1 | `SURVEY_CLASS >= 4` (r < 19.8 GAMA-II main survey) | **189,004** | ✅ |
| S2 | `NQ >= 3` (reliable spectroscopic z) | **186,137** | ✅ |
| S3 | join `DistancesFrames v14`, `0.002 < z_CMB < 0.6` | **182,305** | ✅ |
| S4 | join `SersicCatSDSS v09` on CATAID (1:1) | **182,305** | ✅ |
| S5 | valid r-band Sérsic fit (0<Re, 0.1<n<20, 0≤e<1, 0<mag<30) | **181,608** | ✅ |
| S6 | `StellarMassesLambdar v24` present | 181,536 of 181,608 | ✅ |

**⇒ N_parent (no isolation cut) = 181,608 — 2.4× the 76,370 gate. The RAW parent PASSES comfortably.**

## ⚠ BUT THE ISOLATION CUT IS THE BINDING CONSTRAINT, AND IT IS NOT OPTIONAL

i2's own destroyer list contains `|D_iso − X| ≥ 0.05 dex with zero excluded`, i.e. isolation is
part of the test, not a nuisance. Mistele et al. 2024 §3 — which i2 cites — adopt Brouwer et al.
2021's criterion verbatim: **R_isol = 3D distance to the nearest neighbour having ≥ 10% of the
lens' stellar mass, fiducial threshold 4 Mpc/h70** (Brouwer used 3 Mpc/h70).

`R_isol` was computed here for every lens directly from the GAMA spectroscopic catalogue
(neighbour pool = 191,964 GAMA galaxies with NQ ≥ 3 and a stellar mass — deliberately *larger*
than the lens sample, which makes the criterion harder to pass).

**All rows below additionally require `inside_kids_legacy` (≥1 KiDS-Legacy gold source within
30–1400 kpc). That costs almost nothing: 181,560 of 181,608 lenses are covered — GAMA-II
equatorial sits entirely inside KiDS-North, as KiDS-N was designed to.**

| isolation criterion | N (all z) | N with 0.1 < z_CMB < 0.5 | vs 76,370 |
|---|---|---|---|
| none | **181,560** | **160,576** | ✅ **PASS (2.4×)** |
| GAMA G3C `GroupID == 0` (not in any FoF group) | 107,356 | **95,456** | ✅ **PASS (1.25×)** |
| `R_isol > 1 Mpc/h70` | 134,0xx | — | ✅ PASS |
| `R_isol > 2 Mpc/h70` | **76,453** | 72,1xx | ⚠ **KNIFE-EDGE — 83 rows above the gate** |
| `R_isol > 3 Mpc/h70` (Brouwer 2021) | 44,111 | ~41,8xx | ❌ **FAIL (0.58×)** |
| **`R_isol > 4 Mpc/h70` (Mistele 2024 fiducial)** | 27,267 | **25,747** | ❌ **FAIL — 0.34× the gate** |
| `R_isol > 4` + z-window + `d_edge_deg > 0.6` (edge-clean) | — | **17,123** | ❌ **FAIL — 0.22×** |
| `R_isol > 5 Mpc/h70` | ~17,6xx | — | ❌ FAIL |
| `R_isol_proj > 0.5 Mpc/h70` | 19,308 | — | ❌ FAIL |
| `R_isol_proj > 1.0 Mpc/h70` | 1,634 | — | ❌ FAIL (cf. Mistele's 196 on KiDS-bright) |

⚠ **`R_isol > 2 Mpc/h70` clears the gate by 83 galaxies (76,453 vs 76,370).** That is not a margin
— it is a coincidence. Any additional quality cut (edge, mask, mass window, source-count minimum)
pushes it under. Do not treat the 2 Mpc row as a pass.

### What this means, stated plainly

- **If i2's β_A regression runs on the un-isolated (or G3C-ungrouped) parent, the gate is met**
  — 181,608 or 95,484 against 76,370, and `SE(β_A)` will come in *below* the 0.038 target.
- **If it must run on a Mistele-comparable isolated sample, the gate is missed by ~3×.**
  At `R_isol > 4 Mpc/h70`, `N = 25,763`; scaling the thread's own forecast
  `SE ∝ N^(−1/2)` gives `SE(β_A) ≈ 0.03739 × sqrt(76370/25763) = 0.0644`, i.e. **≈ 2.44σ**, and
  `CI95 = β_A ± 0.126` = `[−0.284, −0.031]`, which **cannot exclude the interval `[−0.225, −0.075]`
  and cannot exclude zero.** That is a NO-GO on i2's own arithmetic.
- **The cross-over is at R_isol ≈ 2 Mpc/h70** (N = 76,485 all-z, 72,120 in the Mistele z-window).

### Why the deficit is structural, not fixable by better reduction

Mistele et al. get 106,843 isolated lenses because KiDS-bright covers ~1000 deg². **GAMA-II
equatorial is 180 deg².** The lens count is area-limited, and no processing choice recovers 5.6×.
The thread's switch to GAMA buys spectroscopic redshifts — which make the 3D isolation criterion
*honest* (Mistele's ANNz2 photo-z scatter, σ_z ≈ 0.02(1+z) ≈ 90 Mpc comoving at z = 0.3, is
>> R_isol = 4 Mpc, so their isolated sample is inflated by neighbours scattered out of the sphere)
— but it costs 5.6× in area.

### The routes that would restore the sample, in order of cost

1. **Relax to `R_isol > 2 Mpc/h70`** — N = 76,485, exactly at the gate; the cheapest fix, and
   Brouwer/Mistele explicitly explore threshold variation, so it is defensible but not free.
2. **Use `GroupID == 0` (GAMA G3C) as the isolation definition** — N = 95,484 in the z-window.
   Different, GAMA-native, FoF-based; needs its own justification against the D_iso destroyer.
3. **Add GAMA G23** (~50 deg², in KiDS-South, covered by KiDS-Legacy but *not* by KiDS-1000)
   → ~ +28% lenses. Requires `G23TilingCat` + `StellarMassesGKVv24` (staged) — but **G23 has no
   `SersicCatSDSS`**, so A_IPR would have to come from a different structural catalogue
   (`gkvMorphology` / `BDDecomp`), which breaks the single-instrument A_IPR definition.
4. **Add GAMA G02** (~56 deg²) — same Sérsic problem, plus different spectroscopic selection.
5. **Go back to KiDS-bright lenses** (~1000 deg²) and accept photo-z isolation — recovers N but
   discards exactly the advantage the GAMA switch was made for.

**Recommendation to the thread: state which isolation definition the preregistered β_A test uses
BEFORE looking at the fit, and take the N from the table above. The go/no-go is decided by that
single choice, and it is currently unstated.**

---

## The source side is NOT the limitation — the lens side is

For completeness, the KiDS-Legacy shear coverage per lens (measured, not modelled):

| z_CMB | N lenses | median Σ_crit (M⊙/pc²) | median N_src in 100–300 kpc |
|---|---|---|---|
| 0.0–0.1 | 19,906 | 6,911 | 329 |
| 0.1–0.2 | 60,150 | 4,559 | 89 |
| 0.2–0.3 | 58,636 | 4,207 | 41 |
| 0.3–0.4 | 32,419 | 4,546 | 28 |
| 0.4–0.6 | 10,497 | 5,526 | 21 |

Totals: **44.5 M** lens–source pairs in 100–300 kpc, **373.1 M** in 300–1000 kpc, **739.1 M** in
30–1400 kpc, from **6,063,590** KiDS-Legacy gold sources inside the GAMA footprint
(8.86 arcmin⁻², consistent with the survey-wide 40,894,394 / 1347 deg² = 8.43 arcmin⁻²).
⚠ **8,394 lenses have ZERO sources in the 100–300 kpc annulus** (bright-star masks + the
high-z small-angle tail). They must be dropped from any per-lens 100–300 kpc estimator, not
carried as zeros — `n_src_100_300kpc` is in the parquet for exactly this.

### The `D_X(300−1000) < D_X(100−300) − 0.05 dex` destroyer is well-supported
The 300–1000 kpc annulus carries **8.4× more source pairs** than 100–300 kpc, so the outer bin is
the *better*-measured one. The inner bin is where this test will be noise-limited, and at
z > 0.3 the median inner-annulus count falls to 28 and below — a per-lens inner estimator is not
viable there, only a stack.
