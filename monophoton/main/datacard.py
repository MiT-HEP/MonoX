#!/usr/bin/env python

import sys

from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Write combine data card.')
argParser.add_argument('model', metavar = 'MODEL', help = 'Signal model name. Use "nomodel" for model-independent limits.')
argParser.add_argument('input', metavar = 'PATH', help = 'Histogram ROOT file.')
argParser.add_argument('--output', '-o', metavar = 'PATH', dest = 'outputName', default = '', help = 'Data card name.')
argParser.add_argument('--observed', '-O', action = 'store_true', dest = 'outFile', help = 'Add observed information.')
argParser.add_argument('--variable', '-v', action = 'store', metavar = 'VARIABLE', dest = 'variable', default = 'phoPtHighMet', help = 'Discriminating variable.')
argParser.add_argument('--shape', '-s', action = 'store_true', dest = 'shape', default = False, help = 'Turn on shape analysis.')

args = argParser.parse_args()
sys.argv = []

import os
import array
import math
import re
import ROOT
from pprint import pprint

ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import *
from datasets import allsamples
import config
from main.plotconfig import getConfig

monophConfig = getConfig('monoph')
source = ROOT.TFile.Open(args.input)

variable = args.variable

lumi = 0.
for sName in monophConfig.obs.samples:
    lumi += allsamples[sName].lumi

# gather process names
signal = args.model
processes = [signal] + [g.name for g in monophConfig.bkgGroups]

# determine column widths (for human-readability)
colw = max(10, max([len(p) for p in processes]) + 1, len(variable)+1)
cols = '%-' + str(colw) + 's'
colsr = '%' + str(colw) + 's'
colf = '%-' + str(colw) + '.2f'
cold = '%-' + str(colw) + 'd'


def getHist(name, syst = ''):
    if syst:
        return source.Get(variable + '-' + name + '_' + syst)
    else:
        return source.Get(variable + '-' + name)


def makeProcessBlock(processes, procs, binLow = 1):
    processBlock = [
        'bin                  ',
        'process              ',
        'process              ',
        'rate                 '
    ]

    signalScale = 1.

    for iP, process in enumerate(processes):
        if process == 'nomodel':
            rate = lumi / 1000. # sigma x A x eff = 1 fb
        else:
            hist = getHist(process)
            integral = hist.Integral(binLow, hist.GetNbinsX())
            rate = integral
            if process == signal:
                while rate < 0.01:
                    signalScale *= 10.
                    rate = integral * signalScale

                while rate > 100.:
                    signalScale *= 0.1
                    rate = integral * signalScale

            elif rate < 0.005:
                continue

        procs.append(process)

        processBlock[0] += cols % variable
        processBlock[1] += cols % process
        processBlock[2] += cold % iP
        processBlock[3] += colf % rate

    return processBlock, signalScale


def makeNuisanceBlock(nuisances, processes, binLow = 1, shape = True):
    block = []

    systList = {}

    for syst in sorted(nuisances.keys()):
        procs = nuisances[syst]

        line = cols % syst

        words = []

        lnN = False

        vals = {}

        # iterate over all processes (=columns)    
        for proc in processes:
            if proc in procs:
                var = getHist(proc, syst + 'Var')

                # this process is affected by this uncertainty
                if not var and shape:
                    if lnN:
                        raise RuntimeError(syst + ' is supposed to be a uniform scale variation')

                    words.append('1')
                else:
                    lnN = True
                    hist = getHist(proc)
                    nominal = hist.Integral(binLow, hist.GetNbinsX())
                    if var:
                        relunc = var.Integral(binLow, hist.GetNbinsX()) / nominal - 1.
                    else:
                        up = getHist(proc, syst + 'Up').Integral(binLow, hist.GetNbinsX())
                        down = getHist(proc, syst + 'Down').Integral(binLow, hist.GetNbinsX())
                        relunc = (up - down) * 0.5 / nominal

                    words.append('%.3f' % (1. + relunc))
                    vals[proc] = 1. + relunc
    
            else:
                words.append('-')

        if lnN:
            line += '   lnN'
        else:
            line += ' shape'
    
        for word in words:
            line += colsr % word
    
        block.append(line)
        systList[syst] = vals

    if shape:
        return block
    else:
        return (block, systList)


