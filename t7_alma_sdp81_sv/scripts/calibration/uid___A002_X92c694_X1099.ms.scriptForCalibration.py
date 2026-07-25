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


# CALIBRATE_AMPLI: J1058+0133
# CALIBRATE_ATMOSPHERE: J0825+0309,J0909+0121,J1058+0133,SDP.81
# CALIBRATE_BANDPASS: J0825+0309
# CALIBRATE_FLUX: J1058+0133
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J0909+0121
# CALIBRATE_POINTING: J0825+0309,J0909+0121,J1058+0133
# OBSERVE_TARGET: SDP.81

# Using reference antenna = DA51

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_X92c694_X1099.ms') == False:
    importasdm('uid___A002_X92c694_X1099', asis='Antenna Station Receiver Source CalAtmosphere CalWVR')
  if applyonly != True: es.fixForCSV2555('uid___A002_X92c694_X1099.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_X92c694_X1099.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X92c694_X1099.ms.listobs')
  listobs(vis = 'uid___A002_X92c694_X1099.ms',
    listfile = 'uid___A002_X92c694_X1099.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_X92c694_X1099.ms',
    mode = 'manual',
    spw = '1~21',
    autocorr = T,
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_X92c694_X1099.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = F)
  
  flagcmd(vis = 'uid___A002_X92c694_X1099.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_X92c694_X1099.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_X92c694_X1099.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X92c694_X1099.ms.wvr') 
  
  os.system('rm -rf uid___A002_X92c694_X1099.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X92c694_X1099.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_X92c694_X1099.ms',
    caltable = 'uid___A002_X92c694_X1099.ms.wvr',
    toffset = 0,
    tie = ['SDP.81,J0909+0121'],
    statsource = 'SDP.81')
  
  casalog.setlogfile(mylogfile)
  
  # This is a temporary workaround, which will be included in a future version of CASA
  
  tb.open('uid___A002_X92c694_X1099.ms.wvr', nomodify=False)
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
  
  
  os.system('rm -rf uid___A002_X92c694_X1099.ms.wvr.smooth') 
  
  smoothcal(vis = 'uid___A002_X92c694_X1099.ms',
    tablein = 'uid___A002_X92c694_X1099.ms.wvr',
    caltable = 'uid___A002_X92c694_X1099.ms.wvr.smooth',
    smoothtype = 'mean',
    smoothtime = 2.016)
  
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_X92c694_X1099.ms.wvr.smooth', spw='11', antenna='DA51',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_X92c694_X1099.ms.wvr.smooth.plots/uid___A002_X92c694_X1099.ms.wvr.smooth') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X92c694_X1099.ms.tsys') 
  gencal(vis = 'uid___A002_X92c694_X1099.ms',
    caltable = 'uid___A002_X92c694_X1099.ms.tsys',
    caltype = 'tsys')
  flagdata('uid___A002_X92c694_X1099.ms.tsys',flagbackup=False,mode='manual',
           spw='9:0~3;124~127,11:0~3;124~127,13:0~3,124~127,15:0~3,124~127')
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_X92c694_X1099.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='5~123',showfdm=True, 
    field='', figfile='uid___A002_X92c694_X1099.ms.tsys.plots.overlayTime/uid___A002_X92c694_X1099.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_X92c694_X1099.ms.tsys', msName='uid___A002_X92c694_X1099.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]
  os.system('rm -rf uid___A002_X92c694_X1099.ms.antpos')
  # no update needed since this was observed after the final LBC position update
  gencal(vis = 'uid___A002_X92c694_X1099.ms',
    caltable = 'uid___A002_X92c694_X1099.ms.antpos',
    caltype = 'antpos',
    antenna = 'DV19,DA65,DA64,DA49,DA48,DA61,DA60,DA45,DV12,DV15,DV14,DV17,DA42,DA63,DA62,PM03,DA54,DA55,DV11,DV07,DA50,DV22,DA51,DA56,DV25,DV08,DV09,DA41,DV05,DV01,PM04',
    parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_X92c694_X1099.ms', tsystable = 'uid___A002_X92c694_X1099.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_X92c694_X1099.ms',
    field = '0',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X92c694_X1099.ms.tsys', 'uid___A002_X92c694_X1099.ms.wvr.smooth', 'uid___A002_X92c694_X1099.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X92c694_X1099.ms',
    field = '1',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X92c694_X1099.ms.tsys', 'uid___A002_X92c694_X1099.ms.wvr.smooth', 'uid___A002_X92c694_X1099.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X92c694_X1099.ms',
    field = '2',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X92c694_X1099.ms.tsys', 'uid___A002_X92c694_X1099.ms.wvr.smooth', 'uid___A002_X92c694_X1099.ms.antpos'],
    gainfield = ['2', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X92c694_X1099.ms',
    field = '3',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X92c694_X1099.ms.tsys', 'uid___A002_X92c694_X1099.ms.wvr.smooth', 'uid___A002_X92c694_X1099.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  if applyonly != True: es.getCalWeightStats('uid___A002_X92c694_X1099.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X92c694_X1099.ms.split') 
  split(vis = 'uid___A002_X92c694_X1099.ms',
    outputvis = 'uid___A002_X92c694_X1099.ms.split',
    datacolumn = 'corrected',
    spw = '11,13,15,17',
    keepflags = T)
  
  

print "# Calibration"

# Listobs, clear pointing table, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X92c694_X1099.ms.split.listobs')
  listobs(vis = 'uid___A002_X92c694_X1099.ms.split',
    listfile = 'uid___A002_X92c694_X1099.ms.split.listobs')
  
  tb.open('uid___A002_X92c694_X1099.ms.split/POINTING', nomodify = False)
  a = tb.rownumbers()
  tb.removerows(a)
  tb.close()
  
  if not os.path.exists('uid___A002_X92c694_X1099.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_X92c694_X1099.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_X92c694_X1099.ms.split',
    mode = 'shadow',
    flagbackup = F)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_X92c694_X1099.ms.split',
    mode = 'manual',
    spw = '0:0~7;120~127,1:0~7;120~127,2:0~7;120~127',
    flagbackup = F)
  flagdata(vis = 'uid___A002_X92c694_X1099.ms.split',
    mode = 'manual',
    antenna = 'DA48',
    flagbackup = F)
  flagdata(vis = 'uid___A002_X92c694_X1099.ms.split',
    mode = 'manual',spw='1,2',
    antenna = 'DA45',
    flagbackup = F)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]
  setjy('uid___A002_X92c694_X1099.ms.split',
        standard='manual', field='J1058+0133', spix=-0.271436,
        reffreq='236.375000GHz', fluxdensity=[3.93,0,0,0]) # 3.204643,0,0,0])
  
