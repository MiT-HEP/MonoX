#!/usr/bin/env python

#-------------------------------------------------------------------------------
# makeJson.py
#
# This script is used to make a lumi list JSON file out of the output from 
# generic ntuples.
# Usage: makeJson.py <ROOT file> [<ROOT file2> ...]
# Wildcard * is allowed for the ROOT file path specification.
#
#-------------------------------------------------------------------------------

import sys
import os
import array
from argparse import ArgumentParser
import ROOT
ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))

ROOT.gROOT.LoadMacro(thisdir + '/GoodLumiFilter.cc+')
ROOT.gROOT.LoadMacro(thisdir + '/MakeLumiList.cc+')

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

mask = {}
if args.mask:
    mask = ROOT.GoodLumiFilter()
    try:
        with open(args.mask) as maskFile:
            maskJSON = eval(maskFile.read())

        for runStr, lumiRanges in maskJSON.items():
            run = int(runStr)
            for begin, end in lumiRanges:
                for lumi in range(begin, end + 1):
                    mask.addLumi(run, lumi)

    except:
        print 'Could not parse mask JSON', args.mask
        sys.exit(1)

else:
    mask = None

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

ROOT.makeJson(source, args.outputFile, mask, args.runBranchName, args.lumiBranchName)
