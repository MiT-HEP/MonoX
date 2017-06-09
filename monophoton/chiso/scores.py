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

chIsoCut = 1.163

tree = ROOT.TChain('events')
tree.Add(config.skimDir + '/sph-16*_dimuAllPhoton.root')
tree.Add(config.skimDir + '/sph-16*_dielAllPhoton.root')
tree.Add(config.skimDir + '/sph-16*_monomuAllPhoton.root')

outputFile = ROOT.TFile.Open(basedir + '/data/vertex_scores.root', 'recreate')

iso = ROOT.TH2D('iso', ';p_{T}^{jet} (GeV);ln(score / GeV^{2});', 3, array.array('d', [175., 200., 250., 6500.]), 20, 0., 15.)
noIso = ROOT.TH2D('noIso', ';p_{T}^{jet} (GeV);ln(score / GeV^{2});', 3, array.array('d', [175., 200., 250., 6500.]), 20, 0., 15.)

tree.Draw('TMath::Log(lvertex.score):photons.scRawPt>>iso', 'photons.sieie > 0.012 && photons.chIso < %f' % chIsoCut, 'goff')
tree.Draw('TMath::Log(lvertex.score):photons.scRawPt>>noIso', 'photons.sieie > 0.012', 'goff')

for hist in [iso, noIso]:
    for iX in range(1, hist.GetNbinsX() + 1):
        sliceTotal = 0.
        for iY in range(1, hist.GetNbinsY() + 1):
            sliceTotal += hist.GetBinContent(iX, iY)
    
        for iY in range(1, hist.GetNbinsY() + 1):
            hist.SetBinContent(iX, iY, hist.GetBinContent(iX, iY) / sliceTotal)


outputFile.cd()
outputFile.Write()

#canvas = SimpleCanvas()
#canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
#canvas.legend.add('low', '175 < p_{T} < 200 GeV', lcolor = ROOT.kRed, lwidth = 2, opt = 'L')
#canvas.legend.add('med', '200 < p_{T} < 250 GeV', lcolor = ROOT.kBlue, lwidth = 2, opt = 'L')
#canvas.legend.add('high', 'p_{T} > 250 GeV', lcolor = ROOT.kGreen, lwidth = 2, opt = 'L')

#canvas.addHistogram(low)
#canvas.addHistogram(med)
#canvas.addHistogram(high)
#
#canvas.applyStyles()
#
#canvas.printWeb('chiso', 'scores_by_pt', logy = False)
