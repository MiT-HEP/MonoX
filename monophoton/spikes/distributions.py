import sys
import array
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas
from datasets import allsamples

lumi = sum(s.lumi for s in allsamples.getmany('sph-16*'))

canvas = SimpleCanvas(lumi = lumi)

combinedFitPtBinning = array.array('d', [175.0, 200., 250., 300., 400., 600., 1000.0])
fitTemplateBinning = array.array('d', [-1 * (bin - 175.) for bin in reversed(combinedFitPtBinning)] + [bin - 175. for bin in combinedFitPtBinning[1:]])
fitTemplateExpression = '( ( (superClusters.rawPt[0] - 175.) * (superClusters.rawPt[0] < 1000.) + 800. * (superClusters.rawPt[0] > 1000.) ) * TMath::Sign(1, TMath::Abs(TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(superClusters.phi + 0.005) - 1.570796)) - 1.570796) - 0.5) )'

import ROOT

outputFile = ROOT.TFile.Open(config.histDir + '/spikes.root', 'recreate')

spikeTree = ROOT.TChain('events')
spikeTree.Add('/data/t3home000/yiiyama/simpletree/uncleanedSkimmed/sph-16*.root')

#uncleanedTime = ROOT.TH1D('uncleanedTime', ';seed time (ns)', 100, -25., 25.)
#spikeTree.Draw('superClusters.time>>uncleanedTime', 'superClusters.rawPt > 175 && superClusters.sieie < 0.0102')
#
#uncleanedTime.SetLineColor(ROOT.kBlack)
#
#canvas.addHistogram(uncleanedTime)
#
#canvas.printWeb('spike', 'uncleanedTime')
#canvas.Clear()

#ROOT.gStyle.SetNdivisions(210, 'X')
#
#uncleanedShower = ROOT.TH1D('uncleanedShower', ';#sigma_{i#etai#eta}', 102, 0., 0.0102)
#spikeTree.Draw('superClusters.sieie>>uncleanedShower', 'superClusters.rawPt > 175 && superClusters.time > -15. && superClusters.time < -10.')
#
#uncleanedShower.SetLineColor(ROOT.kBlack)
#
#canvas.addHistogram(uncleanedShower)
#
#canvas.printWeb('spike', 'uncleanedShower')

outputFile.cd()
uncleanedPt = ROOT.TH1D('uncleanedPt', ';E_{T}^{SC} (GeV)', len(combinedFitPtBinning) - 1, combinedFitPtBinning)
spikeTree.Draw('superClusters.rawPt>>uncleanedPt', 'superClusters.time > -15. && superClusters.time < -10. && superClusters.sieie < 0.0102 && superClusters.sieie > 0.001')
uncleanedPt.Write()

uncleanedPt.SetLineColor(ROOT.kBlack)

canvas.addHistogram(uncleanedPt)

canvas.printWeb('spike', 'uncleanedPt')
canvas.Clear()

outputFile.cd()
fitTemplate = ROOT.TH1D('fitTemplate', ';E_{T}^{SC} (GeV)', len(fitTemplateBinning) - 1, fitTemplateBinning)
spikeTree.Draw(fitTemplateExpression + '>>fitTemplate', 'superClusters.time > -15. && superClusters.time < -10. && superClusters.sieie < 0.0102 && superClusters.sieie > 0.001')
fitTemplate.Write()

fitTemplate.SetLineColor(ROOT.kBlack)

canvas.addHistogram(fitTemplate)

canvas.printWeb('spike', 'fitTemplate')
canvas.Clear()
