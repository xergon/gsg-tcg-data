# Data from: In-orbit test of the weak equivalence principle with atom interferometry

Dataset DOI: [10.5061/dryad.4xgxd25rg](https://doi.org/10.5061/dryad.4xgxd25rg)

## Description of the data and file structure

This dataset: data_for_aeh0529.zip contains the raw experimental data underlying the figures in the main text (Figures 2, 3, 4, and 6) and in the supplementary materials (Figures S1, S3, S4, and S6) of the article entitled *“In‑orbit Test of the Weak Equivalence Principle with Atom Interferometry”*. The data are presented as plain‑text ASCII files, each corresponding to a specific figure panel. File headers provide column labels and units; numerical data follow in subsequent lines. For a full description of the experimental setup, procedures, and data processing, please refer to the main article and its supplementary materials.

### Files and variables

#### **File: data_for_Fig2a.dat**

*Description*: Principal component analysis (PCA) of 2D fluorescence images for ⁸⁷Rb, showing the shearing fringe pattern (as in Fig. 2a). 
*Variables*:

* Pixel coordinate x (mm)
* Pixel coordinate y (mm)
* PCA amplitude (arb. units)

#### **File: data_for_Fig2b.dat**

*Description*: PCA of 2D fluorescence images for ⁸⁵Rb, showing the shearing fringe pattern (as in Fig. 2b).
*Variables*:

* Pixel coordinate x (mm)
* Pixel coordinate y (mm)
* PCA amplitude (arb. units)

#### **File: data_for_Fig2c.txt**

*Description*: 1D interference fringe for ⁸⁷Rb, obtained by averaging the 2D image along x‑direction and normalizing (as in Fig. 2c).
*Variables*:

* Position along y (mm)
* Normalized fluorescence intensity (arb. units)

#### **File: data_for_Fig2d.txt**

*Description*: 1D interference fringe for ⁸⁵Rb (as in Fig. 2d) . 
*Variables*: Same as above.

* Position along y (mm)
* Normalized fluorescence intensity (arb. units)

#### **File: data_for_Fig2ef.txt**

*Description*: Time series of the measured interference phase for ⁸⁷Rb (φ_Rb87) and the differential phase Δφ = φ_Rb85 – φ_Rb87, as shown in Fig. 2e and the histograms in Fig. 2f.
*Variables*:

Fig. 2e

* Experiment index
* φ_Rb87 (rad)
* Δφ (rad)

Fig. 2f

* Phase bin center (rad)
* Counts for φ_Rb87 (rad)
* Counts for Δφ (rad)

#### **File: data_for_Fig2g.txt**

*Description*: Histogram of the acceleration‑induced interference phase, calculated from classical accelerometer data via the sensitivity function (as in Fig. 2g ).
*Variables*:

* Phase bin center (rad)
* Counts (number of occurrences)

#### **File: data_for_Fig3b.txt**

*Description*: Calculated differential phases Δφ₁, Δφ₂ and their average Δφ_avg as a function of the fitting‑position offset y₀ (as in Fig. 3b).
*Variables*:

* y₀ (mm)
* Δφ₁ (rad)
* Δφ₂ (rad)
* Δφ_avg (rad)

#### **File: data_for_Fig3d.txt**

*Description*: Simulated residual phase φ_res as a function of initial velocity v_z0 for δ_tp > 0 and δ_tp < 0, and their average (as in Fig. 3d).
*Variables*:

* v_z0 (mm/s)
* φ_res for δ_tp > 0 (rad)
* φ_res for δ_tp < 0 (rad)
* Average φ_res (rad)

#### **File: data_for_Fig4a.txt**

*Description*: Long‑term averaged differential phases for the four experimental configurations and their overall average (as in Fig. 4a). 
*Variables*:

* Date (days since 2024‑08‑27)
* Averaged phase for each configuration (four columns, rad)
* Overall average phase (rad)

#### **File: data_for_Fig4b.txt**

*Description*: Allan deviation of the averaged differential phase as a function of averaging time (as in Fig. 4b) .
*Variables*:

* Averaging time (days)
* Allan deviation (rad)

#### **File: data_for_Fig6a.txt**

*Description*: Simulated 2D interference fringe for the |a⟩ end state (as in Fig. 6a).
*Variables*:

* y‑coordinate (mm)
* z‑coordinate (mm)
* Population (arb. units)

#### **File: data_for_Fig6b.txt**

*Description*: Simulated 2D interference fringe for the |b⟩ end state (as in Fig. 6b).
*Variables*:

* y‑coordinate (mm)
* z‑coordinate (mm)
* Population (arb. units)

#### **File: data_for_Fig6c.txt**

*Description*: 1D spatial fringe obtained by integrating the |a⟩ 2D population along z (as in Fig. 6c).
*Variables*:

* y‑coordinate (mm)
* Integrated population (arb. units)

#### **File: data_for_Fig6d.txt**

*Description*: 1D spatial fringe obtained by integrating the |b⟩ 2D population along z (as in Fig. 6d).
*Variables*:

* y‑coordinate (mm)
* Integrated population (arb. units)

#### **File: data_for_Figs1a.txt**

*Description*: Recorded residual acceleration a_z during one experimental round (as in Fig. S1a).
*Variables*:

* Time (s)
* a_z (m/s²)

#### **File: data_for_Figs1b.txt**

*Description*: Acceleration‑induced interference phase φ calculated from the sensitivity function (as in Fig. S1b).
*Variables*:

* Time (s)
* φ (rad)

#### **File: data_for_Figs3a.txt**

*Description*: Phase distribution of simulated interference fringes showing skewness (as in Fig. S3a).
*Variables*:

* Fitted phase bin (rad)
* Counts

#### **File: data_for_Figs3b.txt**

*Description*: Differential phase distribution for experimental configuration 1 (⁸⁵Rb before ⁸⁷Rb, δ_tp > 0) (as in Fig. S3b).
*Variables*:

* Δφ bin (rad)
* Counts

#### **File: data_for_Figs3c.txt**

*Description*: Differential phase distribution for configuration 2 (⁸⁷Rb before ⁸⁵Rb, δ_tp > 0) (as in Fig. S3c).
*Variables*:

* Δφ bin (rad)
* Counts

#### **File: data_for_Figs3d.txt**

*Description*: Differential phase distribution for configuration 3 (⁸⁵Rb before ⁸⁷Rb, δ_tp < 0) (as in Fig. S3d).
*Variables*:

* Δφ bin (rad)
* Counts

#### **File: data_for_Figs3e.txt**

*Description*: Differential phase distribution for configuration 4 (⁸⁷Rb before ⁸⁵Rb, δ_tp < 0) (as in Fig. S3e).
*Variables*:

* Δφ bin (rad)
* Counts

#### **File: data_for_Figs4c.txt**

*Description*: Calculated relationship between fringe‑center difference Δy and imposed translational offset y_fri (as in Fig. S4c).
*Variables*:

* y_fri (mm)
* Δy (mm)

#### **File: data_for_Figs4e.txt**

*Description*: Relationship between tilt angle θ_y and Δy for rotational misalignment (as in Fig. S4e).
*Variables*:

* θ_y (rad)
* Δy (mm)

#### **File: data_for_Figs6c.txt**

*Description*: Measured differential phase Δφ as a function of applied image rotation angle θ_rot (as in Fig. S6c).
*Variables*:

* θ_rot (rad)
* Δφ (rad)

## Code/software

All files are plain ASCII text.
