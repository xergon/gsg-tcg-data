# 🔴 GALELLIP in `sersicphotometry v09` — RESOLVED FROM THE PUBLISHED SCHEMA

**ANSWER: `GALELLIP_<band>` IS `1 − (b/a)`, i.e. `1 − q`.  The thread's first branch is correct.**
⇒ axis ratio `q = b/a = 1 − GALELLIP_r`.

Confirmed three independent ways, all agreeing:

### 1. The published online schema page
`https://www.gama-survey.org/dr4/schema/table.php?name=SersicCatSDSS`, description column, verbatim:
```
GALELLIP_r   src.ellipticity;meta.modelled;em.opt.r   GALFIT ellipticity (1-(b/a))
```
Identical wording for u, g, i, z.

### 2. The `.par` descriptor shipped beside the data
`https://www.gama-survey.org/dr4/data/cat/SersicPhotometry/v09/SersicCatSDSSv09.par`, line 98:
```
GALELLIP_r        88  -   src.ellipticity;meta.modelled;em.opt.r   GALFIT ellipticity (1-(b/a))
```

### 3. Empirical distribution in the delivered file (221,373 rows)
```
GALELLIP_r  min = 0.00000   p1 = 0.0254   median = 0.3709   p99 = 0.9269   max = 0.99995
fraction < 0 : 0.0        fraction > 1 : 0.0
```
Strictly bounded in [0, 1), never negative, never > 1, and the median implies
median q = 0.629 — the expected value for a magnitude-limited galaxy sample.
Were the column q itself, the distribution would pile up toward 1 and be bounded away from 0.

---

## 🔴 THE SECOND CONVENTION TRAP, WHICH THE THREAD DID **NOT** ASK ABOUT AND WHICH MATTERS MORE

`GALRE_r` is the **SEMI-MAJOR-AXIS** half-light radius, not a circularised one. Verbatim from the
same `.par`, line 96:
```
GALRE_r   86  arcsec  phys.angSize;meta.modelled;em.opt.r
          GALFIT effective (half-light) radius (semi-major axis)
```
(`GALR90_r` is likewise "rad containing 90% of total light (semi-major axis)".)

So the circularised effective radius is
```
R_e,circ = GALRE_r * sqrt(q) = GALRE_r * sqrt(1 - GALELLIP_r)
```
and the **half-light ELLIPSE area is exactly** `A = π·a·b = π·GALRE_r²·(1−GALELLIP_r) = π·R_e,circ²`
— the two routes coincide, which is a useful internal check.

**Consequence for A_IPR.** Getting this wrong is not a small perturbation:
`log10(π·Re_maj²) − log10(π·Re_maj²·q) = −log10(q)`, whose median over the delivered sample is
**0.1931 dex** with an interquartile range of **0.2357 dex**. Because `q` correlates with
morphology and hence with the lensing signal, a wrong choice does **not** cancel in the slope —
it tilts β_A. Both conventions are therefore materialised in the parquet:

| column | definition |
|---|---|
| `A_IPR_kpc2_ellip` | `π · Re_maj_kpc² · q`  ( = `π · Re_circ_kpc²`, the half-light ellipse area ) |
| `A_IPR_kpc2_major` | `π · Re_maj_kpc²`      ( no inclination deprojection ) |
| `log10_A_IPR_ellip` / `log10_A_IPR_major` | log10 of the above |

`axis_ratio_q_r`, `Re_maj_arcsec_r`, `Re_circ_arcsec_r`, `Re_maj_kpc_r`, `Re_circ_kpc_r` and
`GALELLIP_r` itself are all carried, so any third convention can be built without refetching.
