import os
import sys
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

snames = sys.argv[1:]

ROOT.gSystem.Load(config.libsimpletree)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')

ROOT.gROOT.LoadMacro('Skimmer.cc+')

tree = ROOT.TChain('events')

for sname in snames:
    sample = allsamples[sname]
    tree.Add(config.ntuplesDir + '/' + sample.book + '/' + sample.fullname + '/*.root')

    if sname == snames[0]:
        if sname.startswith('sph-'):
            treeType = ROOT.kDiphoton
        elif sname.startswith('sel-'):
            treeType = ROOT.kDielectron
        elif sname.startswith('smu-'):
            treeType = ROOT.kMuonPhoton
        elif sname.startswith('jht-'):
            treeType = ROOT.kJetHT
            
        suffix = sname[:sname.find('-')]

ROOT.skim(tree, treeType, config.histDir + '/trigger/trigger_' + suffix + '.root')
