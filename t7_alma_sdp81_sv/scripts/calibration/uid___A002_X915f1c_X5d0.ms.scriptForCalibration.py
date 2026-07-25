# ALMA Data Reduction Script

# NOTES:
# - No tsys problems noted
# - Flux cal amplitude updated on all spws
# - Bandpass command was updated to solint='inf,15.6Mhz',field='',intent='BANDPASS'
# - Flagged antennas:
# DA65: no WVR solutions
# PM02: one scan with amp jump, that was not corrected by phase referencing

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


# CALIBRATE_AMPLI: J0750+1231
# CALIBRATE_ATMOSPHERE: J0750+1231,J0825+0309,J0909+0121,SDP.81
# CALIBRATE_BANDPASS: J0825+0309
# CALIBRATE_FLUX: J0750+1231
# CALIBRATE_FOCUS: 
# CALIBRATE_PHASE: J0909+0121
# CALIBRATE_POINTING: J0825+0309
# OBSERVE_TARGET: SDP.81

# Using reference antenna = DV15

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_X915f1c_X5d0.ms') == False:
    importasdm('uid___A002_X915f1c_X5d0', asis='Antenna Station Receiver Source CalAtmosphere CalWVR')
  if applyonly != True: es.fixForCSV2555('uid___A002_X915f1c_X5d0.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_X915f1c_X5d0.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.listobs')
  listobs(vis = 'uid___A002_X915f1c_X5d0.ms',
    listfile = 'uid___A002_X915f1c_X5d0.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_X915f1c_X5d0.ms',
    mode = 'manual',
    spw = '1~21',
    autocorr = T,
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_X915f1c_X5d0.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = F)
  
  flagcmd(vis = 'uid___A002_X915f1c_X5d0.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_X915f1c_X5d0.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_X915f1c_X5d0.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')

  flagdata(vis = 'uid___A002_X915f1c_X5d0.ms',
    mode = 'manual',
    antenna = 'DA65',
    flagbackup = F)
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.wvr') 
  
  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X915f1c_X5d0.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_X915f1c_X5d0.ms',
    caltable = 'uid___A002_X915f1c_X5d0.ms.wvr',
    toffset = 0,
    tie = ['SDP.81,J0909+0121'],
    statsource = 'SDP.81')
  
  casalog.setlogfile(mylogfile)
  
  # This is a temporary workaround, which will be included in a future version of CASA
  
  tb.open('uid___A002_X915f1c_X5d0.ms.wvr', nomodify=False)
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
  
  
  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.wvr.smooth') 
  
  smoothcal(vis = 'uid___A002_X915f1c_X5d0.ms',
    tablein = 'uid___A002_X915f1c_X5d0.ms.wvr',
    caltable = 'uid___A002_X915f1c_X5d0.ms.wvr.smooth',
    smoothtype = 'mean',
    smoothtime = 6.048)

  flagdata(vis = 'uid___A002_X915f1c_X5d0.ms.wvr.smooth',
    mode = 'manual',
    antenna = 'DA65',
    flagbackup = F)
  
