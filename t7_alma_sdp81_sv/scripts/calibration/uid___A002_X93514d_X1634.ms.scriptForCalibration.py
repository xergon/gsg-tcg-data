# ALMA Data Reduction Script

# Notes:
# - No Tsys or WVR problems noted
# - Flux cal amplitude updated on all spws
# - Bandpass command was updated to solint='inf,15.6Mhz',field='',intent='BANDPASS'
# - Reference antenna changed from DA56 to DA61
# - Flagged data for:
# DA56: no bandpass solution for this antenna
# DA45: low gains for spw 1,2


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

# Using reference antenna = DA61

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_X93514d_X1634.ms') == False:
    importasdm('uid___A002_X93514d_X1634', asis='Antenna Station Receiver Source CalAtmosphere CalWVR')
  if applyonly != True: es.fixForCSV2555('uid___A002_X93514d_X1634.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_X93514d_X1634.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X93514d_X1634.ms.listobs')
  listobs(vis = 'uid___A002_X93514d_X1634.ms',
    listfile = 'uid___A002_X93514d_X1634.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_X93514d_X1634.ms',
    mode = 'manual',
    spw = '1~21',
    autocorr = T,
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_X93514d_X1634.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = F)
  
  flagcmd(vis = 'uid___A002_X93514d_X1634.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_X93514d_X1634.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_X93514d_X1634.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X93514d_X1634.ms.wvr') 
  
  os.system('rm -rf uid___A002_X93514d_X1634.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X93514d_X1634.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_X93514d_X1634.ms',
    caltable = 'uid___A002_X93514d_X1634.ms.wvr',
    toffset = 0,
    tie = ['SDP.81,J0909+0121'],
    statsource = 'SDP.81')
  
  casalog.setlogfile(mylogfile)
  
  # This is a temporary workaround, which will be included in a future version of CASA
  
  tb.open('uid___A002_X93514d_X1634.ms.wvr', nomodify=False)
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
  
  
  os.system('rm -rf uid___A002_X93514d_X1634.ms.wvr.smooth') 
  
  smoothcal(vis = 'uid___A002_X93514d_X1634.ms',
    tablein = 'uid___A002_X93514d_X1634.ms.wvr',
    caltable = 'uid___A002_X93514d_X1634.ms.wvr.smooth',
    smoothtype = 'mean',
    smoothtime = 2.016)
  
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_X93514d_X1634.ms.wvr.smooth', spw='11', antenna='DA61',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_X93514d_X1634.ms.wvr.smooth.plots/uid___A002_X93514d_X1634.ms.wvr.smooth') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X93514d_X1634.ms.tsys') 
  gencal(vis = 'uid___A002_X93514d_X1634.ms',
    caltable = 'uid___A002_X93514d_X1634.ms.tsys',
    caltype = 'tsys')
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_X93514d_X1634.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='5~123',showfdm=True, 
    field='', figfile='uid___A002_X93514d_X1634.ms.tsys.plots.overlayTime/uid___A002_X93514d_X1634.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_X93514d_X1634.ms.tsys', msName='uid___A002_X93514d_X1634.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Note: the correction for antenna DV19 is larger than 2mm.
  
  # Position for antenna DV19 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA65 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Note: the correction for antenna DA64 is larger than 2mm.
  
  # Position for antenna DA64 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA49 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Note: the correction for antenna DA48 is larger than 2mm.
  
  # Position for antenna DA48 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA61 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Note: the correction for antenna DA60 is larger than 2mm.
  
  # Position for antenna DA60 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA45 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV10 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV12 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Note: the correction for antenna DA41 is larger than 2mm.
  
  # Position for antenna DA41 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Note: the correction for antenna DV14 is larger than 2mm.
  
  # Position for antenna DV14 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV17 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Note: the correction for antenna DA62 is larger than 2mm.
  
  # Position for antenna DA62 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna PM04 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Note: the correction for antenna DV09 is larger than 2mm.
  
  # Position for antenna DV09 is derived from baseline run made on 2014-10-28 10:15:06.
  
  # Position for antenna DV11 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV22 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Note: no baseline run found for antenna DV04.
  
  # Note: the correction for antenna DA50 is larger than 2mm.
  
  # Position for antenna DA50 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA56 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV08 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Note: the correction for antenna DA55 is larger than 2mm.
  
  # Position for antenna DA55 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV15 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA58 is derived from baseline run made on 2014-10-28 10:15:06.
  
  os.system('rm -rf uid___A002_X93514d_X1634.ms.antpos') 
  gencal(vis = 'uid___A002_X93514d_X1634.ms',
    caltable = 'uid___A002_X93514d_X1634.ms.antpos',
    caltype = 'antpos',
    antenna = 'DV19,DA65,DA64,DA49,DA48,DA61,DA60,DA45,DV10,DV12,DA41,DV14,DV17,DA62,PM04,DA55,DV11,DA50,DV22,DA56,DV08,DV09,DV15,DA58',
    parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
  #  parameter = [0.00199209991843,-0.00241695251316,-0.000750654377043,0.00145686464384,-0.00049380864948,0.000640822574496,0.00131625449285,-0.00160246342421,0.000981457997113,0.000729553909836,-0.0012289927823,-3.24473990347e-05,0.00151744391769,-0.00274957809597,-0.000802640803158,0.000616720201697,-0.00096104142217,-0.00010397392794,0.00157663598657,-0.0011884868145,0.00063002621755,0.000821359258443,-0.00107883062811,-2.72478334509e-05,0.000715788972855,-0.00110288642208,0.00017750967954,0.000746708329552,-0.000467634579217,-4.05779607513e-05,0.00137910107903,-0.0016109602559,-0.000132375480068,0.00142442574725,-0.00163181032985,0.00109102018178,0.000929983011376,-0.000987963437039,5.64787183628e-05,0.0011113230139,-0.00185882393271,-0.000438025221229,0.000592565755724,-0.00114762045875,7.77052623365e-05,0.00156244169921,-0.00270909909159,-0.000404343940318,0.00106661549211,-0.00127298484841,0.000122270060549,0.00112740322948,-0.00209428183734,-0.000740029849112,0.000843322370201,-0.00132927205414,-5.84004446864e-05,0.000952305272222,-0.000921681523323,7.27004371583e-05,0.000903319289676,-0.00176047884593,-0.000238994757158,0.000893874846997,-0.00181254365672,-0.00062388720966,0.000748899765313,-0.00102683529258,-0.000155123416334,0.000413770787418,-0.000389090739191,-0.000332205556333])
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_X93514d_X1634.ms', tsystable = 'uid___A002_X93514d_X1634.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_X93514d_X1634.ms',
    field = '0',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X93514d_X1634.ms.tsys', 'uid___A002_X93514d_X1634.ms.wvr.smooth', 'uid___A002_X93514d_X1634.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X93514d_X1634.ms',
    field = '1',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X93514d_X1634.ms.tsys', 'uid___A002_X93514d_X1634.ms.wvr.smooth', 'uid___A002_X93514d_X1634.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X93514d_X1634.ms',
    field = '2',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X93514d_X1634.ms.tsys', 'uid___A002_X93514d_X1634.ms.wvr.smooth', 'uid___A002_X93514d_X1634.ms.antpos'],
    gainfield = ['2', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X93514d_X1634.ms',
    field = '3',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X93514d_X1634.ms.tsys', 'uid___A002_X93514d_X1634.ms.wvr.smooth', 'uid___A002_X93514d_X1634.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  if applyonly != True: es.getCalWeightStats('uid___A002_X93514d_X1634.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X93514d_X1634.ms.split') 
  split(vis = 'uid___A002_X93514d_X1634.ms',
    outputvis = 'uid___A002_X93514d_X1634.ms.split',
    datacolumn = 'corrected',
    spw = '11,13,15,17',
    keepflags = T)
  
  

print "# Calibration"

# Listobs, clear pointing table, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X93514d_X1634.ms.split.listobs')
  listobs(vis = 'uid___A002_X93514d_X1634.ms.split',
    listfile = 'uid___A002_X93514d_X1634.ms.split.listobs')
  
  tb.open('uid___A002_X93514d_X1634.ms.split/POINTING', nomodify = False)
  a = tb.rownumbers()
  tb.removerows(a)
  tb.close()
  
  if not os.path.exists('uid___A002_X93514d_X1634.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_X93514d_X1634.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_X93514d_X1634.ms.split',
    mode = 'shadow',
    flagbackup = F)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_X93514d_X1634.ms.split',
    mode = 'manual',
    spw = '0:0~7;120~127,1:0~7;120~127,2:0~7;120~127',
    flagbackup = F)

  # Flagging two noisy spws of DA45
  flagdata(vis = 'uid___A002_X93514d_X1634.ms.split',
    mode = 'manual',
    spw = '1,2', antenna='DA45',
    flagbackup = F)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  setjy('uid___A002_X93514d_X1634.ms.split',
        standard='manual', field='J0854+2006', spix=-0.369567,
        reffreq='144.566541GHz', fluxdensity=[4.213249,0,0,0])

"""
  setjy(vis = 'uid___A002_X93514d_X1634.ms.split',
    field = '1', # source name = J0854+2006
    spw = '0', # center frequency of spw = 144.566540735GHz
    standard = 'manual',
    fluxdensity = [5.5809311143, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X93514d_X1634.ms.split',
    field = '1', # source name = J0854+2006
    spw = '1', # center frequency of spw = 154.711586477GHz
    standard = 'manual',
    fluxdensity = [5.5809311143, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X93514d_X1634.ms.split',
    field = '1', # source name = J0854+2006
    spw = '2', # center frequency of spw = 156.444356246GHz
    standard = 'manual',
    fluxdensity = [5.5809311143, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X93514d_X1634.ms.split',
    field = '1', # source name = J0854+2006
    spw = '3', # center frequency of spw = 142.649540735GHz
    standard = 'manual',
    fluxdensity = [5.5809311143, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
"""  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X93514d_X1634.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X93514d_X1634.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_X93514d_X1634.ms.split',
    caltable = 'uid___A002_X93514d_X1634.ms.split.ap_pre_bandpass',
    field = '0', # J0825+0309
    spw = '0:51~76,1:51~76,2:51~76,3:1536~2304',
    solint = 'int',
    refant = 'DA61',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_X93514d_X1634.ms.split.ap_pre_bandpass', msName='uid___A002_X93514d_X1634.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X93514d_X1634.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_X93514d_X1634.ms.split',
    caltable = 'uid___A002_X93514d_X1634.ms.split.bandpass',
    field = '', # J0825+0309
    intent = '*BANDPASS*',
    solint = 'inf,15.6MHz',
    combine = 'scan',
    refant = 'DA61',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_X93514d_X1634.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X93514d_X1634.ms.split.bandpass', msName='uid___A002_X93514d_X1634.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X93514d_X1634.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X93514d_X1634.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_X93514d_X1634.ms.split',
    caltable = 'uid___A002_X93514d_X1634.ms.split.phase_int',
    field = '0~2', # J0825+0309,J0854+2006,J0909+0121
    solint = 'int',
    refant = 'DA61',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X93514d_X1634.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X93514d_X1634.ms.split.phase_int', msName='uid___A002_X93514d_X1634.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X93514d_X1634.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_X93514d_X1634.ms.split',
    caltable = 'uid___A002_X93514d_X1634.ms.split.ampli_inf',
    field = '0~2', # J0825+0309,J0854+2006,J0909+0121
    solint = 'inf',
    refant = 'DA61',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_X93514d_X1634.ms.split.bandpass', 'uid___A002_X93514d_X1634.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_X93514d_X1634.ms.split.ampli_inf', msName='uid___A002_X93514d_X1634.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X93514d_X1634.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_X93514d_X1634.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X93514d_X1634.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_X93514d_X1634.ms.split',
    caltable = 'uid___A002_X93514d_X1634.ms.split.ampli_inf',
    fluxtable = 'uid___A002_X93514d_X1634.ms.split.flux_inf',
    reference = '1') # J0854+2006
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_X93514d_X1634.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_X93514d_X1634.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_X93514d_X1634.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_X93514d_X1634.ms.split',
    caltable = 'uid___A002_X93514d_X1634.ms.split.phase_inf',
    field = '0~2', # J0825+0309,J0854+2006,J0909+0121
    solint = 'inf',
    refant = 'DA61',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X93514d_X1634.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X93514d_X1634.ms.split.phase_inf', msName='uid___A002_X93514d_X1634.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X93514d_X1634.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0', '1']: # J0825+0309,J0854+2006
    applycal(vis = 'uid___A002_X93514d_X1634.ms.split',
      field = str(i),
      gaintable = ['uid___A002_X93514d_X1634.ms.split.bandpass', 'uid___A002_X93514d_X1634.ms.split.phase_int', 'uid___A002_X93514d_X1634.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = F,
      flagbackup = F)
  
  applycal(vis = 'uid___A002_X93514d_X1634.ms.split',
    field = '2,3', # SDP.81
    gaintable = ['uid___A002_X93514d_X1634.ms.split.bandpass', 'uid___A002_X93514d_X1634.ms.split.phase_inf', 'uid___A002_X93514d_X1634.ms.split.flux_inf'],
    gainfield = ['', '2', '2'], # J0909+0121
    interp = 'linear,linear',
    calwt = F,
    flagbackup = F)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X93514d_X1634.ms.split.cal') 
  split(vis = 'uid___A002_X93514d_X1634.ms.split',
    outputvis = 'uid___A002_X93514d_X1634.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)
  
  # Split science target data. We perform limited channel averaging
  # of all spws to reduce file size, without losing any information.
  os.system('rm -rf uid___A002_X93514d_X1634.ms.split.cal.science') 
  split(vis = 'uid___A002_X93514d_X1634.ms.split.cal',
    outputvis = 'uid___A002_X93514d_X1634.ms.split.cal.science',
    datacolumn = 'data',
    field='3', spw='0,1,2,3', width=[16,16,16,20],
    keepflags = T)

  

