import sys
import os
import array
import math
import ROOT as r 
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
from plotstyle import SimpleCanvas, RatioCanvas, DataMCCanvas
import config

canvas = DataMCCanvas(lumi = 2239.9)
# binning = array.array('d', [0. + 10. * x for x in range(13)])

binning = array.array('d', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)]
                      + [200. + 50. * x for x in range(9)] ) 

outputFile = r.TFile.Open(basedir+'/data/gjetsTFactor.root', 'recreate')

dtree = r.TChain('events')
dtree.Add(config.skimDir + '/sph-d*_monoph.root')

btree = r.TChain('events')
btree.Add(config.skimDir + '/sph-d*_hfakeWorst.root')
btree.Add(config.skimDir + '/sph-d*_efake.root')

bmctree = r.TChain('events')
bmctree.Add(config.skimDir + '/znng-130_monoph.root')
bmctree.Add(config.skimDir + '/wnlg-130_monoph.root')
bmctree.Add(config.skimDir + '/wlnu-*_monoph.root')
bmctree.Add(config.skimDir + '/ttg_monoph.root')
bmctree.Add(config.skimDir + '/zllg-130_monoph.root')

mctree = r.TChain('events')
mctree.Add(config.skimDir + '/g-40_monoph.root')
mctree.Add(config.skimDir + '/g-100_monoph.root')
mctree.Add(config.skimDir + '/g-200_monoph.root')
mctree.Add(config.skimDir + '/g-400_monoph.root')
mctree.Add(config.skimDir + '/g-600_monoph.root')

###########################################
####### Get Data/MC Yields ################
###########################################

regions = [ ( 'Low', '(photons.pt[0] > 175. && t1Met.met < 120. && !t1Met.iso)')
            ,('High', '(photons.pt[0] > 175. && t1Met.met < 120. && t1Met.iso)') 
            ] 

dmets = []
bmets = []
gmets = []
mcmets = []

