# 🔴 i2 REPAIR — the Sérsic K(n) participation-area factor

**Date (TRUE UTC): 2026-07-26T04:16:03Z**
**Found by: ChatGPT Pro thread i2. Reproduced independently on disk before any action was taken.**

---

## 1. The defect, verbatim

`build_lens_table.py`, lines **213-214** of the v1 build, read exactly:

```python
df["A_IPR_kpc2_ellip"]  = np.pi * (df["Re_maj_kpc_r"] ** 2) * q      # = pi*a*b = pi*Re_circ^2
df["A_IPR_kpc2_major"]  = np.pi * (df["Re_maj_kpc_r"] ** 2)          # no inclination deprojection
```

Those are **half-light areas**. They are *not* participation areas, and the columns are named
`A_IPR_*`. The programme's canonical inverse-participation statistic
(`LEAD_SPARC_RAR_AEFF_IPR_DISCRIMINATOR.md`, lines 129-132) is

```
IPR   = ∫ s(R)² dA / [∫ s(R) dA]²
A_eff = 1 / IPR = (∫ s dA)² / ∫ s² dA
R_IPR = sqrt(A_eff / π)
X_A   = log10(R_IPR / 1 kpc)
```

`π Re²` is that quantity **only for a profile that happens to give K(n) = 1**, which no Sérsic
profile in the sample does. ⇒ Any downstream use of the v1 `A_IPR_*` columns as participation
areas was wrong, and the error is **n-dependent**, so it does **not** cancel in a slope.

## 2. The correct factor

For `I(R) = I_e exp(−b_n[(R/Re)^(1/n) − 1])` on elliptical isophotes of axis ratio `q`
(`dA = 2π q R dR`, `R` = semi-major coordinate):

```
∫ I  dA = 2π q Re² I_e   e^( b_n) n Γ(2n)   b_n^(−2n)
∫ I² dA = 2π q Re² I_e²  e^(2b_n) n Γ(2n) (2b_n)^(−2n)
```

```
⇒  A_IPR = π · q · Re_maj² · K(n)        with        K(n) = 2 n Γ(2n) · 4ⁿ · b_n^(−2n)
```

`b_n` is solved **exactly** as the median of the Gamma(2n) distribution
(`scipy.special.gammaincinv(2n, 0.5)`) — **not** the `b_n ≈ 2n − 1/3` series, which is invalid at
the low-n end of this sample's `0.1 < GALINDEX_r < 20` cut. All factors are evaluated in log space
(`Γ(40) ≈ 2×10⁴⁶` overflows a naive product).

**Independent confirmations of K(n), all in `repair_A_IPR_Kn.py` and printed at run time:**

| check | value |
|---|---|
| `K(1)` closed form (exponential disk: `A_IPR = 8π h²`, `Re = 1.6783 h`) | **2.840053** |
| `K(1)` analytic formula above | **2.840053** ✔ |
| `K(1)` by direct numerical integration of the profile | **2.840053** ✔ |
| `K(4)` analytic / numerical | **0.862457 / 0.862457** ✔ |
| `K(10)` analytic / numerical | 0.034015 / 0.034100 ✔ (trapezoid tail) |
| `K_IPR(0.5) == K_tot(0.5)` (because `e^{b}=e^{ln2}=2=4^{0.5}` exactly at n=½) | **2.885390** both ✔ |

⚠ An earlier draft of this repair wrote `4^(2n)` instead of `4^n` and was **caught by the
numerical-integration cross-check before anything was written or published.** That check is
retained in the script and runs on every execution.

## 3. What was changed — ADDITIVE ONLY

**Nothing was overwritten or deleted.** `gama_kidslegacy_ipr_rar_inputs_v1.parquet` is unchanged
on disk and its GitHub release asset is untouched. The v1 columns are carried into v2
**bit-identically** (asserted by the script: `np.array_equal` → `True`).

New file: **`gama_kidslegacy_ipr_rar_inputs_v2.parquet`** — 181,608 rows × **94** columns
(85 v1 columns + 9 new).

