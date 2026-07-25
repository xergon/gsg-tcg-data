# This script describes the imaging for the ALMA LBC SV B4 data on SDP.81
# Observed lines
# CO(5-4) at z=3.042, redshifted to freq=142.5700GHz
#
# (Note that prior to 17 April 2015, z=3.04, CO(5-4) redshifted to
# freq=142.640577GHz, was adopted. It has been updated to z=3.042 for
# consistency with the imaging scripts for Bands 6 and 7).

# Requires CASA 4.2.2 or higher. Meant to be run interactively.

###################################################################
# If working from the individual datasets

# NOTE spectral averaging was already done (every 16 channels for
# continuum and 20 for the line data) in the individual calibration
# scripts.

# Concatenate datasets:
band4_calibrated_data = ['uid___A002_X91068d_Xa1e.ms.split.cal.science',
                         'uid___A002_X91068d_Xc50.ms.split.cal.science',
                         'uid___A002_X91068d_Xead.ms.split.cal.science',
                         'uid___A002_X915f1c_X5d0.ms.split.cal.science',
                         'uid___A002_X924c91_X12c.ms.split.cal.science',
                         'uid___A002_X924c91_X34f.ms.split.cal.science',
                         'uid___A002_X924c91_X572.ms.split.cal.science',
                         'uid___A002_X924c91_X847.ms.split.cal.science',
                         'uid___A002_X924c91_Xa47.ms.split.cal.science',
                         'uid___A002_X93514d_X1634.ms.split.cal.science',
                         'uid___A002_X93514d_X1857.ms.split.cal.science',
                         'uid___A002_X93514d_Xfc6.ms.split.cal.science']

os.system('rm -rf SDP.81_Band4.ms')
concat(vis = band4_calibrated_data, concatvis = 'SDP.81_Band4.ms')

# Define spectral windows for the continuum.  
spw_cont = '0~2,4~6,8~10,12~14,16~18,20~22,24~26,28~30,32~34,36~38,40~42,44~46'
os.system('rm -rf SDP.81_Band4_continuum.ms')
split(vis='SDP.81_Band4.ms',outputvis='SDP.81_Band4_continuum.ms',
      spw=spw_cont,datacolumn='data')

###################################################################
###################################################################
# THESE TWO MS FILES ARE CONTAINED IN THE SCIENCE PORTAL (SP) DATA 
# PRODUCT CALLED "CalibratedData". If you have downloaded these 
# products, start below this section for imaging. 
###################################################################
###################################################################


# Define spectral windows for the continuum and line emission
spw_cont = '0~2,4~6,8~10,12~14,16~18,20~22,24~26,28~30,32~34,36~38,40~42,44~46'
spw_line = '3,7,11,15,19,23,27,31,35,39,43,47'

# Split continuum and spectral line observations 

os.system('rm -rf SDP.81_Band4_COline.ms')
split(vis='SDP.81_Band4.ms',outputvis='SDP.81_Band4_COline.ms',
      spw=spw_line,datacolumn='data')


# First, we image the continuum data, using robust=1 weighting,
# multiscale cleaning, and a mask selected during interactive mode

os.system('rm -rf SDP.81.continuum.*')
clean(vis='SDP.81_Band4_continuum.ms',
      imagename='SDP.81.continuum', 
      spw='',field='SDP*',
      mode='mfs',nterms=1,imagermode='csclean',
      imsize=1500,cell='0.01arcsec',
      multiscale=[0,5,15,45],
      interactive=True,negcomponent=10,
      mask = '',
      weighting='briggs',robust=1.0,
      niter=3000,threshold='0.02mJy') # sigma = 0.008mJy/beam

# Since some emission is resolved out at this angular resolution,
# we image the target tapering the uv-data at long baselines
# to emphasize and recover more of the extended emission.

os.system('rm -rf SDP.81.continuum_smooth.*')
clean(vis='SDP.81_Band4_continuum.ms',
      imagename='SDP.81.continuum_smooth',
      spw='',field='SDP*',
      mode='mfs',nterms=1,imagermode='csclean',
      imsize=1500,cell='0.01arcsec',
      multiscale=[0,5,15,45],
      interactive=True,  mask='',
      weighting='briggs',robust=1.0,
      uvtaper=True,outertaper=['1000klambda'],
      niter=1400,threshold='0.025mJy')

