# T1 — NGC 1365 ATCA HI azimuthal-sector profile — SCHEMA

Source: ATCA Fornax HI survey mosaic tile `afs_014` (OBJECT keyword), TELESCOP=ATCA,
published on the MeerKAT Fornax Survey data page as the "pre-MeerKAT ATCA" products.
Files fetched: ATCAmom0.fits (8,038,080 B), ATCAmom1.fits (8,038,080 B). Both verified: magic `SIMPLE  =`,
2-D 1046x952, CDELT=20.0", synthesized beam BMAJ=94.9" BMIN=66.5", BUNIT=JY/BEAM.km/s and km/s.
NGC 1365 (RA 53.40152, Dec -36.14040) falls at pixel (756, 302) -- INSIDE the footprint, with real emission
(mom0 max 7.016 Jy/beam.km/s in a 80x80-pix box) and mom1 velocities 1453-1840 km/s (systemic ~1636 km/s).

Deprojection: PA=201.1 deg, incl=55.4 deg, D=19.57 Mpc (PHANGS-ALMA orientation values).
Eight sectors of 45 deg in the DEPROJECTED galaxy plane, position angle measured from the receding major axis.
Radial bins 30" wide from 0" to 570".

## T1_NGC1365_ATCA_HI_sector_profile.csv  (147 rows, header + data)
sector          1..8, sector index
pa_lo, pa_hi    deprojected azimuth range of the sector, degrees
r_in_arcsec, r_out_arcsec   deprojected radial bin edges, arcsec
r_mid_kpc       bin centre in kpc at D=19.57 Mpc
npix            number of 20"-pixels in the bin
n_beams         npix * pixel_area / beam_area  = independent resolution elements in the bin
mom0_mean, mom0_med   Jy/beam.km/s
snr_mean        mom0_mean / 0.05553 (rms measured on the mom0 map at r > 900")
vfield_npix     number of pixels in the bin with a finite mom1 value
vfield_med_kms  median mom1 velocity in the bin, km/s
