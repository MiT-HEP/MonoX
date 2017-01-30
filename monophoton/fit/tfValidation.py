import sys
sys.dont_write_bytecode = True
import os
import array
import math
from pprint import pprint

plotDir = 'workspace'

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
sys.path.append(basedir.replace('monoph', 'common'))
from workspace import fetchHistograms
from plotstyle import SimpleCanvas, RatioCanvas
import parameters

import ROOT as r

sources = {}
sourcePlots = {}
totals = {}

hstore = r.gROOT.mkdir('hstore')

fetchHistograms(parameters, sources, sourcePlots, totals, hstore)

rcanvas = RatioCanvas(name = 'datamc', lumi = 36400)
rcanvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
rcanvas.legend.add('mc', 'Z/W MC', opt = 'LF', lcolor = r.kRed + 1, lwidth = 2, fcolor = r.kGray, fstyle = 1001, msize = 0)
rcanvas.legend.add('data', 'Z/W Data', opt = 'L', color = r.kBlack, mstyle = 8)

for lep in ['mu', 'el']:

    ### make MC TF 
    mcDilep = sourcePlots['di'+lep]['zg']
    mcMonolep = sourcePlots['mono'+lep]['wg']

    hMcRatio = mcDilep['nominal'].Clone('tf_mc_'+lep)
    hMcRatio.Divide(mcMonolep['nominal'])

    ### Add theory uncertainties to MC TF
    gMcRatio = r.TGraphAsymmErrors(hMcRatio)
    # print gMcRatio.GetErrorXlow(0), gMcRatio.GetErrorXhigh(gMcRatio.GetN()-1)

    for nuis in ['EWK', 'vgQCDscale', 'vgPDF']:
        hMcRatioUp = mcDilep[nuis+'Up'].Clone('tf_mc_'+lep+'_'+nuis+'Up')
        hMcRatioUp.Divide(mcMonolep[nuis+'Up'])
        
        hMcUpErr = hMcRatioUp.Clone('tferr_mc_'+lep+'_'+nuis+'Up')
        hMcUpErr.Add(hMcRatio, -1)

        for iP in range(0, gMcRatio.GetN()):
            uperr = math.sqrt(gMcRatio.GetErrorYhigh(iP)**2 + hMcUpErr.GetBinContent(iP+1)**2)
            # print iP, uperr
            gMcRatio.SetPointEYhigh(iP, uperr)

        hMcRatioDown = mcDilep[nuis+'Down'].Clone('tf_mc_'+lep+'_'+nuis+'Down')
        hMcRatioDown.Divide(mcMonolep[nuis+'Down'])
        
        hMcDownErr = hMcRatio.Clone('tferr_mc_'+lep+'_'+nuis+'Down')
        hMcDownErr.Add(hMcRatioDown, -1)

        for iP in range(0, gMcRatio.GetN()):
            downerr = math.sqrt(gMcRatio.GetErrorYlow(iP)**2 + hMcDownErr.GetBinContent(iP+1)**2)
            # print iP, downerr
            gMcRatio.SetPointEYlow(iP, downerr)
            
    ### Get Data for Data TF
    hDataDilep = sourcePlots['di'+lep]['data_obs']['nominal']
    hDataMonolep = sourcePlots['mono'+lep]['data_obs']['nominal']

    ### Add up dilep backgrounds
    hBkgdDilep = None
    for sname in sourcePlots['di'+lep]:
        if sname == 'zg' or sname == 'data_obs':
            continue
        
        print 'Subtracting ' + sname + ' from di' + lep + ' observed.'

        if hBkgdDilep is None:
            hBkgdDilep = sourcePlots['di'+lep][sname]['nominal'].Clone('di'+lep+'_bkgd')
            # hBkgdDilep.Sumw2(True)
        else:
            hBkgdDilep.Add(sourcePlots['di'+lep][sname]['nominal'])

    ### Add up monolep backgrounds
    hBkgdMonolep = None
    for sname in sourcePlots['mono'+lep]:
        if sname == 'wg' or sname == 'data_obs':
            continue

        print 'Subtracting ' + sname + ' from mono' + lep + ' observed.'
        
        if hBkgdMonolep is None:
            hBkgdMonolep = sourcePlots['mono'+lep][sname]['nominal'].Clone('mono'+lep+'_bkgd')
            # hBkgdMonolep.Sumw2(True)
        else:
            hBkgdMonolep.Add(sourcePlots['mono'+lep][sname]['nominal'])

    ### Subtract backgrounds
    hDataDilep.Add(hBkgdDilep, -1)
    hDataMonolep.Add(hBkgdMonolep, -1)

    ### Make Data TF
    hDataRatio = hDataDilep.Clone('tf_data_'+lep)
    hDataRatio.Divide(hDataMonolep)

    ### Plot the things
    mcplots = gMcRatio
    rcanvas.legend.apply('mc', hMcRatio)
    rcanvas.legend.apply('mc', gMcRatio)
    rcanvas.legend.apply('data', hDataRatio)

    iData = rcanvas.addHistogram(hDataRatio, drawOpt = 'EP')
    iUnc = rcanvas.addHistogram(gMcRatio, drawOpt = 'E2')
    iMc = rcanvas.addHistogram(hMcRatio, drawOpt = 'L')

    outName = 'tf_ratio3_'+lep
    rcanvas.printWeb(plotDir, outName, hList = [iMc, iUnc, iMc, iData], rList = [iMc, iUnc, iMc, iData], logy = False)


