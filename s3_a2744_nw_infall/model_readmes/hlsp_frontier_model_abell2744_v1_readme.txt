http://archive.stsci.edu/pub/hlsp/frontier/abell2744/models/
hlsp_frontier_model_abell2744_v1_readme.txt

This directory contains gravitational lensing models of the Hubble Frontier Fields (HFF) clusters based on pre-HFF imaging.  The models were produced by five map making teams who shared observational constraints but then worked independently to derive these models using robust, established methodologies.

These models may also be interactively displayed:
http://archive.stsci.edu/prepds/frontier/abell2744_models_display.html

And magnification estimates at a given position and redshift (RA, Dec, z) may be extracted using this web tool:
http://archive.stsci.edu/prepds/frontier/lensmodels/webtool/magnif.html

Seven lens models were submitted for Abell 2744.  In addition to models from the Bradac, CATS, Sharon, and Williams teams, the Merten-Zitrin team submitted three models.  More information about the methodologies may be found in the README files in each team's model subdirectory as well as at this webpage:
http://www.stsci.edu/hst/campaigns/frontier-fields/Lensing-Models

The following lensing primer helps explain the contents of the model directories:
http://archive.stsci.edu/prepds/frontier/lensmodels/webtool/hlsp_frontier_model_lensing_primer.pdf

Each team's model subdirectory contains FITS images with the following data:

- z01-magnif: magnification for a lensed galaxy at z = 1
- z02-magnif: magnification for a lensed galaxy at z = 2
- z04-magnif: magnification for a lensed galaxy at z = 4
- z09-magnif: magnification for a lensed galaxy at z = 9

and the following scaled to DLS / DS = 1 (see lensing primer):

- kappa: mass surface density 
- gamma: weak lensing shear

Based on these mass and shear maps, magnification maps may be calculated for any redshift using the Python script provided in this directory, or as described in the lensing primer.

Some teams also provided the following (again scaled to DLS / DS = 1):

- gamma1: weak lensing shear component 1
- gamma2: weak lensing shear component 2

- x-deflect: image deflection along the x-axis in pixels
- y-deflect: image deflection along the y-axis in pixels

Some teams also provided files containing model parameters and/or object catalogs as described in their README files.

All teams also provided a range of possible models as constrained by pre-HFF lensing observables.  Mass and shear maps are given as numbered files in subdirectories under each team:

- range/*map###*.fits

From this range of models, we may calculate a range of possible magnification maps at any redshift (as described above) according to each method.

To download all of the maps in these directories, you may use wget commands such as:
  wget -nH --cut-dirs=7 -r -l0 -c -N -np -R 'index*' -erobots=off http://archive.stsci.edu/pub/hlsp/frontier/abell2744/models/cats/range/

To view these images in ds9, we recommend scalings of:
- magnif: log 1 1000
- kappa: linear 0 3
- shear: linear 0 1

The models cover the following areas with the following resolutions as given in the FITS WCS headers:

model   |   center RA & Dec (J2000)  | width (sq) or area | resolution        | pixels on a side
CATS      00:14:20.312  -30:23:18.10    5.340' x  6.088'    0.2001" x 0.2283"    1600
Sharon    00:14:21.199  -30:23:50.08    3.369'              0.03"                6736
Zitrin    00:14:21.726  -30:24:03.36    3.000'              0.06"                3000
Williams  00:14:21.229  -30:23:48.39    2.329'              0.2794"               500
Bradac    00:14:19.511  -30:23:45.90    3.502'              0.0513"              4096
Merten    00:14:20.666  -30:24:00.86   25.053' x 25.026'    8.333"                180

If you have any questions about these data products, please e-mail Dan Coe <DCoe@STScI.edu>.
