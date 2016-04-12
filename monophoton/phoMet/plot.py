#!/usr/bin/env python
import sys
import os
import math
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import RatioCanvas
from datasets import allsamples

import ROOT as r
r.gROOT.SetBatch(True)

dataTree = r.TChain('skim')
dataTree.Add('/scratch5/ballen/hist/monophoton/phoMet/skim_sel-*.root')

mcTree = r.TChain('skim')
mcTree.Add('/scratch5/ballen/hist/monophoton/phoMet/skim_dy-50-*.root')

lumi = allsamples['sel-d3'].lumi + allsamples['sel-d4'].lumi
canvas = RatioCanvas(lumi = lumi)
canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
canvas.legend.add('data', title = 'Data', lcolor = r.kBlack, lwidth = 2)
canvas.legend.add('mc', title = 'MC', lcolor = r.kRed, lwidth = 2)

njetsCut = 'njets < 2'
recoilCut = 'recoil.pt > 170.'
tagEtaCut = 'TMath::Abs(tag.eta) < 0.2'

cuts = [ recoilCut ]

varString = '(probe.ptReco / probe.ptCorr)'


probeEtaCuts = [ ('TMath::Abs(probe.eta) < 0.8', 'low'), ('TMath::Abs(probe.eta > 0.8)', 'high') ] 

for cut, label in probeEtaCuts:
    allCuts = cuts + [cut]
    cutString = ' && '.join(['(%s)' % c for c in allCuts])
    print cutString

    dataHist = r.TH1D('dataHist_'+label, '', 20, 0., 2.)
    dataHist.Sumw2()
    mcHist = r.TH1D('mcHist_'+label, '', 20, 0., 2.)
    mcHist.Sumw2()


    dataTree.Draw(varString+'>>dataHist_'+label, 'weight * ('+cutString+')', 'goff')
    mcTree.Draw(varString+'>>mcHist_'+label, str(lumi)+' * weight * ('+cutString+')', 'goff')

    canvas.Clear()

    canvas.legend.apply('data', dataHist)
    canvas.legend.apply('mc', mcHist)

    canvas.addHistogram(dataHist, drawOpt = 'L')
    canvas.addHistogram(mcHist, drawOpt = 'L')

    canvas.ylimits = (0.001, -1.)

    canvas.printWeb('monophoton/phoMet', 'ratio_'+label, logy = False)
