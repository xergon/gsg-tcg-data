# TNG first-infall gas-lead census — ENUMERATION ONLY, nothing was run

Enumerated 2026-07-25 (UTC) for S3. **The census was not built this pass**, per instruction.

---

## 🔴 LEAD FINDING — the premise is wrong in both directions

S3 filed this as a heavy-compute job. It is **not**, and it is also **not sufficient**.

- **Not heavy.** The `Cluster Mergers` catalogue is **~20 MB** for TNG-Cluster and **~20 MB** for TNG300-1.
  Both are single HDF5 files. Once fetched, they are **small enough to attach directly to the Pro thread**
  — no Cat compute, no parquet build, no census pipeline.
- **Not sufficient.** The catalogue has **no gas information at all.** Every field is halo/subhalo
  positions, velocities, masses and orbit history from `SubhaloPos` / `SubhaloVel` / `SubhaloMass`. There is
  **no gas centroid, no X-ray peak, no gas–mass offset.** A "gas lead" census therefore **cannot be derived
  from this catalogue** — it requires the snapshots (**209.7 TB** for TNG-Cluster, ~1.0 PB across all TNG),
  or a bespoke run over the 352 zooms.
- **What the catalogue *does* give for free** is the thing the offset must be projected onto:
  `Collision_axis`, a normalized 3-vector per merger event. So the *axis* is already published; only the
  *gas* side is missing.

⇒ **Recommend: do not scope a "gas lead census" against these two files.** Either (a) attach them and let
the thread work in the orbit/axis space they actually cover, or (b) accept that a gas-lead census means
snapshot-level work at the 200 TB scale and treat that as a separate, deliberately-sized job.

---

## 🛑 BLOCKED — a human must fetch these two files. Do not automate around it.

    https://www.tng-project.org/api/TNG-Cluster/files/cluster_mergers.hdf5   ->  HTTP 403
    https://www.tng-project.org/api/TNG300-1/files/cluster_mergers.hdf5      ->  HTTP 403

Exact response body, both URLs:

    {"detail":"Failed session auth (and no API-Key sent)."}

The bare API root `https://www.tng-project.org/api/` returns the same 403. This is a **registration wall**:
an account and an API key are required. **No account was created, no credentials were entered, no side door
was looked for.** The public documentation pages (`/data/cluster/`, `/data/downloads/TNG-Cluster/`,
`/data/docs/specifications/`) are open and returned HTTP 200 — everything below was read from them.

**Human action item:** register at tng-project.org, obtain the API key, and download the two ~20 MB files
above. Everything else needed is already enumerated here.

---

## What exists, exactly

### `Cluster Mergers` supplementary catalogue (Lee+ 2024 — cite this if used)

A merger event = collision between a main cluster (M_halo > 10¹⁴ M☉) and a sub-cluster (M_halo > 10¹³ M☉).

| simulation | coverage | events | size |
|---|---|---|---|
| **TNG-Cluster** | all 352 primary zoom targets at z = 0, plus their main progenitors at earlier snapshots | **2,083** | ~20 MB |
| **TNG300-1** | all halos with M_500c > 10¹⁴ M☉ at z = 0, plus main progenitors | **289** | ~20 MB |

In both: mergers recorded from z = 0 up to a time-since-collision (TSC) of 1 Gyr at z = 1.
Orbit histories span snapshots [30, 99], marked −1 after the merger completes. `M_Crit200/500_pre` = −1
where the group ID was not identified pre-merger. For TNG-Cluster, events are also recorded where the
secondary has **not yet merged** by z = 0.

**S3's "all 2,083 events" is confirmed verbatim** — that is the TNG-Cluster row.

### Full column spec (this is the spec the brief said we did not have)

