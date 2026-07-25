# i3 — VERTICO (CO) + VIVA (HI) chemical-phase-blindness arena

Delivery for row **i3**. Everything below is public, verified by content (FITS `SIMPLE  =` magic + exact
byte-count match against the publisher's VOSpace node lengths), and reachable without registration.

---

## 1. Canonical locations and DOIs

| Product | Identifier | Landing / access |
|---|---|---|
| VERTICO CO(2−1) data products (the actual files) | **DOI `10.11570/23.0018`** (CADC/CANFAR, minted, publisher = CADC, title "VERTICO: The Virgo Environment Traced in CO Survey", Brown T. & The VERTICO Collaboration, 2023) | `https://www.canfar.net/citation/landing?doi=23.0018` |
| VERTICO survey paper | DOI `10.3847/1538-4365/ac28f5` (Brown et al. 2021, ApJS 257, 21) | IOP |
| VERTICO tables 1+2+3 | VizieR `J/ApJS/257/21`, DOI `10.26093/cds/vizier.22570021` | `https://cdsarc.cds.unistra.fr/viz-bin/cat/J/ApJS/257/21` |
| ALMA Large Programme | `2019.1.00763.L` (+ archival PHANGS-ALMA and `2016.1.00912.S` for NGC 4402) | ALMA archive |
| VIVA survey paper | DOI `10.1088/0004-6256/138/6/1741` (Chung et al. 2009, AJ 138, 1741) | IOP; arXiv `0909.0781` |
| VIVA public FITS atlas | **no DOI exists** — hosted at Yale | `http://www.astro.yale.edu/viva/momfits/{mom0,mom1,mom2}/` |
| VIVA reprocessed ~15″ products | **no separate DOI** — live inside the VERTICO VOSpace at `VERTICO/public/multiwavelength/viva/products/v1.2.3/` | CANFAR VOSpace (public) |

⚠ **The VIVA data have no DOI of their own.** The Yale atlas page is a plain Apache directory; the
matched-resolution HI products are an *undoi'd sub-tree of the VERTICO VOSpace*. Cite Chung et al. 2009 +
the VERTICO DOI.

⚠ **`https://ws-cadc.canfar.net/vault/files/<path>` is the download endpoint.**
`https://www.canfar.net/storage/vault/list/...` is a JS shell (HTTP 200, no data — the classic §1 trap).
The node-listing endpoint is `https://cadc-west-01.canfar.net/vault/nodes/<path>` (returns VOSpace XML).

---

## 2. Sample counts — the arena is NOT availability-limited

- VERTICO observed **51** Virgo galaxies (36 new ALMA Cycle-7 + 15 archival ACA); the parent VIVA survey has
  **53**, minus IC 3355 and VCC 2062 which VERTICO dropped as unlikely detections.
- **49 CO detections**, 2 non-detections (**IC 3418**, **VCC 1581**, both 3σ upper limits in VizieR
  `l_Sco == '<'`). This reproduces exactly: the CANFAR DOI tree contains **exactly 49 galaxy directories**,
  and they are **exactly** the 49 with `l_Sco != '<'`. Zero discrepancy.
- **CO: 49/49 galaxies carry the complete 37-product suite.**
- **HI (VERTICO-reprocessed VIVA, ~15″): 48/49.** Breakdown:
  - **NGC 4293 — directory exists but is EMPTY in v1.2.3 and in every earlier version (v1.0, v1.1, v1.2,
    v1.2.1, v1.2.2).** No reprojected HI at all.
  - NGC 4450 (35 files), NGC 4579 (34), NGC 4606 (34) — **the only missing items are PVD (position–velocity)
    files.** All mom0/mom1/mom2 + uncertainty maps + cubes are present, so these three are fully usable.
  - NGC 4694 has one extra child (`Original/`).
- NGC 4293 **does** have public native-resolution VIVA moments (`ngc4293.mom0/mom1/mom2.fits`, both at Yale
  and in `VERTICO/public/multiwavelength/viva/15arcsec/delivered/moment_maps/`), so it is recoverable by
  redoing the reprojection — it is not missing data, only missing *reprocessing*.

**⇒ N with both usable CO and matched-resolution HI = 48 (49 if NGC 4293 is reprojected).**
The stated survival bar is N_valid ≥ 35 out of 49 (>71%). **Availability does not kill the arena** — it costs
at most 1 galaxy before any science cut.

---

## 3. 🔴 STRUCTURAL FACTS THAT CHANGE WHAT CAN BE COMPUTED

Read these before designing anything.

### 3.1 The HI is NOT beam-matched to the CO, and NOT on the CO pixel grid
Verified directly from FITS headers of all 48 matched pairs (`BEAM_GRID_TABLE.csv`).

- **CO**: `BMAJ == BMIN`, `BPA = 0` — genuinely **round** beams, but at **native** resolution, i.e. a
  *different* beam per galaxy, **7.2″–10.2″** (VizieR circularised `Diamb`: min 7.1, median 7.9, max 10.2).
  Pixel scale **2.0″/px** for every galaxy.
- **HI**: `BMAJ != BMIN` with a non-zero `BPA` — the beams are **ELLIPTICAL for 48 out of 48 galaxies; not a
  single one is round.** `BMAJ` **15.779″–25.967″** (median 16.900″), `BMIN` **15.148″–24.108″**, at a
  galaxy-specific `BPA`. Worst offenders: NGC 4713 (25.97 × 24.11 @ +69.2°), NGC 4330 (19.99 × 19.89 @ −24.6°),
  NGC 4535 (19.98 × 19.80 @ +74.4°), NGC 4424 (19.98 × 19.39 @ +44.4°), NGC 4579 (19.89 × 19.03 @ −30.8°).
  Pixel scale **8.0″/px** for every galaxy (exactly 4× the CO).
- The `_round_` and `_15as_` tokens in the HI filenames are **labels, not achieved properties.** A pipeline
  that trusts the filename will silently mismatch beams.
- ⇒ Any per-ring CO/HI comparison must (a) convolve CO to each galaxy's *elliptical* HI beam using the
  header `BMAJ/BMIN/BPA`, and (b) regrid one tracer onto the other. Both are fully determined by the public
  headers, so this is derivable — but it is **not** already done for you.

### 3.2 The tangent point differs between CO and HI for close pairs
For galaxies that share a single VIVA VLA pointing, the reprojected HI inherits the **field centre**, which
is the *companion's* position, not the target's. Confirmed cases include:

**6 of 48 galaxies have a CO↔HI tangent-point offset above 1″**, and the offsets are enormous:

| Galaxy | CO `CRVAL1,CRVAL2` | HI `CRVAL1,CRVAL2` | offset | CO / HI `NAXIS1` |
|---|---|---|---|---|
| NGC 4216 | 183.977526, 13.148889 | 184.096010, 13.308056 | **707.7″** | 174 / 163 |
| NGC 4536 | 188.612707, 2.188137 | 188.592500, 2.325278 | **499.0″** | 149 / 147 |
| NGC 4294 | 185.324167, 11.510000 | 185.420017, 11.501111 | **339.6″** | 51 / 111 |
| NGC 4607 | 190.301969, 11.887222 | 190.240550, 11.911667 | **233.6″** | 61 / 19 |
| NGC 4298 | 185.387973, 14.604167 | 185.426796, 14.594444 | **139.7″** | 81 / 68 |
| NGC 4568 | 189.142884, 11.238056 | 189.135817, 11.258611 | **78.1″** | 58 / 36 |

The remaining 42 are exactly 0. Field sizes diverge wildly for the affected rows (NGC 4222: CO 64×64 px =
128″ across, HI 193×193 px = 1544″; NGC 4607: HI is only 19×19 px = 152″ while CO is 61×61 px = 122″).
**⇒ Do not assume a shared centre. Take ring centres from the VizieR `RAJ2000/DEJ2000` (NED optical centre),
never from `CRVAL`.** The full offset audit is the `tangent_offset_arcsec` column of `BEAM_GRID_TABLE.csv`.

### 3.3 The published VIVA atlas beams are much coarser than the thread assumed
`viva_chung2009_table2_beams.tsv` is Chung et al. 2009 Table 2, extracted from the arXiv LaTeX source
(all 53 rows).

- **Native VIVA beams span 15.44″ × 14.00″ up to 44.58″ × 37.81″.**
- **12 of 53 exceed 20″ in BMAJ**: NGC 4383 (44.58), NGC 4579 (42.42), NGC 4808 (40.01), NGC 4321 (31.10),
  NGC 4294 & NGC 4299 (28.93), NGC 4192 (27.99), NGC 4396 (27.39), NGC 4254 (26.78), NGC 4330 (26.36),
  NGC 4713 (25.95), NGC 4535 (24.98).
- ⇒ **"VIVA is 15.2″–20″, average 17″" is wrong for the published atlas.** It is right only for the
  CS-configuration subset.
- The VERTICO `~15as` products reach 15–18″ on galaxies whose published atlas beam is 25–45″, so they are a
  **bespoke re-imaging from the VLA visibilities, not a smoothing of the published VIVA cubes.** They are a
  different HI dataset from the Chung et al. atlas and should be described as such.

### 3.4 Only NATIVE-resolution CO is public
Brown et al. state cubes were also produced at 9″ and 15″ beams. **Those do not exist in the public tree** —
`VERTICO/public/cubes/` contains only `native/`, and `products/` only `co21_native` (a VOSpace `LinkNode`
pointing at the DOI tree) plus `continuum`. `cubes/9as`, `cubes/15as`, `products/co21_9as`, `products/co21_15as`
all return **404**. Matching CO to the HI beam is therefore the user's job.

### 3.5 Channel width is 10.6 km/s, not 10
Brown et al.: raw 1.953 MHz ≈ 2.5 km/s, binned ×4 to "∼10 km/s"; the **actual delivered channel is
10.6 km s⁻¹** (paper text, figure caption, and the VizieR column description all say 10.6). Adopted distance
to every Virgo galaxy: **16.5 Mpc** (Mei et al. 2007).

---

## 4. What is in this delivery

| File | Contents |
|---|---|
| `MANIFEST_FULL.tsv` | **4,040 rows** — every public file in both trees plus the ancillary sets, with its complete download URL and exact byte count. Total 2.478 GB of enumerated bytes. |
| `BEAM_GRID_TABLE.csv` | Per-galaxy CO and HI `NAXIS`, pixel scale, `BMAJ/BMIN/BPA`, `CRVAL`, projection, and the CO↔HI tangent-point offset. Read straight from the mirrored headers. |
| `vertico_vizier_J_ApJS_257_21_table12.tsv` | VizieR `J/ApJS/257/21/vertico` — 51 rows: `RAJ2000, DEJ2000, Vel, Inc, PA, S/N, Diamb, rms, Vlsr, Delv, Sco, logLCO, TCO, logMmol` with the 3σ upper-limit flags. |
| `viva_chung2009_table2_beams.tsv` | VIVA Table 2 — 53 rows of native synthesized beam FWHM, BPA and per-channel rms. |
| release asset `i3_vertico_viva_2dproducts_v1.tar.gz` | Mirrored science-ready 2-D products (see §5). |

### 5. Mirrored subset (release asset) vs deferred

**Mirrored (~213 MB):**
- CO, 49 galaxies × 15: `mom0_Kkms-1`, `mom0_Msolpc-2`, `mom0_SN`, `mom0_unc`, `mom1`, `mom1_unc`, `mom2`,
  `mom2_unc`, `peakT`, `pvd_major`, `pvd_minor`, `noise_subcube_slab`, `rad_prof.csv`, `spectrum.csv`
- HI, 48 galaxies, the same suite (`mom0_Jyb-1kms-1` in place of `mom0_Kkms-1`)
- Stellar-mass surface-density maps at **15″ and 9″** (`mstar_w1+w3`, `mstar_w1+w4`), 49 galaxies
- VIVA native moment maps as delivered to VERTICO (155 files) **and** the Yale public atlas (156 files,
  mom0/mom1/mom2 for 52 galaxies incl. NGC 4293)

**🔴 DEFERRED — not mirrored, fully manifested:**
- **All spectral cubes: 582 files, 2.26 GB** — `mask_cube`, `subcube`, `subcube_slab`, `unclipped_subcube`,
  `mask_subcube_slab` for both tracers. Every URL and byte count is in `MANIFEST_FULL.tsv`; each is directly
  `curl`-able from `https://ws-cadc.canfar.net/vault/files/...` with no auth.
- **All 1,741 preview PDFs (120 MB)** — deliberately excluded, they carry no numbers not in the FITS.
- `VERTICO/public/multiwavelength/{dustpedia,heracles,ngvs,sdss,spitzer,things,z=0mgs}` and
  `products/continuum` — enumerated as available but out of scope for a two-tracer phase test.

---

## 6. Building `ring_profiles.parquet` — what is and is not derivable

Requested columns, against what the public products actually support:

**Derivable now, from this delivery:**
- `g_HI`, `g_H2` per ring — from `mom0_Msolpc-2` (both tracers already carry a Msol/pc² map).
  ⚠ the CO `Msolpc-2` map is built with **one fixed α_CO**; to get α_CO ∈ {0.5, 1, 2} rescale the
  `mom0_Kkms-1` map yourself. The baked-in VERTICO convention (Brown et al. eq. 7) is
  **α_CO = 4.35 M⊙ pc⁻² (K km s⁻¹)⁻¹ (Bolatto et al. 2013, Milky-Way disk) with R₂₁ = 0.8**, i.e.
  `M_mol = (α_CO / R₂₁) · L_CO`, equivalent to `X_CO = 2 × 10²⁰ cm⁻² (K km s⁻¹)⁻¹`. So the shipped
  `mom0_Msolpc-2` map is **α_CO/R₂₁ = 5.4375** applied to the CO(2−1) intensity — divide it out before
  re-applying your own α_CO grid, and state whether your {0.5, 1, 2} are α_CO or α_CO/R₂₁.
- `g_bar` at each α_CO — sum of the above with `g_star`.
- `g_star` — from `mstar_w1+w3_15as` / `mstar_w1+w4_15as` (**already at 15″, i.e. already close to the HI
  beam**). Two SFR-corrected variants ship; pick one and state it.
- `beam FWHM in kpc` — header `BMAJ/BMIN` × 16.5 Mpc. **Per galaxy and per tracer; there is no single value.**
- `channel width` — 10.6 km/s (CO). HI channel widths are per-galaxy: VIVA `ΔB` column, 3.125 MHz typical
  (2.629 MHz for NGC 4321 / NGC 4579, 6.25 MHz for NGC 4606 / NGC 4607).
- `V1t/V1r/V2t/V2r` harmonics per tracer — derivable by running a tilted-ring / harmonic decomposition
  (`mom1` + `mom1_unc` are both public for both tracers). **Not shipped; nobody has published them.**
- `dispersion model` inputs — `mom2` + `mom2_unc` for both tracers.

**NOT derivable from public products — must be modelled or declared:**
- `pressure-corrected V_circ` — **no public asymmetric-drift or pressure-support correction exists for either
  survey.** Requires assuming a scale height / vertical structure. This is a modelling choice, not data.
- `pressure-support terms` — same; not published.
- `kinematic_covariances.npz` — **does not exist publicly.** VERTICO ships per-pixel `mom1_unc`/`mom2_unc`
  maps but **no covariance between rings or between harmonic coefficients.** Any covariance must be generated
  (bootstrap over the cubes, or MC over the noise maps). The cubes needed for that are in the deferred set.
- `massmodel_covariances.npz` — **does not exist publicly.** There is no published covariance between α_CO,
  stellar M/L and inclination for this sample. Inclination and PA come as **point values with no errors** in
  VizieR (`Inc`, `PA` have no `e_` columns).
- A CO map at the HI resolution — see §3.4; must be produced by convolution.

**⇒ Of the three requested files, only `ring_profiles.parquet` is buildable from public data, and only after
per-galaxy beam matching. Both `.npz` covariance files have to be *generated*, not fetched — there is no
published covariance for either survey.**
