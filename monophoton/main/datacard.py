#!/usr/bin/env python

import sys

from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Write combine data card.')
argParser.add_argument('model', metavar = 'MODEL', help = 'Signal model name.')
argParser.add_argument('input', metavar = 'PATH', help = 'Histogram ROOT file.')
argParser.add_argument('--output', '-o', metavar = 'PATH', dest = 'outputName', default = '', help = 'Data card name.')
argParser.add_argument('--observed', '-O', action = 'store_true', dest = 'outFile', help = 'Add observed information.')

args = argParser.parse_args()
sys.argv = []

import os
import array
import math
import re
import ROOT

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

variable = 'metHigh'

def getHist(name, syst = ''):
    if syst:
        return source.Get(variable + '-' + name + '_' + syst)
    else:
        return source.Get(variable + '-' + name)


processIds = {
    args.model: 0
}
rates = {
    args.model: getHist(args.model).GetSumOfWeights()
}

iP = 1
for group in monophConfig.bkgGroups:
    rate = getHist(group.name).GetSumOfWeights()
    if rate == 0.:
        continue

    rates[group.name] = rate
    processIds[group.name] = iP
    iP += 1

processes = [args.model] + [g.name for g in monophConfig.bkgGroups if g.name in rates]
colw = max(10, max([len(p) for p in processes]) + 1)
cols = '%-' + str(colw) + 's'
colsr = '%' + str(colw) + 's'
colf = '%-' + str(colw) + '.2f'
cold = '%' + str(colw) + 'd'

obs = source.Get(variable + '-data_obs')

lines = [
    'imax 1',
    'jmax %d' % (len(processes) - 1),
    'kmax *',
    '---------------',
    'shapes * * %s $CHANNEL-$PROCESS $CHANNEL-$PROCESS_$SYSTEMATIC' % args.input,
    '---------------',
    'bin         ' + variable,
    'observation %.0f' % obs.GetSumOfWeights(),
    '---------------------------------'
]

pblock = [
    'bin                  ',
    'process              ',
    'process              ',
    'rate                 '
]
for proc in processes:
    pblock[0] += cols % variable
    pblock[1] += cols % proc
    pblock[2] += cols % processIds[proc]
    pblock[3] += colf % rates[proc]

lines += pblock

lines.append('---------------------------------')

nuisances = {}
for key in source.GetListOfKeys():
    matches = re.match(variable + '-([0-9a-zA-Z-]+)_([0-9a-zA-Z]+)Up', key.GetName())
    if not matches:
        continue

    proc = matches.group(1)
    syst = matches.group(2)

    if proc not in processes or not getHist(proc, syst + 'Down'):
        continue

    if syst not in nuisances:
        nuisances[syst] = [proc]
    else:
        nuisances[syst].append(proc)
    
for syst, procs in nuisances.items():
    line = cols % syst
    
    if syst == 'lumi':
        line += '   lnN'
    else:
        line += ' shape'

    words = []

    for proc in processes:
        if proc in procs:
            if syst == 'lumi':
                words.append('%.3f' % (getHist(proc, 'lumiUp').GetSumOfWeights() / rates[proc]))
            else:
                words.append('1')

        else:
            words.append('-')

    for word in words:
        line += colsr % word

    lines.append(line)

outputName = args.outputName
if not outputName:
    outputName = variable + '-' + args.model + '.dat'

with open(outputName, 'w') as datacard:
    for line in lines:
        datacard.write(line + '\n')