for region, sel in regions:
    dname = 'dmet'+region
    dmet = r.TH1D(dname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    dmet.SetMinimum(0.02)
    dmet.SetMaximum(3000.)
    dmet.Sumw2()
    dtree.Draw('t1Met.met>>'+dname, sel, 'goff')

    bname = 'bmet'+region
    bmet = r.TH1D(bname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    bmet.SetMinimum(0.02)
    bmet.SetMaximum(3000.)
    bmet.Sumw2()
    btree.Draw('t1Met.met>>'+bname, 'weight * '+sel, 'goff')

    bmcmet = r.TH1D(bname+'MC', ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    bmcmet.Sumw2()
    bmctree.Draw('t1Met.met>>'+bname, '2239.9 * weight * '+sel, 'goff')
    bmet.Add(bmcmet)

    gname ='gmet'+region
    gmet = dmet.Clone(gname)
    gmet.Add(bmet, -1)

    mcname = 'mcmet'+region
    mcmet = r.TH1D(mcname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    mcmet.SetMinimum(0.02)
    mcmet.SetMaximum(3000.)
    mcmet.Sumw2()
    mctree.Draw('t1Met.met>>'+mcname, '2239.9 * weight * '+sel, 'goff')
    
    dmet.Scale(1., 'width')
    bmet.Scale(1., 'width')
    gmet.Scale(1., 'width')
    mcmet.Scale(1., 'width')

    outputFile.cd()
    dmet.Write()
    bmet.Write()
    gmet.Write()
    mcmet.Write()

    dmets.append(dmet)
    bmets.append(bmet)
    gmets.append(gmet)
    mcmets.append(mcmet)

    canvas.cd()
    canvas.ylimits = (0.2, 2000.)
    canvas.Clear()
    canvas.legend.Clear()

    canvas.ylimits = (0.2, 2000.)
    canvas.SetLogy(True)

    canvas.legend.setPosition(0.6, 0.7, 0.95, 0.9)

    canvas.addStacked(bmet, title = 'Background', color = r.TColor.GetColor(0x55, 0x44, 0xff), idx = -1)

    canvas.addStacked(mcmet, title = '#gamma + jet MC', color = r.TColor.GetColor(0xff, 0xaa, 0xcc), idx = -1)

    canvas.addObs(dmet, title = 'Data')

    canvas.xtitle = canvas.obsHistogram().GetXaxis().GetTitle()
    canvas.ytitle = canvas.obsHistogram().GetYaxis().GetTitle()

    canvas.Update(logy = True, ymax = 2000.)

    canvas.printWeb('monophoton/gjetsTFactor', 'distributions'+region)

###########################################
####### Transfer Factors ##################
###########################################

methods = [ ('Data', gmets), ('MC', mcmets) ]
scanvas = SimpleCanvas(lumi = 2239.9)

tfacts = []

for method, hists in methods:
    tname = 'tfact'+method
    tfact = hists[1].Clone(tname)
    tfact.Divide(hists[0])
    tfact.GetYaxis().SetTitle("")

    outputFile.cd()
    tfact.Write()
    tfacts.append(tfact)

    scanvas.Clear()
    scanvas.legend.Clear()

    scanvas.ylimits = (0.01, 2.5)
    scanvas.SetLogy(True)

    scanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
    scanvas.legend.add(tname, title = 'Transfer factor', lcolor = r.kBlack, lwidth = 1)

    scanvas.legend.apply(tname, tfact)

    scanvas.addHistogram(tfact, drawOpt = 'EP')

    scanvas.printWeb('monophoton/gjetsTFactor', 'tfactor'+method)

canvas.Clear()
canvas.legend.Clear()

canvas.ylimits = (0.01, 2.5)
canvas.SetLogy(True)

canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

canvas.addObs(tfacts[0], 'Data')
canvas.addSignal(tfacts[1], title = 'MC', color = r.kRed, idx = -1)
canvas.addStacked(tfacts[1], title = 'MC', idx = -1)

canvas.printWeb('monophoton/gjetsTFactor', 'tfactorRatio')

###########################################
####### Plain Root Attempt ################
###########################################

expo = r.TF1("expo", "[0] * TMath::Exp([1] * x) + [2]", 0., 600.)
expo.SetParameters(1., -0.1, 0.)
expo.SetParLimits(1, -10., 0.)
expo.SetParLimits(2, 0., 10.)

rayleigh = r.TF1("rayleigh", "[0] * x * TMath::Exp( -x**2 / ( 2 * [1]**2))", 0., 600.)
rayleigh.SetParameters(1., 10.)
rayleigh.SetParLimits(1, 0.001, 600.)

pepe = r.TF1("pepe", "[0] * x * TMath::Exp( -x**2 /([1] + [2]*x)**2)", 0., 600.)
pepe.SetParameters(1., 10., 100.)
pepe.SetParLimits(1, 0.001, 150.)
pepe.SetParLimits(2, 0.1, 600.)

gauss = r.TF1("gauss", "[0] * TMath::Exp( -x**2 /([1] + [2]*x)**2)", 0., 600.)
gauss.SetParameters(1., 10., 100.)
gauss.SetParLimits(1, 0.001, 150.)
gauss.SetParLimits(2, 0.1, 600.)

## choosing model ##
model = gauss

tfacts[0].SetMinimum(0.0000001)
tfacts[0].Fit(model, "M WL B V", "goff", 0., 120.)

outputFile.cd()
model.Write()

tcanvas = r.TCanvas()

tfacts[0].Draw()
model.Draw("same")

leg = r.TLegend(0.6, 0.7, 0.9, 0.9)
leg.SetFillColor(r.kWhite)
leg.SetTextSize(0.03)
leg.AddEntry(tfacts[0], "Measured", "P")
leg.AddEntry(model, "Fit", "L")
leg.Draw("same")

tcanvas.SetLogy(False)

outName = '/home/ballen/public_html/cmsplots/monophoton/gjetsTFactor/tfactFit'
tcanvas.SaveAs(outName+'.pdf')
tcanvas.SaveAs(outName+'.png')

tcanvas.SetLogy(True)

outName = outName+'Logy'
tcanvas.SaveAs(outName+'.pdf')
tcanvas.SaveAs(outName+'.png')

###########################################
####### RooFit Attempt     ################
###########################################

"""
###########################################
####### Fitting on Low MET ################
###########################################

met = r.RooRealVar('met', 'E_T^{miss} (GeV)', 0., 120.)
met.setRange("fitting", 0., 120.)
met.setRange("plotting", 0., 600.)

fitTemplate = r.RooDataHist('fitTemp', '', r.RooArgList(met), tfacts[0])

norm = r.RooRealVar('norm', 'norm', 1., 0., 10.)

rate = r.RooRealVar('rate', 'rate', -0.1, -5., 0.)
expo = r.RooExponential("expo", "", met, rate)
expo.setNormRange('fitting')
eexpo = r.RooExtendPdf("eexpo", "", expo, norm, "fitting")

model = expo

fitResult = model.fitTo(fitTemplate, r.RooFit.Extended(), r.RooFit.Strategy(1), r.RooFit.Save())

tcanvas = r.TCanvas()

frame = met.frame()
frame.SetTitle('#gamma + jets Transfer Factor')
frame.SetMinimum(0.01)
frame.SetMaximum(1.0)

fitTemplate.plotOn(frame, r.RooFit.Name('Measured'))
model.plotOn(frame, r.RooFit.Name('Fit'), r.RooFit.Range("fitting"), r.RooFit.NormRange("fitting"))

model.Print('t')

frame.Draw("goff")

leg = r.TLegend(0.6, 0.6, 0.85, 0.75)
leg.SetFillColor(r.kWhite)
leg.SetTextSize(0.03)
leg.AddEntry(frame.findObject('Measured'), "Measured", "P")
leg.AddEntry(frame.findObject("Fit"), "Fit", "L")
leg.Draw()

tcanvas.SetLogy(False)

outName = '/home/ballen/public_html/cmsplots/monophoton/gjetsTFactor/tfactFit'
tcanvas.SaveAs(outName+'.pdf')
tcanvas.SaveAs(outName+'.png')

###########################################
####### Extrapolate to High MET ###########
###########################################

metPlot = r.RooRealVar('metPlot', 'E_T^{miss} (GeV)', 0., 600.)
metPlot.setRange("fitting", 0., 120.)
metPlot.setRange("plotting", 0., 600.)

fitTemplatePlot = r.RooDataHist('fitTempPlot', '', r.RooArgList(met), tfacts[0])

expoPlot = r.RooExponential("expoPlot", "", metPlot, rate)
eexpoPlot = r.RooExtendPdf("eexpoPlot", "", expoPlot, norm, "fitting")

modelPlot = eexpoPlot

frame = metPlot.frame()
frame.SetTitle('#gamma + jets Transfer Factor')
frame.SetMinimum(0.00001)
frame.SetMaximum(1.0)

fitTemplatePlot.plotOn(frame, r.RooFit.Name('Measured'))
modelPlot.plotOn(frame, r.RooFit.Name('Fit'), r.RooFit.Range("plotting"), r.RooFit.NormRange("fitting"))

modelPlot.Print('t')

frame.Draw("goff")

leg = r.TLegend(0.6, 0.6, 0.85, 0.75)
leg.SetFillColor(r.kWhite)
leg.SetTextSize(0.03)
leg.AddEntry(frame.findObject('Measured'), "Measured", "P")
leg.AddEntry(frame.findObject("Fit"), "Fit", "L")
leg.Draw()

tcanvas.SetLogy(False)

outName = '/home/ballen/public_html/cmsplots/monophoton/gjetsTFactor/tfactExtrap'
tcanvas.SaveAs(outName+'.pdf')
tcanvas.SaveAs(outName+'.png')
"""

###########################################
####### Numpy attempt at fitting ##########
###########################################

"""
from pprint import pprint
import numpy as np
from scipy.optimize import leastsq
import matplotlib.pyplot as plot
import matplotlib.axes as axes

print 'stuff'

metVals = np.asarray( [5. + 10. * x for x in range(12) ])
tVals = np.asarray( [ (tfacts[0].GetBinContent(iBin), tfacts[0].GetBinError(iBin)) 
                      for iBin in range(tfacts[0].GetNbinsX()+1) ] )

print 'stuff stuff'

pprint(metVals)
pprint(tVals)

params = [-0.1, 0.]
paramsInit = params

print 'stuff stuff stuff'

def fitFunc(_params, _met):
    tfact_ = np.exp(_met / _params[0]) + _params[1]
    return tfact_

def resFunc(_params, _met, _tfact):
    err_ = ( _tfact[0] - fitFunc(_params, _met) ) / _tfact[1]

paramsFit = leastsq(resFunc, paramsInit, args=(metVals, tVals), full_output=1, warning=True)
pprint(paramsFit)

metFits = np.asarray( [5. + 10. * x for x in range(12)] + [130. + 20. * x for x in range (4) ] 
                      + [225. + 50. * x for x in range(9)] )
tFits = [ fitFunc(paramsFit[0], met) for met in metFits ]

pprint(metFits)
pprint(tFits)

plot.figure()

plot.errorbar(metVals, tVals[0], yerr=tVals[1], fmt='ko', markersize=8.0, capsize=8, solid_capstyle='projecting', elinewidth=2)
plot.plot(metFits, tFits, 'r-', linewidth=1.0)

plot.legend(['Measured','Fit'])

plot.xlim(0.,600.)
plot.ylim(0.0,1.0)

plot.tick_params(axis='both', which='major', labelsize=16)
plot.ylabel(r'Transfer Factor', fontsize=24)
plot.xlabel(r'E_T^{miss} (GeV)', fontsize=24)

outName = '/home/ballen/public_html/cmsplots/monophoton/gjetsTFactor/tfactPyFit'
plot.savefig(outName+'.pdf', format='pdf')
plot.savefig(outName+'.png', format='png')
"""
