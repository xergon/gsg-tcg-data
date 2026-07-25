# S3 — Abell 2744 NW first-infall polarity (z = 0.3072)

Fetched 2026-07-25 (UTC) for ChatGPT-Pro row **S3**.
Target break: **Δ_NW ≥ 150 kpc** along the infall axis, conjoined with
UNCOVER + **≥3 HFF model families sharing sign, ≥1 of them free-form**, and **|Δ_⊥| ≤ 50 kpc**.

---

## 🔴 GO/NO-GO — READ FIRST

**Only 3 of the 11 HFF model families cover the NW substructure at their latest version.
GRALE — one of the two free-form families S3 named — does NOT cover it at any version.**

The NW clump (Medezinski+2016) sits **127.7″ = 578 kpc** from the cluster X-ray centre.
Most HFF strong-lensing maps are only 144″–240″ across, i.e. half-widths of 72″–120″.
The NW clump falls **outside their footprint entirely**.

| Family | Method | Latest ver. | FOV (″) | pix (″) | kpc/pix | **Covers NW?** |
|---|---|---|---|---|---|---|
| **CATS** | Lenstool, parametric | v4.1 | 600×600 | 0.3002 | 1.36 | **YES** |
| **Diego / WSLAP+** | **FREE-FORM** | v4.1 | 264×264 | 0.5156 | 2.33 | **YES** |
| **Merten / SaWLens** | **FREE-FORM** (adaptive mesh) | v1 | 1500×1500 | 8.3333 | 37.73 | **YES** |
| Sharon | Lenstool, parametric | v4/v4cor | 200×200 | 0.0500 | 0.23 | no |
| ↳ Sharon | *(superseded)* | **v2, v3** | 300×300 | 0.0600 | 0.27 | **YES** |
| **Williams / GRALE** | **FREE-FORM** | v4 | 169×169 | 0.2500 | 1.13 | **no** |
| GLAFIC | parametric | v4 | 161×183 | 0.0300 | 0.14 | no |
| Keeton | parametric | v4 | 240×240 | 0.0600 | 0.27 | no |
| Bradač / SWUnited | free-form hybrid | v2 | 210×210 | 0.2051 | 0.93 | no |
| Zitrin-NFW | parametric | v3 | 144×144 | 0.0600 | 0.27 | no |
| Zitrin-LTM | parametric | v1 | 180×180 | 0.0600 | 0.27 | no |
| Zitrin-LTM-Gauss | parametric | v3 | 144×144 | 0.0600 | 0.27 | no |

Coverage was tested for **every version of every family (29 model versions)** — see
`hff_a2744_model_geometry.csv`. GRALE fails at v1 (140″), v3 (140″) and v4 (169″) alike.

### The gate IS satisfiable, but only just — and not with the families S3 named

Counting only **latest** versions: **CATS + WSLAP+ + SaWLens = exactly 3 families**, of which
**2 are free-form** (WSLAP+, SaWLens). That meets "≥3 sharing sign, ≥1 free-form" **with zero margin** —
any one family dropping out fails the gate.

Two ways to widen the margin, both with caveats S3 must rule on:
- **Sharon v2/v3** covers the NW and would be a 4th family — but only at a **superseded** version.
- **UNCOVER v2.0** (Furtak & Zitrin) covers it at 0.04″/pix over 7.6′×7.6′ — but it is built with
  **the Zitrin et al. (2015) analytic code**, so it is **not method-independent of the Zitrin family**,
  and it is parametric, not free-form.

### 🔴🔴 The free-form requirement is in worse shape than "2 of 3 are free-form" suggests

Covering the clump is not enough — **the 33.13″ displacement itself has to fit inside the map.**
Headroom from the NW clump to each map edge (`nw_edge_headroom.json`):

| Family | N | S | E | W | **min headroom** | Δ_NW = 33.13″ fits? |
|---|---|---|---|---|---|---|
| CATS v4.1 | 148.1″ | 451.9″ | 382.5″ | 218.2″ | **148.1″ = 670 kpc** | yes |
| **WSLAP+ v4.1** | **18.4″** | 245.1″ | 217.5″ | 46.1″ | **18.4″ = 83 kpc** | **NO** |
| SaWLens v1 | 594.3″ | 897.3″ | 829.4″ | 666.1″ | **594.3″ = 2691 kpc** | yes |

**The NW clump sits only 18.4″ (83 kpc) below the northern edge of the WSLAP+ map** — less than the
150 kpc being measured. A displacement with any significant northward component **runs off the map**.

So each free-form leg is independently compromised:
- **GRALE** — does not cover the NW clump at any version.
- **WSLAP+** — covers, but has only 83 kpc of northward headroom, < the 150 kpc threshold.
- **SaWLens** — ample headroom, but **v1 only, a PRE-HFF model**, at **8.33″ = 37.7 kpc/pixel**,
  so 150 kpc is **≈4 pixels**.

**⇒ There is no free-form leg that both covers the NW clump with room to measure 150 kpc *and* is
a post-HFF model at a resolution that resolves it.** S3 should treat "≥1 free-form" as the binding
constraint and decide explicitly whether pre-HFF SaWLens v1 qualifies — the answer decides the row.

