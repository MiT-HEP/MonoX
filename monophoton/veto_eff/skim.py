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

puSource = ROOT.TFile.Open(basedir + '/data/pileup.root')
puweight = npvSource.Get('puweight')

source = ROOT.TChain('events')
source.Add(config.ntuplesDir + '/' + sample.book + '/' + sample.fullname + '/*.root')

ROOT.gROOT.LoadMacro(thisdir + '/' + skim + '.cc+')

outName = config.histDir + '/veto_eff/' + skim +'_' + sname + '.root'

if sample.data:
    getattr(ROOT, skim)(source, outName)
else:
    getattr(ROOT, skim)(source, outName, sample.crosssection / sample.sumw, puweight)
