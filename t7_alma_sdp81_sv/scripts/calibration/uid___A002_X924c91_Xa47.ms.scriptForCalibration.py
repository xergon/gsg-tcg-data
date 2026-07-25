# ALMA Data Reduction Script

# Notes:
# - No Tsys or WVR problems noted
# - Flux cal amplitude updated on all spws
# - Bandpass command was updated to solint='inf,15.6Mhz',field='',intent='BANDPASS'
# - Flagged data for:
# PM04: spw 2 high amps when plotting averaged in time

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

# Using reference antenna = DA56

# Import of the ASDM
mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  if os.path.exists('uid___A002_X924c91_Xa47.ms') == False:
    importasdm('uid___A002_X924c91_Xa47', asis='Antenna Station Receiver Source CalAtmosphere CalWVR')
  if applyonly != True: es.fixForCSV2555('uid___A002_X924c91_Xa47.ms')

# Fix of SYSCAL table times
mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  from recipes.almahelpers import fixsyscaltimes
  fixsyscaltimes(vis = 'uid___A002_X924c91_Xa47.ms')

print "# A priori calibration"

# listobs
mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X924c91_Xa47.ms.listobs')
  listobs(vis = 'uid___A002_X924c91_Xa47.ms',
    listfile = 'uid___A002_X924c91_Xa47.ms.listobs')
  
  

# A priori flagging
mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  flagdata(vis = 'uid___A002_X924c91_Xa47.ms',
    mode = 'manual',
    spw = '1~21',
    autocorr = T,
    flagbackup = F)
  
  flagdata(vis = 'uid___A002_X924c91_Xa47.ms',
    mode = 'manual',
    intent = '*POINTING*,*ATMOSPHERE*',
    flagbackup = F)
  
  flagcmd(vis = 'uid___A002_X924c91_Xa47.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'plot',
    plotfile = 'uid___A002_X924c91_Xa47.ms.flagcmd.png')
  
  flagcmd(vis = 'uid___A002_X924c91_Xa47.ms',
    inpmode = 'table',
    useapplied = True,
    action = 'apply')
  

# Generation and time averaging of the WVR cal table
mystep = 4
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X924c91_Xa47.ms.wvr') 
  
  os.system('rm -rf uid___A002_X924c91_Xa47.ms.wvrgcal') 
  
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X924c91_Xa47.ms.wvrgcal')
  
  wvrgcal(vis = 'uid___A002_X924c91_Xa47.ms',
    caltable = 'uid___A002_X924c91_Xa47.ms.wvr',
    toffset = 0,
    tie = ['SDP.81,J0909+0121'],
    statsource = 'SDP.81')
  
  casalog.setlogfile(mylogfile)
  
  # This is a temporary workaround, which will be included in a future version of CASA
  
  tb.open('uid___A002_X924c91_Xa47.ms.wvr', nomodify=False)
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
  
  
  os.system('rm -rf uid___A002_X924c91_Xa47.ms.wvr.smooth') 
  
  smoothcal(vis = 'uid___A002_X924c91_Xa47.ms',
    tablein = 'uid___A002_X924c91_Xa47.ms.wvr',
    caltable = 'uid___A002_X924c91_Xa47.ms.wvr.smooth',
    smoothtype = 'mean',
    smoothtime = 2.016)
  
  
  if applyonly != True: aU.plotWVRSolutions(caltable='uid___A002_X924c91_Xa47.ms.wvr.smooth', spw='11', antenna='DA56',
    yrange=[-199,199],subplot=22, interactive=False,
    figfile='uid___A002_X924c91_Xa47.ms.wvr.smooth.plots/uid___A002_X924c91_Xa47.ms.wvr.smooth') 
  
  #Note: If you see wraps in these plots, try changing yrange or unwrap=True 
  #Note: If all plots look strange, it may be a bad WVR on the reference antenna.
  #      To check, you can set antenna='' to show all baselines.
  

# Generation of the Tsys cal table
mystep = 5
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X924c91_Xa47.ms.tsys') 
  gencal(vis = 'uid___A002_X924c91_Xa47.ms',
    caltable = 'uid___A002_X924c91_Xa47.ms.tsys',
    caltype = 'tsys')
  
  if applyonly != True: aU.plotbandpass(caltable='uid___A002_X924c91_Xa47.ms.tsys', overlay='time', 
    xaxis='freq', yaxis='amp', subplot=22, buildpdf=False, interactive=False,
    showatm=True,pwv='auto',chanrange='5~123',showfdm=True, 
    field='', figfile='uid___A002_X924c91_Xa47.ms.tsys.plots.overlayTime/uid___A002_X924c91_Xa47.ms.tsys') 
  
  
  if applyonly != True: es.checkCalTable('uid___A002_X924c91_Xa47.ms.tsys', msName='uid___A002_X924c91_Xa47.ms', interactive=False) 
  

