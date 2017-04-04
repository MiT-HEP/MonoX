#!/usr/bin/env python

import sys
import os
import array
import math
import random

NENTRIES = -1

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

ROOT.gSystem.Load(config.libobjs)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/Objects/interface')
ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')

lumi = 0.
for sname in lumiSamples:
    lumi += allsamples[sname].lumi

# ID integers stored in the trees.
# Comes handy when processing a pool of samples through TChain
sampleIds = {
    'sph-16b-m': 0,
    'sph-16c-m': 0,
    'sph-16d-m': 0,
    'sph-16e-m': 0,
    'sph-16f-m': 0,
    'sph-16g-m': 0,
    'sph-16h-m': 0,
    'smu-16b-m': 0,
    'smu-16c-m': 0,
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
    targets = sampleIds.keys()

# if target contains mc / eldata / mudata
for confName in skimConfig:
    if confName in targets:
        targets.remove(confName)
        for sname in skimConfig[confName][0]:
            if sname not in targets:
                targets.append(sname)

samples = allsamples.getmany(targets)

suffix = {'kEG': 'eg', 'kMG': 'mg', 'kMMG': 'mmg'}

puSource = ROOT.TFile.Open(basedir + '/data/pileup.root')
if not puSource:
    print 'NPV reweight absent - run monophoton/ssw2.py'
    sys.exit(1)

reweight = puSource.Get('puweight_PUMoriond17')
reweight.SetDirectory(ROOT.gROOT)
puSource.Close()

for sample in samples:
    skimmer = ROOT.Skimmer()

    try:
        # Find the config group this sample is in
        confName, skimTypes = next((confName, skimTypes) for confName, (snames, skimTypes) in skimConfig.items() if sample.name in snames)
    except StopIteration:
        print sample.name, 'not found in dataset list'
        continue

    if confName == 'mc':
        skimmer.setReweight(reweight)

    for skimType in skimTypes:
        skimmer.addSkim(getattr(ROOT, skimType), outputDir + '/' + sample.name + '_' + suffix[skimType] + '.root')

    sampleId = sampleIds[sample.name]

    inputTree = ROOT.TChain('events')
    if os.path.exists(config.photonSkimDir + '/' + sample.name + '.root'):
        print 'Reading', sample.name, 'from photon skim'
        inputTree.Add(config.photonSkimDir + '/' + sample.name + '.root')
    else:
        print 'No photon skim for', sample.name, 'found'
        continue

    if sample.data:
        skimmer.fillSkim(inputTree, 1., sampleId, NENTRIES)
    else:
        skimmer.fillSkim(inputTree, lumi * sample.crosssection / sample.sumw, sampleId, NENTRIES)
