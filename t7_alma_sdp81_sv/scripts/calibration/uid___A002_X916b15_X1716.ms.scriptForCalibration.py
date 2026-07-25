# ALMA Data Reduction Script

# Calibration

thesteps = []
step_title = {0: 'Import of the ASDM',
              1: 'Fix of SYSCAL table times',
              2: 'listobs',
              3: 'A priori flagging',
              4: 'Generation and time averaging of the WVR cal table',
              5: 'Generation of the Tsys cal table',
              6: 'Generation of the antenna position cal table',
              7: 'Application of the WVR, Tsys and antpos cal tables',
              8: 'Split out science SPWs and time average',
              9: 'Listobs, clear pointing table, and save original flags',
              10: 'Initial flagging',
              11: 'Putting a model for the flux calibrator(s)',
              12: 'Save flags before bandpass cal',
              13: 'Bandpass calibration',
              14: 'Save flags before gain cal',
              15: 'Gain calibration',
              16: 'Save flags before applycal',
              17: 'Application of the bandpass and gain cal tables',
              18: 'Split out corrected column'}

if 'applyonly' not in globals(): applyonly = False
try:
  print 'List of steps to be executed ...', mysteps
  thesteps = mysteps
except:
  print 'global variable mysteps not set.'
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print 'Executing all steps: ', thesteps

# The Python variable 'mysteps' will control which steps
# are executed when you start the script using
#   execfile('scriptForCalibration.py')
# e.g. setting
#   mysteps = [2,3,4]# before starting the script will make the script execute
# only steps 2, 3, and 4
# Setting mysteps = [] will make it execute all steps.

import re

import os

if applyonly != True: es = aU.stuffForScienceDataReduction() 


if re.search('^4.2.2', casadef.casa_version) == None:
 sys.exit('ERROR: PLEASE USE THE SAME VERSION OF CASA THAT YOU USED FOR GENERATING THE SCRIPT: 4.2.2')


# CALIBRATE_AMPLI: J0854+2006
# CALIBRATE_ATMOSPHERE: J0825+0309,J0854+2006,J0914+0245,SDP.81
# CALIBRATE_BANDPASS: J0825+0309
# CALIBRATE_FLUX: J0854+2006
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J0914+0245
# CALIBRATE_POINTING: J0825+0309
# OBSERVE_TARGET: SDP.81