#viewer('SDP.81.continuum_smooth.image')
#RMS = 0.011mJy


# Export to fits files:
exportfits(imagename='SDP.81.continuum.image',fitsimage='SDP.81_B4_cont.fits')
exportfits(imagename='SDP.81.continuum_smooth.image', fitsimage='SDP.81_B4_cont_smooth.fits')


##############################################################
# Spectral line:
# CO(5-4) at z=3.042, redshifted to freq=142.5700GHz



# Plot the data to determine uvcontsub parameters

plotms('SDP.81_Band4_COline.ms',yaxis='amp',xaxis='velocity',avgtime='1e8',
       coloraxis='spw',restfreq='142.5700GHz',freqframe='LSRK',transform=True)

os.system('rm -rf SDP.81_Band4_COline.ms.contsub')
uvcontsub(vis='SDP.81_Band4_COline.ms',
          fitorder=1,fitspw='0~11:5~45;170~187')

# Imaging target - robust=1 weighting and uvtapering of longest baselines:
# -----------------------------------------------------------------------
# CO emission detected between -200 to +400 km/s, hence only these channels
# have a cleaning box, defined during interactive cleaning
os.system('rm -rf SDP.81.Band4.CO_smooth.*')
clean(vis='SDP.81_Band4_COline.ms.contsub',
      imagename='SDP.81.Band4.CO_smooth',
      mask='prior.mask',
      mode='velocity',imagermode='csclean',
      imsize=672, cell='0.02arcsec',
      start='-1000km/s',width='21km/s',nchan=119,
      outframe='LSRK',restfreq='142.5700GHz',
      multiscale=[0,5,15,45],negcomponent=10,
      interactive=True,usescratch=True,
      weighting='briggs',robust=1.0,
      uvtaper=True,outertaper=['1000klambda'],
      niter=2000,threshold='0.52mJy')

#viewer('SDP.81.Band4.CO_smooth.image')
# RMS = 0.20mJy


# Imaging target - robust=1 weighting and no uvtapering:
# ------------------------------------------------------
# we defined a cleaning box during interactive cleaning.
os.system('rm -rf SDP.81.Band4.CO.*')
clean(vis='SDP.81_Band4_COline.ms.contsub',
      imagename='SDP.81.Band4.CO',
      mask='prior.mask',
      mode='velocity',imagermode='csclean',
      imsize=1500,cell='0.01arcsec',
      start='-1000km/s',width='21km/s',nchan=119,
      outframe='LSRK',restfreq='142.5700GHz',
      multiscale=[0,5,15,45],negcomponent=10,
      interactive=True,usescratch=True,
      weighting='briggs',robust=1.0,
      niter=2000,threshold='0.35mJy')

#viewer('SDP.81.Band4.CO.image')
# RMS = 0.18mJy . km/s




##############################################

immoments(imagename='SDP.81.Band4.CO.image',
           chans='33~71',moments=[0],includepix=[2*0.18e-3,100], # -300 to +500 km/s
           outfile='SDP.81.Band4.CO.image.mom0_2sigma')

immoments(imagename='SDP.81.Band4.CO_smooth.image',
           chans='33~71',moments=[0],includepix=[2*0.20e-3,100], # -300 to +500 km/s
           outfile='SDP.81.Band4.CO_smooth.image.mom0_2sigma')

exportfits(imagename='SDP.81.Band4.CO.image', fitsimage='SDP.81.Band4.CO_z3.042.fits')
exportfits(imagename='SDP.81.Band4.CO_smooth.image', fitsimage='SDP.81.Band4.CO_smooth_z3.042.fits')

exportfits(imagename='SDP.81.Band4.CO.image.mom0_2sigma', fitsimage='SDP.81.Band4.CO.mom0_z3.042.fits')
exportfits(imagename='SDP.81.Band4.CO_smooth.image.mom0_2sigma', fitsimage='SDP.81.Band4.CO_smooth.mom0_z3.042.fits')