| dataset | shape | units | description |
|---|---|---|---|
| `HaloIDs` | N | — | haloIDs of the primary cluster during each merger event |
| `Snap_coll` | N | — | closest snapshot number after first pericentre passage |
| `Snap_full_coll` | N | — | closest **full** snapshot number after first pericentre passage |
| `MainclusterID` | N | — | subhalo ID of the main cluster |
| `SubclusterID` | N | — | subhalo ID of the colliding sub-cluster |
| `Subcluster_mass` | N | 10¹⁴ M☉ | maximum `SubhaloMass` over all past time, of the sub-cluster |
| `Mass_ratio` | N | — | M_sub / M_main at the snapshot where sub-cluster mass peaks |
| `M_Crit200_pre` | N | 10¹⁴ M☉ | `Group_M_Crit200` of the main cluster when separation passes Σ 2×R_200c |
| `M_Crit500_pre` | N | 10¹⁴ M☉ | `Group_M_Crit500`, same epoch |
| `M_Crit200_coll` | N | 10¹⁴ M☉ | `Group_M_Crit200` at first pericentre passage |
| `M_Crit500_coll` | N | 10¹⁴ M☉ | `Group_M_Crit500` at first pericentre passage |
| `T_coll` | N | Gyr | time of first pericentre passage |
| `TSC_full` | N | Gyr | time since collision at the closest full snapshot |
| `d_peri` | N | ckpc/h | main–sub separation at first pericentre, from `SubhaloPos` |
| `V_coll` | N | km/s | maximum relative velocity at first pericentre, from `SubhaloVel` |
| **`Collision_axis`** | **N,3** | — | **normalized collision-axis vector at first pericentre**, from the cluster displacement one snapshot before and after collision |
| `Mhistory_snap` | N,70 | — | snapshot index of each recorded orbit sample |
| `Mhistory_mass` | N,70,2 | 10¹⁴ M☉ | `SubhaloMass` of [main, sub] |
| `Mhistory_orbit` | N,70,6 | ckpc/h | `SubhaloPos` as [x_m, y_m, z_m, x_s, y_s, z_s] |
| `Mhistory_vel` | N,70,6 | km/s | `SubhaloVel` as [vx_m, vy_m, vz_m, vx_s, vy_s, vz_s] |

**No gas field of any kind.** This is the structural fact above.

### The 352 cluster zooms and the snapshot volume

TNG-Cluster: **100 snapshots** (20 full + 80 mini), **209.7 TB** total; 1,786,922,267 FoF groups,
1,291,729,937 Subfind groups, 3,054,824,461,857 particles over all snapshots. All TNG public data ≈ 1.0 PB.
Both LHaloTree and SubLink merger trees exist; Rockstar and consistent-trees do not.

⚠ TNG-Cluster is a **stitched collection of zooms**, not a uniform box: only the regions near the 352
targets are at TNG300-1 resolution. The documentation warns explicitly that one *cannot* analyse all
(sub)halos or all regions of the box indiscriminately.

### Other supplementary catalogues in the same family (sizes, for scoping)

`Cluster Relaxedness` 1 MB · `Cluster Cool-core Criteria` 5 MB · `Cluster Projections` 16 GB per physical
quantity per FoV (all halos, 3 projections each) · `X-ray Cavities` (TNG-Cluster z = 0, mock-Chandra
cavity candidates, Prunier+ 2025a) · `Merger History` ~100s MB to ~few GB per snapshot ·
`Nearest Neighbors` 580 MB (TNG50-1) → 5.5 GB (TNG300-1).

**`Cluster Projections` is the one worth a second look** for a gas-lead census: it is a projected-quantity
product covering all 352 halos in 3 projections at z = 0, i.e. it may already carry projected gas maps —
which is the missing half. 16 GB per quantity per FoV, so it is genuinely a Cat-scale fetch. Same 403 wall.

### Citation requirements

Any use of TNG-Cluster data: **Nelson et al. (2024)** (arXiv:2311.06338) + **Nelson et al. (2019a)**.
Physical model: Weinberger et al. (2017), Pillepich et al. (2018a).
`Cluster Mergers` catalogue specifically: **Lee et al. (2024)** (arXiv:2311.06340).
Refer to the simulation as "TNG-Cluster", not "Cluster-TNG" or "TNG-Clusters".

### Related literature already located (not fetched)

- Lee et al. 2023, A&A 673, A131 — *Merging galaxy clusters in IllustrisTNG* (arXiv:2304.13585)
- Lee et al. 2024 — *Radio relics in massive galaxy cluster mergers in the TNG-Cluster simulation*
  (arXiv:2311.06340) — the `Cluster Mergers` catalogue paper
- Nelson et al. 2024 — TNG-Cluster introduction (arXiv:2311.06338)

---

## Public documentation URLs (all HTTP 200, no auth)

    https://www.tng-project.org/data/
    https://www.tng-project.org/data/cluster/
    https://www.tng-project.org/data/downloads/TNG-Cluster/
    https://www.tng-project.org/data/downloads/TNG300-1/
    https://www.tng-project.org/data/docs/specifications/
