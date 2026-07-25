# This script describes the imaging for the ALMA LBC SV B7 data on SDP.81

# Requires CASA 4.2.2 or higher. Meant to be run interactively.

###################################################################
# If working from the individual datasets
# Combine the 11-dataset, 4-spw continuum
os.system('rm -rf SDP81_band7_11exec.ms.calavg')
vislist = ['../Xb6/SDP81_Xb6.ms.split.calavg',  
            '../X2eb/SDP81_X2eb.ms.split.calavg',
            '../X517/SDP81_X517.ms.split.calavg',
            '../X5e6/SDP81_X5e6.ms.split.calavg',
            '../X812/SDP81_X812.ms.split.calavg',
            '../Xe29/SDP81_Xe29.ms.split.calavg',
            '../X1059/SDP81_X1059.ms.split.calavg',
            '../X1336/SDP81_X1336.ms.split.calavg',
            '../X1562/SDP81_X1562.ms.split.calavg',
            '../Xa99/SDP81_Xa99.ms.split.calavg',
            '../Xcc5/SDP81_Xcc5.ms.split.calavg']
concat(vis=vislist,  concatvis='SDP81_band7_11exec.ms.calavg')

# Create 11-dataset, 4-spw all data (only build this to split out the
# CO 10-9 spw).
os.system('rm -rf SDP81_band7_11exec.ms.cal')
concat(vis=['../Xb6/uid___A002_X91dc9f_Xb6.ms.split.cal',
            '../X2eb/uid___A002_X91dc9f_X2eb.ms.split.cal',
            '../X517/uid___A002_X91dc9f_X517.ms.split.cal',
            '../X5e6/uid___A002_X91f01f_X5e6.ms.split.cal',
            '../X812/uid___A002_X91f01f_X812.ms.split.cal',
            '../Xe29/uid___A002_X920302_Xe29.ms.split.cal',
            '../X1059/uid___A002_X920302_X1059.ms.split.cal',
            '../X1336/uid___A002_X920302_X1336.ms.split.cal',
            '../X1562/uid___A002_X920302_X1562.ms.split.cal',
            '../Xa99/uid___A002_X925649_Xa99.ms.split.cal',
            '../Xcc5/uid___A002_X925649_Xcc5.ms.split.cal'],
       concatvis='SDP81_band7_11exec.ms.cal')

split('SDP81_band7_11exec.ms.cal', spw='3', field='SDP.81',
      outputvis = 'SDP81_band7_11exec.ms.spw3', datacolumn='data')


###################################################################
###################################################################
# THESE TWO MS FILES ARE CONTAINED IN THE SCIENCE PORTAL (SP) DATA 
# PRODUCT CALLED "CalibratedData". If you have downloaded these 
# products, start below this section for imaging. 
###################################################################
###################################################################

# Here we flag the second channel of spw3 because 230/240 channels in the
# parent datasets that contribute to this channel were flagged due to the
# presence of the CO 10-9 line, and CASA version 4.2.2 does not produce
# channelized weights that would allow one to perform a proper weighted sum.
# The loss in sensitivity is negligible.
# 
flagdata(vis='SDP81_band7_11exec.ms.calavg', spw='3:1', flagbackup=False,
         mode='manual')

os.system('rm -f SDP81_band7_11exec.ms.calavg.listobs')
listobs('SDP81_band7_11exec.ms.calavg',
        listfile='SDP81_band7_11exec.ms.calavg.listobs')

#################################################################
# Create a continuum image at nominal resolution.
os.system('rm -rf SDP81_band7_11exec.contR1.*')
clean(vis='SDP81_band7_11exec.ms.calavg',
      imagename='SDP81_band7_11exec.contR1',multiscale=[0,5,15],
      mode='mfs',nterms=1,imagermode='csclean',
      imsize=3000,cell='0.005arcsec',negcomponent=10,
      mask='',
      interactive=True,  weighting='briggs', robust=1.0,
      niter=50000,threshold='0.018mJy')   # sigma=9uJy

exportfits('SDP81_band7_11exec.contR1.image',
           'SDP81_band7_11exec.contR1.image.fits')

####################################################################
# Continuum subtract and image the line data    

listobs('SDP81_band7_11exec.ms.spw3',
        listfile='SDP81_band7_11exec.ms.spw3.listobs')

os.system('rm -rf SDP81_band7_11exec.ms.spw3.contuub')
uvcontsub(vis='SDP81_band7_11exec.ms.spw3',
          fitorder=1,fitspw='0:0~218;608~959')

# Clean with the same parameters as CO8-7, and same image
# dimensions, even though there is no data in the -1000 to 
# -818 km/s range.  This will make it easier to blink between
# them in the viewer.
os.system('rm -rf SDP81_11exec.co109.R1uvtaper1000kl.*')
clean(vis='SDP81_band7_11exec.ms.spw3.contsub',
      imagename='SDP81_11exec.co109.R1uvtaper1000kl',
      mode='velocity',imagermode='csclean',
      imsize=672,cell='0.02arcsec',multiscale=[0,5,15],
      start='-1000km/s',width='21km/s',nchan=100,
      outframe='LSRK',restfreq='285.00382GHz',
      interactive=True,  mask='',
      uvtaper=True,
      outertaper=['1000klambda'], usescratch=True,
      weighting='briggs',robust=1.0,
      niter=500000,threshold='0.5mJy')
# beam = 0.172 x 0.112 at +42 deg

os.system('rm -rf SDP81_11exec.co109.R1uvtaper1000kl.image.mom0_2.5sigma')
immoments('SDP81_11exec.co109.R1uvtaper1000kl.image',moments=[0],
          outfile='SDP81_11exec.co109.R1uvtaper1000kl.image.mom0_2.5sigma',
          includepix=[2.5*0.25e-3, 100], chans='10~90')

exportfits('SDP81_11exec.co109.R1uvtaper1000kl.image.mom0_2.5sigma',
           'SDP81_11exec.co109.R1uvtaper1000kl.image.mom0_2.5sigma.fits')

exportfits('SDP81_11exec.co109.R1uvtaper1000kl.image',
           'SDP81_11exec.co109.R1uvtaper1000kl.image.fits')

# Make a continuum image at the same taper as the lines
clean(vis='SDP81_band7_11exec.ms.calavg',
      imagename='SDP81_band7_11exec.R1uvtaper1000klambda',multiscale=[0,5,15],
      mode='mfs',nterms=1,imagermode='csclean',negcomponent=10,
      imsize=672,cell='0.02arcsec', uvtaper=True,
      outertaper=['1000klambda'],
      interactive=True,  weighting='briggs', robust=1.0,
      niter=500000,threshold='0.03mJy') 

