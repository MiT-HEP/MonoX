import os
import sys
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

sname = sys.argv[1]
sample = allsamples[sname]

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')

ROOT.gROOT.LoadMacro('Dumper.cc+')

tree = ROOT.TChain('events')
tree.Add(config.ntuplesDir + '/' + sample.book + '/' + sample.directory + '/*.root')

ROOT.triggerRates(tree, 'test.root', 10000)
