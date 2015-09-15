#!/usr/bin/env python

import sys
import os
import ROOT
ROOT.gROOT.SetBatch(True)

sample = sys.argv[1]

cutTree = ROOT.TChain('nero/events')
eventsTree = ROOT.TChain('nero/events')
allTree = ROOT.TChain('nero/all')
with open('sourceFiles/' + sample + '.txt') as sourceList:
    for line in sourceList:
        if not line.strip().startswith('#'):
            cutTree.Add(line.strip())
            eventsTree.Add(line.strip())
            allTree.Add(line.strip())

ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src')
ROOT.gSystem.Load('libNeroProducerCore.so')
ROOT.gROOT.LoadMacro(os.path.dirname(os.path.realpath(__file__)) + '/skimslim.cc+')

outputFile = ROOT.TFile.Open('/scratch5/yiiyama/monophoton/' + sample + '.root', 'recreate')
ROOT.skimslim(cutTree, eventsTree, outputFile)

outputFile.cd()
allTree.CloneTree()

outputFile.Write()