# Using reference antenna = DV09

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_X916b15_X1716.ms') == False:
    importasdm('uid___A002_X916b15_X1716', asis='Antenna Station Receiver Source CalAtmosphere CalWVR')
  if applyonly != True: es.fixForCSV2555('uid___A002_X916b15_X1716.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_X916b15_X1716.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X916b15_X1716.ms.listobs')
  listobs(vis = 'uid___A002_X916b15_X1716.ms',
    listfile = 'uid___A002_X916b15_X1716.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_X916b15_X1716.ms',
    mode = 'manual',
    spw = '1~21',
    autocorr = T,
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_X916b15_X1716.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = F)
  
  flagcmd(vis = 'uid___A002_X916b15_X1716.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_X916b15_X1716.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_X916b15_X1716.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X916b15_X1716.ms.wvr') 
  
  os.system('rm -rf uid___A002_X916b15_X1716.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X916b15_X1716.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_X916b15_X1716.ms',
    caltable = 'uid___A002_X916b15_X1716.ms.wvr',
    toffset = 0,
    tie = ['SDP.81,J0914+0245'],
    statsource = 'SDP.81')
  
  casalog.setlogfile(mylogfile)
  
  # This is a temporary workaround, which will be included in a future version of CASA
  
  tb.open('uid___A002_X916b15_X1716.ms.wvr', nomodify=False)
  count = 0
  numrows = tb.nrows()
  mycparamcol = tb.getcol('CPARAM')
  for i in range(0, numrows):
      if mycparamcol[0][0][i] == (1.+0.j):
          tb.putcell('FLAG', i, [[True]])
          count += 1
  tb.close()
  del mycparamcol
  if(numrows>0):
      print 'Flagged', count, 'of', numrows, 'solutions =', 100.*count/float(numrows),'%'
  
  
  os.system('rm -rf uid___A002_X916b15_X1716.ms.wvr.smooth') 
  
  smoothcal(vis = 'uid___A002_X916b15_X1716.ms',
    tablein = 'uid___A002_X916b15_X1716.ms.wvr',
    caltable = 'uid___A002_X916b15_X1716.ms.wvr.smooth',
    smoothtype = 'mean',
    smoothtime = 6.048)
  
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_X916b15_X1716.ms.wvr.smooth', spw='11', antenna='DV09',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_X916b15_X1716.ms.wvr.smooth.plots/uid___A002_X916b15_X1716.ms.wvr.smooth') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X916b15_X1716.ms.tsys') 
  gencal(vis = 'uid___A002_X916b15_X1716.ms',
    caltable = 'uid___A002_X916b15_X1716.ms.tsys',
    caltype = 'tsys')
  flagdata('uid___A002_X916b15_X1716.ms.tsys',flagbackup=False,mode='manual',
           spw='9:0~3;124~127,11:0~3;124~127,13:0~3,124~127,15:0~3,124~127')
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_X916b15_X1716.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='5~123',showfdm=True, 
    field='', figfile='uid___A002_X916b15_X1716.ms.tsys.plots.overlayTime/uid___A002_X916b15_X1716.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_X916b15_X1716.ms.tsys', msName='uid___A002_X916b15_X1716.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]
  os.system('rm -rf uid___A002_X916b15_X1716.ms.antpos') 
  gencal(vis = 'uid___A002_X916b15_X1716.ms',
    caltable = 'uid___A002_X916b15_X1716.ms.antpos',
    caltype = 'antpos',
    parameter = [-0.0017382, +0.002224, +0.000802, # DA41 on S301 change=2.935mm
                 -0.0020990, +0.002281, +0.000397, # DA43 on S306 change=3.125mm
                 -0.0002283, +0.000688, +0.000188, # DA45 on A127 change=0.749mm
                 -0.0013670, +0.001688, -0.000025, # DA46 on A058 change=2.172mm
                 +0.0003610, -0.000860, -0.000305, # DA48 on W207 change=0.981mm
                 -0.0002937, +0.000536, +0.000205, # DA49 on A029 change=0.645mm
                 +0.0013120, -0.002341, -0.000482, # DA50 on W204 change=2.727mm
                 -0.0003235, +0.000310, -0.000253, # DA51 on A082 change=0.515mm
                 -0.0006170, -0.000772, -0.002025, # DA55 on S309 change=2.253mm
                 -0.0012060, +0.001494, +0.000602, # DA56 on A131 change=2.012mm
                 -0.0002500, +0.000522, +0.000186, # DA61 on A075 change=0.607mm
                 +0.0008350, -0.001575, -0.000489, # DA62 on W206 change=1.849mm
                 -0.0004555, +0.001180, +0.000210, # DA63 on A132 change=1.282mm
                 -0.0023837, +0.002720, +0.000299, # DA64 on P402 change=3.629mm
                 -0.0014020, +0.001740, +0.000449, # DA65 on P401 change=2.279mm
                 -0.0005062, +0.000614, +0.000190, # DV01 on A072 change=0.818mm
                 -0.0015335, +0.001681, -0.000106, # DV04 on A078 change=2.278mm
                 +0.0002210, -0.001266, +0.000329, # DV07 on W201 change=1.327mm
                 -0.0012494, +0.000979, +0.000365, # DV08 on A133 change=1.629mm
                 -0.0008851, +0.001659, +0.000376, # DV09 on A124 change=1.918mm
                 -0.0004107, +0.000539, +0.000109, # DV10 on A024 change=0.687mm
                 -0.0009172, +0.001557, +0.000406, # DV11 on A121 change=1.852mm
                 -0.0004596, +0.000429, +0.000536, # DV12 on A113 change=0.826mm
                 -0.0017830, +0.000726, -0.001078, # DV13 on S303 change=2.206mm
                 -0.0003510, +0.001720, -0.000659, # DV14 on P405 change=1.875mm
                 -0.0019810, +0.002374, +0.000330, # DV15 on A118 change=3.110mm
                 -0.0018450, +0.003876, +0.000473, # DV19 on P410 change=4.319mm
                 -0.0025370, +0.002050, -0.000760, # PM02 on T702 change=3.349mm
                 -0.0001749, +0.000694, +0.000152], # PM03 on T701 change=0.732mm
    antenna = 'DA41,DA43,DA45,DA46,DA48,DA49,DA50,DA51,DA55,DA56,DA61,DA62,DA63,DA64,DA65,DV01,DV04,DV07,DV08,DV09,DV10,DV11,DV12,DV13,DV14,DV15,DV19,PM02,PM03')
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_X916b15_X1716.ms', tsystable = 'uid___A002_X916b15_X1716.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_X916b15_X1716.ms',
    field = '0',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X916b15_X1716.ms.tsys', 'uid___A002_X916b15_X1716.ms.wvr.smooth', 'uid___A002_X916b15_X1716.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X916b15_X1716.ms',
    field = '1',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X916b15_X1716.ms.tsys', 'uid___A002_X916b15_X1716.ms.wvr.smooth', 'uid___A002_X916b15_X1716.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X916b15_X1716.ms',
    field = '2',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X916b15_X1716.ms.tsys', 'uid___A002_X916b15_X1716.ms.wvr.smooth', 'uid___A002_X916b15_X1716.ms.antpos'],
    gainfield = ['2', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X916b15_X1716.ms',
    field = '3',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X916b15_X1716.ms.tsys', 'uid___A002_X916b15_X1716.ms.wvr.smooth', 'uid___A002_X916b15_X1716.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  if applyonly != True: es.getCalWeightStats('uid___A002_X916b15_X1716.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X916b15_X1716.ms.split') 
  split(vis = 'uid___A002_X916b15_X1716.ms',
    outputvis = 'uid___A002_X916b15_X1716.ms.split',
    datacolumn = 'corrected',
    spw = '11,13,15,17',
    keepflags = T)
  
  

print "# Calibration"

# Listobs, clear pointing table, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X916b15_X1716.ms.split.listobs')
  listobs(vis = 'uid___A002_X916b15_X1716.ms.split',
    listfile = 'uid___A002_X916b15_X1716.ms.split.listobs')
  
  tb.open('uid___A002_X916b15_X1716.ms.split/POINTING', nomodify = False)
  a = tb.rownumbers()
  tb.removerows(a)
  tb.close()
  
  if not os.path.exists('uid___A002_X916b15_X1716.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_X916b15_X1716.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_X916b15_X1716.ms.split',
    mode = 'shadow',
    flagbackup = F)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_X916b15_X1716.ms.split',
    mode = 'manual',
    spw = '0:0~7;120~127,1:0~7;120~127,2:0~7;120~127',
    flagbackup = F)
  flagdata(vis = 'uid___A002_X916b15_X1716.ms.split',
    mode = 'manual',
    antenna = 'DA49,PM02,DV04', # low gain, variable gain, low gain
    flagbackup = F)
  flagdata(vis = 'uid___A002_X916b15_X1716.ms.split',
    mode = 'manual',
    timerange = '10:17:27~10:17:35',  # ICT-3835
    flagbackup = F)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  setjy('uid___A002_X916b15_X1716.ms.split',
        standard='manual', field='J0854+2006', spix=-0.402335,
        reffreq='236.375000GHz', fluxdensity=[3.514612,0,0,0])
