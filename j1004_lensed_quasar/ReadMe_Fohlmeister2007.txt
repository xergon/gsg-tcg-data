J/ApJ/662/62        Optical monitoring of SDSS J1004+4112   (Fohlmeister+, 2007)
================================================================================
A time delay for the cluster-lensed quasar SDSS J1004+4112.
    Fohlmeister J., Kochanek C.S., Falco E.E., Wambsganss J., Morgan N.,
    Morgan C.W., Ofek E.O., Maoz D., Keeton C.R., Barentine J.C., Dalton G.,
    Dembicky J., Ketzeback W., McMillan R., Peters C.S.
   <Astrophys. J., 662, 62-71 (2007)>
   =2007ApJ...662...62F
================================================================================
ADC_Keywords: QSOs ; Gravitational lensing ; Photometry
Keywords: cosmology: observations - gravitational lensing -
          quasars: individual (SDSS J1004+4112)

Abstract:
    We present 426 epochs of optical monitoring data spanning 1000 days
    from 2003 December to 2006 June for the gravitationally lensed quasar
    SDSS J1004+4112. The time delay between the A and B images is
    {Delta}t_BA_=38.4+/-2.0days ({Delta}{chi}^2^=4) in the expected sense
    that B leads A and the overall time ordering is C-B-A-D-E. The
    measured delay invalidates all published models. The models probably
    failed because they neglected the perturbations from cluster member
    galaxies. Models including the galaxies can fit the data well, but
    conclusions about the cluster mass distribution should await the
    measurement of the longer, and less substructure sensitive, delays of
    the C and D images. For these images, a delay of
    {Delta}t_CB_~=681+/-15days is plausible but requires confirmation,
    while delays of {delta}t_CB_>560days and {delta}t_AD_>800 days are
    required. We clearly detect microlensing of the A/B images, with the
    delay-corrected flux ratios changing from mB-mA=0.44+/-0.01mag in the
    first season to 0.29+/-0.01mag in the second season and 0.32+/-0.01mag
    in the third season.

Description:
    The photometric monitoring observations presented here took place
    between 2003 December and 2006 June. The bulk of data were taken with
    the 1.2m telescope at Fred Lawrence Whipple Observatory on Mount
    Hopkins using the 4Shooter (R band, 93 epochs, 0.66"/pixels), Minicam
    (SDSS r band, 74 epochs, 0.604"/pixels), and Keplercam (SDSS r band,
    91 epochs, 0.672"/pixels, plus 4 epochs in R band) during the first,
    second, and third season, respectively. Additional data were obtained
    with the Apache Point Observatory (APO) 3.5m telescope using SPICam
    (SDSS r band, 9 epochs, 0.282"/pixels), the MDM 2.4m Hiltner
    telescope using the RETROCAM (SDSS r band, 27 epochs, 0.259"/pixels),
    8K (R band, 12 epochs, 0.344"/pixels), Templeton (R band, 8 epochs,
    0.275"/pixels) and Echelle (R band, 3 epochs, 0.275"/pixels)
    detectors, the MDM 1.3m McGraw-Hill telescope using the Templeton
    detector (R band, 6 epochs, 0.508"/pixels), the Palomar Observatory
    1.5m telescope using the SITe detector (R band, 13 epochs,
    0.379"/pixels), the Wise Observatory 1.0m telescope with the Tektronix
    (R band, 30 epochs, 0.696"/pixels) and TAVAS (clear, 53 epochs,
    0.991"/pixels) detectors, and the WIYN 3.5m telescope using the WTTM
    (SDSS r band, 3 epochs, 0.216"/pixels) detector. The combined data set
    consists of 426 epochs.

Objects:
    ---------------------------------------------------------------
       RA   (2000)   DE         Designation(s)
    ---------------------------------------------------------------
    10 04 34.9   +41 12 42.8    SDSS J1004+4112 = QSO J1004+4112
    ---------------------------------------------------------------

File Summary:
--------------------------------------------------------------------------------
 FileName   Lrecl  Records   Explanations
--------------------------------------------------------------------------------
ReadMe         80        .   This file
table1.dat     89      426   Light curves for SDSS J1004+4112
--------------------------------------------------------------------------------

See also:
  J/MNRAS/382/412 : Catalog of SDSS-DR5/2MASS spectroscopic quasars (Ofek, 2007)
  J/AJ/132/999    : SDSS quasar lens search (Oguri+, 2006)

Byte-by-byte Description of file: table1.dat
--------------------------------------------------------------------------------
   Bytes Format Units   Label     Explanations
--------------------------------------------------------------------------------
   1- 11  F11.3 d       HJD       Heliocentric Julian Date
  13- 18  F6.2  ---     Rchi2     The {chi}^2^ divided by degrees of freedom (1)
  20- 25  F6.3  mag     ImAmag    Image A magnitude (2)
  27- 31  F5.3  mag   e_ImAmag    Uncertainty in Image A
      32  A1    ---   f_ImAmag    [)] not used in the time delay estimates.
  34- 39  F6.3  mag     ImBmag    Image B magnitude (2)
  41- 45  F5.3  mag   e_ImBmag    Uncertainty in Image B
      46  A1    ---   f_ImBmag    [)] not used in the time delay estimates.
  48- 52  F5.3  mag     ImCmag    Image C magnitude (2)
  54- 58  F5.3  mag   e_ImCmag    Uncertainty in Image C
  60- 65  F6.3  mag     ImDmag    Image D magnitude (2)
  67- 71  F5.3  mag   e_ImDmag    Uncertainty in Image D
  73- 79  A7    ---     Obs       Observatory (4)
  81- 89  A9    ---     Det       Detector
--------------------------------------------------------------------------------
Note (1): Indicates how well our photometric model fit the imaging data.
     When {chi}^2^ > N_Dof_ we rescale the photometric errors presented in
     this Table by ({chi}^2^/N_dof_)^1/2^ before carrying out the time
     delay analysis to reduce the weight of images that were fit poorly.
Note (2): Relative to the comparison stars (see text).
Note (4): Observatories as follows:
      MDM = MDM 2.4m/1.3m Hiltner/McGraw-Hill telescopes
     FLWO = 1.2m telescope at Fred Lawrence Whipple Observatory on Mount Hopkins
     Wise = Wise Observatory 1.0m telescope
  Palomar = Palomar Observatory 1.5m telescope
      APO = Apache Point Observatory 3.5m telescope
     WIYN = WIYN 3.5m telescope
--------------------------------------------------------------------------------

History:
    From electronic version of the journal
================================================================================
(End)                  Greg Schwarz [AAS], Patricia Vannier [CDS]    16-Apr-2009
