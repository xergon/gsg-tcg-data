# S3 — A2744 NW: the SIGN of the gas lead along the infall axis

Built 2026-07-25 (UTC) for ChatGPT-Pro row **S3**, after S3 withdrew the published >150 kpc offset as a
signed first-infall result and re-framed the test: **magnitude is no longer the discriminator, SIGN is.**

---

## 🔴 THE ANSWER — the sign is settled, and it is NEGATIVE in every combination

**All 88 (mass tracer × axis definition) pairs give Δ_lead < 0.** The NW gas sits **outward** of the NW mass
along the infall axis. There is no pairing, and no axis definition, under which the gas leads.

| statistic over all 88 pairs | kpc |
|---|---|
| median Δ_lead | **−296.4** |
| range | **−425.6 … −28.0** |
| pairs with Δ_lead > 0 | **0 of 88** |

**Against S3's own kill conditions, both fire:**
- *"Δ_lead ≤ 50 kpc (median)"* → median is **−296 kpc**. **FIRES.**
- *"≥2 non-parametric families returning Δ_lead ≤ 0"* → WSLAP+/Diego (free-form) **−319**, SaWLens/Merten
  (free-form) **−314**, Merten+2011 WL **−410**, Medezinski+2016 WL **−171** (all on AX_A). **FIRES, 4-fold.**

The tightest and most conservative pairing — the gas against the **nearest** mass peak (UNCOVER
`North-West-2` / `NW-BCG2`) — gives **Δ_lead = −133 kpc with |Δ_⊥| ≤ 27 kpc**, and the mass→gas offset
vector is **anti-parallel to the NW→S2 axis to within 2.8°**. The displacement is almost purely along the
axis, and it points the wrong way for a leading gas core.

⇒ Under S3's re-framing this is **ordinary trailing gas**. The row can be closed on sign.

---

## Sign convention — read this before using any number

- `dpar` is **positive TOWARD the axis endpoint**, i.e. **positive = INWARD (NW → S2)**. Negative = outward, NW-ward.
- `dperp` is positive when rotated **toward East** (increasing position angle) from the inward axis direction.
- `pa` is position angle in degrees **East of North**, measured at the axis origin.
- **`delta_lead_kpc = dpar(gas) − dpar(mass)`.** `> 0` ⇒ gas leads the infall. `< 0` ⇒ gas trails.

Every raw component is in the CSV, so the opposite convention is one sign flip away. **Nothing here silently
chooses the sign** — the axis is carried as a column and emitted under seven independent definitions.

## Angular scale

**4.5277 kpc/arcsec** at z = 0.3072 (H0 = 70, Ωm = 0.3, ΩΛ = 0.7; D_A = 933.9 Mpc). This is the value used
in every conversion in these files, and it is stated in the `kpc_per_arcsec` column of every row.
Independent check: Medezinski+2016 adopt the same cosmology and quote 1′ = 272 kpc → 4.533 kpc/arcsec. Agree.

---

## The axes — all seven emitted as separate columns, none preferred by the files

