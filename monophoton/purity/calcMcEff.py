#!/usr/bin/env python

import sys
import os
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

ROOT.gSystem.Load(config.libsimpletree)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')

loc = sys.argv[1]
pid = sys.argv[2]
chiso = sys.argv[3]
pt = sys.argv[4]
met = sys.argv[5]

inputKey = loc+'_'+pid+'_ChIso'+chiso+'_PhotonPt'+pt+'_Met'+met

source = ROOT.TChain('events')
print config.skimDir
source.Add(config.skimDir + '/gj-40_purity.root')
source.Add(config.skimDir + '/gj-100_purity.root')
source.Add(config.skimDir + '/gj-200_purity.root')
source.Add(config.skimDir + '/gj-400_purity.root')
source.Add(config.skimDir + '/gj-600_purity.root')

ROOT.gROOT.LoadMacro(thisdir + '/Calculator.cc+')

print source.GetEntries()

calc = ROOT.Calculator()
calc.setMaxDR(0.2)
calc.setMaxDPt(0.2)

if loc == 'barrel':
    minEta = 0.
    maxEta = 1.5
elif loc == 'endcap':
    minEta = 1.5
    maxEta = 2.5
calc.setMinEta(minEta)
calc.setMaxEta(maxEta)

idmap = { 'loose' : 0, 'medium' : 1, 'tight' : 2 }
calc.setWorkingPoint(idmap[pid])

(minPt, maxPt) = pt.split('to')
if maxPt == 'Inf':
    maxPt = 6500.
calc.setMinPhoPt(float(minPt))
calc.setMaxPhoPt(float(maxPt))

(minMet, maxMet) = met.split('to')
if maxMet == 'Inf':
    maxMet = 6500.
calc.setMinMet(float(minMet))
calc.setMaxMet(float(maxMet))

calc.calculate(source)

effs= []
for iEff in range(4):
    effs.append( calc.getEfficiency(iEff) )
print effs
