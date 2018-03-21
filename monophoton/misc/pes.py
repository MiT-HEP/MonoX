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
from main.plotutil import PlotDef
from main.plotconfig import getConfig
import config

import ROOT as r
r.gROOT.SetBatch(True)

lumi = sum([s.lumi for s in allsamples.getmany('sph-16*-m')])
canvas = DataMCCanvas(lumi = lumi)

varDef = PlotDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175.0, 200., 250., 300., 400., 600., 1000.0],  unit = 'GeV', overflow = True)

gj = ['gj-100', 'gj-200', 'gj-400', 'gj-600']
wlnun = ['wlnun-0', 'wlnun-50', 'wlnun-100', 'wlnun-250', 'wlnun-400', 'wlnun-600']
top = ['ttg', 'tg']
gg = ['gg-40', 'gg-80']
zllg = ['zllg-130-o', 'zllg-300-o']

samples = [ ('minor', top + gj + wlnun + gg + zllg + ['ww', 'wz', 'zz'], r.TColor.GetColor(0x55, 0x44, 0xff)),
            ('wg', ['wnlg-130-p'], r.TColor.GetColor(0xff, 0x44, 0x99)),
            ('zg', ['znng-130-o'], r.TColor.GetColor(0x99, 0xff, 0xaa)) 
            ]

regions = [ ('offtimeIso', '(1)', r.TColor.GetColor(0x66, 0x66, 0x66)),
            ('halo', '(metFilters.globalHalo16 && photons.mipEnergy[0] > 4.9)', r.TColor.GetColor(0xff, 0x99, 0x33)),
            ('hfake', 'photons.nhIsoX[0][2] < 2.792 && photons.phIsoX[0][2] < 2.176 && photons.chIsoMaxX[0][2] > 1.146', r.TColor.GetColor(0xbb, 0xaa, 0xff)),
            ('efake', '(1)', r.TColor.GetColor(0xff, 0xee, 0x99))
            ]

print config.skimDir

dataTree = r.TChain('events')
dataTree.Add(config.skimDir+'/sph-16*-m_monoph.root')
print dataTree.GetEntries()

mcTrees = []
for group, slist, color in samples:
    mcTree = r.TChain('events')
    for sample in slist:
        mcTree.Add(config.skimDir+'/'+sample+'_monoph.root')
    mcTrees.append( (group, color, mcTree) )

bkgTrees = []
for region, cut, color in regions:
    bkgTree = r.TChain('events')
    bkgTree.Add(config.skimDir+'/sph-16*-m_' + region + '.root')
    bkgTrees.append( (region, cut, color, bkgTree) )

cutString = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.minJetDPhi > 0.5 && t1Met.photonDPhi > 0.5 && (photons.scRawPt[0] / t1Met.pt) < 1.4'
print cutString

canvas.Clear()
canvas.legend.Clear()
canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

dataName = varDef.name + '-dataHist'
dataHist = varDef.makeHist(dataName)
print dataHist.GetName()
dataTree.Draw(varDef.expr + '>>' + dataName, 'weight * ('+cutString+')', 'goff')
print dataHist.Integral()
canvas.addObs(dataHist, title = 'Data')

for region, cut, color, bkgTree in bkgTrees:
    bkgHist = varDef.makeHist(varDef.name + '-' + region)
    print bkgHist.GetName()
    fullCut = cutString + ' && ' + cut
    bkgTree.Draw(varDef.expr + '>>' + varDef.name + '-' + region, 'weight * ('+cutString+')', 'goff')
    if region == 'offtimeIso':
        bkgHist.Scale(23.9 / bkgHist.Integral())
    elif region == 'halo':
        bkgHist.Scale(1./3000.)
        
    print bkgHist.Integral()
    canvas.addStacked(bkgHist, title = region, color = color)

for sample, color, mcTree in mcTrees:
    mcHist = varDef.makeHist(varDef.name + '-' + sample)
    print mcHist.GetName()
    mcTree.Draw("1.02 * " + varDef.expr + '>>' + varDef.name + '-' + sample, str(lumi)+' * weight * ('+cutString+')', 'goff')
    print mcHist.Integral()
    canvas.addStacked(mcHist, title = sample, color = color)

# canvas.ylimits = (0.001, -1.)
canvas.xtitle = varDef.title
canvas.ytitle = 'Events'

canvas.printWeb('monophoton/pes/', varDef.name+"02")
