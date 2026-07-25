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

# Using reference antenna = DV11

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_X8fd70d_X188b.ms') == False:
    importasdm('uid___A002_X8fd70d_X188b', asis='Antenna Station Receiver Source CalAtmosphere CalWVR')
  if applyonly != True: es.fixForCSV2555('uid___A002_X8fd70d_X188b.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_X8fd70d_X188b.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.listobs')
  listobs(vis = 'uid___A002_X8fd70d_X188b.ms',
    listfile = 'uid___A002_X8fd70d_X188b.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_X8fd70d_X188b.ms',
    mode = 'manual',
    spw = '1~21',
    autocorr = T,
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_X8fd70d_X188b.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = F)
  
  flagcmd(vis = 'uid___A002_X8fd70d_X188b.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_X8fd70d_X188b.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_X8fd70d_X188b.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.wvr') 
  
  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X8fd70d_X188b.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_X8fd70d_X188b.ms',
    caltable = 'uid___A002_X8fd70d_X188b.ms.wvr',
    toffset = 0,
    tie = ['SDP.81,J0914+0245'],
    statsource = 'SDP.81')
  
  casalog.setlogfile(mylogfile)
  
  # This is a temporary workaround, which will be included in a future version of CASA
  
  tb.open('uid___A002_X8fd70d_X188b.ms.wvr', nomodify=False)
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
  
  
  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.wvr.smooth') 
  
  smoothcal(vis = 'uid___A002_X8fd70d_X188b.ms',
    tablein = 'uid___A002_X8fd70d_X188b.ms.wvr',
    caltable = 'uid___A002_X8fd70d_X188b.ms.wvr.smooth',
    smoothtype = 'mean',
    smoothtime = 6.048)
  
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_X8fd70d_X188b.ms.wvr.smooth', spw='11', antenna='DV11',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_X8fd70d_X188b.ms.wvr.smooth.plots/uid___A002_X8fd70d_X188b.ms.wvr.smooth') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.tsys') 
  gencal(vis = 'uid___A002_X8fd70d_X188b.ms',
    caltable = 'uid___A002_X8fd70d_X188b.ms.tsys',
    caltype = 'tsys')
  flagdata('uid___A002_X8fd70d_X188b.ms.tsys',flagbackup=False,mode='manual',
           spw='9:0~3;124~127,11:0~3;124~127,13:0~3,124~127,15:0~3,124~127')
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_X8fd70d_X188b.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='5~123',showfdm=True, 
    field='', figfile='uid___A002_X8fd70d_X188b.ms.tsys.plots.overlayTime/uid___A002_X8fd70d_X188b.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_X8fd70d_X188b.ms.tsys', msName='uid___A002_X8fd70d_X188b.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]
  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.antpos') 
  gencal(vis = 'uid___A002_X8fd70d_X188b.ms',
    caltable = 'uid___A002_X8fd70d_X188b.ms.antpos',
    caltype = 'antpos',
    parameter = [-0.0007932, -0.000306, -0.000694, # DA41 on S301 change=1.097mm
                 -0.0016006, +0.001708, -0.001228, # DA43 on S306 change=2.643mm
                 +0.0001748, +0.000003, -0.000053, # DA45 on A127 change=0.183mm
                 +0.0004140, -0.000617, -0.000349, # DA46 on A058 change=0.821mm
                 -0.0001840, +0.000954, +0.000826, # DA48 on W207 change=1.275mm
                 -0.0000190, +0.001558, +0.001333, # DA50 on W204 change=2.051mm
                 -0.0003235, +0.000310, -0.000253, # DA51 on A082 change=0.515mm
                 -0.0003280, -0.002877, -0.001613, # DA52 on A035 change=3.314mm
                 -0.0000120, +0.000383, +0.000218, # DA54 on A122 change=0.441mm
                 +0.0002904, -0.000623, -0.000277, # DA55 on A080 change=0.741mm
                 -0.0000882, +0.002211, -0.000172, # DA56 on A131 change=2.219mm
                 +0.0005700, -0.000524, -0.001783, # DA60 on P404 change=1.944mm
                 +0.0003928, +0.000022, -0.000121, # DA63 on A132 change=0.411mm
                 -0.0004407, +0.001632, -0.000706, # DA64 on P402 change=1.832mm
                 +0.0008220, -0.001699, -0.002352, # DA65 on P401 change=3.016mm
                 -0.0002829, +0.000607, +0.000133, # DV04 on A078 change=0.683mm
                 -0.0001538, +0.000233, -0.000095, # DV06 on A084 change=0.295mm
                 -0.0003365, +0.000363, +0.000507, # DV08 on A133 change=0.709mm
                 -0.0000637, +0.000428, -0.000186, # DV09 on A124 change=0.471mm
                 -0.0004376, +0.000927, -0.000138, # DV11 on A121 change=1.034mm
                 -0.0002223, -0.000072, +0.000046, # DV12 on A113 change=0.238mm
                 -0.0009430, -0.005122, -0.002383, # DV13 on S303 change=5.727mm
                 -0.0003510, +0.001720, -0.000659, # DV14 on P405 change=1.875mm
                 -0.0004090, +0.000275, -0.000229, # DV15 on A118 change=0.544mm
                 +0.0001466, -0.000036, +0.000099, # DV16 on A136 change=0.181mm
                 +0.0005096, +0.000044, -0.000411, # DV17 on W210 change=0.656mm
                 -0.0007650, +0.002156, -0.000274, # DV19 on P410 change=2.304mm
                 -0.0004450, +0.000684, +0.000186, # DV22 on A011 change=0.837mm
                 +0.0002464, +0.000306, +0.000105], # DV25 on A134 change=0.407mm
    antenna = 'DA41,DA43,DA45,DA46,DA48,DA50,DA51,DA52,DA54,DA55,DA56,DA60,DA63,DA64,DA65,DV04,DV06,DV08,DV09,DV11,DV12,DV13,DV14,DV15,DV16,DV17,DV19,DV22,DV25')


# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_X8fd70d_X188b.ms', tsystable = 'uid___A002_X8fd70d_X188b.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_X8fd70d_X188b.ms',
    field = '0',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X8fd70d_X188b.ms.tsys', 'uid___A002_X8fd70d_X188b.ms.wvr.smooth', 'uid___A002_X8fd70d_X188b.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X8fd70d_X188b.ms',
    field = '1',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X8fd70d_X188b.ms.tsys', 'uid___A002_X8fd70d_X188b.ms.wvr.smooth', 'uid___A002_X8fd70d_X188b.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X8fd70d_X188b.ms',
    field = '2',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X8fd70d_X188b.ms.tsys', 'uid___A002_X8fd70d_X188b.ms.wvr.smooth', 'uid___A002_X8fd70d_X188b.ms.antpos'],
    gainfield = ['2', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X8fd70d_X188b.ms',
    field = '3',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X8fd70d_X188b.ms.tsys', 'uid___A002_X8fd70d_X188b.ms.wvr.smooth', 'uid___A002_X8fd70d_X188b.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  if applyonly != True: es.getCalWeightStats('uid___A002_X8fd70d_X188b.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.split') 
  split(vis = 'uid___A002_X8fd70d_X188b.ms',
    outputvis = 'uid___A002_X8fd70d_X188b.ms.split',
    datacolumn = 'corrected',
    spw = '11,13,15,17',
    keepflags = T)
  
  

print "# Calibration"

# Listobs, clear pointing table, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.split.listobs')
  listobs(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    listfile = 'uid___A002_X8fd70d_X188b.ms.split.listobs')
  
  tb.open('uid___A002_X8fd70d_X188b.ms.split/POINTING', nomodify = False)
  a = tb.rownumbers()
  tb.removerows(a)
  tb.close()
  
  if not os.path.exists('uid___A002_X8fd70d_X188b.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_X8fd70d_X188b.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    mode = 'shadow',
    flagbackup = F)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    mode = 'manual',
    spw = '0:0~7;120~127,1:0~7;120~127,2:0~7;120~127',
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    mode = 'manual',
    antenna='DV06',
    flagbackup = F)

  flagdata(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    mode = 'manual',
    antenna = 'DA46',
    spw = '3',
    flagbackup = F)
  flagdata(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    mode = 'manual',
    antenna = 'DV14',
    spw = '2',
    flagbackup = F)
  flagdata(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    mode = 'manual',
    antenna = 'DA45',
    spw = '1,2',
    flagbackup = F)
  
# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]
  f0 = au.getALMAFluxForMS('uid___A002_X8fd70d_X188b.ms.split',spw='0',field=1)['J0854+2006']['fluxDensity']
  f1 = au.getALMAFluxForMS('uid___A002_X8fd70d_X188b.ms.split',spw='1',field=1)['J0854+2006']['fluxDensity']
  f2 = au.getALMAFluxForMS('uid___A002_X8fd70d_X188b.ms.split',spw='2',field=1)['J0854+2006']['fluxDensity']
  f3 = au.getALMAFluxForMS('uid___A002_X8fd70d_X188b.ms.split',spw='3',field=1)['J0854+2006']['fluxDensity']
  setjy(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    field = '1', # source name = J0854+2006
    spw = '0', # center frequency of spw = 243.0GHz
    standard = 'manual',
    fluxdensity = [f0, 0, 0, 0])
  
  setjy(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    field = '1', # source name = J0854+2006
    spw = '1', # center frequency of spw = 230.0GHz
    standard = 'manual',
    fluxdensity = [f1, 0, 0, 0])
  
  setjy(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    field = '1', # source name = J0854+2006
    spw = '2', # center frequency of spw = 228.0GHz
    standard = 'manual',
    fluxdensity = [f2, 0, 0, 0])
  
  setjy(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    field = '1', # source name = J0854+2006
    spw = '3', # center frequency of spw = 244.5GHz
    standard = 'manual',
    fluxdensity = [f3, 0, 0, 0])
  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    caltable = 'uid___A002_X8fd70d_X188b.ms.split.ap_pre_bandpass',
    field = '0', # J0825+0309
    spw = '0:51~76,1:51~76,2:51~76,3:768~1152',
    solint = 'int',
    refant = 'DV11',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_X8fd70d_X188b.ms.split.ap_pre_bandpass', msName='uid___A002_X8fd70d_X188b.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    caltable = 'uid___A002_X8fd70d_X188b.ms.split.bandpass',
    field = '0', # J0825+0309
    scan = '3',
    solint = 'inf,8MHz',
    combine = 'scan',
    refant = 'DV11',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_X8fd70d_X188b.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X8fd70d_X188b.ms.split.bandpass', msName='uid___A002_X8fd70d_X188b.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    caltable = 'uid___A002_X8fd70d_X188b.ms.split.phase_int',
    field = '0~2', # J0825+0309,J0854+2006,J0914+0245
    solint = 'int',
    refant = 'DV11',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X8fd70d_X188b.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X8fd70d_X188b.ms.split.phase_int', msName='uid___A002_X8fd70d_X188b.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    caltable = 'uid___A002_X8fd70d_X188b.ms.split.ampli_inf',
    field = '0~2', # J0825+0309,J0854+2006,J0914+0245
    solint = 'inf',
    refant = 'DV11',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_X8fd70d_X188b.ms.split.bandpass', 'uid___A002_X8fd70d_X188b.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_X8fd70d_X188b.ms.split.ampli_inf', msName='uid___A002_X8fd70d_X188b.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X8fd70d_X188b.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    caltable = 'uid___A002_X8fd70d_X188b.ms.split.ampli_inf',
    fluxtable = 'uid___A002_X8fd70d_X188b.ms.split.flux_inf',
    reference = '1') # J0854+2006
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_X8fd70d_X188b.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_X8fd70d_X188b.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    caltable = 'uid___A002_X8fd70d_X188b.ms.split.phase_inf',
    field = '0~2', # J0825+0309,J0854+2006,J0914+0245
    solint = 'inf',
    refant = 'DV11',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X8fd70d_X188b.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X8fd70d_X188b.ms.split.phase_inf', msName='uid___A002_X8fd70d_X188b.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0', '1']: # J0825+0309,J0854+2006
    applycal(vis = 'uid___A002_X8fd70d_X188b.ms.split',
      field = str(i),
      gaintable = ['uid___A002_X8fd70d_X188b.ms.split.bandpass', 'uid___A002_X8fd70d_X188b.ms.split.phase_int', 'uid___A002_X8fd70d_X188b.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = F,
      flagbackup = F)
  
  applycal(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    field = '2,3', # SDP.81
    gaintable = ['uid___A002_X8fd70d_X188b.ms.split.bandpass', 'uid___A002_X8fd70d_X188b.ms.split.phase_inf', 'uid___A002_X8fd70d_X188b.ms.split.flux_inf'],
    gainfield = ['', '2', '2'], # J0914+0245
    interp = 'linear,linear',
    calwt = F,
    flagbackup = F)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X8fd70d_X188b.ms.split.cal') 
  split(vis = 'uid___A002_X8fd70d_X188b.ms.split',
    outputvis = 'uid___A002_X8fd70d_X188b.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)
  
  os.system('rm -rf SDP81_X188b.ms.split.cal') 
  split(vis = 'uid___A002_X8fd70d_X188b.ms.split', field='SDP.81',
    outputvis = 'SDP81_X188b.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)
mystep = 19
if(mystep in thesteps):
  flagmanager('uid___A002_X8fd70d_X188b.ms.split',mode='save',versionname='noCOflag')
  flagdata('uid___A002_X8fd70d_X188b.ms.split',spw='2:50~80',mode='manual',flagbackup=False)
  os.system('rm -rf SDP81_X188b.ms.split.calavg') 
  split(vis = 'uid___A002_X8fd70d_X188b.ms.split', field='SDP.81',
    outputvis = 'SDP81_X188b.ms.split.calavg',
#    datacolumn = 'corrected',width=[128,128,128,1920],
    datacolumn = 'corrected',width=[64,64,64,960], # 2 channels per spw
    keepflags = T)
  flagmanager('uid___A002_X8fd70d_X188b.ms.split',mode='restore',versionname='noCOflag')

