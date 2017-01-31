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

    for nuis, corr in [('EWK', 1.0), ('vgQCDscale', 0.8), ('vgPDF', 1.0)]:
        print nuis, corr
        hMcDilepUp     = mcDilep[nuis+'Up']
        hMcMonolepUp   = mcMonolep[nuis+'Up']
        hMcDilepDown   = mcDilep[nuis+'Down']
        hMcMonolepDown = mcMonolep[nuis+'Down']

        for iP in range(1, gMcRatio.GetN()+1):
            rNom = hMcRatio.GetBinContent(iP)
            upup     = hMcDilepUp.GetBinContent(iP)   / hMcMonolepUp.GetBinContent(iP)   - rNom
            updown   = hMcDilepUp.GetBinContent(iP)   / hMcMonolepDown.GetBinContent(iP) - rNom
            downup   = hMcDilepDown.GetBinContent(iP) / hMcMonolepUp.GetBinContent(iP)   - rNom
            downdown = hMcDilepDown.GetBinContent(iP) / hMcMonolepDown.GetBinContent(iP) - rNom
            
            dUp = math.sqrt( (1 + corr)/2 * upup**2 + (1 - corr)/2 * updown**2 )
            dDown = math.sqrt( (1 + corr)/2 * downdown**2 + (1 - corr)/2 * downup**2 )
            # print '%i %6.5f %6.5f' % (iP, dUp, dDown)

            eUp = math.sqrt(gMcRatio.GetErrorYhigh(iP-1)**2 + dUp**2)
            eDown = math.sqrt(gMcRatio.GetErrorYlow(iP-1)**2 + dDown**2)
            # print '%i %6.5f %6.5f' % (iP, eUp, eDown)

            gMcRatio.SetPointEYhigh(iP-1, eUp)
            gMcRatio.SetPointEYlow(iP-1, eDown)
            
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

    """
    print 'Data ratio'
    for iB in range(1, hDataRatio.GetNbinsX()+1):
        print iB, hDataRatio.GetBinContent(iB)
    """

    ### Plot the things
    mcplots = gMcRatio
    rcanvas.legend.apply('mc', hMcRatio)
    rcanvas.legend.apply('mc', gMcRatio)
    rcanvas.legend.apply('data', hDataRatio)

    rcanvas.Clear()
    rcanvas.ylimits = (0, 0.7)

    iData = rcanvas.addHistogram(hDataRatio, drawOpt = 'PE0')
    iUnc = rcanvas.addHistogram(gMcRatio, drawOpt = 'E2')
    iMc = rcanvas.addHistogram(hMcRatio, drawOpt = 'L')

    outName = 'tf_ratio4_'+lep
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

hUpRatios = {}
hDownRatios = {}

for nuis, corr in [('EWK', 1.0), ('vgQCDscale', 0.8), ('vgPDF', 1.0)]:
    print nuis, corr
    hMcDimuUp     = mcDimu[nuis+'Up']
    hMcMonomuUp   = mcMonomu[nuis+'Up']
    hMcDimuDown   = mcDimu[nuis+'Down']
    hMcMonomuDown = mcMonomu[nuis+'Down']

    hMcDielUp     = mcDiel[nuis+'Up']
    hMcMonoelUp   = mcMonoel[nuis+'Up']
    hMcDielDown   = mcDiel[nuis+'Down']
    hMcMonoelDown = mcMonoel[nuis+'Down']

    for iP in range(1, gMcRatio.GetN()+1):
        rNom = hMcRatio.GetBinContent(iP)
        upup     = ( hMcDimuUp.GetBinContent(iP)   + hMcDielUp.GetBinContent(iP)   ) / ( hMcMonomuUp.GetBinContent(iP)   + hMcMonoelUp.GetBinContent(iP)   )  - rNom
        updown   = ( hMcDimuUp.GetBinContent(iP)   + hMcDielUp.GetBinContent(iP)   ) / ( hMcMonomuDown.GetBinContent(iP) + hMcMonoelDown.GetBinContent(iP) ) - rNom
        downup   = ( hMcDimuDown.GetBinContent(iP) + hMcDielDown.GetBinContent(iP) ) / ( hMcMonomuUp.GetBinContent(iP)   + hMcMonoelUp.GetBinContent(iP)   ) - rNom
        downdown = ( hMcDimuDown.GetBinContent(iP) + hMcDielDown.GetBinContent(iP) ) / ( hMcMonomuDown.GetBinContent(iP) + hMcMonoelDown.GetBinContent(iP) ) - rNom

        dUp = math.sqrt( (1 + corr)/2 * upup**2 + (1 - corr)/2 * updown**2 )
        dDown = math.sqrt( (1 + corr)/2 * downdown**2 + (1 - corr)/2 * downup**2 )
        # print '%i %6.5f %6.5f' % (iP, dUp, dDown)

        eUp = math.sqrt(gMcRatio.GetErrorYhigh(iP-1)**2 + dUp**2)
        eDown = math.sqrt(gMcRatio.GetErrorYlow(iP-1)**2 + dDown**2)
        # print '%i %6.5f %6.5f' % (iP, eUp, eDown)

        gMcRatio.SetPointEYhigh(iP-1, eUp)
        gMcRatio.SetPointEYlow(iP-1, eDown)

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

