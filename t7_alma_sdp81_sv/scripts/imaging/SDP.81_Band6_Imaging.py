# This script describes the imaging for the ALMA LBC SV B6 data on SDP.81

# Requires CASA 4.2.2 or higher. Meant to be run interactively.

###################################################################
# If working from the individual datasets

# 9-dataset combination of Continuum
# The CO8-7 channels were flagged in spw 2 in each *.scriptForCalibration.py
# prior to the generation of the .split.calavg measurement set.
os.system('rm -rf SDP81_band6_9exec.ms.calavg')
concat(vis=['../X188b/SDP81_X188b.ms.split.calavg',
            '../X1484/SDP81_X1484.ms.split.calavg',
            '../X11d6/SDP81_X11d6.ms.split.calavg',
            '../X8be/SDP81_X8be.ms.split.calavg',
            '../X1716/SDP81_X1716.ms.split.calavg',
            '../X43c/SDP81_X43c.ms.split.calavg',
            '../X65f/SDP81_X65f.ms.split.calavg',
            '../X1099/SDP81_X1099.ms.split.calavg',
            '../X1f23/SDP81_X1f23.ms.split.calavg',
            ],
       concatvis='SDP81_band6_9exec.ms.calavg')

# 9-dataset combination at full resolution (needed to split off the line spw)
os.system('rm -rf SDP81_band6_9exec.ms')
concat(vis=['../X188b/SDP81_X188b.ms.split.cal',
            '../X1484/SDP81_X1484.ms.split.cal',
            '../X11d6/SDP81_X11d6.ms.split.cal',
            '../X8be/SDP81_X8be.ms.split.cal',
            '../X1716/SDP81_X1716.ms.split.cal',
            '../X43c/SDP81_X43c.ms.split.cal',
            '../X65f/SDP81_X65f.ms.split.cal',
            '../X1099/SDP81_X1099.ms.split.cal',
            '../X1f23/SDP81_X1f23.ms.split.cal',
            ],
       concatvis='SDP81_band6_9exec.ms')

# split of the CO8-7 line spw
os.system('rm -rf SDP81_band6_9exec.ms.co87')
split(vis='SDP81_band6_9exec.ms',
      outputvis='SDP81_band6_9exec.ms.co87', 
      width=1,datacolumn='data',spw='2') # gives 128 channels of ~20.5km/s each

# H2O 2(0,2)-1(1,1)
# Note that the channel averaging was increased by a factor of two after the
# first 5 datasets so we resample the first 5 datasets (spw=3) with the same
# resolution as the latter 4 (spw=4).
os.system('rm -rf SDP81_band6_9exec.ms.h2o')
split(vis='SDP81_band6_9exec.ms',
      outputvis='SDP81_band6_9exec.ms.h2o', 
      width=[2,1],datacolumn='data',spw='3,4') # gives 960 chans of 2.5km/s

###################################################################
###################################################################
# THESE THREE MS FILES ARE CONTAINED IN THE SCIENCE PORTAL (SP) DATA 
# PRODUCT CALLED "CalibratedData". If you have downloaded these 
# products, start below this section for imaging. 
###################################################################
###################################################################

###################################################################
# Continuum imaging
os.system('rm -rf SDP81_band6_9exec.contR1.*')
clean(vis='SDP81_band6_9exec.ms.calavg',
      imagename='SDP81_band6_9exec.contR1',multiscale=[0,5,15],
      mode='mfs',nterms=1,imagermode='csclean',
      imsize=3000,cell='0.005arcsec',  # use same cellsize as Band 7
      interactive=False,  weighting='briggs', robust=1.0,
      niter=500000,threshold='0.020mJy', negcomponent=10)  

exportfits('SDP81_band6_9exec.contR1.image',
           'SDP81_band6_9exec.contR1.image.fits')

###################################################################
# Line imaging

# CO 8-7
# restfreq = 921.79970;  sky freq = 228.05534 GHz
# ch 1 = 228.992188 increment=-15.625 MHz
# peak of line = 60 channels from 1 = channel 61
# width of line = +- 400km/s = 304MHz =  19.5 channels
# Define continuum as channels: 0~41;81~127
uvcontsub(vis='SDP81_band6_9exec.ms.co87',
          fitorder=1,fitspw='0:0~41;81~127')

# Plotms shwos that scan 163 is noisier than the rest.   Flag it.
flagmanager(vis='SDP81_band6_9exec.ms.co87.contsub',
            mode='save', versionname='before_scan163')
flagdata(vis='SDP81_band6_9exec.ms.co87.contsub',
         mode='manual', scan='163', flagbackup=False)

# The final obsID = 8 is noisier than the rest due to high PWV and
# low elevation (30 deg), but the weights are correctly lower by
# a factor of ~4, so it should not be a problem to include it.


