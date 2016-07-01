import sys
import os
import array
import math
import ROOT as r 
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
from plotstyle import SimpleCanvas, RatioCanvas, DataMCCanvas
from datasets import allsamples
import config
from pprint import pprint

outputFile = r.TFile.Open(basedir+'/data/gjetsTFactor.root', 'recreate')

dtree = r.TChain('events')
dtree.Add(config.skimDir + '/sph-16*_monoph.root')

btree = r.TChain('events')
btree.Add(config.skimDir + '/sph-16*_hfake.root')
btree.Add(config.skimDir + '/sph-16*_efake.root')

bmctree = r.TChain('events')
# bmctree.Add(config.skimDir + '/znng-130_monoph.root')
# bmctree.Add(config.skimDir + '/wnlg-130_monoph.root') 
# bmctree.Add(config.skimDir + '/wg_monoph.root') # NLO sample to get around pT/MET > 130 GeV cut on LO sample
bmctree.Add(config.skimDir + '/wglo_monoph.root')
bmctree.Add(config.skimDir + '/wlnu-*_monoph.root')
bmctree.Add(config.skimDir + '/ttg_monoph.root')
bmctree.Add(config.skimDir + '/zg_monoph.root')

znntree = r.TChain('events')
znntree.Add(config.skimDir + '/zg_dimu.root')

mctree = r.TChain('events')
mctree.Add(config.skimDir + '/gj04-40_monoph.root')
mctree.Add(config.skimDir + '/gj04-100_monoph.root')
mctree.Add(config.skimDir + '/gj04-200_monoph.root')
mctree.Add(config.skimDir + '/gj04-400_monoph.root')
mctree.Add(config.skimDir + '/gj04-600_monoph.root')

###########################################
####### Get Data/MC Yields ################
###########################################

fitMax = 120.

regions = [
    ('Low', '(photons.pt[0] > 175. && t1Met.photonDPhi > 2.0 && t1Met.minJetDPhi < 0.5)'),
    ('High', '(photons.pt[0] > 175. && t1Met.photonDPhi > 2.0 && t1Met.minJetDPhi > 0.5 && t1Met.met < '+str(fitMax)+')')
] 

"""
binnings = {
    'Low': array.array('d', [0. + 2. * x for x in range(100)]),
    'High': array.array('d', [0. + 2. * x for x in range(65)])
}
"""

binnings =  {
    'Low': array.array('d', [0. + 10. * x for x in range(10)] + [100., 120., 140., 170.]
                       + [200. + 50. * x for x in range(9)] ),
    'High': array.array('d', [0. + 10. * x for x in range(10)] + [100., 120., 140., 170.]
                       + [200. + 50. * x for x in range(9)] )
}

dmets = []
bmets = []
gmets = []
mcmets = []

lumi = allsamples['sph-16b2'].lumi
canvas = DataMCCanvas(lumi = lumi)

