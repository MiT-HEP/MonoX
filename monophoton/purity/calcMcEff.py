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
calc.setMinPhoPt(175.)
# calc.setMaxPhoPt(200.)
calc.setMaxDR(5)
calc.setMaxDPt(1)
calc.calculate(source)

effs= []
for iEff in range(4):
    effs.append( calc.getEfficiency(iEff) )
print effs