# Clean the whole CO8-7 cube with optimum parameters: R=1.0, taper=1000
# from -1000 to +1079 km/s.  Yields beam = 0.169 x 0.117
os.system('rm -rf SDP81_9exec.co87.R1uvtaper1000klambda.*')
clean(vis='SDP81_band6_9exec.ms.co87.contsub',
      imagename='SDP81_9exec.co87.R1uvtaper1000klambda',
      mode='velocity',imagermode='csclean',negcomponent=10,
      imsize=672,cell='0.02arcsec', multiscale=[0,5,15],
      start='-1000km/s',width='21km/s',nchan=100,
      outframe='LSRK',restfreq='228.05534GHz',
      interactive=True,  uvtaper=True,
      outertaper=['1000klambda'], usescratch=True,
      weighting='briggs',robust=1.0,
      niter=10000,threshold='0.40mJy')  # 1-sigma  = 0.15mJy

exportfits('SDP81_9exec.co87.R1uvtaper1000klambda.image',
           'SDP81_9exec.co87.R1uvtaper1000klambda.fits')

immoments('SDP81_9exec.co87.R1uvtaper1000klambda.image',moments=[0],
          outfile='SDP81_9exec.co87.R1uvtaper1000klambda.mom2sigma',
          includepix=[2*0.15e-3, 100])

immoments('SDP81_9exec.co87.R1uvtaper1000klambda.image',moments=[1],
          outfile='SDP81_9exec.co87.R1uvtaper1000klambda.mom',
          includepix=[5*0.15e-3, 100])

exportfits('SDP81_9exec.co87.R1uvtaper1000klambda.mom2sigma',
           'SDP81_9exec.co87.R1uvtaper1000klambda.mom0.2sigma.fits')

exportfits('SDP81_9exec.co87.R1uvtaper1000klambda.mom.weighted_coord',
           'SDP81_9exec.co87.R1uvtaper1000klambda.mom1.fits')



os.system('rm SDP81_band6_9exec.ms.h2o.listobs')
listobs('SDP81_band6_9exec.ms.h2o',listfile='SDP81_band6_9exec.ms.h2o.listobs')

# Water line rest freq = 987.92676 GHz,  sky freq = 244.415 GHz
# spw 3 ch 0 = 243.562988  inc=0.976562, or 872 channels
# so channel 873 of 1920 is the line peak (0 velocity)
# 400km/s = 325 channels, so 548-1198 is possibly line emission
# resampling to 960 channels, means divide by 2, which gives 274~599
# so for the continuum, use 0~273;600~959
os.system('rm -rf SDP81_band6_9exec.ms.h2o.contsub')
uvcontsub(vis='SDP81_band6_9exec.ms.h2o',
          fitorder=1,fitspw='0:0~273;600~959,1:0~273;600~959')

# Use the same imaging parameters for H2O as for CO 8-7, and
# covering -600 to +555 km/s at 10.5 km/s resolution, wich
# is 1/2 of the CO channel width.
os.system('rm -rf SDP81_9exec.h2o.R1uvtaper1000klambda.10.5kms.*')
clean(vis='SDP81_band6_9exec.ms.h2o.contsub',
      imagename='SDP81_9exec.h2o.R1uvtaper1000klambda.10.5kms',
      mode='velocity',imagermode='csclean',usescratch=True,
      imsize=672,cell='0.02arcsec',multiscale=[0,5,15],
      start='-600km/s',width='10.5km/s',nchan=110,
      outframe='LSRK',restfreq='244.415GHz',
      interactive=True,  mask='',
      uvtaper=True, outertaper=['1000klambda'], 
      weighting='briggs',robust=1.0,
      niter=10000,threshold='0.9mJy')  # rms=0.45 mJy/b
# beam = 0.169 x 0.113 arcsec

immoments('SDP81_9exec.h2o.R1uvtaper1000klambda.10.5kms.image',moments=[0],
          outfile='SDP81_9exec.h2o.R1uvtaper1000klambda.10.5kms.mom0_4sigma',
          includepix=[4*0.45e-3, 100])

exportfits('SDP81_9exec.h2o.R1uvtaper1000klambda.10.5kms.image',
           'SDP81_9exec.h2o.R1uvtaper1000klambda.10.5kms.fits')
    
exportfits('SDP81_9exec.h2o.R1uvtaper1000klambda.10.5kms.mom0_4sigma',
           'SDP81_9exec.h2o.R1uvtaper1000klambda.10.5kms.mom0_4sigma.fits')

# Make a continuum image at the same taper as the line cubes.
clean(vis='SDP81_band6_9exec.ms.calavg',
      imagename='SDP81_band6_9exec.R1uvtaper1000klambda',multiscale=[0,5,15],
      mode='mfs',nterms=1,imagermode='csclean',negcomponent=10,
      mask='SDP81_B67.continuum.mask',
      interactive=False,  weighting='briggs', robust=1.0,
      imsize=672,cell='0.02arcsec', uvtaper=True,
      outertaper=['1000klambda'],
      niter=500000,threshold='0.03mJy')  
