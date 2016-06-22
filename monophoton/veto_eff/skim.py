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

skim = sys.argv[1]
sname = sys.argv[2]

sample = allsamples[sname]

npvSource = ROOT.TFile.Open(basedir + '/data/npv.root')
npvweight = npvSource.Get('npvweight')

source = ROOT.TChain('events')
source.Add(config.ntuplesDir + '/' + sample.directory + '/*.root')

ROOT.gROOT.LoadMacro(thisdir + '/' + skim + '.cc+')

outName = '/scratch5/yiiyama/studies/monophoton/veto_eff/' + skim +'_' + sname + '.root'

if sample.data:
    getattr(ROOT, skim)(source, outName)
else:
    getattr(ROOT, skim)(source, outName, sample.crosssection / sample.sumw, npvweight)
