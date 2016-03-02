#!/usr/bin/env python

#-------------------------------------------------------------------------------
# makeJson.py
#
# This script is used to make a lumi list JSON file out of the output from
# the RunLumiListMod.
# Usage: makeJson.py <ROOT file> [<ROOT file2> ...]
# Wildcard * is allowed for the ROOT file path specification.
#
#-------------------------------------------------------------------------------

import sys
import array
from argparse import ArgumentParser
import ROOT
ROOT.gROOT.SetBatch(True)

argParser = ArgumentParser(description = 'Make JSON lumi list')
argParser.add_argument('paths', metavar = 'PATH', nargs = '+', help = 'Paths to ROOT files (wildcard allowed) containing lumi list trees.')
argParser.add_argument('--out', '-o', metavar = 'FILE', dest = 'outputFile', default = 'lumis.txt', help = 'Output file name.')

args = argParser.parse_args()
sys.argv = []

source = ROOT.TChain('skimmedEvents')
for path in args.paths:
    source.Add(path)

run = array.array('i', [0])
lumi = array.array('i', [0])

source.SetBranchAddress('run', run)
source.SetBranchAddress('lumi', lumi)

allLumis = {}

iEntry = 0
while source.GetEntry(iEntry) > 0:
    iEntry += 1

    if run[0] not in allLumis:
        allLumis[run[0]] = []
        
    lumis = allLumis[run[0]]

    if lumi[0] not in lumis:
        lumis.append(lumi[0])

text = ''
for run in sorted(allLumis.keys()):
    text += '  "%d": [\n' % run

    current = -1
    for lumi in sorted(allLumis[run]):
        if lumi == current + 1:
            current = lumi
            continue

        if current > 0:
            text += '%d],\n' % current

        current = lumi
        text += '    [%d, ' % current

    text += '%d]\n' % current
    text += '  ],\n'

with open(args.outputFile, 'w') as json:
    json.write('{\n' + text[:-2] + '\n}')