"""
  setjy(vis = 'uid___A002_X916b15_X1716.ms.split',
    field = '1', # source name = J0854+2006
    spw = '0', # center frequency of spw = 243.0GHz
    standard = 'manual',
    fluxdensity = [4.57587735179, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X916b15_X1716.ms.split',
    field = '1', # source name = J0854+2006
    spw = '1', # center frequency of spw = 230.0GHz
    standard = 'manual',
    fluxdensity = [4.57587735179, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X916b15_X1716.ms.split',
    field = '1', # source name = J0854+2006
    spw = '2', # center frequency of spw = 228.0GHz
    standard = 'manual',
    fluxdensity = [4.57587735179, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X916b15_X1716.ms.split',
    field = '1', # source name = J0854+2006
    spw = '3', # center frequency of spw = 244.5GHz
    standard = 'manual',
    fluxdensity = [4.57587735179, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
"""  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X916b15_X1716.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X916b15_X1716.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_X916b15_X1716.ms.split',
    caltable = 'uid___A002_X916b15_X1716.ms.split.ap_pre_bandpass',
    field = '0', # J0825+0309
    spw = '0:51~76,1:51~76,2:51~76,3:768~1152',
    solint = 'int',
    refant = 'DV09',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_X916b15_X1716.ms.split.ap_pre_bandpass', msName='uid___A002_X916b15_X1716.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X916b15_X1716.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_X916b15_X1716.ms.split',
    caltable = 'uid___A002_X916b15_X1716.ms.split.bandpass',
    scan = '3',
    field = '0', # J0825+0309
    solint = 'inf,8MHz',
    combine = 'scan',
    refant = 'DV09',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_X916b15_X1716.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X916b15_X1716.ms.split.bandpass', msName='uid___A002_X916b15_X1716.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X916b15_X1716.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X916b15_X1716.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_X916b15_X1716.ms.split',
    caltable = 'uid___A002_X916b15_X1716.ms.split.phase_int',
    field = '0~2', # J0825+0309,J0854+2006,J0914+0245
    solint = 'int',
    refant = 'DV09',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X916b15_X1716.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X916b15_X1716.ms.split.phase_int', msName='uid___A002_X916b15_X1716.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X916b15_X1716.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_X916b15_X1716.ms.split',
    caltable = 'uid___A002_X916b15_X1716.ms.split.ampli_inf',
    field = '0~2', # J0825+0309,J0854+2006,J0914+0245
    solint = 'inf',
    refant = 'DV09',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_X916b15_X1716.ms.split.bandpass', 'uid___A002_X916b15_X1716.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_X916b15_X1716.ms.split.ampli_inf', msName='uid___A002_X916b15_X1716.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X916b15_X1716.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_X916b15_X1716.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X916b15_X1716.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_X916b15_X1716.ms.split',
    caltable = 'uid___A002_X916b15_X1716.ms.split.ampli_inf',
    fluxtable = 'uid___A002_X916b15_X1716.ms.split.flux_inf',
    reference = '1') # J0854+2006
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_X916b15_X1716.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_X916b15_X1716.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_X916b15_X1716.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_X916b15_X1716.ms.split',
    caltable = 'uid___A002_X916b15_X1716.ms.split.phase_inf',
    field = '0~2', # J0825+0309,J0854+2006,J0914+0245
    solint = 'inf',
    refant = 'DV09',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X916b15_X1716.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X916b15_X1716.ms.split.phase_inf', msName='uid___A002_X916b15_X1716.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X916b15_X1716.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0', '1']: # J0825+0309,J0854+2006
    applycal(vis = 'uid___A002_X916b15_X1716.ms.split',
      field = str(i),
      gaintable = ['uid___A002_X916b15_X1716.ms.split.bandpass', 'uid___A002_X916b15_X1716.ms.split.phase_int', 'uid___A002_X916b15_X1716.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = F,
      flagbackup = F)
  
  applycal(vis = 'uid___A002_X916b15_X1716.ms.split',
    field = '2,3', # SDP.81
    gaintable = ['uid___A002_X916b15_X1716.ms.split.bandpass', 'uid___A002_X916b15_X1716.ms.split.phase_inf', 'uid___A002_X916b15_X1716.ms.split.flux_inf'],
    gainfield = ['', '2', '2'], # J0914+0245
    interp = 'linear,linear',
    calwt = F,
    flagbackup = F)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X916b15_X1716.ms.split.cal') 
  split(vis = 'uid___A002_X916b15_X1716.ms.split',
    outputvis = 'uid___A002_X916b15_X1716.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)
  os.system('rm -rf SDP81_X1716.ms.split.cal')
  split(vis = 'uid___A002_X916b15_X1716.ms.split',
    outputvis = 'SDP81_X1716.ms.split.cal', field='SDP.81',
    datacolumn = 'corrected',
    keepflags = T)
  
mystep = 19
if(mystep in thesteps):
  flagmanager('uid___A002_X916b15_X1716.ms.split',mode='save',versionname='noCOflag')
  flagdata('uid___A002_X916b15_X1716.ms.split',spw='2:50~80',mode='manual',flagbackup=False)
  os.system('rm -rf SDP81_X1716.ms.split.calavg')
  split(vis = 'uid___A002_X916b15_X1716.ms.split',
    outputvis = 'SDP81_X1716.ms.split.calavg', field='SDP.81',
    datacolumn = 'corrected',width=[64,64,64,960], # 2 channels per spw
#    datacolumn = 'corrected',width=[128,128,128,1920],
    keepflags = T)
