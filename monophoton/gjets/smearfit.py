import sys
import os
import array
import math
import time
import ROOT
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
from plotstyle import RatioCanvas
import config
from datasets import allsamples

ROOT.gROOT.SetBatch(True)
ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load('/home/yiiyama/cms/studies/RooFit/libCommonRooFit.so')

photonData = ['sph-16h'] # ['sph-16b-r', 'sph-16c-r', 'sph-16d-r', 'sph-16e-r', 'sph-16f-r', 'sph-16g-r', 'sph-16h'] # ['sph-16c-r'] #

lumi = 0.
for sname in photonData:
    lumi += allsamples[sname].lumi

canvas = RatioCanvas(lumi = lumi)
canvas.legend.add('data', title = 'Data', mstyle = 8, color = ROOT.kBlack, opt = 'LP')
canvas.legend.add('fit', title = 'Fit', color = ROOT.kBlue, lwidth = 2, opt = 'L')
canvas.legend.add('gjets', title = '#gamma+jets', color = ROOT.kGreen, lstyle = ROOT.kDashed, lwidth = 2, opt = 'L')
canvas.legend.add('mcpdf', title = '#gamma+jets raw', color = ROOT.kRed, lstyle = ROOT.kDotted, lwidth = 2, opt = 'L')

# direct smear

inputFile = ROOT.TFile.Open(config.histDir + '/gjets/fitTemplates.root_16hOnly')
outputFile = ROOT.TFile.Open(config.histDir + '/gjets/smearfit.root', 'recreate')

space = ROOT.RooWorkspace('space', 'space')

mcpdf = inputFile.Get('mcpdf')
bpdf = inputFile.Get('bpdf')
dmet = inputFile.Get('dmet')
ddata = inputFile.Get('ddata')
counter = inputFile.Get('counter')

nbkgval = counter.GetBinContent(1)

getattr(space, 'import')(mcpdf)
getattr(space, 'import')(bpdf)
getattr(space, 'import')(dmet)
getattr(space, 'import')(ddata)

met = space.factory('met[0., 400.]')
met.setUnit('GeV')
met.setBins(75)

sigmar = space.factory('sigmar[5.0, 0.1, 10.0]')
alpha = space.factory('alpha[0.1, 0.01, 0.2]')
beta = space.factory('beta[0.0, 0., 0.2]')
mean = space.factory('mean[0., 0., 50.]')

constant = space.factory('expr::constant("@0", {{sigmar}})')
linear = space.factory('expr::linear("@0*(1. + @1*@2)", {{sigmar, alpha, met}})')
quadratic = space.factory('expr::quadratic("@0*(1. + @1*@3 + @2*@3*@3)", {{sigmar, alpha, beta, met}})')

sfuncs = { 
    # 'landau' : space.factory('Landau::landau(met, mean, constant)'),
    # 'gaussConst' : space.factory('Gaussian::gaussConst(met, mean, constant)'),
    # 'gaussLin' : space.factory('Gaussian::gaussLin(met, mean, linear)'),
    # 'gaussQuad' : space.factory('Gaussian::gaussQuad(met, mean, quadratic)'),
    # 'rayConst' : space.factory("EXPR::rayConst('((@0 / @1**2) * TMath::Exp(-1. * (@0 / @1)**2))', met, constant)"),
    'rayLin' : space.factory("EXPR::rayLin('((@0 / (@1 + @2*@0)**2) * TMath::Exp(-1. * (@0 / (@1 + @2*@0))**2))', met, sigmar, alpha)"),
    # 'rayQuad' : space.factory("EXPR::rayQuad('((@0 / (@1*(1. + @2*@0 + @3*@0**2))**2) * TMath::Exp(-1. * (@0 / (@1*(1. + @2*@0 + @3*@0**2)))**2))', met, sigmar, alpha, beta)")
    # 'rayMeanConst' : space.factory("EXPR::rayMeanConst('@0*TMath::Exp(-1. * ((@0 - @1) / @2)**2)', met, mean, constant)"),
    # 'rayMeanLin' : space.factory("EXPR::rayMeanLin('@0*TMath::Exp(-1. * ((@0 - @1) / (@2*(1. + @3*@0))**2))', met, mean, sigmar, alpha)"),
    # 'rayMeanQuad' : space.factory("EXPR::rayMeanQuad('@0*TMath::Exp(-1. * ((@0 - @1) / (@2*(1. + @3*@0 + @4*@0**2))**2))', met, mean, sigmar, alpha, beta)")
           }

