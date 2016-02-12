import sys
import os
import array
import math
import ROOT

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
from plotstyle import SimpleCanvas
import config

canvas = SimpleCanvas(lumi = 2239.9)

binning = array.array('d', [175., 180., 185., 190., 200., 210., 230., 250., 300., 350., 400.])

gtree = ROOT.TChain('events')
gtree.Add(config.skimDir + '/sph-d*_monoph.root')
htree = ROOT.TChain('events')
htree.Add(config.skimDir + '/sph-d*_emplusjet.root')

inputFile = ROOT.TFile.Open('../data/impurity.root')
impurityHist = inputFile.Get("ChIso50to80imp")

outputFile = ROOT.TFile.Open('../data/hadronTFactor.root', 'recreate')
gpt = ROOT.TH1D('gpt', ';p_{T} (GeV)', len(binning) - 1, binning)
gpt.Sumw2()
hpt = ROOT.TH1D('hpt', ';p_{T} (GeV)', len(binning) - 1, binning)
hpt.Sumw2()

gtree.Draw('photons.pt[0]>>gpt', 'Sum$(jets.pt > 100. && TMath::Abs(jets.eta) < 2.5) != 0 && photons.size == 1 && t1Met.met < 60.', 'goff')
gpt.Scale(1., 'width')
fpt = gpt.Clone('fpt')
for iX in range(1, fpt.GetNbinsX() + 1):
    cent = fpt.GetXaxis().GetBinCenter(iX)
    bin = impurityHist.FindBin(cent)
    imp = impurityHist.GetBinContent(bin) / 100.
    err = impurityHist.GetBinError(bin) / 100.

    print "Bin center: %.2f, imp: %.2f,  err: %.2f" % (cent, imp*100, err*100)

    cont = fpt.GetBinContent(iX) * imp 
    stat = fpt.GetBinError(iX) * imp 
    syst = fpt.GetBinContent(iX) * err
    fpt.SetBinContent(iX, cont)
    fpt.SetBinError(iX, math.sqrt(stat * stat + syst * syst))

htree.Draw('photons.pt[0]>>hpt', 't1Met.met < 60.', 'goff')
hpt.Scale(1., 'width')
tfact = fpt.Clone('tfact')
tfact.Divide(hpt)

outputFile.Write()

canvas.legend.add('gpt', title = '#gamma + jet', lcolor = ROOT.kBlack, lwidth = 2)
canvas.legend.add('fpt', title = '#gamma + jet #times impurity', lcolor = ROOT.kRed, lwidth = 2, lstyle = ROOT.kDashed)
canvas.legend.add('hpt', title = 'EMobject + jet', lcolor = ROOT.kBlue, lwidth = 2)
canvas.legend.setPosition(0.6, 0.7, 0.95, 0.9)

canvas.legend.apply('gpt', gpt)
canvas.legend.apply('fpt', fpt)
canvas.legend.apply('hpt', hpt)

canvas.addHistogram(gpt, drawOpt = 'HIST')
canvas.addHistogram(fpt, drawOpt = 'HIST')
canvas.addHistogram(hpt, drawOpt = 'HIST')

canvas.ylimits = (0.1, 2000.)

canvas.printWeb('hadronTFactor', 'photon')

canvas.Clear()
canvas.legend.Clear()

canvas.ylimits = (0., -1.)
canvas.SetLogy(False)

canvas.legend.add('tfact', title = 'Transfer factor', lcolor = ROOT.kBlack, lwidth = 1)

canvas.legend.apply('tfact', tfact)

canvas.addHistogram(tfact, drawOpt = 'EP')

canvas.printWeb('hadronTFactor', 'tfactor')
