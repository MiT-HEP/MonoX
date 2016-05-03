#!/usr/bin/env python
import sys
import os
import math
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import DataMCCanvas
from datasets import allsamples

import ROOT as r
r.gROOT.SetBatch(True)

dataTree = r.TChain('skim')
dataTree.Add('/scratch5/ballen/hist/monophoton/phoMet/phi_sph-*.root')

samples = [ # ('dipho', r.TColor.GetColor(0x99, 0xee, 0xff)), 
            ('gj', r.TColor.GetColor(0xff, 0xaa, 0xcc))
            ]

mcTrees = []
for sample, color in samples:
    mcTree = r.TChain('skim')
    mcTree.Add('/scratch5/ballen/hist/monophoton/phoMet/phi_'+sample+'*.root')
    mcTrees.append( (sample, color, mcTree) )

lumi = allsamples['sph-d3'].lumi + allsamples['sph-d4'].lumi
canvas = DataMCCanvas(lumi = lumi)

probeEtaCuts = [ ('TMath::Abs(probe.eta) < 0.8', 'low'), ('TMath::Abs(probe.eta > 0.8)', 'high') ] 
recoilCuts = [ ('recoil.pt > %i.' % pt, 'recoil'+str(pt)) for pt in [170, 200, 250, 300, 400] ]

njetsCut = 'njets < 2'
tagEtaCut = 'TMath::Abs(tag.eta) < 0.2'

dPhiCut = 'TMath::Abs(TVector2::Phi_mpi_pi(tag.phi - probe.phi)) > 3.'
probeJetCut = '!probe.isPhoton'
ratioCut = ' (tag.pt / probe.pt) < 0.5'

cuts = [ dPhiCut, probeJetCut, ratioCut]

varString = 't1Met.met / (probe.pt - tag.pt)' # ('(tag.pt / probe.pt)', 
label = 'metPtDiff'

"""
for recoilCut in recoilCuts:
    allCuts = cuts + [recoilCut[0]]
    for probeEtaCut in probeEtaCuts:
        finalCuts = allCuts + [probeEtaCut[0]]
"""

cutString = ' && '.join(['(%s)' % c for c in cuts])
print cutString

# label = recoilCut[1]+'_'+probeEtaCut[1]


canvas.Clear()
canvas.legend.Clear()
canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

dataName = 'dataHist_'+label
dataHist = r.TH1D(dataName, '', 20, 0., 2.)
# dataHist = r.TH1D(dataName, '', 20, 0., 500.)
dataHist.Sumw2()
dataTree.Draw(varString+'>>'+dataName, 'weight * ('+cutString+')', 'goff')
canvas.addObs(dataHist, title = 'Data')

for sample, color, mcTree in mcTrees:
    mcName = sample+'_'+label
    mcHist = r.TH1D(mcName, '', 20, 0., 2.)
    # mcHist = r.TH1D(mcName, '', 20, 0., 500.)
    mcHist.Sumw2()
    mcTree.Draw(varString+'>>'+mcName, str(lumi)+' * weight * ('+cutString+')', 'goff')

    canvas.addStacked(mcHist, title = sample, color = color)

canvas.ylimits = (0.001, -1.)

canvas.printWeb('monophoton/phoMet', 'ratio_'+label, logy = True)