| new column | definition |
|---|---|
| `sersic_bn_r` | `b_n` for `GALINDEX_r`, exact (`gammaincinv(2n, ½)`) |
| `K_IPR_sersic_r` | `K(n) = 2 n Γ(2n) 4ⁿ b_n^(−2n)` — **the repair factor** |
| `K_totlight_sersic_r` | alternative convention `L_tot/I_e = π Re² K_tot(n)`, `K_tot(n) = 2 n Γ(2n) e^{b_n} b_n^(−2n)`. **Not** used for `A_IPR_*_Kn`; shipped so the thread can switch convention without a round-trip. `K_tot(1) = 3.803324`. |
| **`A_IPR_kpc2_ellip_Kn`** | `A_IPR_kpc2_ellip · K(n)` — **the corrected participation area** |
| **`A_IPR_kpc2_major_Kn`** | `A_IPR_kpc2_major · K(n)` |
| `log10_A_IPR_ellip_Kn` | **the corrected regressor X** (supersedes `log10_A_IPR_ellip`) |
| `log10_A_IPR_major_Kn` | as above, major-axis convention |
| `R_IPR_kpc_ellip_Kn` | `sqrt(A_IPR_kpc2_ellip_Kn / π)` |
| `X_A_ellip_Kn` | `log10(R_IPR_kpc_ellip_Kn)` — the canonical `X_A` of the lead doc |

### ⛔ SUPERSEDED — do not use as participation areas

`A_IPR_kpc2_ellip`, `A_IPR_kpc2_major`, `log10_A_IPR_ellip`, `log10_A_IPR_major`.
They remain valid as **half-light areas** (`π Re_circ²`, `π Re_maj²`) and are retained for exactly
that reason, and so that any number computed before 2026-07-26 stays reproducible.

## 4. Verification of the written artifact (re-read from disk)

```
rows = 181,608   cols = 94
GALINDEX_r      min=0.1          median=1.8274    max=19.9999   nonfinite=0
sersic_bn_r     min=0.0207463    median=3.32742   max=39.667    nonfinite=0
K_IPR_sersic_r  min=0.000103663  median=2.25061   max=2.92703   nonfinite=0

ratio A_IPR_kpc2_ellip_Kn / A_IPR_kpc2_ellip : min=0.000103663  median=2.25061  max=2.92703
ratio A_IPR_kpc2_major_Kn / A_IPR_kpc2_major : min=0.000103663  median=2.25061  max=2.92703
(identical by construction — the two areas differ only by q, which K(n) does not touch)

K_IPR percentiles:
  p0.1=0.000104  p1=0.003047  p5=0.233489  p25=1.168457  p50=2.250615
  p75=2.823686   p95=2.923617 p99=2.926889 p99.9=2.927031

v1 A_IPR_* columns bit-identical in v2: True
```

**Median correction = ×2.25 — order unity, as required.** ✔

## 5. 🔴 What this changes for the science — read this part

1. **The correction is strongly n-dependent, and therefore morphology-dependent.**
   `K` runs from 2.93 (n ≈ 0.75, its peak) down to 1.0×10⁻⁴ at n = 20. It is **not** a constant
   offset: it re-orders galaxies in `log10 A_IPR`. A slope `β_A` fitted on the v1 column is a slope
   against a **different regressor**, not a rescaled one, and cannot be corrected after the fact.
   The **v1-based `β_A` forecast and the `SE(β_A) ≈ 0.03739` power arithmetic in `POWER_GO_NOGO.md`
   are unaffected** (they depend on N, not on X), but any *fitted* `β_A` on the v1 column must be
   refitted on `log10_A_IPR_ellip_Kn`.
2. **`log10 A_IPR` spread is now much larger.** Because K spans 4.5 decades, `log10 A_IPR_Kn` has a
   substantially wider dynamic range than `log10 A_IPR`. That **helps** the test: `SE(β) ∝ 1/sd(X)`,
   so the effective leverage per lens goes up. The `ΔX = 0.90` figure in `POWER_GO_NOGO.md` was
   computed on the v1 regressor and is now a **lower bound** — recompute it on the Kn column.