for sname in sorted(sfuncs.keys()):
    mean.setVal(0.)
    sigmar.setVal(5.0)
    alpha.setVal(0.1)
    sigmar.setVal(0.)

    print 'make smear'
    smear = sfuncs[sname]
    print 'made smear'

    start = time.time()
    print 'starting FFTconv'
    gjets = ROOT.RooFFTConvPdf('gjets', 'gjets', met, mcpdf, smear)
    elapsed = time.time() - start
    print 'finished. took %i seconds' % elapsed

    ngjets = space.factory('ngjets[%f, 0., %f]' % (dmet.GetSumOfWeights(), dmet.GetSumOfWeights() * 1.5))
    nbkg = space.factory('nbkg[%f]' % nbkgval)

    model = ROOT.RooAddPdf('model', 'model', ROOT.RooArgList(gjets, bpdf), ROOT.RooArgList(ngjets, nbkg))

    start = time.time()
    print 'starting fit'
    model.fitTo(ddata)
    elapsed = time.time() - start
    print 'finished. took %i seconds' % elapsed

    paramsOut = file('../data/gjSmearParams_' + sname + '.txt', 'w')
    paramsOut.write('%10s %20.16f %20.16f \n' % ('mean', mean.getValV(), mean.getError()))
    paramsOut.write('%10s %20.16f %20.16f \n' % ('sigmar', sigmar.getValV(), sigmar.getError()))
    paramsOut.write('%10s %20.16f %20.16f \n' % ('alpha', alpha.getValV(), alpha.getError()))
    paramsOut.write('%10s %20.16f %20.16f \n' % ('beta', beta.getValV(), beta.getError()))
    paramsOut.close()

    frame = met.frame()
    ddata.plotOn(frame)
    model.plotOn(frame)
    model.plotOn(frame, ROOT.RooFit.Components('gjets'), ROOT.RooFit.LineColor(ROOT.kGreen), ROOT.RooFit.LineStyle(ROOT.kDashed))
    mcpdf.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.LineStyle(ROOT.kDotted))
    # frame.SetTitle('min#Delta#phi(j, E_{T}^{miss}) < 0.5')
    #frame.GetXaxis().SetTitle('E_{T}^{miss} (GeV)')
    frame.GetXaxis().SetTitle('')
    frame.GetXaxis().SetTitleSize(0.)
    frame.GetXaxis().SetLabelSize(0.)
    frame.GetYaxis().SetLabelSize(0.)
    frame.GetYaxis().SetTickSize(0.)

    canvas.Clear()
    canvas.xtitle = 'E_{T}^{miss} (GeV)'
    canvas.ylimits = (0.1, 1000000.)

    canvas.addHistogram(frame, clone = True, drawOpt = '')

    canvas.Update(rList = [])

    fitcurve = frame.findObject('model_Norm[met]')
    rawcurve = frame.findObject('mcpdf_Norm[met]')

    rdata = ROOT.TGraphErrors(dmet.GetNbinsX())
    for iP in range(rdata.GetN()):
        x = dmet.GetXaxis().GetBinCenter(iP + 1)
        norm = fitcurve.interpolate(x)
        rdata.SetPoint(iP, x, dmet.GetBinContent(iP + 1) / norm)
        rdata.SetPointError(iP, 0., dmet.GetBinError(iP + 1) / norm)

    rdata.SetMarkerStyle(8)
    rdata.SetMarkerColor(ROOT.kBlack)
    rdata.SetLineColor(ROOT.kBlack)

    rraw = ROOT.TGraph(rawcurve.GetN())
    pre = -1
    last = -1.
    for iP in range(rraw.GetN()):
        x = rawcurve.GetX()[iP]
        if x < 0.:
            pre = iP
            continue

        if x > 400.:
            rraw.SetPoint(iP, x, last)
            continue

        last = rawcurve.interpolate(x) / fitcurve.interpolate(x)
        rraw.SetPoint(iP, x, last)

    iP = 0
    while iP <= pre:
        rraw.SetPoint(iP, rawcurve.GetX()[iP], rraw.GetY()[pre + 1])
        iP += 1

    rraw.SetLineWidth(2)
    rraw.SetLineColor(ROOT.kRed)
    rraw.SetLineStyle(ROOT.kDotted)

    canvas.ratioPad.cd()

    rframe = ROOT.TH1F('rframe', '', 1, 0., 400.)
    rframe.GetYaxis().SetRangeUser(0., 2.)
    rframe.Draw()

    line = ROOT.TLine(0., 1., 400., 1.)
    line.SetLineWidth(2)
    line.SetLineColor(ROOT.kBlue)
    line.Draw()

    rraw.Draw('L')

    rdata.Draw('EP')

    canvas._needUpdate = False

    canvas.printWeb('monophoton/smearfit', sname)
###

outputFile.cd()
space.Write()
outputFile.Close()

print 'done'
