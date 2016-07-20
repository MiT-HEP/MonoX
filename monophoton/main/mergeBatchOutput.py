#!/usr/bin/env python

import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config
from ssw2 import defaults, selectors, processSampleNames

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
if not os.path.exists(tmpDir):
    os.makedirs(tmpDir)

snames = processSampleNames(args.snames, selectors.keys(), args.plotConfig)

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

        if inputs == []:
            print "Nothing to merge."
            continue

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
