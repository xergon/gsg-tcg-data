# Cha et al. 2025 (ApJL 987 L15, arXiv 2503.21870) — Figure 4 profiles

Radial profiles of the Bullet Cluster convergence κ and BCG+ICL surface brightness μ,
Western vs Eastern sides. Extracted directly from the vector coordinates embedded in
`wing_detection2.pdf` (the paper's own matplotlib PDF from the arXiv source bundle) —
these are the paper's own plotted numbers, not eyeball digitization.

Landmarks that validate the extraction:
- SL-regime vertical line at 150.000 kpc (exact)
- Trail-region vertical line at 152.0 kpc
- "Sky Limit" horizontal at μ = 27.32 mag/arcsec²
- Sig panel top at 7.000

40 rows total (log-spaced 0.184 → 404.16 kpc). Row 40 lies beyond the axis limit (400)
and is clipped in the published figure but present in the drawing commands.

## Columns

- `semi_major_axis_kpc` — SMA in kpc
- `kappa_W`, `kappa_W_err` — West, WL-only, linear κ + 1σ from WL bootstrap
- `kappa_E`, `kappa_E_err` — East, WL-only
- `kappa_E_xraysub`, `kappa_E_xraysub_err` — East with X-ray gas mass subtracted
  (Note: `kappa_E_err == kappa_E_xraysub_err` at every radius — X-ray subtraction removes
  a smooth model without adding WL noise. This is a real property of the analysis,
  confirmed by symmetry test with worst-residual 8e-8, not a duplication bug.)
- `mu_W_magarcsec2`, `mu_W_err` — West, F277W surface brightness in **mag/arcsec²**
  (Note: The requesting thread asked for "f277w_east/west_counts_per_pixel" but the
  paper publishes surface brightness in magnitudes. Cat delivered what the figure
  actually contains; conversion to counts/pixel would require the paper's F277W
  zero-point and pixel scale, which are not in Figure 4.)
- `mu_E_magarcsec2`, `mu_E_err` — East (colored orange in the paper)
- `sig_kappa`, `sig_kappa_xraysub`, `sig_mu` — normalized asymmetry significance
  W vs E; unitless. No error bars plotted in the source. `sig_mu` peaks at 39.55
  at SMA=41.3 kpc (off the panel's y=7 top — clipped in the figure but present in
  the drawing commands).

W-side data (`mu_W_magarcsec2`, `sig_mu`) end at row 39 (334.75 kpc); last row blank
in those 3 columns.

No gas-model uncertainty is separately propagated in the paper, so there is no
`kappa_*_gassub_err` distinct from `kappa_E_err`. The West side has no X-ray-subtracted
curve in the figure, so no `kappa_W_xraysub*` columns are produced.