for region, sel in regions:
    binning = binnings[region]

    dname = 'dmet'+region
    dmet = r.TH1D(dname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    dmet.SetMinimum(0.002)
    dmet.Sumw2()
    dtree.Draw('t1Met.met>>'+dname, sel, 'goff')

    bname = 'bmet'+region
    bmet = r.TH1D(bname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    bmet.SetMinimum(0.002)
    bmet.Sumw2()
    btree.Draw('t1Met.met>>'+bname, 'weight * '+sel, 'goff')

    bmcmet = r.TH1D(bname+'MC', ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    bmcmet.Sumw2()
    bmctree.Draw('t1Met.met>>'+bname, str(lumi)+' * weight * '+sel, 'goff')
    znntree.Draw('t1Met.met>>+' + bname, str(lumi)+' * 6.112 * weight * ' + sel, 'goff')
    bmet.Add(bmcmet)

    gname ='gmet'+region
    gmet = dmet.Clone(gname)
    gmet.Add(bmet, -1)

    mcname = 'mcmet'+region
    mcmet = r.TH1D(mcname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
    mcmet.SetMinimum(0.002)
    mcmet.Sumw2()
    mctree.Draw('t1Met.met>>'+mcname, str(lumi)+' * weight * '+sel, 'goff')
    
    dmet.Scale(1., 'width')
    bmet.Scale(1., 'width')
    gmet.Scale(1., 'width')
    mcmet.Scale(1., 'width')

    for iBin in range(gmet.GetNbinsX()+2):
        # print iBin, gmet.GetBinLowEdge(iBin)
        if (gmet.GetBinContent(iBin) < 0.):
            gmet.SetBinContent(iBin, 0.)

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
    canvas.Clear()
    canvas.legend.Clear()

    canvas.ylimits = (0.002, 2500)

    canvas.SetLogy(True)

    canvas.legend.setPosition(0.6, 0.7, 0.95, 0.9)

    canvas.addStacked(bmet, title = 'Background', color = r.TColor.GetColor(0x55, 0x44, 0xff), idx = -1)

    canvas.addStacked(mcmet, title = '#gamma + jet MC', color = r.TColor.GetColor(0xff, 0xaa, 0xcc), idx = -1)

    canvas.addObs(dmet, title = 'Data')

    canvas.xtitle = canvas.obsHistogram().GetXaxis().GetTitle()
    canvas.ytitle = canvas.obsHistogram().GetYaxis().GetTitle()

    canvas.Update(logy = True)

    canvas.printWeb('monophoton/gjetsTFactor', 'distributions'+region)

###########################################
####### Transfer Factors ##################
###########################################

methods = [ ('Data', gmets), ('MC', mcmets) ]
scanvas = SimpleCanvas(lumi = lumi)

tfacts = []

for method, hists in methods:
    tname = 'tfact'+method
    tfact = hists[1].Clone(tname)
    tfact.Divide(hists[0])

    tfact.GetYaxis().SetTitle("")

    tfact.SetMarkerStyle(8)
    tfact.SetMarkerSize(0.8)

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

canvas.SetLogy(True)
canvas.ylimits = (0.01, 2.5)

canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

canvas.addObs(tfacts[0], 'Data')
canvas.addSignal(tfacts[1], title = 'MC', color = r.kRed, idx = -1)
canvas.addStacked(tfacts[1], title = 'MC', idx = -1)

canvas.printWeb('monophoton/gjetsTFactor', 'tfactorRatio', ymax = 2.5)

###########################################
####### Plain Root Attempt ################
###########################################

expo = r.TF1("SingleExpo", "[0] * TMath::Exp([1] * x) + [2]", 0., 600.)
expo.SetParameters(1., -0.1, 0.)
expo.SetParLimits(1, -10., 0.)
expo.SetParLimits(2, 0., 10.)

dexpo = r.TF1("Expo", "[0] * TMath::Exp([2] * x) + [1] * TMath::Exp([3] * x)", 0., 600.)
dexpo.SetParameters(10., 0.1, -0.1, -0.1)
dexpo.SetParLimits(0, 0., 10000.)
dexpo.SetParLimits(1, 0., 10000.)
dexpo.SetParLimits(2, -1., 0.)
dexpo.SetParLimits(3, -1., 0.)

rayleigh = r.TF1("Rayleigh", "[0] * x * TMath::Exp( -x**2 / ( 2 * [1]**2))", 0., 600.)
rayleigh.SetParameters(1., 10.)
rayleigh.SetParLimits(1, 0.1, 600.)

pepe = r.TF1("Rayleigh1", "[0] * x * TMath::Exp( -x**2 /([1] + [2]*x)**2)", 0., 600.)
pepe.SetParameters(1., 10., 10.)
pepe.SetParLimits(1, 0.1, 300.)
pepe.SetParLimits(2, 0.000001, 10.)

pepeplus = r.TF1("Rayleigh2", "[0] * x * TMath::Exp( -x**2 /([1] + [2]*x + [3]*x**2))", 0., 600.)
pepeplus.SetParameters(1., 10., 10., 0.1)
pepeplus.SetParLimits(1, 0.1, 2000.)
pepeplus.SetParLimits(2, 0.00001, 100.)
pepeplus.SetParLimits(3, 0.000001, 1.)

rpepe = r.TF1("RayleighRatio", "[0] * TMath::Exp( -x**2 /([1] + [2]*x + [3]*x**2)) / TMath::Exp( -x**2 /([4] + [5]*x + [6]*x**2)) ", 0., 600.)
rpepe.SetParameters(1., 10., 10., 0.1, 10., 10., 0.1)
rpepe.SetParLimits(1, 0.1, 1000.)
rpepe.SetParLimits(2, 0.001, 100.)
rpepe.SetParLimits(3, 0.00001, 1.)
rpepe.SetParLimits(4, 0.1, 1000.)
rpepe.SetParLimits(5, 0.001, 100.)
rpepe.SetParLimits(6, 0.00001, 1.)

gauss = r.TF1("Gauss", "[0] * TMath::Exp( -x**2 /([1] + [2]*x)**2)", 0., 600.)
gauss.SetParameters(1., 10., 100.)
gauss.SetParLimits(1, 0.001, 150.)
gauss.SetParLimits(2, 0.1, 600.)

smear = r.TF1("Smear", "[0] * TMath::Exp( -x**2/[1]**2)", 0., 600.)
smear.SetParameters(1., 10.)
smear.SetParLimits(1, 0.1, 150.)

constant = r.TF1("constant", str(tfacts[0].GetBinContent(tfacts[0].FindBin(fitMax-1.))), 0., 600.)


## choosing model ##
models = [ gauss, dexpo ] # , constant] 
colors = [ r.kRed, r.kBlue, r.kMagenta ] 
"""
for model in models[:]:
    convolve = r.TF1Convolution(model, smear)
    smeared = r.TF1(model.GetName()+"Smeared", convolve, 0., 600., convolve.GetNpar())
    models.append(smeared)
"""

tfacts[0].SetMinimum(0.00001)
tfacts[0].SetMaximum(1.1)
fit = tfacts[0].Clone('fit')
for iM, model in enumerate(models):
    print "\nFitting with", model.GetName(), "\n"
    fit.Fit(model, "M WL B ", "goff", 30., fitMax)

    model.SetLineColor(colors[iM])

    outputFile.cd()
    model.Write()

tcanvas = r.TCanvas()

tfacts[0].SetMarkerColor(1)
tfacts[0].SetMarkerStyle(8)
tfacts[0].SetMarkerSize(1.2)
tfacts[0].Draw("PE")
for model in models[:]:
    model.Draw("same")

leg = r.TLegend(0.6, 0.7, 0.9, 0.9)
leg.SetFillColor(r.kWhite)
leg.SetTextSize(0.03)
leg.AddEntry(tfacts[0], "Measured", "P")
for model in models[:]:
    leg.AddEntry(model, model.GetName(), "L")
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
####### Apply Transfer Factor #############
###########################################

for iBin in range(gmets[0].GetNbinsX()+2):
    # print iBin, gmets[0].GetBinLowEdge(iBin)
    if (gmets[0].GetBinContent(iBin) < 0.):
        gmets[0].SetBinContent(iBin, 0.)

scanvas.Clear()
scanvas.legend.Clear()

scanvas.ylimits = (0.000005, 50000)
scanvas.SetLogy(True)

scanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

for iM, model in enumerate(models):
    gname = 'gmetScaled'+model.GetName()
    gmet = gmets[0].Clone(gname)
    gmet.Multiply(model)

    scanvas.legend.add(gname, title = model.GetName(), lcolor = colors[iM], lwidth = 1, mcolor = colors[iM], mstyle = 8, msize = 0.8)

    scanvas.legend.apply(gname, gmet)

    scanvas.addHistogram(gmet, drawOpt = 'EP')

    outputFile.cd()
    gmet.Write()

    print '%s predicts %.4f events for MET > 170' % (model.GetName(), gmet.Integral(14, gmet.GetNbinsX()+1))

scanvas.printWeb('monophoton/gjetsTFactor', 'gjetsPrediction')

print '\n\n\n\n'

###########################################
####### Fit MET Spectrum   ################
###########################################

gfits = []

pepe = r.TF1("Rayleigh1", "[0] * x * TMath::Exp( -x**2 /([1] + [2]*x)**2)", 0., 600.)
pepe.SetParameters(1., 10., 10.)
pepe.SetParLimits(1, 0.1, 150.)
pepe.SetParLimits(2, 0.001, 10.)

pepe2 = r.TF1("Rayleigh1Denom", "[3] * x * TMath::Exp( -x**2 /([4] + [5]*x)**2)", 0., 600.)
pepe.SetParameters(0., 0., 0., 1., 10., 10.)
pepe.SetParLimits(4, 0.1, 300.)
pepe.SetParLimits(5, 0.001, 10.)

pepeplus = r.TF1("Rayleigh2", "[0] * x * TMath::Exp( -x**2 /([1] + [2]*x + [3]*x**2))", 0., 600.)
pepeplus.SetParameters(1., 10., 10., 0.1)
pepeplus.SetParLimits(1, 0.1, 2000.)
pepeplus.SetParLimits(2, 0.0001, 100.)
pepeplus.SetParLimits(3, 0.0001, 1.)

pepeplus2 = r.TF1("Rayleigh2Denom", "[4] * x * TMath::Exp( -x**2 /([5] + [6]*x + [7]*x**2))", 0., 600.)
pepeplus.SetParameters(1., 10., 10., 0.1)
pepeplus.SetParLimits(5, 0.1, 1000.)
pepeplus.SetParLimits(6, 0.001, 100.)
pepeplus.SetParLimits(7, 0.0001, 1.)

# models = [ (pepe2, pepe), (pepeplus2, pepeplus) ] 
models = [ pepe, pepeplus ] 
colors = [ r.kOrange-3, r.kGreen-3 ] 

for iG, gmet in enumerate(gmets):
    gfits.append([])
    for iM, model in enumerate(models):
        gfit = model.Clone(gmet.GetName()+model.GetName())
        gmet.Fit(gfit, "M WL B ", "goff", 0., fitMax)

        gfit.SetLineColor(colors[iM])

        outputFile.cd()
        gfit.Write()
        gfits[iG].append(gfit)

    tcanvas.Clear()
    
    gmet.SetMinimum(0.001)
    gmet.SetMarkerColor(1)
    gmet.SetMarkerStyle(8)
    gmet.SetMarkerSize(1.2)
    gmet.GetListOfFunctions().RemoveLast()
    gmet.Draw("PE")
    for gfit in gfits[iG]:
        gfit.Draw("same")

    leg = r.TLegend(0.6, 0.7, 0.9, 0.9)
    leg.SetFillColor(r.kWhite)
    leg.SetTextSize(0.03)
    leg.AddEntry(gmet, "Measured", "P")
    for iM, gfit in enumerate(gfits[iG]):
        leg.AddEntry(gfit, models[iM].GetName(), "L")
    leg.Draw("same")

    tcanvas.SetLogy(False)

    outName = '/home/ballen/public_html/cmsplots/monophoton/gjetsTFactor/'+gmet.GetName()+'Fit'
    tcanvas.SaveAs(outName+'.pdf')
    tcanvas.SaveAs(outName+'.png')

    tcanvas.SetLogy(True)

    outName = outName+'Logy'
    tcanvas.SaveAs(outName+'.pdf')
    tcanvas.SaveAs(outName+'.png')

###########################################
####### Get TF from Fits   ################
###########################################

tcanvas.Clear()
scanvas.SetLogy(True)

leg = r.TLegend(0.6, 0.7, 0.9, 0.9)
leg.SetFillColor(r.kWhite)
leg.SetTextSize(0.03)

tfacts = []



for iM, model in enumerate(models):
    print '\n\n putting some space \n\n'
    tname = 'tfact'+model.GetName()
    # print tname
    #fstring = gfits[1][iM].GetName()+' / '+gfits[0][iM].GetName()

    print gfits[0][iM].GetName()
    print gfits[0][iM].GetParameter(0), gfits[0][iM].GetParameter(1), gfits[0][iM].GetParameter(2), gfits[0][iM].GetParameter(3)

    print gfits[1][iM].GetName()
    print gfits[1][iM].GetParameter(0), gfits[1][iM].GetParameter(1), gfits[1][iM].GetParameter(2), gfits[1][iM].GetParameter(3)

    fstring = '('+str(gfits[1][iM].GetExpFormula()).replace('*x*', '*')+') / ('+str(gfits[0][iM].GetExpFormula()).replace('[p','[q').replace('*x*', '*')+')'
    print fstring
    tfact = r.TF1(tname, str(fstring), 0., 600.)
    # print tfact

    print tfact.GetExpFormula()

    tfact.SetLineColor(colors[iM])
    
    tfact.GetXaxis().SetTitle("E_{T}^{miss} (GeV)")
    
    tfact.SetMinimum(0.0001)
    

    numPar = gfits[1][iM].GetNpar()
    denPar = gfits[0][iM].GetNpar()
    for iP in range(0, numPar+denPar):
        if iP < numPar:
            parVal = gfits[1][iM].GetParameter(iP)
            parErr = gfits[1][iM].GetParError(iP)
        else:
            parVal = gfits[0][iM].GetParameter(iP - numPar)
            parErr = gfits[0][iM].GetParError(iP - numPar)
        
        # print iP, parVal, parErr

        tfact.SetParameter(iP, parVal)
        tfact.SetParError(iP, parErr)
        # print iP, tfact.GetParameter(iP), tfact.GetParError(iP)

    # print fstring
    print tfact.GetParameter(0), tfact.GetParameter(1), tfact.GetParameter(2), tfact.GetParameter(3), tfact.GetParameter(4), tfact.GetParameter(5), tfact.GetParameter(6), tfact.GetParameter(7)

    outputFile.cd()
    tfact.Write()
    tfacts.append(tfact)

    tcanvas.cd()
    if iM:
        tfact.Draw("L same")
    else:
        tfact.Draw("L")

    leg.AddEntry(tfact, model.GetName(), "L")

leg.Draw("same")

outName = '/home/ballen/public_html/cmsplots/monophoton/gjetsTFactor/tfactFitMet'
tcanvas.SaveAs(outName+'.pdf')
tcanvas.SaveAs(outName+'.png') 

###########################################
####### Apply new TFs      ################
###########################################

print "\nis it here\n"

scanvas.Clear()
scanvas.legend.Clear()

scanvas.ylimits = (0.00000000005, 50000)
scanvas.SetLogy(True)

scanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

for iF, tfact in enumerate(tfacts):
    gname = 'gmetScaledFit'+tfact.GetName().strip('tfact')
    gmet = gmets[0].Clone(gname)
    gmet.GetListOfFunctions().RemoveLast()
    gmet.Multiply(tfact)

    scanvas.legend.add(gname, title = tfact.GetName().strip('tfact'), lcolor = colors[iF], lwidth = 1, mcolor = colors[iF], mstyle = 8, msize = 0.8)

    scanvas.legend.apply(gname, gmet)

    scanvas.addHistogram(gmet, drawOpt = 'EP')

    outputFile.cd()
    gmet.Write()

    print '%s predicts %.4f events for MET > 170' % (tfact.GetName(), gmet.Integral(14, gmet.GetNbinsX()+1))

scanvas.printWeb('monophoton/gjetsTFactor', 'gjetsFitPrediction')

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
