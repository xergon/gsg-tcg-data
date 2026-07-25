# Mistele et al. equations 4.1–4.3 — VERBATIM, read from the arXiv LaTeX source

Paper: T. Mistele, S. McGaugh, F. Lelli, J. Schombert, P. Li,
*"Radial acceleration relation of galaxies with joint kinematic and weak-lensing data"*,
JCAP **04** (2024) 020, DOI 10.1088/1475-7516/2024/04/020, arXiv:**2310.15248**.

Source obtained from `https://arxiv.org/e-print/2310.15248` (tarball, main file
`lensing-RAR.tex`), i.e. the LaTeX, not the rendered HTML.

Section 4 is **"Masses and mass distributions"** and contains exactly three numbered equations,
so 4.1 / 4.2 / 4.3 are unambiguous. All three are the **baryonic gas corrections applied to the
stellar mass** to obtain M_bar for g_bar; none of them is the ESD→acceleration deprojection
(that is Eq. 2.11 `eq:gobs_from_esd` in Sec. 2).

### Eq. 4.1 — hot gas (label `eq:fhot`), from Chae et al. 2021b
```
M_g,hot / M_* = 10^(-5.414) * (M_* / M_sun)^0.47
```

### Eq. 4.2 — cold gas (label `eq:fcold`)
```
M_g,cold / M_* = (1/X) * ( 11550 * (M_* / M_sun)^(-0.46) + 0.07 )
```
First term = atomic gas (Lelli et al. 2016 scaling with M_* = 0.5 L_[3.6]); second = molecular gas.

### Eq. 4.3 — hydrogen mass fraction (label `eq:metal`), from McGaugh et al. 2020b
```
X = 0.75 - 38.2 * ( M_* / (1.5e24 M_sun) )^0.22
```

⇒ **M_bar = M_* (1 + f_hot + f_cold)**.

---

## Things in the same paper that bear directly on i2 and are NOT in the thread's brief

1. **Cosmology mismatch.** Mistele et al. adopt **H0 = 73 km/s/Mpc** (`h70 = 73/70`) "for consistency
   with the RAR derived from kinematic measurements". GAMA's `DistancesFrames v14` ships
   `DM_70_30_70` (H0 = 70, Om = 0.3). The delivered parquet is built at **H0 = 70** and carries an
   explicit `h70 = 1.0` column; radii scale as 1/h70 and A_IPR as 1/h70².

2. **The isolation criterion is Brouwer et al. (2021)'s, and Mistele call it "of great practical
   importance".** Verbatim: *"for each lens, we enforce a lower bound R_isol on the 3D distance to
   the closest neighboring galaxy with at least 10% of its stellar mass. We use
   R_isol = 4 Mpc/h70 unless stated otherwise."* Brouwer used 3 Mpc/h70.
   **This is the `D_iso` of i2's destroyer list, and it is the single biggest driver of N.**

3. **Their lens sample after that cut is 106,843** (KiDS-bright, ~1000 deg², 0.1 < z_ANN < 0.5,
   plus a stellar-mass upper limit), "which is less than the 259,383 used by Ref. [Brouwer2021]".

4. **A projected isolation criterion collapses the sample.** Verbatim: *"for
   R_isol,proj = 1 Mpc/h70, there are only 196 lenses left."*
   Reproduced independently on GAMA below: **1,634** at R_isol,proj > 1 Mpc/h70 out of 181,608.

5. **Mistele's isolation uses ANNz2 photometric redshifts** — there are no spectroscopic redshifts
   for KiDS-bright. Photo-z scatter σ_z ≈ 0.02(1+z) is ≈ 90 Mpc in line-of-sight comoving distance
   at z = 0.3, i.e. **>> R_isol = 4 Mpc**. That scatters genuine close neighbours out of the
   isolation sphere, so their 106,843 is an **over-count of truly isolated galaxies**.
   GAMA's spectroscopic redshifts make the same criterion strictly more honest — and strictly
   more restrictive. That is a real methodological gain of the thread's GAMA switch, and it is
   also why the GAMA N cannot be obtained by area-scaling Mistele's number.