3. **⚠ The Sérsic-index ceiling now matters far more than it did.**
   `GALINDEX_r ≥ 19.99` for **245 lenses** and `> 15` for **1,618**; `> 8` for **5,568**.
   These are the GALFIT non-convergence pile-up leaking past the `n < 20` bound (the v1 README
   excludes only `n == 20` exactly). Under `K(n)` they acquire the most extreme `A_IPR` values in
   the sample — `K(19.9999) = 1.04×10⁻⁴` — i.e. **the least trustworthy fits become the highest-
   leverage points in the regression.** Recommend a preregistered `GALINDEX_r < 8` (or `< 6`)
   quality cut *before* the fit, declared before looking at `β_A`. This was harmless with the
   v1 half-light column and is a first-order threat with the corrected one.
4. `β_R = 2 β_A` consistency check: **no longer valid as stated.** With `A_IPR = π q Re² K(n)`,
   `log A_IPR = 2 log Re_circ + log K(n) + const`, so the check holds only at fixed `n`. Either run
   it in narrow `n` bins or drop it.

## 6. Sibling sweep — result

The whole `implementation_lanes/` tree (519 lanes) was grepped for the same build pattern
(`math.pi`/`np.pi` × a squared effective radius). **Only this one site computes a column named as a
participation area from `π Re²`.** All other hits are a *different and correct* quantity:

| file:line | expression | verdict |
|---|---|---|
| `fleet_fanout_harvest_2026_07_25/i2_gama_kidslegacy/build/build_lens_table.py:213` | `np.pi*Re_maj_kpc**2*q` | **THE DEFECT** |
| `fleet_fanout_harvest_2026_07_25/i2_gama_kidslegacy/build/build_lens_table.py:214` | `np.pi*Re_maj_kpc**2` | **THE DEFECT** |
| `card2_gamma_participation_realML_2026_07_21/scripts/card2_pipeline.py:319` and `card2_pipeline_v2.py:319` | `Aeff = math.pi*(Reff*1e3)**2` | ⚠ **named `Aeff` in a lane named "gamma_participation"** — but used only as the denominator of a mean-surface-density proxy `Σ = M/(π Re²)` (same file, line 443). Correct for that use, misleadingly named. **Not repaired — it never enters an IPR statistic.** |
| `card2_pipeline{,_v2}.py:443` | `(M*/(math.pi*(Reff*1e3)**2))` | mean surface density — correct |
| `r5_1_coldeye_values_structure_arm_2026_07_14/work/stage2_degraded_covariates.py:108` | `SBeff = 0.5*Ltot/(math.pi*(Re*1e3)**2)` | **correct** — half the light over the half-light area is the textbook `⟨μ⟩_e` |
| `seg0_f1_execution_2026_07_19/stage_s.py:137`, `seg0_f1_cleanroom_rerun_2026_07_19/stage_s_cleanroom.py:156` | `Mb/(math.pi*Reff²*1e6)` | mean surface density — correct |
| `r5_1_coldeye_values_structure_arm_2026_07_14/work/stage1_xa_gate.py:80-82` | `I1=∫s dA; I2=∫s² dA; A_eff=I1²/I2` | **the canonical IPR, computed by direct integration — correct, and the reference implementation this repair reproduces analytically** |
| `.../stage_s*.py:126,91`, `c_triangle_ext_cmk1/step1:61`, `mwrider_compute.py:178` | `π(b_j² − b_{j−1}²)` | annulus areas — correct |
| all `beam_area = math.pi*bmaj*bmin/(4 ln2)` sites | Gaussian beam area | correct |
| `c_pincer_huang2021.../vendor/jianbing/profile.py:58` | vendor code, not ours | out of scope |

**⇒ One defective site, in one file, in one delivery. No sibling delivery is affected.**

## 7. Reproduce

`repair_A_IPR_Kn.py` is published alongside the data. It reads v1, writes v2 and the companion
table, and re-opens what it wrote to verify. Run with the numpy thread pins:

```
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 python3 repair_A_IPR_Kn.py
```
