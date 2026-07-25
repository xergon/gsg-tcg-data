# SDP.81 Science Verification — complete archive enumeration
### `ADS/JAO.ALMA#2011.0.00016.SV` — for row T7 (tracer-dependent lens potential)

Enumerated 2026-07-25 from the ALMA Science Archive's own interfaces. **No identifier here is guessed.**

## READ `FINDINGS.md` FIRST
It contains seven things that change what can validly be computed, including: the published
reference line images are **uv-tapered at 1 Mlambda** (half the 2 Mlambda you specified); the line beam is
**~170 mas** against a **2.0 mas** kill threshold; ObsCore under-reports the execution blocks by 6x;
and three measured packaging defects in the ALMA archive itself (two package members are empty tars
served as HTTP 200).

## The identifiers that were owed
```
MOUS   uid://A002/X8fa7af/X12     <- the ONLY MOUS; covers Bands 4, 6 and 7 together
GOUS   uid://A002/X8fa7af/X11
SGOUS  uid://A002/X8fa7af/X10
32 execution blocks:  Band 4 = 12,  Band 6 = 9,  Band 7 = 11   (full uid list in SUMMARY.json)
```

## Files here
| file | what it is |
|---|---|
| `FINDINGS.md` | structural facts that constrain the analysis — read before computing |
| `MANIFEST.tsv` / `.json` | all 74 published files: URL, bytes, band, execution block, ETag, mtime |
| `URLS.md` | every URL complete and verbatim, one per line, grouped by route |
| `SUMMARY.json` | machine-readable summary: identifiers, EB lists, SPW map, beams, defects |
| `readmes/` | the three official ALMA band READMEs |
| `scripts/calibration/` | all 32 `scriptForCalibration.py`, one per execution block |
| `scripts/imaging/` | the 4 official CASA imaging scripts (these are NOT on the science portal) |
| `scripts/*.tgz` | the original calibration-script tarballs as published |

Reference-image tarballs (all four, 1.67 GiB total) are attached to the GitHub **release**, not
committed here.

## Volume, and what could not be re-hosted
- ASA route **540.84 GiB** / SV-portal route **402.19 GiB** (heavily overlapping).
- GitHub's release-asset cap is **2 GiB**. **Nothing in the uv-data path fits**: the smallest raw
  ASDM is 3.40 GiB and the smallest per-EB calibrated MS is 6.16 GiB. The requested ~1 GiB
  band/EB-keyed shards **do not exist upstream**. The uv data is therefore **manifested, not
  mirrored** — fetch it directly from the verbatim URLs in `URLS.md`.

## Verification
All 74 URLs were swept by HTTP HEAD on 2026-07-25: **74/74 returned HTTP 200**, and **zero**
disagreed with the byte count the archive itself declares via DataLink and the request handler.
**ALMA publishes no checksum** for any of these files (no `Content-MD5`, no `Digest`, empty
DataLink `content_qualifier`); the Apache `ETag` encodes inode/size/mtime, not content. Integrity
gates available are byte count and tar/gzip magic only. Every file committed in this directory was
downloaded, magic-byte checked, and opened.

## Acknowledgement required by ALMA for any publication
> This paper makes use of the following ALMA data: ADS/JAO.ALMA#2011.0.00016.SV. ALMA is a
> partnership of ESO (representing its member states), NSF (USA) and NINS (Japan), together with
> NRC (Canada) and NSC and ASIAA (Taiwan), and KASI (Republic of Korea), in cooperation with the
> Republic of Chile. The Joint ALMA Observatory is operated by ESO, AUI/NRAO and NAOJ.
