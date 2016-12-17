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
snames = sys.argv[2:]

puSource = ROOT.TFile.Open(basedir + '/data/pileup.root')
puweight = puSource.Get('puweight')

ROOT.gROOT.LoadMacro(thisdir + '/monoph.cc+')
ROOT.gROOT.LoadMacro(thisdir + '/dimu.cc+')

for sample in allsamples.getmany(snames):
    source = ROOT.TChain('events')
    source.Add(config.ntuplesDir + '/' + sample.book + '/' + sample.fullname + '/*.root')
    
    outName = config.histDir + '/veto_eff/' + skim +'_' + sample.name + '.root'
    
    if sample.data:
        getattr(ROOT, skim)(source, outName)
    else:
        getattr(ROOT, skim)(source, outName, sample.crosssection / sample.sumw, puweight)
