#!/usr/bin/env python

import sys
import os
from argparse import ArgumentParser
import json
import ROOT
ROOT.gROOT.SetBatch(True)

argParser = ArgumentParser(description = 'Skim & slim')
argParser.add_argument('sample', metavar = 'SAMPLE', help = 'Sample to skim.')
argParser.add_argument('--json', '-j', metavar = 'FILE', dest = 'json', help = 'JSON file.')

args = argParser.parse_args()
sys.argv = []

thisdir = os.path.dirname(os.path.realpath(__file__))

if args.sample == 'all':
    samples = []
    for slist in os.listdir(thisdir + '/sourceFiles'):
        samples.append(slist.replace('.txt', ''))
else:
    samples = [args.sample]

ROOT.gSystem.AddIncludePath('-I/home/yiiyama/src')
ROOT.gSystem.Load('/home/yiiyama/src/NeroProducer/Core/bin/libBare.so')
ROOT.gROOT.LoadMacro(thisdir + '/skimslim.cc+')

skimmer = ROOT.Skimmer()

if args.json:
    with open(args.json) as source:
        goodlumis = json.loads(source.read())

    for run, lumiranges in goodlumis.items():
        for lumirange in lumiranges:
            lumirange[1] += 1
            for lumi in range(*tuple(lumirange)):
                skimmer.addGoodLumi(int(run), lumi)

for sample in samples:
    print sample

    with open('sourceFiles/' + sample + '.txt') as sourceList:
        for line in sourceList:
            if not line.strip().startswith('#'):
                skimmer.addInputPath(line.strip())
    
    outputFile = ROOT.TFile.Open('/data/blue/yiiyama/monophoton/' + sample + '.root', 'recreate')
    skimmer.run(outputFile)