### merge the regions
### make MC TF 
mcDimu = sourcePlots['dimu']['zg']
mcMonomu = sourcePlots['monomu']['wg']

mcDiel = sourcePlots['diel']['zg']
mcMonoel = sourcePlots['monoel']['wg']

hMcRatio = mcDimu['nominal'].Clone('tf_mc_lep')
hMcRatio.Add(mcDiel['nominal'], 1)
hMcMonolep = mcMonomu['nominal'].Clone('mc_monolep')
hMcMonolep.Add(mcMonoel['nominal'], 1)

hMcRatio.Divide(hMcMonolep)

### Add theory uncertainties to MC TF
gMcRatio = r.TGraphAsymmErrors(hMcRatio)
# print gMcRatio.GetErrorXlow(0), gMcRatio.GetErrorXhigh(gMcRatio.GetN()-1)

for nuis in ['EWK', 'vgQCDscale', 'vgPDF']:
    hMcRatioUp = mcDimu[nuis+'Up'].Clone('tf_mc_lep_'+nuis+'Up')
    hMcRatioUp.Add(mcDiel[nuis+'Up'], 1)
    hMcMonolepUp = mcMonolep[nuis+'Up'].Clone('mc_monolep_'+nuis+'Up')
    hMcMonolepUp.Add(mcDiel[nuis+'Up'], 1)
    hMcRatioUp.Divide(hMcMonolepUp)

    hMcUpErr = hMcRatioUp.Clone('tferr_mc_lep_'+nuis+'Up')
    hMcUpErr.Add(hMcRatio, -1)

    for iP in range(0, gMcRatio.GetN()):
        uperr = math.sqrt(gMcRatio.GetErrorYhigh(iP)**2 + hMcUpErr.GetBinContent(iP+1)**2)
        # print iP, uperr
        gMcRatio.SetPointEYhigh(iP, uperr)

    hMcRatioDown = mcDimu[nuis+'Down'].Clone('tf_mc_lep_'+nuis+'Down')
    hMcRatioDown.Add(mcDiel[nuis+'Down'], 1)
    hMcMonolepDown = mcMonolep[nuis+'Down'].Clone('mc_monolep_'+nuis+'Down')
    hMcMonolepDown.Add(mcDiel[nuis+'Down'], 1)
    hMcRatioDown.Divide(hMcMonolepDown)

    hMcDownErr = hMcRatio.Clone('tferr_mc_lep_'+nuis+'Down')
    hMcDownErr.Add(hMcRatioDown, -1)

    for iP in range(0, gMcRatio.GetN()):
        downerr = math.sqrt(gMcRatio.GetErrorYlow(iP)**2 + hMcDownErr.GetBinContent(iP+1)**2)
        # print iP, downerr
        gMcRatio.SetPointEYlow(iP, downerr)

