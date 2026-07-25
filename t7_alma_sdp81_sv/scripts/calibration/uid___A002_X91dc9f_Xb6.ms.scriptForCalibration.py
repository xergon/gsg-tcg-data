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
# CALIBRATE_ATMOSPHERE: J0825+0309,J0854+2006,J0909+0121,SDP.81
# CALIBRATE_BANDPASS: J0825+0309
# CALIBRATE_FLUX: J0854+2006
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J0909+0121
# CALIBRATE_POINTING: J0825+0309
# OBSERVE_TARGET: SDP.81

# Using reference antenna = DA51

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_X91dc9f_Xb6.ms') == False:
    importasdm('uid___A002_X91dc9f_Xb6', asis='Antenna Station Receiver Source CalAtmosphere CalWVR')
  if applyonly != True: es.fixForCSV2555('uid___A002_X91dc9f_Xb6.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_X91dc9f_Xb6.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.listobs')
  listobs(vis = 'uid___A002_X91dc9f_Xb6.ms',
    listfile = 'uid___A002_X91dc9f_Xb6.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_X91dc9f_Xb6.ms',
    mode = 'manual',
    spw = '1~21',
    autocorr = T,
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_X91dc9f_Xb6.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = F)
  
  flagcmd(vis = 'uid___A002_X91dc9f_Xb6.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_X91dc9f_Xb6.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_X91dc9f_Xb6.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.wvr') 
  
  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X91dc9f_Xb6.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_X91dc9f_Xb6.ms',
    caltable = 'uid___A002_X91dc9f_Xb6.ms.wvr',
    toffset = 0,
    tie = ['SDP.81,J0909+0121'],
    statsource = 'SDP.81')
  
  casalog.setlogfile(mylogfile)
  
  # This is a temporary workaround, which will be included in a future version of CASA
  
  tb.open('uid___A002_X91dc9f_Xb6.ms.wvr', nomodify=False)
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
  
  
  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.wvr.smooth') 
  
  smoothcal(vis = 'uid___A002_X91dc9f_Xb6.ms',
    tablein = 'uid___A002_X91dc9f_Xb6.ms.wvr',
    caltable = 'uid___A002_X91dc9f_Xb6.ms.wvr.smooth',
    smoothtype = 'mean',
    smoothtime = 2.016)
  
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_X91dc9f_Xb6.ms.wvr.smooth', spw='9', antenna='DA51',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_X91dc9f_Xb6.ms.wvr.smooth.plots/uid___A002_X91dc9f_Xb6.ms.wvr.smooth') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.tsys') 
  gencal(vis = 'uid___A002_X91dc9f_Xb6.ms',
    caltable = 'uid___A002_X91dc9f_Xb6.ms.tsys',
    caltype = 'tsys')
  
  flagdata('uid___A002_X91dc9f_Xb6.ms.tsys',mode='manual',flagbackup=F,
           spw='9:0~3;124~127,11:0~3;124~127,13:0~3,124~127,15:0~3,124~127')
           
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_X91dc9f_Xb6.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='5~123',showfdm=True, 
    field='', figfile='uid___A002_X91dc9f_Xb6.ms.tsys.plots.overlayTime/uid___A002_X91dc9f_Xb6.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_X91dc9f_Xb6.ms.tsys', msName='uid___A002_X91dc9f_Xb6.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]
  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.antpos')
  gencal(vis = 'uid___A002_X91dc9f_Xb6.ms',
    caltable = 'uid___A002_X91dc9f_Xb6.ms.antpos',
    caltype = 'antpos',
    parameter = [-0.0008697, +0.001222, +0.000256, # DA41 on S301 change=1.522mm
                 -0.0003200, +0.000568, +0.000236, # DA42 on A006 change=0.694mm
                 -0.0014970, +0.001400, +0.000099, # DA43 on S306 change=2.052mm
                 -0.0002283, +0.000688, +0.000188, # DA45 on A127 change=0.749mm
                 +0.0000730, -0.000050, -0.000048, # DA46 on A058 change=0.101mm
                 -0.0012640, +0.001862, +0.002036, # DA48 on W207 change=3.035mm
                 -0.0002937, +0.000536, +0.000205, # DA49 on A029 change=0.645mm
                 -0.0010850, +0.001596, +0.002260, # DA50 on W204 change=2.972mm
                 -0.0006087, +0.001071, +0.000465, # DA51 on A082 change=1.316mm
                 -0.0001640, -0.000059, +0.000255, # DA52 on A035 change=0.309mm
                 -0.0018410, +0.002545, -0.000182, # DA55 on S309 change=3.146mm
                 -0.0012060, +0.001494, +0.000602, # DA56 on A131 change=2.012mm
                 -0.0006330, +0.000739, +0.000357, # DA57 on A076 change=1.037mm
                 -0.0019700, +0.002534, +0.000251, # DA60 on P404 change=3.219mm
                 -0.0002500, +0.000522, +0.000186, # DA61 on A075 change=0.607mm
                 -0.0009160, +0.001854, +0.001766, # DA62 on W206 change=2.719mm
                 -0.0004555, +0.001180, +0.000210, # DA63 on A132 change=1.282mm
                 -0.0015970, +0.001863, +0.000410, # DA64 on P402 change=2.488mm
                 -0.0005062, +0.000614, +0.000190, # DV01 on A072 change=0.818mm
                 -0.0003217, +0.000758, +0.000398, # DV04 on A078 change=0.914mm
                 -0.0017090, +0.002554, +0.002883, # DV07 on W201 change=4.214mm
                 -0.0003491, +0.000434, +0.000493, # DV08 on A133 change=0.744mm
                 -0.0008851, +0.001659, +0.000376, # DV09 on A124 change=1.918mm
                 -0.0004107, +0.000539, +0.000109, # DV10 on A024 change=0.687mm
                 -0.0009172, +0.001557, +0.000406, # DV11 on A121 change=1.852mm
                 -0.0004596, +0.000429, +0.000536, # DV12 on A113 change=0.826mm
                 +0.0001300, +0.000163, -0.000306, # DV13 on S303 change=0.370mm
                 -0.0018860, +0.002389, +0.000649, # DV14 on P405 change=3.112mm
                 -0.0008740, +0.001594, +0.000995, # DV15 on A118 change=2.072mm
                 -0.0008194, +0.000678, +0.001152, # DV17 on W210 change=1.568mm
                 -0.0015010, +0.001498, +0.000097, # DV19 on P410 change=2.123mm
                 +0.0011389, +0.000239, -0.002278, # DV25 on A005 change=2.558mm
                 -0.0001749, +0.000694, +0.000152, # PM03 on T701 change=0.732mm
                 -0.0003207, +0.000686, +0.000122], # PM04 on T703 change=0.767mm
    antenna = 'DA41,DA42,DA43,DA45,DA46,DA48,DA49,DA50,DA51,DA52,DA55,DA56,DA57,DA60,DA61,DA62,DA63,DA64,DV01,DV04,DV07,DV08,DV09,DV10,DV11,DV12,DV13,DV14,DV15,DV17,DV19,DV25,PM03,PM04')

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_X91dc9f_Xb6.ms', tsystable = 'uid___A002_X91dc9f_Xb6.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_X91dc9f_Xb6.ms',
    field = '0',
    spw = '9,13,15,18',
    gaintable = ['uid___A002_X91dc9f_Xb6.ms.tsys', 'uid___A002_X91dc9f_Xb6.ms.wvr.smooth', 'uid___A002_X91dc9f_Xb6.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X91dc9f_Xb6.ms',
    field = '1',
    spw = '9,13,15,18',
    gaintable = ['uid___A002_X91dc9f_Xb6.ms.tsys', 'uid___A002_X91dc9f_Xb6.ms.wvr.smooth', 'uid___A002_X91dc9f_Xb6.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X91dc9f_Xb6.ms',
    field = '2',
    spw = '9,13,15,18',
    gaintable = ['uid___A002_X91dc9f_Xb6.ms.tsys', 'uid___A002_X91dc9f_Xb6.ms.wvr.smooth', 'uid___A002_X91dc9f_Xb6.ms.antpos'],
    gainfield = ['2', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X91dc9f_Xb6.ms',
    field = '3',
    spw = '9,13,15,18',
    gaintable = ['uid___A002_X91dc9f_Xb6.ms.tsys', 'uid___A002_X91dc9f_Xb6.ms.wvr.smooth', 'uid___A002_X91dc9f_Xb6.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  if applyonly != True: es.getCalWeightStats('uid___A002_X91dc9f_Xb6.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.split') 
  split(vis = 'uid___A002_X91dc9f_Xb6.ms',
    outputvis = 'uid___A002_X91dc9f_Xb6.ms.split',
    datacolumn = 'corrected',
    spw = '9,13,15,18',
    keepflags = T)
  
  

print "# Calibration"

# Listobs, clear pointing table, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.split.listobs')
  listobs(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    listfile = 'uid___A002_X91dc9f_Xb6.ms.split.listobs')
  
  tb.open('uid___A002_X91dc9f_Xb6.ms.split/POINTING', nomodify = False)
  a = tb.rownumbers()
  tb.removerows(a)
  tb.close()
  
  if not os.path.exists('uid___A002_X91dc9f_Xb6.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    mode = 'shadow',
    flagbackup = F)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    mode = 'manual',
    spw = '0:0~7;120~127,1:0~7;120~127,2:0~7;120~127',
    flagbackup = F)
  flagdata(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    mode = 'manual',
    spw='1',antenna='DA41,DA42,DA43,DA45,DA46,DA48,DA49,DA50,DA51,DA62,DV04,DV06,DV07,DV08,DV10,DV13,DV17,DV19',
    flagbackup = F)
  flagdata(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    mode = 'manual',
    antenna = 'DA61,DV06,DA42,DA48', # no Tsys, low gain, bad pointing, low gain(no fringes)
    flagbackup = F)
  flagdata(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    mode = 'manual',
    timerange = '11:17:55~11:18:00',  
    flagbackup = F)
  
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]
  setjy('uid___A002_X91dc9f_Xb6.ms.split',
        standard='manual', field='J0854+2006', spix=-0.402335,
        reffreq='289.918950GHz', fluxdensity=[2.5,0,0,0])

"""
  setjy(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    field = '1', # source name = J0854+2006
    spw = '0', # center frequency of spw = 282.934575GHz
    standard = 'manual',
    fluxdensity = [4.57587735179, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    field = '1', # source name = J0854+2006
    spw = '1', # center frequency of spw = 294.934575GHz
    standard = 'manual',
    fluxdensity = [4.57587735179, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    field = '1', # source name = J0854+2006
    spw = '2', # center frequency of spw = 296.934575GHz
    standard = 'manual',
    fluxdensity = [4.57587735179, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    field = '1', # source name = J0854+2006
    spw = '3', # center frequency of spw = 284.872075GHz
    standard = 'manual',
    fluxdensity = [4.57587735179, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
"""  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    caltable = 'uid___A002_X91dc9f_Xb6.ms.split.ap_pre_bandpass',
    field = '0', # J0825+0309
    spw = '0:51~76,1:51~76,2:51~76,3:384~576',
    solint = 'int',
    refant = 'DA51',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_X91dc9f_Xb6.ms.split.ap_pre_bandpass', msName='uid___A002_X91dc9f_Xb6.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    caltable = 'uid___A002_X91dc9f_Xb6.ms.split.bandpass',
    field = '0', # J0825+0309
    scan = '3',
    solint = 'inf,4MHz',
    combine = 'scan',
    refant = 'DA51',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_X91dc9f_Xb6.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X91dc9f_Xb6.ms.split.bandpass', msName='uid___A002_X91dc9f_Xb6.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    caltable = 'uid___A002_X91dc9f_Xb6.ms.split.phase_int',
    field = '0~2', # J0825+0309,J0854+2006,J0909+0121
    solint = 'int',
    refant = 'DA51',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X91dc9f_Xb6.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X91dc9f_Xb6.ms.split.phase_int', msName='uid___A002_X91dc9f_Xb6.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    caltable = 'uid___A002_X91dc9f_Xb6.ms.split.ampli_inf',
    field = '0~2', # J0825+0309,J0854+2006,J0909+0121
    solint = 'inf',
    refant = 'DA51',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_X91dc9f_Xb6.ms.split.bandpass', 'uid___A002_X91dc9f_Xb6.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_X91dc9f_Xb6.ms.split.ampli_inf', msName='uid___A002_X91dc9f_Xb6.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X91dc9f_Xb6.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    caltable = 'uid___A002_X91dc9f_Xb6.ms.split.ampli_inf',
    fluxtable = 'uid___A002_X91dc9f_Xb6.ms.split.flux_inf',
    reference = '1') # J0854+2006
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_X91dc9f_Xb6.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_X91dc9f_Xb6.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    caltable = 'uid___A002_X91dc9f_Xb6.ms.split.phase_inf',
    field = '0~2', # J0825+0309,J0854+2006,J0909+0121
    solint = 'inf',
    refant = 'DA51',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X91dc9f_Xb6.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X91dc9f_Xb6.ms.split.phase_inf', msName='uid___A002_X91dc9f_Xb6.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0', '1']: # J0825+0309,J0854+2006
    applycal(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
      field = str(i),
      gaintable = ['uid___A002_X91dc9f_Xb6.ms.split.bandpass', 'uid___A002_X91dc9f_Xb6.ms.split.phase_int', 'uid___A002_X91dc9f_Xb6.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = F,
      flagbackup = F)
  
  applycal(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    field = '2,3', # SDP.81
    gaintable = ['uid___A002_X91dc9f_Xb6.ms.split.bandpass', 'uid___A002_X91dc9f_Xb6.ms.split.phase_inf', 'uid___A002_X91dc9f_Xb6.ms.split.flux_inf'],
    gainfield = ['', '2', '2'], # J0909+0121
    interp = 'linear,linear',
    calwt = F,
    flagbackup = F)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X91dc9f_Xb6.ms.split.cal') 
  split(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    outputvis = 'uid___A002_X91dc9f_Xb6.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)

  os.system('rm -rf SDP81_Xb6.ms.split.cal') 
  split(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
    outputvis = 'SDP81_Xb6.ms.split.cal', field='3',
    datacolumn = 'corrected',
    keepflags = T)

mystep = 19
if(mystep in thesteps):
  os.system('rm -rf SDP81_Xb6.ms.split.calavg') 
  flagmanager('uid___A002_X91dc9f_Xb6.ms.split',mode='save',versionname='noCOflag')
  # 0 km/s ~ chan 395, flag +-15% of spectrum to be consistent with +12.5% done in CO8-7 
  flagdata('uid___A002_X91dc9f_Xb6.ms.split',spw='3:250~540',mode='manual',flagbackup=False)
  split(vis = 'uid___A002_X91dc9f_Xb6.ms.split',
        outputvis = 'SDP81_Xb6.ms.split.calavg', field='3',
        datacolumn = 'corrected', width=[32,32,32,240], keepflags = T) # 4 channels per spw
#        datacolumn = 'corrected', width=[128,128,128,960], keepflags = T) # 1 channel per spw
  flagmanager('uid___A002_X91dc9f_Xb6.ms.split',mode='restore',versionname='noCOflag')