# Generation of the antenna position cal table
mystep = 6
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Position for antenna DA64 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA63 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA62 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA61 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA60 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV11 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV10 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV12 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA41 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV14 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV17 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV08 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV22 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV04 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV21 is derived from baseline run made on 2014-10-28 10:15:06.
  
  # Position for antenna DA50 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA56 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA57 is derived from baseline run made on 2014-10-28 10:15:06.
  
  # Position for antenna DA54 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA55 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DV15 is derived from baseline run made on 2014-10-31 11:27:40.
  
  # Position for antenna DA58 is derived from baseline run made on 2014-10-28 10:15:06.
  
  # Position for antenna PM04 is derived from baseline run made on 2014-10-31 11:27:40.
  
  os.system('rm -rf uid___A002_X924c91_Xa47.ms.antpos') 
  gencal(vis = 'uid___A002_X924c91_Xa47.ms',
    caltable = 'uid___A002_X924c91_Xa47.ms.antpos',
    caltype = 'antpos',
    antenna = 'DA64,DA63,DA62,DA61,DA60,DV11,DV10,DV12,DA41,DV22,DV17,DV08,DA58,DV21,DA50,DA56,DA57,DA54,DA55,DV15,DV04,DV14,PM04',
    parameter = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
  #  parameter = [-0.000280747148228,0.000260536231857,0.00139145711779,0.000302242768553,0.000288619723124,5.82788823303e-06,0.000195323180763,-4.82359813651e-06,0.00132797537174,0.000366501735273,-0.000439086569423,8.02836383996e-05,-0.000393365014781,0.00134551239913,0.000881025169293,0.000149064038203,0.000285254792851,0.000523979594708,0.000304970384897,-0.000563369310629,0.000284684183223,0.000286656186021,-3.77763572723e-05,0.000494088228809,0.000509150786399,-0.000388546968195,0.000120385755867,-0.000964678690944,0.00107472729344,0.000388599109595,0.000109515262149,-0.000307546290173,0.00120603262259,0.000553798277887,-0.00132566015047,0.000252868805633,-2.01631337404e-07,-3.65078449249e-07,-1.42026692629e-07,1.08033418655e-07,1.42492353916e-07,-5.91389834881e-07,4.24030543424e-05,-0.000498282362632,0.00151997193003,-0.000253694951325,0.00057231738937,0.000674700435376,-0.000273570365526,0.000336041428119,0.000231515471824,0.000792693077352,-0.00116213455814,-4.01242308588e-05,-0.000278559874423,-0.000164098158698,-0.000586345623906,-0.000125100674967,0.000567163615418,0.000839876928167,0.00037079963796,-0.000436426754164,0.000407358953183,-0.000461575205449,0.000757189980536,0.00174002001801,0.000271744719226,-0.000460987916921,0.00019758276247])
  

# Application of the WVR, Tsys and antpos cal tables
mystep = 7
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  
  from recipes.almahelpers import tsysspwmap
  tsysmap = tsysspwmap(vis = 'uid___A002_X924c91_Xa47.ms', tsystable = 'uid___A002_X924c91_Xa47.ms.tsys', tsysChanTol = 1)
  
  
  
  applycal(vis = 'uid___A002_X924c91_Xa47.ms',
    field = '0',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X924c91_Xa47.ms.tsys', 'uid___A002_X924c91_Xa47.ms.wvr.smooth', 'uid___A002_X924c91_Xa47.ms.antpos'],
    gainfield = ['0', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X924c91_Xa47.ms',
    field = '1',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X924c91_Xa47.ms.tsys', 'uid___A002_X924c91_Xa47.ms.wvr.smooth', 'uid___A002_X924c91_Xa47.ms.antpos'],
    gainfield = ['1', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X924c91_Xa47.ms',
    field = '2',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X924c91_Xa47.ms.tsys', 'uid___A002_X924c91_Xa47.ms.wvr.smooth', 'uid___A002_X924c91_Xa47.ms.antpos'],
    gainfield = ['2', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  
  
  applycal(vis = 'uid___A002_X924c91_Xa47.ms',
    field = '3',
    spw = '11,13,15,17',
    gaintable = ['uid___A002_X924c91_Xa47.ms.tsys', 'uid___A002_X924c91_Xa47.ms.wvr.smooth', 'uid___A002_X924c91_Xa47.ms.antpos'],
    gainfield = ['3', '', ''],
    interp = 'linear,linear',
    spwmap = [tsysmap,[],[]],
    calwt = T,
    flagbackup = F)
  
  if applyonly != True: es.getCalWeightStats('uid___A002_X924c91_Xa47.ms') 
  

# Split out science SPWs and time average
mystep = 8
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split') 
  split(vis = 'uid___A002_X924c91_Xa47.ms',
    outputvis = 'uid___A002_X924c91_Xa47.ms.split',
    datacolumn = 'corrected',
    spw = '11,13,15,17',
    keepflags = T)
  
  

print "# Calibration"

# Listobs, clear pointing table, and save original flags
mystep = 9
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split.listobs')
  listobs(vis = 'uid___A002_X924c91_Xa47.ms.split',
    listfile = 'uid___A002_X924c91_Xa47.ms.split.listobs')
  
  tb.open('uid___A002_X924c91_Xa47.ms.split/POINTING', nomodify = False)
  a = tb.rownumbers()
  tb.removerows(a)
  tb.close()
  
  if not os.path.exists('uid___A002_X924c91_Xa47.ms.split.flagversions/Original.flags'):
    flagmanager(vis = 'uid___A002_X924c91_Xa47.ms.split',
      mode = 'save',
      versionname = 'Original')
  
  

# Initial flagging
mystep = 10
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  # Flagging shadowed data
  
  flagdata(vis = 'uid___A002_X924c91_Xa47.ms.split',
    mode = 'shadow',
    flagbackup = F)
  
  # Flagging edge channels
  
  flagdata(vis = 'uid___A002_X924c91_Xa47.ms.split',
    mode = 'manual',
    spw = '0:0~7;120~127,1:0~7;120~127,2:0~7;120~127',
    flagbackup = F)
  
  

# Putting a model for the flux calibrator(s)
mystep = 11
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  setjy('uid___A002_X924c91_Xa47.ms.split',
        standard='manual', field='J1058+0133', spix=-0.271436,
        reffreq='144.566352GHz', fluxdensity=[3.662186,0,0,0])

"""
setjy(vis = 'uid___A002_X924c91_Xa47.ms.split',
    field = '1', # source name = J1058+0133
    spw = '0', # center frequency of spw = 144.566352343GHz
    standard = 'manual',
    fluxdensity = [3.7447486083, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X924c91_Xa47.ms.split',
    field = '1', # source name = J1058+0133
    spw = '1', # center frequency of spw = 154.711391639GHz
    standard = 'manual',
    fluxdensity = [3.7447486083, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X924c91_Xa47.ms.split',
    field = '1', # source name = J1058+0133
    spw = '2', # center frequency of spw = 156.444159225GHz
    standard = 'manual',
    fluxdensity = [3.7447486083, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
  
  setjy(vis = 'uid___A002_X924c91_Xa47.ms.split',
    field = '1', # source name = J1058+0133
    spw = '3', # center frequency of spw = 142.649352343GHz
    standard = 'manual',
    fluxdensity = [3.7447486083, 0, 0, 0]) # frequency of measurement = 114.11900198GHz
"""  
  

# Save flags before bandpass cal
mystep = 12
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X924c91_Xa47.ms.split',
    mode = 'save',
    versionname = 'BeforeBandpassCalibration')
  
  

# Bandpass calibration
mystep = 13
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split.ap_pre_bandpass') 
  
  gaincal(vis = 'uid___A002_X924c91_Xa47.ms.split',
    caltable = 'uid___A002_X924c91_Xa47.ms.split.ap_pre_bandpass',
    field = '0', # J0825+0309
    spw = '0:51~76,1:51~76,2:51~76,3:1536~2304',
    solint = 'int',
    refant = 'DA56',
    calmode = 'p')
  
  if applyonly != True: es.checkCalTable('uid___A002_X924c91_Xa47.ms.split.ap_pre_bandpass', msName='uid___A002_X924c91_Xa47.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split.bandpass') 
  bandpass(vis = 'uid___A002_X924c91_Xa47.ms.split',
    caltable = 'uid___A002_X924c91_Xa47.ms.split.bandpass',
    field = '', # J0825+0309
    intent = '*BANDPASS*',
    solint = 'inf,15.6MHz',
    combine = 'scan',
    refant = 'DA56',
    solnorm = True,
    bandtype = 'B',
    gaintable = 'uid___A002_X924c91_Xa47.ms.split.ap_pre_bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X924c91_Xa47.ms.split.bandpass', msName='uid___A002_X924c91_Xa47.ms.split', interactive=False) 
  

# Save flags before gain cal
mystep = 14
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X924c91_Xa47.ms.split',
    mode = 'save',
    versionname = 'BeforeGainCalibration')
  
  

# Gain calibration
mystep = 15
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split.phase_int') 
  gaincal(vis = 'uid___A002_X924c91_Xa47.ms.split',
    caltable = 'uid___A002_X924c91_Xa47.ms.split.phase_int',
    field = '0~2', # J0825+0309,J1058+0133,J0909+0121
    solint = 'int',
    refant = 'DA56',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X924c91_Xa47.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X924c91_Xa47.ms.split.phase_int', msName='uid___A002_X924c91_Xa47.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split.ampli_inf') 
  gaincal(vis = 'uid___A002_X924c91_Xa47.ms.split',
    caltable = 'uid___A002_X924c91_Xa47.ms.split.ampli_inf',
    field = '0~2', # J0825+0309,J1058+0133,J0909+0121
    solint = 'inf',
    refant = 'DA56',
    gaintype = 'T',
    calmode = 'a',
    gaintable = ['uid___A002_X924c91_Xa47.ms.split.bandpass', 'uid___A002_X924c91_Xa47.ms.split.phase_int'])
  
  if applyonly != True: es.checkCalTable('uid___A002_X924c91_Xa47.ms.split.ampli_inf', msName='uid___A002_X924c91_Xa47.ms.split', interactive=False) 
  
  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split.flux_inf') 
  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split.fluxscale') 
  mylogfile = casalog.logfile()
  casalog.setlogfile('uid___A002_X924c91_Xa47.ms.split.fluxscale')
  
  fluxscaleDict = fluxscale(vis = 'uid___A002_X924c91_Xa47.ms.split',
    caltable = 'uid___A002_X924c91_Xa47.ms.split.ampli_inf',
    fluxtable = 'uid___A002_X924c91_Xa47.ms.split.flux_inf',
    reference = '1') # J1058+0133
  
  casalog.setlogfile(mylogfile)
  
  if applyonly != True: es.fluxscale2(caltable = 'uid___A002_X924c91_Xa47.ms.split.ampli_inf', removeOutliers=True, msName='uid___A002_X924c91_Xa47.ms', writeToFile=True, preavg=10000)
  
  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split.phase_inf') 
  gaincal(vis = 'uid___A002_X924c91_Xa47.ms.split',
    caltable = 'uid___A002_X924c91_Xa47.ms.split.phase_inf',
    field = '0~2', # J0825+0309,J1058+0133,J0909+0121
    solint = 'inf',
    refant = 'DA56',
    gaintype = 'G',
    calmode = 'p',
    gaintable = 'uid___A002_X924c91_Xa47.ms.split.bandpass')
  
  if applyonly != True: es.checkCalTable('uid___A002_X924c91_Xa47.ms.split.phase_inf', msName='uid___A002_X924c91_Xa47.ms.split', interactive=False) 
  

# Save flags before applycal
mystep = 16
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  
  flagmanager(vis = 'uid___A002_X924c91_Xa47.ms.split',
    mode = 'save',
    versionname = 'BeforeApplycal')
  
  

# Application of the bandpass and gain cal tables
mystep = 17
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  for i in ['0', '1']: # J0825+0309,J1058+0133
    applycal(vis = 'uid___A002_X924c91_Xa47.ms.split',
      field = str(i),
      gaintable = ['uid___A002_X924c91_Xa47.ms.split.bandpass', 'uid___A002_X924c91_Xa47.ms.split.phase_int', 'uid___A002_X924c91_Xa47.ms.split.flux_inf'],
      gainfield = ['', i, i],
      interp = 'linear,linear',
      calwt = F,
      flagbackup = F)
  
  applycal(vis = 'uid___A002_X924c91_Xa47.ms.split',
    field = '2,3', # SDP.81
    gaintable = ['uid___A002_X924c91_Xa47.ms.split.bandpass', 'uid___A002_X924c91_Xa47.ms.split.phase_inf', 'uid___A002_X924c91_Xa47.ms.split.flux_inf'],
    gainfield = ['', '2', '2'], # J0909+0121
    interp = 'linear,linear',
    calwt = F,
    flagbackup = F)
  

# Split out corrected column
mystep = 18
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print 'Step ', mystep, step_title[mystep]

  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split.cal') 
  split(vis = 'uid___A002_X924c91_Xa47.ms.split',
    outputvis = 'uid___A002_X924c91_Xa47.ms.split.cal',
    datacolumn = 'corrected',
    keepflags = T)

  # Additional flags
  flagdata(vis = 'uid___A002_X924c91_Xa47.ms.split.cal',
    mode = 'manual',
    antenna='PM04', spw='2',
    flagbackup = F)
   
  # Split science target data. We perform limited channel averaging
  # of all spws to reduce file size, without losing any information.
  os.system('rm -rf uid___A002_X924c91_Xa47.ms.split.cal.science') 
  split(vis = 'uid___A002_X924c91_Xa47.ms.split.cal',
    outputvis = 'uid___A002_X924c91_Xa47.ms.split.cal.science',
    datacolumn = 'data',
    field='3', spw='0,1,2,3', width=[16,16,16,20],
    keepflags = T)

