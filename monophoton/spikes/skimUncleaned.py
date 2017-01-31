#!/usr/bin/env python

import os
import sys
import shutil
import json

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from datasets import allsamples

import ROOT

sname = sys.argv[1]
sample = allsamples[sname]

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
ROOT.gROOT.LoadMacro(thisdir + '/skimUncleaned.cc+')

input = ROOT.TChain('events')

if sname == 'sph-16h':
    input.Add('/mnt/hadoop/scratch/yiiyama/simpletree/' + sample.fullname.replace('-v1', '-v2') + '/*.root')
    input.Add('/mnt/hadoop/scratch/yiiyama/simpletree/' + sample.fullname.replace('-v1', '-v3') + '/*.root')
else:
    input.Add('/mnt/hadoop/scratch/yiiyama/simpletree/' + sample.fullname + '/*.root')

ROOT.skimUncleaned(input, '/data/t3home000/yiiyama/simpletree/uncleanedSkimmed/' + sname + '.root')