def writeCard(outputName, blocks, signalScale = 1.):
    with open(outputName, 'w') as datacard:
        for block in blocks:
            for line in block:
                datacard.write(line + '\n')

            datacard.write('---------------------------------\n')

        if signalScale != 1.:
            # signal yield is scaled by signalScale -> scale r factor back by 1/signalScale
            datacard.write('# R x %.3e\n' % (1. / signalScale))


obs = source.Get(variable + '-data_obs')

headerBlock = [
    'imax 1',
    '', # jmax %d - need to be set when we know how many processes have non-zero rate
    'kmax *'
]

# collect names of nuisance parameters for each process
nuisances = {}
for key in source.GetListOfKeys():
    matches = re.match(variable + '-([0-9a-zA-Z-]+)_([0-9a-zA-Z]+)(Up|Var)', key.GetName())
    if not matches:
        continue

    proc = matches.group(1)
    syst = matches.group(2)
    vartype = matches.group(3)

    if proc not in processes:
        continue

    if vartype == 'Up' and not getHist(proc, syst + 'Down'):
        continue

    if syst not in nuisances:
        nuisances[syst] = [proc]
    else:
        nuisances[syst].append(proc)

# set the output name
outputName = args.outputName
if not outputName:
    outputName = args.model + '-' + variable + '.dat'

# start writing cards

if args.model == 'nomodel':
    # Model independent
    
    nBins = obs.GetNbinsX()

    systLists = {}

    # iterate over bins and make one datacard for each integral
    for binLow in range(1, nBins + 1):
        obsBlock = [
            'bin         ' + variable,
            'observation %.0f' % obs.Integral(binLow, nBins)
        ]

        procs = []
        processBlock, signalScale = makeProcessBlock(processes, procs, binLow = binLow)
        # this is nomodel; ignore signalScale (is 1 anyway)

        headerBlock[1] = 'jmax %d' % (len(procs) - 1) # -1 for signal

        (nuisanceBlock, systList) = makeNuisanceBlock(nuisances, procs, binLow = binLow, shape = False)

        if outputName.rfind('.') == -1:
            outName = outputName
            ext = '.dat'
        else:
            outName = outputName[:outputName.rfind('.')]
            ext = outputName[outputName.rfind('.'):]

        bound = obs.GetXaxis().GetBinLowEdge(binLow)
        if math.floor(bound) == bound:
            outName += ('_%.0f' % bound) + ext
        else:
            outName += ('_%f' % bound) + ext

        writeCard(outName, [headerBlock, obsBlock, processBlock, nuisanceBlock])
        systLists[bound] = systList

    header = "%-20s" % " "
    for bound in sorted(systLists.keys()):
        header += " %6.0f" % bound
    print header

    systs = systLists[obs.GetBinLowEdge(1)]
    for syst in sorted(systs):
        for proc in systs[syst]:
            # print syst, proc
            temp = "%s_%s:" % (syst, proc)
            string = "%-20s" % temp
            for bound in sorted(systLists.keys()):
                try:
                    string += " %6.2f" % systLists[bound][syst][proc]
                except KeyError:
                    string += " %6s" % "-"
            print string
        

elif args.shape:
    shapeBlock = [
        'shapes * * %s $CHANNEL-$PROCESS $CHANNEL-$PROCESS_$SYSTEMATIC' % args.input,
    ]

    obsBlock = [
        'bin         ' + variable,
        'observation %.0f' % obs.GetSumOfWeights(),
    ]

    procs = []
    processBlock, signalScale = makeProcessBlock(processes, procs)

    headerBlock[1] = 'jmax %d' % (len(procs) - 1) # -1 for signal

    nuisanceBlock = makeNuisanceBlock(nuisances, procs)

    writeCard(outputName, [headerBlock, shapeBlock, obsBlock, processBlock, nuisanceBlock], signalScale = signalScale)

else:
    obsBlock = [
        'bin         ' + variable,
        'observation %.0f' % obs.GetSumOfWeights(),
    ]

    procs = []
    processBlock, signalScale = makeProcessBlock(processes, procs)

    headerBlock[1] = 'jmax %d' % (len(procs) - 1) # -1 for signal

    (nuisanceBlock, systList) = makeNuisanceBlock(nuisances, procs, shape = False)

    writeCard(outputName, [headerBlock, obsBlock, processBlock, nuisanceBlock], signalScale = signalScale)