---

## The angular scale — measure in a common frame

At **z = 0.3072**, H0=70, Ωm=0.3, ΩΛ=0.7: **4.5277 kpc/arcsec** (D_A = 933.9 Mpc).

> **Δ_NW ≥ 150 kpc  ⇔  ≥ 33.13 arcsec**
> **|Δ_⊥| ≤ 50 kpc  ⇔  ≤ 11.04 arcsec**

Independent check: Medezinski+2016 adopt the same cosmology and state 1′ = 272 kpc → 4.533 kpc/arcsec. **Agrees.**

**All 29 model versions share one frame**: `CTYPE = RA---TAN/DEC--TAN`, `EQUINOX 2000.0`, `RADESYS FK5`,
and **`CD1_2 = CD2_1 = 0` in every single one — no rotation anywhere.** Scales are from the
**CDELT/CD headers read off the files**, not from filenames. Full WCS (CRVAL/CRPIX/NAXIS) in the CSV.

---

## Sky geometry — the infall axis

Reference centre: **00:14:18.9, −30:23:22 (J2000)** = Ebeling+2010 X-ray peak, the frame
Medezinski+2016 use. Substructure positions derived from their Table 4 offsets:

| Clump | RA (deg) | Dec (deg) | r from X-ray centre | S/N_κ |
|---|---|---|---|---|
| Core | 3.585126 | −30.401444 | 47.5″ = 215 kpc | 12.1 |
| W | 3.552473 | −30.399278 | 88.9″ = 403 kpc | 7.9 |
| NE | 3.610050 | −30.375278 | 109.8″ = 497 kpc | 4.7 |
| **NW** | **3.559815** | **−30.357944** | **127.7″ = 578 kpc** | **7.0** |

⚠ The sign convention (X_c positive = West, Y_c positive = North) is **inferred** from the signs of
W (+1.36) vs NE (−1.62); the paper does not state it verbatim. **Verify before relying on it.**

### The published offset already clears the threshold

Medezinski+2016 Table 5, NW subhalo, 90% CL:

| Offset of NW mass peak from | arcsec | kpc @ 4.5277 |
|---|---|---|
| **X-ray interloper** | 87 (+34, −28) | **394 (267 … 548)** |
| nearest BCG | 68 (+25, −42) | 308 (118 … 421) |
| M11 DM halo | 69 (+32, −63) | 312 (27 … 457) |

**vs the X-ray interloper, both the central value and the 90% lower bound (267 kpc) exceed 150 kpc.**
vs the nearest BCG the central value clears it but the lower bound (118 kpc) does not.

⚠ These are **the published numbers, converted** — arithmetic only, no re-derivation.

---

## Contents

| Path | What |
|---|---|
| `kappa_nw_covering/` | κ (+γ, deflection) for the **3 families that actually cover the NW**, verified FITS |
| `hff_a2744_model_geometry.csv` | WCS, CDELT, FOV, kpc/pixel, per-clump coverage for **all 29 model versions** |
| `a2744_geometry_and_substructures.json` | cosmology, thresholds in arcsec, substructure sky positions |
| `medezinski2016/` | arXiv `/e-print/` **LaTeX source** + extracted Tables 4 & 5 |
| `uncover_v2/` | UNCOVER v2.0 lens-model README + DR4.1 MSA magnification catalogues |
| `chandra_cdc257/` | all **102** ObsIDs + per-ObsID retrieval URLs |
| `MANIFEST_URLS.txt` | 89 complete verbatim URLs |
| `URL_VERIFICATION.txt` | 13/13 sampled URLs verified by range-read + magic bytes |

**Not mirrored, by design** (all fetchable from `MANIFEST_URLS.txt`):
the 8 families that cannot see the NW clump (GLAFIC 125 MB/map, Keeton and Sharon 61 MB/map,
Zitrin 22–34 MB/map — ~1.4 GB total, and **none of it can contribute to a NW measurement**);
the range/ realisation sets (CATS ~9 GB, WSLAP+ ~800 MB); and Chandra CDC 257 (2.1 Ms, 102 obs).

---

## 🔴 Standing gate (S3's own), carried forward

**Any Cat-derived weak-lensing product is quarantined unless it reproduces the published
colour-bin split with inverse-Σ_crit² weighting.** Two earlier lanes failed exactly this way, ~10× low in ESD.

**Nothing here is a derived weak-lensing contrast.** This delivery is published products plus
(a) FITS header metadata read off the files and (b) unit conversion of published table values.
**No ESD, no shear profile, no stacked contrast was computed.** The gate is therefore not yet
engaged — but it binds the moment anyone computes a contrast from these maps.

## Blocked

`https://archive.stsci.edu/pub/hlsp/glass-jwst/` returns **HTTP 200 carrying a MyST SSO login page**,
not a listing — an auth wall wearing a 200. Not circumvented; a human must retrieve GLASS-JWST
(`10.17909/mrt6-wm89`, `10.17909/9a2g-sj78`, `10.17909/te6f-cg91`) via the MAST Portal.
The four MAST DOI resolvers are JS shells and yield no file list to curl.
