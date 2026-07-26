# T7 — JVAS B0218+357 / VLBA BC214 · FETCH RESULT 2026-07-26

## HEADLINE — BC214 DOES **NOT** DIE THE SDP.81 DEATH
SDP.81 failed because every delivered line image was tapered to ~170 mas against a 2.0 mas threshold —
someone else's weighting choice, frozen into the only available product.
**BC214 has no delivered images at all.** All 24 archive products are RAW correlator IDIFITS, flagged
`cal_status = "Do Not Calibrate"`. The resolution is therefore set by the array geometry, not by a taper,
and the weighting choice is OURS.

Measured from ITRF positions of the 10 VLBA stations, max baseline MK–SC = **8611.585 km**:

| band | freq | lambda/B_max | published beam | min/diffraction-limit | <= 2.0 mas? |
|---|---|---|---|---|---|
| S | 2.3 GHz | 3.122 mas | 7.8 x 2.9 mas | 0.929 | NO (both axes) |
| X | 8.4 GHz | 0.855 mas | 2.0 x 0.7 mas | 0.819 | YES (both axes) |
| K | 22 GHz  | 0.326 mas | 0.8 x 0.3 mas | 0.919 | YES (both axes) |

The published beams sit at **0.82–0.93 x the diffraction limit** — i.e. they ARE the full-array limit,
achieved on these exact data. **2.0 mas is met at X band on both axes and beaten by 2.5x (major) / 6.7x
(minor) at 22 GHz.** Reachability is not the constraint here. Calibration effort is.

## WHAT EXISTS, PER EPOCH AND BAND
16 segments BC214A..BC214P, 2012-09-24 to 2012-11-25, PI C. (Teddy) Cheung, all **PUBLIC**, released
2013-06-09. 24 exec blocks, **8,135,089,920 bytes = 7.576 GiB total**. 10 antennas (9 on BC214K, BC214N).
- **16 epochs at 22 GHz (K)** — 20 exec blocks, 43–381 MiB each.
- **4 dates carry the dual-band 2.3/8.4 GHz sequence** — 2012-09-24, 2012-10-02, 2012-10-23, 2012-11-25
  (segments A, C, I, P), one S-labelled block each, 338–355 MiB.
- Format: **IDIFITS raw correlator output only.** No calibrated MS, no images, no derived products.

## 🔴 THREE FINDINGS THAT CHANGE WHAT CAN BE COMPUTED
1. **The archive band label UNDER-REPORTS the frequency setup.** `segment_bands` shows only `['K','S']` for
   every segment — X band appears NOWHERE in the archive metadata. It would be easy to read this as "8.4 GHz
   does not exist" and kill the arena. It does exist: Spingola+2016 §2.1 states the 2.3 and 8.4 GHz
   observations were **simultaneous**, and Table 1 reports 8.4 GHz fluxes on all four dual-band dates.
   The X IFs are inside the S-labelled IDIFITS. **Verify by FITS FQ table before relying on it.**
2. **The uv path is deliverable in size but not in effort.** 7.576 GiB total is far under the 2,048 MB/file
   mount cap per file (largest single file 381 MiB) — unlike SDP.81's 540.84 GiB. But it is RAW: it needs
   a priori Tsys/gain amplitude calibration, opacity correction at 22 GHz, fringe fitting with a source
   model, and several rounds of phase + amplitude self-calibration in AIPS before any of the columns T7
   specified (`real_Jy`, `weight`, `phase_solution`, `bandpass_*`, `fringe_delay`, ...) even exist.
   **Those columns are pipeline OUTPUTS, not archive contents.** No calibration pipeline was staged, per brief.
3. **One epoch label in the paper disagrees with the archive.** Spingola+2016 Table 1 prints `6/10/2012`;
   the archive has segment BC214E at `2012-10-09`, and there is no 2012-10-06 observation in BC214.
   The other 15 epochs match the archive exactly. Treated as a typo in the paper and reconciled to
   `2012-10-09`; the original label is preserved in `paper_epoch_label`.

## WHAT IS DELIVERED HERE
The imaged, calibrated measurements — which is what T7 can actually compute on today:
per-epoch/per-band/per-image flux densities (48 rows), the derived A/B magnification ratio (24 rows),
the 22 GHz Gaussian component structure (7 rows, positions to 0.01 mas, sizes to 0.125 mas),
the full archive inventory (24 rows), and the resolution budget (3 rows). See `SCHEMA.md`.

## BLOCKER — DOWNLOADING THE RAW uv DATA NEEDS A HUMAN
Metadata is fully anonymous. **Retrieval is not.** The portal routes downloads through its
`multi-download-operation` workflow launcher; `https://data.nrao.edu/archive-service/download_form_controls`
returns **HTTP 500 "Internal Server Error"** and `get_is_authorized` returns **HTTP 500 "Missing request data"**
to an unauthenticated GET. Submitting the request requires entering an email address into the portal form.
**No credentials were entered and no access control was probed further.**
EXACT HUMAN STEP (Stefan, ~5 min): open `https://data.nrao.edu/portal/#/`, search project code `BC214`,
tick the segments wanted, click Download, enter an email; NRAO returns a fetchable staging URL.
⚠ Do this ONLY if T7 rules that a full AIPS calibration of raw VLBI visibilities is worth the effort.
