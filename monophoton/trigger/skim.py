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
    'photon': {'sph': ROOT.Skimmer.kDiphoton, 'sel': ROOT.Skimmer.kElectronPhoton, 'smu': ROOT.Skimmer.kMuonPhoton, 'jht': ROOT.Skimmer.kJetHT},
    'muon': {'smu': ROOT.Skimmer.kDimuon},
    'electron': {'sel': ROOT.Skimmer.kDielectron},
    'met': {'sel': ROOT.Skimmer.kElectronMET}
}

secondaries = []

for sample in samples:
    try:
        treeType = configs[obj][sample.name[:sample.name.find('-')]]
    except KeyError:
        print 'treeType for', obj, sample.name, 'not found'
        continue

    tree = ROOT.TChain('events')

    treePath = config.ntuplesDir + '/' + sample.book + '/' + sample.fullname + '/*.root'
    print sample.name, "adding files from", treePath
    tree.Add(treePath)

    print tree.GetEntries(), 'entries'
    
    skimmer = ROOT.Skimmer()

    if sample.name.startswith('sel-16'):
        secondary = ROOT.TChain('events')
        for fname in os.listdir('/data/t3serv014/yiiyama/hist/simpletree19/gsfix'):
            if fname.startswith(sample.fullname):
                secondary.Add('/data/t3serv014/yiiyama/hist/simpletree19/gsfix/' + fname)

        print secondary.GetEntries(), 'secondary events'
        skimmer.setSecondaryInput(secondary)
        secondaries.append(secondary)
        
    skimmer.skim(tree, treeType, '/tmp/trigger_' + sample.name + '_' + obj + '.root')

    shutil.move('/tmp/trigger_' + sample.name + '_' + obj + '.root', config.histDir + '/trigger_gsfix/' + sample.name + '_' + obj + '.root')