"""
print 'Data ratio'
for iB in range(1, hDataRatio.GetNbinsX()+1):
    print iB, hDataRatio.GetBinContent(iB)
"""

### Plot the things
mcplots = gMcRatio
rcanvas.legend.apply('mc', hMcRatio)
rcanvas.legend.apply('mc', gMcRatio)
rcanvas.legend.apply('data', hDataRatio)

rcanvas.Clear()
rcanvas.ylimits = (0, 0.7)

iData = rcanvas.addHistogram(hDataRatio, drawOpt = 'PE0')
iUnc = rcanvas.addHistogram(gMcRatio, drawOpt = 'E2')
iMc = rcanvas.addHistogram(hMcRatio, drawOpt = 'L')

"""
rcanvas.legend.add('EWK', 'Z/W EWK', opt = 'L', lstyle = r.kDashed, lcolor = r.kRed + 2, lwidth = 2, msize = 0)
rcanvas.legend.apply('EWK', hUpRatios['EWK'])
rcanvas.legend.apply('EWK', hDownRatios['EWK'])
iEWKUp = rcanvas.addHistogram(hUpRatios['EWK'])
iEWKDown = rcanvas.addHistogram(hDownRatios['EWK'])

rcanvas.legend.add('vgQCDscale', 'Z/W vgQCDscale', opt = 'L', lstyle = r.kDashed, lcolor = r.kRed + 3, lwidth = 2, msize = 0)
rcanvas.legend.apply('vgQCDscale', hUpRatios['vgQCDscale'])
rcanvas.legend.apply('vgQCDscale', hDownRatios['vgQCDscale'])
ivgQCDscaleUp = rcanvas.addHistogram(hUpRatios['vgQCDscale'])
ivgQCDscaleDown = rcanvas.addHistogram(hDownRatios['vgQCDscale'])

rcanvas.legend.add('vgPDF', 'Z/W vgPDF', opt = 'L', lstyle = r.kDashed, lcolor = r.kRed + 4, lwidth = 2, msize = 0)
rcanvas.legend.apply('vgPDF', hUpRatios['vgPDF'])
rcanvas.legend.apply('vgPDF', hDownRatios['vgPDF'])
ivgPDFUp = rcanvas.addHistogram(hUpRatios['vgPDF'])
ivgPDFDown = rcanvas.addHistogram(hDownRatios['vgPDF'])

theoList = [iEWKUp, iEWKDown, ivgQCDscaleUp, ivgQCDscaleDown, ivgPDFUp, ivgPDFDown]
"""
theoList = []

outName = 'tf_ratio4_lep'
rcanvas.printWeb(plotDir, outName, hList = [iMc, iUnc, iMc, iData] + theoList, rList = [iMc, iUnc, iMc, iData] + theoList, logy = False)
