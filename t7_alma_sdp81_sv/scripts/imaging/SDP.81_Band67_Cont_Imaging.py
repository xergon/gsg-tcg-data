# This script describes the combined imaging of the ALMA LBC SV data
# for Band 6 + Band 7

# requires CASA 4.2.2 or higher. Meant to be run interactively.

# It requires that you have either downloaded the Band 6 and 7
# CalibratedData from the ALMA Science Portal SV page and applied
# the flagdata commands in their individual imaging scripts along
# with the self-calibration tables supplied at the Science Portal.


#########################################################################

# Make a combined continuum image with same parameters as the spectral
# line cubes using nterms=2 to solve for spectral index.  
# Note: the signal-to-noise is not high enough to do this at full
# resolution (and achieve an image with a reliable flux scale).



os.system('rm -rf SDP81_B67.continuum.R1uvtaper1000klambda.*')
clean(vis=['SDP81_band6_9exec.ms.calavg',
           'SDP81_band7_11exec.ms.calavg'],
      imagename='SDP81_B67.continuum.R1uvtaper1000klambda',
      mode='mfs',nterms=2,imagermode='csclean',
      imsize=672,cell='0.02arcsec', uvtaper=True,
      outertaper=['1000klambda'],
      multiscale=[0,5,15],negcomponent=10,
      interactive=True,  weighting='briggs', robust=1.0,
      niter=20000,threshold='0.03mJy')    

# Output the image at the combined (mean) frequency
exportfits('SDP81_B67.continuum.R1uvtaper1000klambda.image.tt0',
           'SDP81_B67.continuum.R1uvtaper1000klambda.image.tt0.fits')

# Output the spectral index image
exportfits('SDP81_B67.continuum.R1uvtaper1000klambda.image.alpha',
           'SDP81_B67.continuum.R1uvtaper1000klambda.image.alpha.fits')
# beam = 0.163 x 0.110   rms=0.015mJy/beam

