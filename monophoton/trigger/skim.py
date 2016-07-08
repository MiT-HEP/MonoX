#!/usr/bin/env python 

import os
import sys
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

obj = sys.argv[1]
snames = sys.argv[2:]

ROOT.gSystem.Load(config.libsimpletree)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')

ROOT.gROOT.LoadMacro('Skimmer.cc+')

tree = ROOT.TChain('events')

for sname in snames:
    sample = allsamples[sname]
    treePath = config.ntuplesDir + '/' + sample.book + '/' + sample.fullname + '/*.root'
    print "adding files from", treePath
    tree.Add(treePath)

    print tree.GetEntries()

    if sname == snames[0]:
        if obj == 'muon':
            treeType = ROOT.kDimuon
        elif obj == 'electron':
            treeType = ROOT.kDielectron
        elif sname.startswith('sph-'):
            treeType = ROOT.kDiphoton
        elif sname.startswith('sel-'):
            treeType = ROOT.kElectronPhoton
        elif sname.startswith('smu-'):
            treeType = ROOT.kMuonPhoton
        elif sname.startswith('jht-'):
            treeType = ROOT.kJetHT
            
        suffix = sname[:sname.find('-')]

outDir = config.histDir + '/trigger'
if not os.path.exists(outDir):
    os.makedirs(outDir)

ROOT.skim(tree, treeType, outDir + '/trigger_' + suffix + '_' + obj + '.root')
