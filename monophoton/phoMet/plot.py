#!/usr/bin/env python
import sys
import os
import math
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import RatioCanvas, DataMCCanvas
from datasets import allsamples

import ROOT as r
r.gROOT.SetBatch(True)

dataTree = r.TChain('skim')
dataTree.Add('/scratch5/ballen/hist/monophoton/phoMet/skim_sel-*.root')

dyTree = r.TChain('skim')
dyTree.Add('/scratch5/ballen/hist/monophoton/phoMet/skim_dy-50-*.root')
wlnuTree = r.TChain('skim')
wlnuTree.Add('/scratch5/ballen/hist/monophoton/phoMet/skim_wlnu-*.root')

samples = [ ('zllg', r.TColor.GetColor(0xff, 0x99, 0x33)), 
            ('ttg', r.TColor.GetColor(0xbb, 0xaa, 0xff)), 
            ('wlnu', r.TColor.GetColor(0xff, 0xee, 0x99)), 
            ('wg', r.TColor.GetColor(0x99, 0xee, 0xff)), 
            ('tt', r.TColor.GetColor(0xff, 0xaa, 0xcc)),
            ('dy-50', r.TColor.GetColor(0x99, 0xff, 0xaa)) 
            ]

mcTrees = []
for sample, color in samples:
    mcTree = r.TChain('skim')
    mcTree.Add('/scratch5/ballen/hist/monophoton/phoMet/skim_'+sample+'*.root')
    mcTrees.append( (sample, color, mcTree) )

lumi = allsamples['sel-d3'].lumi + allsamples['sel-d4'].lumi
canvas = DataMCCanvas(lumi = lumi)

# canvas = RatioCanvas(lumi = lumi)
# canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
# canvas.legend.add('data', title = 'Data', lcolor = r.kBlack, lwidth = 2)
# canvas.legend.add('mc', title = 'MC', mcolor = r.kRed, lcolor = r.kRed, lwidth = 2)

varStrings = '(probe.ptReco / probe.ptCorr)'

probeEtaCuts = [ ('TMath::Abs(probe.eta) < 0.8', 'low'), ('TMath::Abs(probe.eta > 0.8)', 'high') ] 
recoilCuts = [ ('recoil.pt > %i.' % pt, 'recoil'+str(pt)) for pt in [170, 200, 250, 300, 400] ]

njetsCut = 'njets < 2'
tagEtaCut = 'TMath::Abs(tag.eta) < 0.2'

cuts = [ ]

for recoilCut in recoilCuts:
    allCuts = cuts + [recoilCut[0]]
    for probeEtaCut in probeEtaCuts:
        finalCuts = allCuts + [probeEtaCut[0]]
        cutString = ' && '.join(['(%s)' % c for c in finalCuts])
        print cutString

        label = recoilCut[1]+'_'+probeEtaCut[1]

        canvas.Clear()
        canvas.legend.Clear()
        canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

        dataName = 'dataHist_'+label
        dataHist = r.TH1D(dataName, '', 20, 0., 2.)
        dataHist.Sumw2()
        dataTree.Draw(varString+'>>'+dataName, 'weight * ('+cutString+')', 'goff')
        canvas.addObs(dataHist, title = 'Data')

        # canvas.legend.apply('data', dataHist)
        # canvas.addHistogram(dataHist, drawOpt = 'L')

        for sample, color, mcTree in mcTrees:
            mcName = sample+'_'+label
            mcHist = r.TH1D(mcName, '', 20, 0., 2.)
            mcHist.Sumw2()
            mcTree.Draw(varString+'>>'+mcName, str(lumi)+' * weight * ('+cutString+')', 'goff')

            canvas.addStacked(mcHist, title = sample, color = color)

            # canvas.legend.apply('mc', mcHist)        
            # canvas.addHistogram(mcHist, drawOpt = 'L')

        canvas.ylimits = (0.001, -1.)

        canvas.printWeb('monophoton/phoMet', 'ratio_'+label, logy = True)
