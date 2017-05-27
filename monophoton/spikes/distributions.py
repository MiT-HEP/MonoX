import sys
import array
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import WEBDIR, SimpleCanvas
from datasets import allsamples

lumi = sum(s.lumi for s in allsamples.getmany('sph-16*'))

canvas = SimpleCanvas(lumi = lumi)

finePtBinning = array.array('d', [175. + 25 * x for x in range(17)] + [600., 700., 800., 1000.])
combinedFitPtBinning = array.array('d', [175.0, 200., 250., 300., 400., 600., 1000.0])
fitTemplateBinning = array.array('d', [-1 * (bin - 175.) for bin in reversed(combinedFitPtBinning)] + [bin - 175. for bin in combinedFitPtBinning[1:]])
fitTemplateExpression = '( ( (cluster.rawPt - 175.) * (cluster.rawPt < 1000.) + 800. * (cluster.rawPt > 1000.) ) * TMath::Sign(1, TMath::Abs(TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(cluster.phi + 0.005) - 1.570796)) - 1.570796) - 0.5) )'
baseline = 'cluster.isEB && cluster.rawPt > 175 && cluster.trackIso < 10. && cluster.mipEnergy < 4.9 && TMath::Abs(cluster.eta) > 0.05 && cluster.sieie < 0.0102 && met.met > 170.'
offtime = 'cluster.time > -15. && cluster.time < -10.'

import ROOT

outputFile = ROOT.TFile.Open(config.histDir + '/spikes.root', 'recreate')

spikeTree = ROOT.TChain('events')
spikeTree.Add('/data/t3home000/yiiyama/simpletree/uncleanedSkimmed/sph-16*_highmet.root')

# pt fine

outputFile.cd()
uncleanedPt = ROOT.TH1D('uncleanedPt', ';E_{T}^{SC} (GeV)', len(finePtBinning) - 1, finePtBinning)
spikeTree.Draw('cluster.rawPt>>uncleanedPt', 'cluster.time > -15. && cluster.time < -10. && cluster.sieie < 0.0102 && cluster.sieie > 0.001 && cluster.sipip > 0.001')
uncleanedPt.Write()

uncleanedPt.SetLineColor(ROOT.kBlack)

uncleanedPt.Scale(1., 'width')

canvas.addHistogram(uncleanedPt)

canvas.printWeb('spike', 'uncleanedPtFine')
canvas.Clear()

sys.exit(0)

# time

uncleanedTime = ROOT.TH1D('uncleanedTime', ';seed time (ns)', 100, -25., 25.)
spikeTree.Draw('cluster.time>>uncleanedTime', baseline, 'goff')

uncleanedTime.SetLineColor(ROOT.kBlack)

canvas.addHistogram(uncleanedTime)

canvas.printWeb('spike', 'uncleanedTime', logy = False)
canvas.Clear()

# shower

ROOT.gStyle.SetNdivisions(210, 'X')

uncleanedShower = ROOT.TH1D('uncleanedShower', ';#sigma_{i#etai#eta}', 102, 0., 0.0102)
spikeTree.Draw('cluster.sieie>>uncleanedShower', baseline, 'goff')

uncleanedShower.SetLineColor(ROOT.kBlack)

canvas.addHistogram(uncleanedShower)

canvas.printWeb('spike', 'uncleanedShower', logy = False)
canvas.Clear()

# time-shower

uncleanedCorr = ROOT.TH2D('uncleanedCorr', ';#sigma_{i#etai#eta};seed time (ns)', 102, 0., 0.0102, 100, -25., 25.)
spikeTree.Draw('cluster.time:cluster.sieie>>uncleanedCorr', baseline, 'goff')

c2 = ROOT.TCanvas('c2', 'c2', 600, 600)
c2.SetLeftMargin(0.15)
c2.SetRightMargin(0.05)

uncleanedCorr.Draw('COL')
c2.Print(WEBDIR + '/spike/uncleanedCorr.png')
c2.Print(WEBDIR + '/spike/uncleanedCorr.pdf')

# pt

outputFile.cd()
uncleanedPt = ROOT.TH1D('uncleanedPt', ';E_{T}^{SC} (GeV)', len(combinedFitPtBinning) - 1, combinedFitPtBinning)
spikeTree.Draw('cluster.rawPt>>uncleanedPt', 'cluster.time > -15. && cluster.time < -10. && cluster.sieie < 0.0102 && cluster.sieie > 0.001 && cluster.sipip > 0.001')
uncleanedPt.Write()

uncleanedPt.SetLineColor(ROOT.kBlack)

canvas.addHistogram(uncleanedPt)

canvas.printWeb('spike', 'uncleanedPt')
canvas.Clear()

# fitTemplate

outputFile.cd()
fitTemplate = ROOT.TH1D('fitTemplate', ';E_{T}^{SC} (GeV)', len(fitTemplateBinning) - 1, fitTemplateBinning)
spikeTree.Draw(fitTemplateExpression + '>>fitTemplate', 'cluster.time > -15. && cluster.time < -10. && cluster.sieie < 0.0102 && cluster.sieie > 0.001 && cluster.sipip > 0.001')
fitTemplate.Write()

fitTemplate.SetLineColor(ROOT.kBlack)

canvas.addHistogram(fitTemplate)

canvas.printWeb('spike', 'fitTemplate')
canvas.Clear()