#  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_X915f1c_X5d0.ms.wvr.smooth', spw='11', antenna='DV15',
#    yrange=[-199,199],subplot=22, interactive=False, showFlaggedSolutions=False,
#    figfile='uid___A002_X915f1c_X5d0.ms.wvr.smooth.plots/uid___A002_X915f1c_X5d0.ms.wvr.smooth') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.tsys') 
  gencal(vis = 'uid___A002_X915f1c_X5d0.ms',
    caltable = 'uid___A002_X915f1c_X5d0.ms.tsys',
    caltype = 'tsys')
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_X915f1c_X5d0.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='5~123',showfdm=True, 
    field='', figfile='uid___A002_X915f1c_X5d0.ms.tsys.plots.overlayTime/uid___A002_X915f1c_X5d0.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_X915f1c_X5d0.ms.tsys', msName='uid___A002_X915f1c_X5d0.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Note: the correction for antenna DA64 is larger than 2mm.
  
  # Position for antenna DA64 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Note: the correction for antenna DA62 is larger than 2mm.
  
  # Position for antenna DA62 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Note: no baseline run found for antenna DA45.
  
  # Position for antenna DV10 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Note: the correction for antenna DV13 is larger than 2mm.
  
  # Position for antenna DV13 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Note: the correction for antenna DV15 is larger than 2mm.
  
  # Position for antenna DV15 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Position for antenna DV14 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Position for antenna DA48 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Note: no baseline run found for antenna PM02.
  
  # Note: the correction for antenna PM04 is larger than 2mm.
  
  # Position for antenna PM04 is derived from baseline run made on 2014-09-05 03:49:41.
  
  # Position for antenna DV09 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Position for antenna DV11 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Position for antenna DA50 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Note: the correction for antenna DA57 is larger than 2mm.
  
  # Position for antenna DA57 is derived from baseline run made on 2014-09-05 03:49:41.
  
  # Position for antenna DA55 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Position for antenna DV04 is derived from baseline run made on 2014-10-20 00:38:20.
  
  # Note: the correction for antenna DV01 is larger than 2mm.
  
  # Position for antenna DV01 is derived from baseline run made on 2014-09-05 03:49:41.
  
  # Position for antenna DV08 is derived from baseline run made on 2014-10-20 00:38:20.
  
  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.antpos') 
  gencal(vis = 'uid___A002_X915f1c_X5d0.ms',
    caltable = 'uid___A002_X915f1c_X5d0.ms.antpos',
    caltype = 'antpos',
    antenna = 'DA50,DA64,PM04,DA62,DV08,DV09,DV11,DV10,DV13,DA55,DV15,DV14,DV01,DA57,DV04,DA48',
    parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
  #  parameter = [0.000929844869988,-0.00121202373745,-0.000479471560804,-0.00216401536542,0.00150183599432,0.000644677550705,-0.000900289509445,0.00173603091389,0.000736685469747,0.00150644285176,-0.0026544047851,-0.00122481638265,-0.000287301911653,0.000591817343895,-0.000230700765117,-0.000393744228921,0.000555729369593,-1.09247408639e-05,-0.000599562958936,0.000707300722662,0.000477526906042,0.000310009289689,-0.000586255334413,-0.000347047436497,-0.00321740140646,0.00302617422003,0.00165461650533,7.93021172285e-07,-1.01141631603e-06,-7.34813511372e-07,-0.00455063894171,0.00357201047151,-0.000393024698505,0.000644528128892,-0.00143047081611,-0.00101184274239,-0.000846908653256,0.0018538888927,0.00113338374197,-0.000978342723101,0.00163009297103,0.000727996230125,-0.000683304573599,0.000386893416529,-0.000779482741275,0.000578655879557,-0.00157797915241,-0.00070093449596])
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_X915f1c_X5d0.ms', tsystable = 'uid___A002_X915f1c_X5d0.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_X915f1c_X5d0.ms',
    field = '0',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X915f1c_X5d0.ms.tsys', 'uid___A002_X915f1c_X5d0.ms.wvr.smooth', 'uid___A002_X915f1c_X5d0.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X915f1c_X5d0.ms',
    field = '1',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X915f1c_X5d0.ms.tsys', 'uid___A002_X915f1c_X5d0.ms.wvr.smooth', 'uid___A002_X915f1c_X5d0.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X915f1c_X5d0.ms',
    field = '2',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X915f1c_X5d0.ms.tsys', 'uid___A002_X915f1c_X5d0.ms.wvr.smooth', 'uid___A002_X915f1c_X5d0.ms.antpos'],
    gainfield = ['2', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X915f1c_X5d0.ms',
    field = '3',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X915f1c_X5d0.ms.tsys', 'uid___A002_X915f1c_X5d0.ms.wvr.smooth', 'uid___A002_X915f1c_X5d0.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  if applyonly != True: es.getCalWeightStats('uid___A002_X915f1c_X5d0.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split') 
  split(vis = 'uid___A002_X915f1c_X5d0.ms',
    outputvis = 'uid___A002_X915f1c_X5d0.ms.split',
    datacolumn = 'corrected',
    spw = '11,13,15,17',
    keepflags = T)
  
  

print "# Calibration"

# Listobs, clear pointing table, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split.listobs')
  listobs(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    listfile = 'uid___A002_X915f1c_X5d0.ms.split.listobs')
  
  tb.open('uid___A002_X915f1c_X5d0.ms.split/POINTING', nomodify = False)
  a = tb.rownumbers()
  tb.removerows(a)
  tb.close()
  
  if not os.path.exists('uid___A002_X915f1c_X5d0.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_X915f1c_X5d0.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    mode = 'shadow',
    flagbackup = F)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    mode = 'manual',
    spw = '0:0~7;120~127,1:0~7;120~127,2:0~7;120~127',
    flagbackup = F)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # au.getALMAFluxForMS('uid___A002_X915f1c_X5d0.ms.split',field='1',frequency='144.566072174GHz')
  setjy('uid___A002_X915f1c_X5d0.ms.split',
        standard='manual', field='J0750+1231', spix=-0.664182,
        reffreq='144.566072GHz', fluxdensity=[0.870601,0,0,0])

"""
  setjy(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    field = '1', # source name = J0750+1231
    spw = '0', # center frequency of spw = 144.566072174GHz
    standard = 'manual',
    fluxdensity = [0.89797321186840673, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  # au.getALMAFluxForMS('uid___A002_X915f1c_X5d0.ms.split',field='1',frequency='144.566072174GHz')

  setjy(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    field = '1', # source name = J0750+1231
    spw = '1', # center frequency of spw = 154.711101882GHz
    standard = 'manual',
    fluxdensity = [0.85552786925829694, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  # au.getALMAFluxForMS('uid___A002_X915f1c_X5d0.ms.split',field='1',frequency='154.711101882GHz')
  
  setjy(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    field = '1', # source name = J0750+1231
    spw = '2', # center frequency of spw = 156.443866223GHz
    standard = 'manual',
    fluxdensity = [0.84875194486317684, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  # au.getALMAFluxForMS('uid___A002_X915f1c_X5d0.ms.split',field='1',frequency='156.443866223GHz')
  
  setjy(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    field = '1', # source name = J0750+1231
    spw = '3', # center frequency of spw = 142.649072174GHz
    standard = 'manual',
    fluxdensity = [0.90657222174783381, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  # au.getALMAFluxForMS('uid___A002_X915f1c_X5d0.ms.split',field='1',frequency='142.649072174GHz')
"""  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    caltable = 'uid___A002_X915f1c_X5d0.ms.split.ap_pre_bandpass',
    field = '0', # J0825+0309
    spw = '0:51~76,1:51~76,2:51~76,3:1536~2304',
    solint = 'int',
    refant = 'DV15',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_X915f1c_X5d0.ms.split.ap_pre_bandpass', msName='uid___A002_X915f1c_X5d0.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    caltable = 'uid___A002_X915f1c_X5d0.ms.split.bandpass',
    field = '', # J0825+0309
    intent = '*BANDPASS*',
    solint = 'inf,15.6MHz',
    combine = 'scan',
    refant = 'DV15',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_X915f1c_X5d0.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X915f1c_X5d0.ms.split.bandpass', msName='uid___A002_X915f1c_X5d0.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    caltable = 'uid___A002_X915f1c_X5d0.ms.split.phase_int',
    field = '0~2', # J0825+0309,J0750+1231,J0909+0121
    solint = 'int',
    refant = 'DV15',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X915f1c_X5d0.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X915f1c_X5d0.ms.split.phase_int', msName='uid___A002_X915f1c_X5d0.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    caltable = 'uid___A002_X915f1c_X5d0.ms.split.ampli_inf',
    field = '0~2', # J0825+0309,J0750+1231,J0909+0121
    solint = 'inf',
    refant = 'DV15',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_X915f1c_X5d0.ms.split.bandpass', 'uid___A002_X915f1c_X5d0.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_X915f1c_X5d0.ms.split.ampli_inf', msName='uid___A002_X915f1c_X5d0.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X915f1c_X5d0.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    caltable = 'uid___A002_X915f1c_X5d0.ms.split.ampli_inf',
    fluxtable = 'uid___A002_X915f1c_X5d0.ms.split.flux_inf',
    reference = '1') # J0750+1231
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_X915f1c_X5d0.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_X915f1c_X5d0.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    caltable = 'uid___A002_X915f1c_X5d0.ms.split.phase_inf',
    field = '0~2', # J0825+0309,J0750+1231,J0909+0121
    solint = 'inf',
    refant = 'DV15',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X915f1c_X5d0.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X915f1c_X5d0.ms.split.phase_inf', msName='uid___A002_X915f1c_X5d0.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0', '1']: # J0825+0309,J0750+1231
    applycal(vis = 'uid___A002_X915f1c_X5d0.ms.split',
      field = str(i),
      gaintable = ['uid___A002_X915f1c_X5d0.ms.split.bandpass', 'uid___A002_X915f1c_X5d0.ms.split.phase_int', 'uid___A002_X915f1c_X5d0.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = F,
      flagbackup = F)
  
  applycal(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    field = '2,3', # SDP.81
    gaintable = ['uid___A002_X915f1c_X5d0.ms.split.bandpass', 'uid___A002_X915f1c_X5d0.ms.split.phase_inf', 'uid___A002_X915f1c_X5d0.ms.split.flux_inf'],
    gainfield = ['', '2', '2'], # J0909+0121
    interp = 'linear,linear',
    calwt = F,
    flagbackup = F)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split.cal') 
  split(vis = 'uid___A002_X915f1c_X5d0.ms.split',
    outputvis = 'uid___A002_X915f1c_X5d0.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)

  # Additional flags
  flagdata(vis='uid___A002_X915f1c_X5d0.ms.split.cal',
           mode='manual',
           spw='',
           antenna='PM02',
           scan='29~31')

  # Split science target data. We perform limited channel averaging
  # of all spws to reduce file size, without losing any information.
  os.system('rm -rf uid___A002_X915f1c_X5d0.ms.split.cal.science') 
  split(vis = 'uid___A002_X915f1c_X5d0.ms.split.cal',
    outputvis = 'uid___A002_X915f1c_X5d0.ms.split.cal.science',
    datacolumn = 'data',
    field='3', spw='0,1,2,3', width=[16,16,16,20],
    keepflags = T)