| id | definition | axis PA (E of N) | length |
|---|---|---|---|
| `AX_A` | UNCOVER `North-West-1` → `Main-2`  *(S3's "NW→S2", S2 = Main-2/BCG2)* | 130.76° | 130.5″ = 591 kpc |
| `AX_B` | UNCOVER `North-West-2` → `Main-2` | 126.06° | 171.6″ = 777 kpc |
| `AX_C` | UNCOVER `North-West-1` → `Main-1`  *(alternative S2 = Main-1/BCG1)* | 131.38° | 155.3″ = 703 kpc |
| `AX_D` | UNCOVER `North-West-2` → `Main-1` | 127.14° | 196.2″ = 888 kpc |
| `AX_E` | UNCOVER `North-West-1` → Ebeling+2010 X-ray centre | 121.97° | 87.6″ = 396 kpc |
| `AX_F` | Medezinski+2016 NW → Medezinski+2016 Core  *(WL only)* | 153.35° | 175.2″ = 793 kpc |
| `AX_G` | Merten+2011 NW → Merten+2011 Core  *(WL only)* | 136.34° | 121.7″ = 551 kpc |
| `AX_H` | NW X-ray peak → main X-ray peak  *(gas only, no mass input)* | 122.01° | 159.6″ = 722 kpc |

The per-axis medians of Δ_lead span only **−257 to −300 kpc**. The result is not axis-sensitive.

### ⚠ "S2" is ambiguous in the source and is therefore NOT resolved here
Chadayammuri+2024 (arXiv:2407.03142) label five BCGs S1, S2, N, NW-1, NW-2 but **never give S1 or S2 a
coordinate**, and state outright *"SE lies near two BCGs, S1 and S2, and it is unclear which one is
associated with."* The only handle: S1 carries the ~5030 km/s velocity offset and is judged unbound, while
"BCG-N and BCG-S2 have nearly the same redshift". Kempner & David 2004 measure the BCG at 00:14:20.6
−30:24:00 at z = 0.30000 (the *bluer*, lower-z component) and the BCG at 00:14:22.0 near the *redder*
z = 0.3148 component — which maps S2 → Furtak `BCG2`/`Main-2` and S1 → `BCG1`/`Main-1`. **That is an
inference, not a published identification.** Both readings are emitted (`AX_A`/`AX_B` vs `AX_C`/`AX_D`)
and they differ by 0.6° in axis PA and <1 kpc in Δ_lead. **The ambiguity does not touch the result.**

---

## Files

| file | what |
|---|---|
| `A2744_NW_uncoversolo_geometry.csv` | **the deliverable.** 28 objects × 75 columns. RA/Dec (deg + sexagesimal, FK5 J2000), positional error, provenance, and for each of the 8 axes: separation, PA, and the **signed** along-axis and perpendicular components in arcsec **and** kpc. |
| `A2744_NW_signed_lead_pairs.csv` | 88 rows: every (NW gas peak × NW mass tracer × axis) → `delta_lead_kpc`, `delta_perp_kpc`, and a plain-language `sign` column. |
| `A2744_NW_axis_definitions.json` | machine-readable axis table + the sign convention. |
| `chandra_xray_peaks_2p16Ms.json` | the X-ray measurement: method, caveats, four independent validations, and per-ObsID metadata for all 102 observations. |

---

## Where every position comes from — nothing is read from a filename

**Mass, strong lensing (UNCOVER v2.0 — the "uncoversolo" leg).** Furtak+2022 (arXiv:2212.04381), Table
*"Median DM halo PIEMD parameters"* and Table *"Median dPIE parameters … BCGs"*. Five PIEMD halo centres and
five BCGs, all in FK5 J2000 sexagesimal. Halo centres are free within 3″ of their BCG (the North halo is
fixed on its BCG). This is the model released as UNCOVER v2.0 (Furtak & Zitrin, 2024-07-26).

**Mass, weak lensing.** Medezinski+2016 (arXiv:1507.03992) Table 4 and Merten+2011 (arXiv:1103.2772) Table
*"Structures identified within our lensing reconstruction"*, converted from their (x, y) arcsec/arcmin
offsets to RA/Dec.

> 🔴 **The Medezinski sign-convention flag can be retired.** The earlier delivery flagged "X_c positive =
> West, Y_c positive = North" as *inferred, verify before relying on it*. It is now **verified by
> measurement**: reprojecting the Merten+2011 table under the WEST convention and comparing against local
> maxima of the published `merten_v1` κ map reproduces the W clump to **6″** and the NW clump to **24″**;
> under the EAST convention the same clumps land **350″** and **168″** away. West is correct. Medezinski's
> table is self-evidently the same convention — under EAST their clump named "W" would sit east.
>
> 🔴 **Stronger still: the reconstructed Medezinski NW position reproduces two *independent* published
> offsets to better than 0.5″.** Medezinski+2016 state their NW peak is "68 +25 −42 arcsec north of the
> closest BCG in the northwest clump" and "58 +45 −14 arcsec west of the closest BCG in the north clump".
> Measured from the reconstructed position against the Furtak+2022 BCGs: **68.38″** to NW-BCG1 and
> **58.04″** to N-BCG. The Table-4 → RA/Dec chain is correct.

**Mass, κ-map local maxima (measured here).** Local maximum of the *published* κ map, Gaussian-smoothed to
20″ FWHM, inside a ±30″ box centred on each NW BCG. Done for CATS v4.1, WSLAP+/Diego v4.1, SaWLens/Merten
v1 and UNCOVER v2.0. All four independent families put the NW mass peak within **2.95″–4.39″ of NW-BCG1**,
and UNCOVER puts a second peak **2.03″ from NW-BCG2**. WCS taken from the FITS headers
(`CTYPE=RA---TAN/DEC--TAN`, `EQUINOX 2000.0`, `RADESYS FK5`, `CD1_2 = CD2_1 = 0` in all four).

**Gas, X-ray (measured here).** All **102** ObsIDs of Chandra CDC 257 (DOI 10.25574/cdc.257),
**2.1621 Ms**, 975,070 events at 0.5–2 keV, accumulated into one 2″/pixel TAN grid. Positions are the mean
of 15 variants (5 smoothing scales × {all, split-half A, split-half B}); rms scatter **1.1″** (main) and
**1.3″** (NW), worst-case excursion 4.6″.

| | RA/Dec (FK5 J2000) | validation |
|---|---|---|
| main X-ray peak | 00:14:18.82 −30:23:25.1 | **3.29″** from the Ebeling+2010 centre that Medezinski+2016 adopt |
| **NW interloper peak** | **00:14:08.37 −30:22:00.6** | **722 kpc NW** of the main peak (Owers+2011: "~750 kpc to the northwest"); **83.86″** from the Medezinski NW WL peak (published: 87 +34 −28 arcsec, 90% CL); **432 kpc** from the Merten+2011 NW1 WL peak (Merten+2011: "at least 400 kpc"); **133 kpc** from the nearest mass peak, UNCOVER `North-West-2` |

Four independent published quantities reproduced. **No exposure map, no vignetting correction, no
background subtraction, no point-source removal** — see the caveats block in `chandra_xray_peaks_2p16Ms.json`.

## 🔴 The lensing quarantine is NOT engaged

S3's standing gate — *any Cat-derived weak-lensing product is quarantined unless it reproduces the published
colour-bin split with inverse-Σ_crit² weighting* — **does not bind here.** Nothing in this delivery is a
lensing contrast. **No ESD, no shear profile, no stacked contrast, no Σ_crit weighting was computed.**
What was computed is (a) the *argmax location* of published κ maps, (b) the *argmax location* of a Chandra
counts image, and (c) spherical trigonometry and unit conversion on positions. The gate binds the moment
anyone forms a contrast from these maps; it has not been crossed.

---

## 🔴 THREE STRUCTURAL FACTS S3 MUST HAVE BEFORE IT COMPUTES

**1. The 2024 deep-Chandra paper's own first-infall scenario predicts NO offset — which is in tension with
S3's re-framing.** S3's re-frame says: given first infall, gas lying outward to the NW is "ordinary trailing
gas". But Chadayammuri+2024 §"binary mergers" states verbatim that in the first-infall scenario *"the BCG is
always well aligned with the subcluster X-ray peak"*, and on that basis **"our binary simulations therefore
disfavour a first-infall scenario for NW."** It is the *slingshot* geometry that reproduces an offset — and
in that geometry *"NW-1 would be leading the gas core"*, i.e. the mass leads and the gas is left outward,
which is exactly the configuration measured here. The paper's overall verdict (first infall) comes from its
**triple**-merger runs, which rule out slingshot on *cool-core survival*, not on the offset. **So the
observed −133 kpc is a datum the adopted scenario does not predict, not a confirmation of it.**

**2. The WL and SL NW mass positions disagree by ~70″ = 317 kpc, and that is the largest systematic in the
problem.** All four lens models put the NW mass on the NW BCGs (~00:14:13.0 −30:22:34.7). Medezinski's
Subaru WL peak sits at 00:14:14.36 −30:21:28.6, **68.38″ from NW-BCG1** — the paper itself says
"68 +25 −42 arcsec north of the closest BCG in the northwest clump". Chadayammuri+2024 side against the WL peaks: *"the positions of the X-ray peaks and BCGs … are
nevertheless better traces of the subcluster positions than low-significance weak lensing peaks."* This
choice moves Δ_lead from −171 kpc (WL) to −307 kpc (SL) on AX_A — **it moves the magnitude, not the sign.**

**3. The NW substructure is two objects, not one, and they give different magnitudes.** NW-1 (east) and
NW-2 (west) are separated by 42.9″ = 194 kpc (their BCGs by 41.3″ = 187 kpc). The gas sits between them in
projection: **133 kpc** from NW-2 and **323 kpc** from NW-1. Any single number for "the NW mass peak" is a choice between them. **Both are emitted.**

---

## Deferred / not done

- **UNCOVER v2.0 lens maps are not mirrored here** — the κ map (0.1″/pix, 4561², 83.2 MB uncompressed) was
  fetched and used, but re-hosting the full UNCOVER release is out of scope for this pass. Direct
  Google-Drive file IDs for every map are in `MANIFEST_URLS.txt`.
- **No error propagation onto Δ_lead.** Positional errors are carried per object in `pos_err_arcsec` so S3
  can propagate them itself. The largest single term is the WL-vs-SL choice (item 2 above), which is a
  systematic, not a random error, and is already spanned by the emitted rows.
- **The uncorrected Chandra counts image is not published as a FITS product** (it is a derived intermediate,
  not archival data). Everything needed to regenerate it is in `chandra_xray_peaks_2p16Ms.json`.
