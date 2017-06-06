"""
Obtain the score distribution of PV of leptons + isolated EM-jet events.
"""

import os
import sys
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas, RatioCanvas
import config

import ROOT

canvas = SimpleCanvas()
canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
canvas.legend.add('low', '175 < p_{T} < 200 GeV', lcolor = ROOT.kRed, lwidth = 2, opt = 'L')
canvas.legend.add('med', '200 < p_{T} < 250 GeV', lcolor = ROOT.kBlue, lwidth = 2, opt = 'L')
canvas.legend.add('high', 'p_{T} > 250 GeV', lcolor = ROOT.kGreen, lwidth = 2, opt = 'L')

tree = ROOT.TChain('events')
tree.Add(config.skimDir + '/sph-16*_dimuAllPhoton.root')
tree.Add(config.skimDir + '/sph-16*_dielAllPhoton.root')
tree.Add(config.skimDir + '/sph-16*_monomuAllPhoton.root')

outputFile = ROOT.TFile.Open(basedir + '/data/vertex_scores.root', 'recreate')

low = ROOT.TH1D('low', ';ln(score / GeV^{2})', 20, 0., 15.)
med = ROOT.TH1D('med', ';ln(score / GeV^{2})', 20, 0., 15.)
high = ROOT.TH1D('high', ';ln(score / GeV^{2})', 20, 0., 15.)

tree.Draw('TMath::Log(lvertex.score)>>low', 'Sum$(photons.sieie > 0.012 && photons.chIso < 1. && photons.scRawPt < 200.) != 0')
tree.Draw('TMath::Log(lvertex.score)>>med', 'Sum$(photons.sieie > 0.012 && photons.chIso < 1. && photons.scRawPt > 200. && photons.scRawPt < 250.) != 0')
tree.Draw('TMath::Log(lvertex.score)>>high', 'Sum$(photons.sieie > 0.012 && photons.chIso < 1. && photons.scRawPt > 250.) != 0')

low.Scale(1. / low.GetSumOfWeights())
med.Scale(1. / med.GetSumOfWeights())
high.Scale(1. / high.GetSumOfWeights())

outputFile.cd()
outputFile.Write()

canvas.addHistogram(low)
canvas.addHistogram(med)
canvas.addHistogram(high)

canvas.applyStyles()

canvas.printWeb('chiso', 'scores_by_pt', logy = False)
