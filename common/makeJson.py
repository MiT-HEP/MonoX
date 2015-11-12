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
argParser.add_argument('paths', metavar = 'PATH', nargs = '*', help = 'Paths to ROOT files (wildcard allowed) containing lumi list trees.')
argParser.add_argument('--mask', '-m', metavar = 'FILE', dest = 'mask', default = '', help = 'Lumi mask (e.g. Golden JSON) to apply.')
argParser.add_argument('--out', '-o', metavar = 'FILE', dest = 'outputFile', default = 'lumis.txt', help = 'Output file name.')
argParser.add_argument('--list', '-i', metavar = 'FILE', dest = 'listFile', default = '', help = 'File that contains the list of input files.')
argParser.add_argument('--tree', '-t', metavar = 'NAME', dest = 'treeName', default = 'nero/all', help = 'Name of the input tree.')
argParser.add_argument('--run-branch', '-r', metavar = 'NAME', dest = 'runBranchName', default = 'runNum', help = 'Name of the run branch.')
argParser.add_argument('--lumi-branch', '-l', metavar = 'NAME', dest = 'lumiBranchName', default = 'lumiNum', help = 'Name of the lumi branch.')

args = argParser.parse_args()
sys.argv = []

if args.mask:
    try:
        with open(args.mask) as maskFile:
            maskJSON = eval(maskFile.read())

        mask = {}
        for runStr, lumiRanges in maskJSON.items():
            run = int(runStr)
            mask[run] = []
            for begin, end in lumiRanges:
                mask[run] += range(begin, end + 1)
    except:
        print 'Could not parse mask JSON', args.mask
        sys.exit(1)

source = ROOT.TChain(args.treeName)
if args.listFile:
    with open(args.listFile) as listFile:
        for line in listFile:
            if line.strip().startswith('#'):
                continue

            source.Add(line.strip())
else:
    for path in args.paths:
        source.Add(path)

runArr = array.array('i', [0])
lumiArr = array.array('i', [0])

source.SetBranchAddress(args.runBranchName, runArr)
source.SetBranchAddress(args.lumiBranchName, lumiArr)

allLumis = {}

iEntry = 0
while source.GetEntry(iEntry) > 0:
    iEntry += 1

    run = int(runArr[0])
    lumi = int(lumiArr[0])

    if len(mask):
        if run not in mask or lumi not in mask[run]:
            continue

    if run not in allLumis:
        allLumis[run] = []
        
    lumis = allLumis[run]

    if lumi not in lumis:
        lumis.append(lumi)

text = ''
for run in sorted(allLumis.keys()):
    text += '\n  "%d": [\n' % run

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
    text += '  ],'

with open(args.outputFile, 'w') as json:
    json.write('{' + text[:-1] + '\n}')
