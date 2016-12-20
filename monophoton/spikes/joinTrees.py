#!/usr/bin/env python

import os
import re
import sys
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import SimpleCanvas
from datasets import allsamples
import config

import ROOT

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
ROOT.gROOT.LoadMacro(thisdir + '/joinTrees.cc+')

outputDir = config.photonSkimDir + '/withUncleaned'
try:
    os.makedirs(outputDir)
except OSError:
    pass

sname = sys.argv[1]

for sample in allsamples.getmany(sname):
    if not os.path.exists(config.photonSkimDir + '/' + sample.name + '.root'):
        print 'Main input has to be a photon skim.'
        continue

    source = ROOT.TFile.Open(config.photonSkimDir + '/' + sample.name + '.root')

    outputFile = ROOT.TFile.Open('/tmp/' + sample.name + '.root', 'recreate')
    output = ROOT.TTree('events', 'Events')

    for key in source.GetListOfKeys():
        if key.GetName() == 'events':
            continue

        outputFile.cd()
        key.ReadObj().Write()
        
    mainInput = source.Get('events')

    scInput = ROOT.TChain('events')
#    scInput.Add('/mnt/hadoop/cms/store/user/yiiyama/simpletree/' + re.sub('-v[0-9]/', '-v*/', sample.fullname) + '/*.root')
    scInput.Add('/data/t3home000/yiiyama/simpletree/uncleaned/' + sample.name + '.root')

    ROOT.joinTrees(mainInput, scInput, output)

    outputFile.cd()
    output.Write()
    outputFile.Close()

    source.Close()

    shutil.move('/tmp/' + sample.name + '.root', outputDir)
