#!/usr/bin/env python 

import os
import sys
import shutil
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

try:
    os.makedirs(config.histDir + '/trigger')
except OSError:
    pass

obj = sys.argv[1]
snames = sys.argv[2:]

samples = allsamples.getmany(snames)

print 'Skimming samples'
print [s.name for s in samples]

ROOT.gSystem.Load(config.libsimpletree)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')

ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')

# available object - sample - skim type configurations
configs = {
    'photon': {'sph': ROOT.kDiphoton, 'sel': ROOT.kElectronPhoton, 'smu': ROOT.kMuonPhoton, 'jht': ROOT.kJetHT},
    'muon': {'smu': ROOT.kDimuon},
    'electron': {'sel': ROOT.kDielectron},
    'met': {'sel': ROOT.kElectronMET}
}

tree = ROOT.TChain('events')

for sample in samples:
    try:
        treeType = configs[obj][sample.name[:sample.name.find('-')]]
    except KeyError:
        print 'treeType for', obj, sample.name, 'not found'
        continue

    treePath = config.ntuplesDir + '/' + sample.book + '/' + sample.fullname + '/*.root'
    print sample.name, "adding files from", treePath
    tree.Add(treePath)

    print tree.GetEntries(), 'entries'
            
    ROOT.skim(tree, treeType, '/tmp/trigger_' + sample.name + '_' + obj + '.root')

    shutil.move('/tmp/trigger_' + sample.name + '_' + obj + '.root', config.histDir + '/trigger/' + sample.name + '_' + obj + '.root')
