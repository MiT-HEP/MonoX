#!/usr/bin/env python

import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config
from ssw2 import defaults, selectors

from glob import glob
from subprocess import Popen, PIPE
from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Plot and count')
argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '*', help = 'Sample names to skim.')
argParser.add_argument('--plot-config', '-p', metavar = 'PLOTCONFIG', dest = 'plotConfig', default = '', help = 'Run on samples used in PLOTCONFIG.')
argParser.add_argument('--cleanup', '-c', action = 'store_true', dest = 'cleanup', default = False, help = 'Remove unmerged files after merging.')

args = argParser.parse_args()
sys.argv = []

tmpDir = '/tmp/ballen'

snames = []

if args.plotConfig:
    # if a plot config is specified, use the samples for that
    snames = plotconfig.getConfig(args.plotConfig).samples()
    
else:
    snames = args.snames

# handle special group names
if 'all' in snames:
    snames.remove('all')
    snames = selectors.keys()
elif 'dmfs' in snames:
    snames.remove('dmfs')
    snames += [key for key in selectors.keys() if key.startswith('dm') and key[3:5] == 'fs']
elif 'dm' in snames:
    snames.remove('dm')
    snames += [key for key in selectors.keys() if key.startswith('dm')]
elif 'add' in snames:
    snames.remove('add')
    snames += [key for key in selectors.keys() if key.startswith('add')]
if 'fs' in snames:
    snames.remove('fs')
    snames += [key for key in selectors.keys() if 'fs' in key]

# filter out empty samples
tmp = [name for name in snames if allsamples[name].sumw != 0.]
snames = tmp

for sname in snames:
    sample = allsamples[sname]
    print 'Starting sample %s (%d/%d)' % (sname, snames.index(sname) + 1, len(snames))

    for selconf in selectors[sname]:
        if type(selconf) == str:
            rname = selconf
            gen = defaults[rname]
        else:
            rname, gen = selconf

        outName = sname + '_' + rname + '.root'
        inName  = sname + '_*_' + rname + '.root'

        print 'Merging', outName

        inputs = glob(config.skimDir + '/' + inName)
        # print inputs

        haddCmd = ['hadd', '-f', tmpDir + '/' + outName] + inputs
        hadd = Popen(haddCmd, stdout=PIPE, stderr=PIPE)
        (hout, herr) = hadd.communicate()
        print hout, '\n'
        # print herr, '\n'

        if args.cleanup:
            print 'Removing', inName
            rmCmd = ['rm'] + inputs
            rm = Popen(rmCmd, stdout=PIPE, stderr=PIPE)
            (rout, rerr) = rm.communicate()
            print rout, '\n'
            print rerr, '\n'

        moveCmd = ['mv', tmpDir + '/' + outName, config.skimDir + '/' + outName]
        move = Popen(moveCmd, stdout=PIPE, stderr=PIPE)
        (mout, merr) = move.communicate()
        # print mout, '\n'
        # print merr, '\n'
