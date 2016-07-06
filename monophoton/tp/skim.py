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

from efake_conf import skimDir, skimConfig, lumiSamples

targets = sys.argv[1:]

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

# skim output directory
outputDir = skimDir

ROOT.gSystem.Load(config.libsimpletree)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')
ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')

lumi = 0.
for sname in lumiSamples:
    lumi += allsamples[sname].lumi

# ID integers stored in the trees.
# Comes handy when processing a pool of samples through TChain
sampleIds = {
    'sel-16b2': 0,
    'smu-16b2': 0,
    'dy-50': 1,
    'gg-80': 2,
    'tt': 3,
    'wlnu': 4,
    'wlnu-100': 4,
    'wlnu-200': 4,
    'wlnu-400': 4,
    'wlnu-600': 4,
    'ww': 5,
    'wz': 6,
    'zz': 7
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

suffix = {'kEG': 'eg', 'kMG': 'mg', 'kMMG': 'mmg'}

puSource = ROOT.TFile.Open(basedir + '/data/pileup.root')
if not puSource:
    print 'NPV reweight absent - run monophoton/ssw2.py'
    sys.exit(1)

reweight = puSource.Get('puweight')
reweight.SetDirectory(ROOT.gROOT)
puSource.Close()

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
        skimmer.addSkim(getattr(ROOT, skimType), outputDir + '/' + sname + '_' + suffix[skimType] + '.root')

    sampleId = sampleIds[sname]

    sample = allsamples[sname]
    inputTree = ROOT.TChain('events')
    inputTree.Add(config.ntuplesDir + '/' + sample.book + '/' + sample.fullname + '/simpletree_*.root')

    if sample.data:
        skimmer.fillSkim(inputTree, 1., sampleId)
    else:
        skimmer.fillSkim(inputTree, lumi * sample.crosssection / sample.sumw, sampleId)