### Get Data for Data TF
hDataDilep = sourcePlots['dimu']['data_obs']['nominal'].Clone('data_dilep')
hDataDilep.Add(sourcePlots['diel']['data_obs']['nominal'], 1)
hDataMonolep = sourcePlots['monomu']['data_obs']['nominal'].Clone('data_monolep')
hDataMonolep.Add(sourcePlots['monoel']['data_obs']['nominal'], 1)

### Add up dilep backgrounds
hBkgdDilep = None
for sname in sourcePlots['dimu']:
    if sname == 'zg' or sname == 'data_obs':
        continue

    print 'Subtracting ' + sname + ' from dilep observed.'

    if hBkgdDilep is None:
        hBkgdDilep = sourcePlots['dimu'][sname]['nominal'].Clone('dilep_bkgd')
    else:
        hBkgdDilep.Add(sourcePlots['dimu'][sname]['nominal'])

for sname in sourcePlots['diel']:
    if sname == 'zg' or sname == 'data_obs':
        continue

    print 'Subtracting ' + sname + ' from dilep observed.'

    if hBkgdDilep is None:
        hBkgdDilep = sourcePlots['diel'][sname]['nominal'].Clone('dilep_bkgd')
    else:
        hBkgdDilep.Add(sourcePlots['diel'][sname]['nominal'])

### Add up monolep backgrounds
hBkgdMonolep = None
for sname in sourcePlots['monomu']:
    if sname == 'wg' or sname == 'data_obs':
        continue

    print 'Subtracting ' + sname + ' from monolep observed.'

    if hBkgdMonolep is None:
        hBkgdMonolep = sourcePlots['monomu'][sname]['nominal'].Clone('monolep_bkgd')
        # hBkgdMonolep.Sumw2(True)
    else:
        hBkgdMonolep.Add(sourcePlots['monomu'][sname]['nominal'])

for sname in sourcePlots['monoel']:
    if sname == 'wg' or sname == 'data_obs':
        continue

    print 'Subtracting ' + sname + ' from monolep observed.'

    if hBkgdMonolep is None:
        hBkgdMonolep = sourcePlots['monoel'][sname]['nominal'].Clone('monolep_bkgd')
        # hBkgdMonolep.Sumw2(True)
    else:
        hBkgdMonolep.Add(sourcePlots['monoel'][sname]['nominal'])

### Subtract backgrounds
hDataDilep.Add(hBkgdDilep, -1)
hDataMonolep.Add(hBkgdMonolep, -1)

### Make Data TF
hDataRatio = hDataDilep.Clone('tf_data_lep')
hDataRatio.Divide(hDataMonolep)

### Plot the things
mcplots = gMcRatio
rcanvas.legend.apply('mc', hMcRatio)
rcanvas.legend.apply('mc', gMcRatio)
rcanvas.legend.apply('data', hDataRatio)

iData = rcanvas.addHistogram(hDataRatio, drawOpt = 'EP')
iUnc = rcanvas.addHistogram(gMcRatio, drawOpt = 'E2')
iMc = rcanvas.addHistogram(hMcRatio, drawOpt = 'L')

outName = 'tf_ratio3_lep'
rcanvas.printWeb(plotDir, outName, hList = [iMc, iUnc, iMc, iData], rList = [iMc, iUnc, iMc, iData], logy = False)
