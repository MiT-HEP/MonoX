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
ROOT.gROOT.LoadMacro('metTree.cc+')

lumi = allsamples['sph-d3'].lumi + allsamples['sph-d4'].lumi

canvas = RatioCanvas(cms = False)

# direct smear

outputFile = ROOT.TFile.Open(config.histDir + '/smearfit.root', 'recreate')

dsource = ROOT.TChain('events')
dsource.Add(config.skimDir + '/sph-d*_monoph.root')

bsource = ROOT.TChain('events')
bsource.Add(config.skimDir + '/sph-d*_hfake.root')
bsource.Add(config.skimDir + '/sph-d*_efake.root')

bmcsource = ROOT.TChain('events')
bmcsource.Add(config.skimDir + '/wg_monoph.root') # NLO sample to get around pT/ MET > 130 GeV cut on LO sample
bmcsource.Add(config.skimDir + '/wlnu-*_monoph.root')
bmcsource.Add(config.skimDir + '/ttg_monoph.root')
bmcsource.Add(config.skimDir + '/zg_monoph.root')

znnsource = ROOT.TChain('events')
znnsource.Add(config.skimDir + '/zg_dimu.root')

mcsource = ROOT.TChain('events')
mcsource.Add(config.skimDir + '/gj-40_monoph.root')
mcsource.Add(config.skimDir + '/gj-100_monoph.root')
mcsource.Add(config.skimDir + '/gj-200_monoph.root')
mcsource.Add(config.skimDir + '/gj-400_monoph.root')
mcsource.Add(config.skimDir + '/gj-600_monoph.root')

binning = array.array('d', [4. * x for x in range(51)])
sel = '(photons.pt[0] > 175. && t1Met.minJetDPhi < 0.5 && t1Met.photonDPhi > 2.)'

dname = 'dmetLow'
dmet = ROOT.TH1D(dname, ';E_{T}^{miss} (GeV); Events / GeV', len(binning) - 1, binning)
dmet.Sumw2()
dsource.Draw('t1Met.met>>'+dname, sel, 'goff')

btree = ROOT.TTree('btree', 'met')
ROOT.metTree(bsource, btree, sel)
ROOT.metTree(bmcsource, btree, sel, lumi)
ROOT.metTree(znnsource, btree, sel, lumi * 6.122)

counter = ROOT.TH1D('counter', '', 1, 0., 1.)
btree.Draw('0.5>>counter', 'weight', 'goff')
nbkgval = counter.GetBinContent(1)

mctree = ROOT.TTree('mctree', 'met')
ROOT.metTree(mcsource, mctree, sel)

space = ROOT.RooWorkspace('space', 'space')

met = space.factory('met[0., 200.]')
met.setUnit('GeV')
met.setBins(50)

ddata = ROOT.RooDataHist('ddata', 'ddata', ROOT.RooArgList(met), dmet)

bpdf = ROOT.KeysShape('bpdf', 'bpdf', met, btree, 'weight', 0.5, 8)

print 'Constructing KeysShape from', mcsource.GetEntries(), 'events.'
mcname = 'mcmetLow'
mcpdf = ROOT.KeysShape('mcpdf', 'mcpdf', met, mctree, 'weight', 0.5, 8)
print 'Done.'

smear = space.factory('Landau::smear(met, mean[0., -1., 10.], sigmar[1., 0., 100.])')

gjets = ROOT.RooFFTConvPdf('gjets', 'gjets', met, mcpdf, smear)

ngjets = space.factory('ngjets[%f, 0., %f]' % (dmet.GetSumOfWeights(), dmet.GetSumOfWeights() * 1.5))
nbkg = space.factory('nbkg[%f]' % nbkgval)

model = ROOT.RooAddPdf('model', 'model', ROOT.RooArgList(gjets, bpdf), ROOT.RooArgList(ngjets, nbkg))

model.fitTo(ddata)

frame = met.frame()
ddata.plotOn(frame)
model.plotOn(frame)
model.plotOn(frame, ROOT.RooFit.Components('gjets'), ROOT.RooFit.LineColor(ROOT.kGreen), ROOT.RooFit.LineStyle(ROOT.kDashed))
mcpdf.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kRed), ROOT.RooFit.LineStyle(ROOT.kDotted))
frame.SetTitle('min#Delta#phi(j, E_{T}^{miss}) < 0.5')
#frame.GetXaxis().SetTitle('E_{T}^{miss} (GeV)')
frame.GetXaxis().SetTitle('')
frame.GetXaxis().SetTitleSize(0.)
frame.GetXaxis().SetLabelSize(0.)
frame.GetYaxis().SetLabelSize(0.)
frame.GetYaxis().SetTickSize(0.)

canvas.xtitle = 'E_{T}^{miss} (GeV)'
canvas.legend.add('data', title = 'Data', mstyle = 8, color = ROOT.kBlack, opt = 'LP')
canvas.legend.add('fit', title = 'Fit', color = ROOT.kBlue, lwidth = 2, opt = 'L')
canvas.legend.add('gjets', title = '#gamma+jets', color = ROOT.kGreen, lstyle = ROOT.kDashed, lwidth = 2, opt = 'L')
canvas.legend.add('mcpdf', title = '#gamma+jets raw', color = ROOT.kRed, lstyle = ROOT.kDotted, lwidth = 2, opt = 'L')

canvas.addHistogram(frame, clone = False, drawOpt = '')

canvas.Update()

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

    if x > 200.:
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

rframe = ROOT.TH1F('rframe', '', 1, 0., 200.)
rframe.GetYaxis().SetRangeUser(0., 2.)
rframe.Draw()

line = ROOT.TLine(0., 1., 200., 1.)
line.SetLineWidth(2)
line.SetLineColor(ROOT.kBlue)
line.Draw()

rraw.Draw('L')

rdata.Draw('EP')

canvas._needUpdate = False

canvas.printWeb('smearfit', 'direct')

outputFile.cd()
space.Write()
