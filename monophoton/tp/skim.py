#!/usr/bin/env python

import sys
import os
import array
import math
import random

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

targets = sys.argv[1:]

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

# skim output directory
outputDir = '/scratch5/yiiyama/studies/egfake_skim'

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')

lumi = allsamples['sel-d3'].lumi + allsamples['sel-d4'].lumi

# Grouping of samples for convenience.
# Argument targets can be individual sample names or the config names (eldata/mudata/mc).
# Samples in the same data are skimmed for skimTypes (second parameters of the tuples) in the group.
skimConfig = {
    'eldata': (['sel-d3', 'sel-d4'], [ROOT.kEG]),
    'mudata': (['smu-d3', 'smu-d4'], [ROOT.kMG, ROOT.kMMG]),
    'mc': (['dy-50', 'tt', 'wlnu-100', 'wlnu-200', 'wlnu-400', 'wlnu-600', 'ww', 'wz', 'zz'], [ROOT.kEG, ROOT.kMG, ROOT.kMMG])
}

# ID integers stored in the trees.
# Comes handy when processing a pool of samples through TChain
sampleIds = {
    'sel-d3': 0,
    'sel-d4': 0,
    'smu-d3': 0,
    'smu-d4': 0,
    'dy-50': 1,
    'tt': 2,
    'wlnu': 3,
    'wlnu-100': 3,
    'wlnu-200': 3,
    'wlnu-400': 3,
    'wlnu-600': 3,
    'ww': 4,
    'wz': 5,
    'zz': 6
}

# Special target names

if targets[0] == 'list':
    names = ' '.join(sorted(sampleIds.keys()))
    print names
    sys.exit(0)

elif targets[0] == 'all':
    dsNames = sampleIds.keys()

# if target contains mc / eldata / mudata
for confName in skimConfig:
    if confName in targets:
        targets.remove(confName)
        for sname in skimConfig[targets][0]:
            if sname not in targets:
                targets.append(sname)

suffix = {ROOT.kEG: 'eg', ROOT.kMG: 'mg', ROOT.kMMG: 'mmg'}

npvSource = ROOT.TFile.Open(basedir + '/data/npv.root')
if not npvSource:
    print 'NPV reweight absent - run monophoton/ssw2.py'
    sys.exit(1)

reweight = npvSource.Get('npvweight')
reweight.SetDirectory(ROOT.gROOT)
npvSource.Close()

for sname in targets:
    skimmer = ROOT.Skimmer()

    try:
        # Find the config group this sample is in
        confName, skimTypes = next((confName, skimTypes) for confName, (snames, skimTypes) in skimConfig.items() if sname in snames)
    except StopIteration:
        print sname, 'not found in dataset list'
        continue

    if confName == 'mc':
        skimmer.setReweight(reweight)

    for skimType in skimTypes:
        skimmer.addSkim(skimType, outputDir + '/' + sname + '_' + suffix[skimType] + '.root')

    sampleId = sampleIds[sname]

    sample = allsamples[sname]
    inputTree = ROOT.TChain('events')
    inputTree.Add(config.ntuplesDir + '/' + sample.book + '/' + sample.directory + '/simpletree_*.root')

    if sample.data:
        skimmer.fillSkim(inputTree, 1., sampleId)
    else:
        skimmer.fillSkim(inputTree, lumi * sample.crosssection / sample.sumw, sampleId)