"""
  setjy(vis = 'uid___A002_X92c694_X1099.ms.split',
    field = '1', # source name = J1058+0133
    spw = '0', # center frequency of spw = 243.0GHz
    standard = 'manual',
    fluxdensity = [3.7447486083, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X92c694_X1099.ms.split',
    field = '1', # source name = J1058+0133
    spw = '1', # center frequency of spw = 230.0GHz
    standard = 'manual',
    fluxdensity = [3.7447486083, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X92c694_X1099.ms.split',
    field = '1', # source name = J1058+0133
    spw = '2', # center frequency of spw = 228.0GHz
    standard = 'manual',
    fluxdensity = [3.7447486083, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X92c694_X1099.ms.split',
    field = '1', # source name = J1058+0133
    spw = '3', # center frequency of spw = 244.5GHz
    standard = 'manual',
    fluxdensity = [3.7447486083, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
"""  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X92c694_X1099.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X92c694_X1099.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_X92c694_X1099.ms.split',
    caltable = 'uid___A002_X92c694_X1099.ms.split.ap_pre_bandpass',
    field = '0', # J0825+0309
    spw = '0:51~76,1:51~76,2:51~76,3:384~576',
    solint = 'int',
    refant = 'DA51',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_X92c694_X1099.ms.split.ap_pre_bandpass', msName='uid___A002_X92c694_X1099.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X92c694_X1099.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_X92c694_X1099.ms.split',
    caltable = 'uid___A002_X92c694_X1099.ms.split.bandpass',
    field = '0', # J0825+0309
    scan = '3',
    solint = 'inf,8MHz',
    combine = 'scan',
    refant = 'DA51',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_X92c694_X1099.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X92c694_X1099.ms.split.bandpass', msName='uid___A002_X92c694_X1099.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X92c694_X1099.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X92c694_X1099.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_X92c694_X1099.ms.split',
    caltable = 'uid___A002_X92c694_X1099.ms.split.phase_int',
    field = '0~2', # J0825+0309,J1058+0133,J0909+0121
    solint = 'int',
    refant = 'DA51',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X92c694_X1099.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X92c694_X1099.ms.split.phase_int', msName='uid___A002_X92c694_X1099.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X92c694_X1099.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_X92c694_X1099.ms.split',
    caltable = 'uid___A002_X92c694_X1099.ms.split.ampli_inf',
    field = '0~2', # J0825+0309,J1058+0133,J0909+0121
    solint = 'inf',
    refant = 'DA51',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_X92c694_X1099.ms.split.bandpass', 'uid___A002_X92c694_X1099.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_X92c694_X1099.ms.split.ampli_inf', msName='uid___A002_X92c694_X1099.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X92c694_X1099.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_X92c694_X1099.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X92c694_X1099.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_X92c694_X1099.ms.split',
    caltable = 'uid___A002_X92c694_X1099.ms.split.ampli_inf',
    fluxtable = 'uid___A002_X92c694_X1099.ms.split.flux_inf',
    reference = '1') # J1058+0133
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_X92c694_X1099.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_X92c694_X1099.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_X92c694_X1099.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_X92c694_X1099.ms.split',
    caltable = 'uid___A002_X92c694_X1099.ms.split.phase_inf',
    field = '0~2', # J0825+0309,J1058+0133,J0909+0121
    solint = 'inf',
    refant = 'DA51',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X92c694_X1099.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X92c694_X1099.ms.split.phase_inf', msName='uid___A002_X92c694_X1099.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X92c694_X1099.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0', '1']: # J0825+0309,J1058+0133
    applycal(vis = 'uid___A002_X92c694_X1099.ms.split',
      field = str(i),
      gaintable = ['uid___A002_X92c694_X1099.ms.split.bandpass', 'uid___A002_X92c694_X1099.ms.split.phase_int', 'uid___A002_X92c694_X1099.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = F,
      flagbackup = F)
  
  applycal(vis = 'uid___A002_X92c694_X1099.ms.split',
    field = '2,3', # SDP.81
    gaintable = ['uid___A002_X92c694_X1099.ms.split.bandpass', 'uid___A002_X92c694_X1099.ms.split.phase_inf', 'uid___A002_X92c694_X1099.ms.split.flux_inf'],
    gainfield = ['', '2', '2'], # J0909+0121
    interp = 'linear,linear',
    calwt = F,
    flagbackup = F)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X92c694_X1099.ms.split.cal') 
  split(vis = 'uid___A002_X92c694_X1099.ms.split',
    outputvis = 'uid___A002_X92c694_X1099.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)
  
  os.system('rm -rf SDP81_X1099.ms.split.cal') 
  split(vis = 'uid___A002_X92c694_X1099.ms.split', field='SDP.81',
    outputvis = 'SDP81_X1099.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)

mystep = 19
if(mystep in thesteps):
  flagmanager('uid___A002_X92c694_X1099.ms.split',mode='save',versionname='noCOflag')
  flagdata('uid___A002_X92c694_X1099.ms.split',spw='2:50~80',mode='manual',flagbackup=False)
  os.system('rm -rf SDP81_X1099.ms.split.calavg') 
  split(vis = 'uid___A002_X92c694_X1099.ms.split', field='SDP.81',
    outputvis = 'SDP81_X1099.ms.split.calavg',
#    datacolumn = 'corrected',width=[128,128,128,1920], # 1 channel per spw
    datacolumn = 'corrected',width=[64,64,64,480], # 2 channels per spw
    keepflags = T)
