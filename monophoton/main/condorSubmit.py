#!/usr/bin/env python

import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config
from ssw2 import selectors, processSampleNames

from glob import glob
from subprocess import Popen, PIPE
from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Plot and count')
argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '*', help = 'Sample names to skim.')
argParser.add_argument('--plot-config', '-p', metavar = 'PLOTCONFIG', dest = 'plotConfig', default = '', help = 'Run on samples used in PLOTCONFIG.')
argParser.add_argument('--nero-input', '-n', action = 'store_true', dest = 'neroInput', help = 'Specify that input is Nero instead of simpletree.')
argParser.add_argument('--files', '-f', metavar = 'nFilesPerJob', dest = 'nFiles', type = int, default = -1, help = 'Number of files to run on')

args = argParser.parse_args()
sys.argv = []

snames = processSampleNames(args.snames, selectors.keys(), args.plotConfig)

if not os.path.exists(config.skimDir):
    os.makedirs(config.skimDir)

for sname in snames:
    sample = allsamples[sname]
    print 'Starting sample %s (%d/%d)' % (sname, snames.index(sname) + 1, len(snames))

    argFile = file('condorArgs.txt', 'w')
    condorCmd = ['/home/ballen/bin/condor-run', 'ssw2.py', '-a', 'condorArgs.txt']

    argList = [sname]
    if args.neroInput:
        argList.append('-n')

    if os.path.exists(config.photonSkimDir + '/' + sname + '.root'):
        print 'Using photon skim.'
        arguments = ' '.join(argList)
        argFile.write(arguments + '\n')
        argFile.close()

        condor = Popen(condorCmd, stdout=PIPE, stderr=PIPE)
        (cout, cerr) = condor.communicate()
        print cout, '\n'
        # print cerr, '\n'

    elif args.nFiles < 0:
        print 'Not splitting into smaller jobs.'
        arguments = ' '.join(argList)
        argFile.write(arguments + '\n')
        argFile.close()

        condor = Popen(condorCmd, stdout=PIPE, stderr=PIPE)
        (cout, cerr) = condor.communicate()
        print cout, '\n'
        # print cerr, '\n'

    else:
        if sample.data:
            sourceDir = config.dataNtuplesDir + sample.book + '/' + sample.fullname
        else:
            sourceDir = config.ntuplesDir + sample.book + '/' + sample.fullname
            
        print 'Reading', sname, 'from', sourceDir

        if args.neroInput:
            lsCmd = ['/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select', 'ls', sourceDir + '/*.root']
            listFiles = Popen(lsCmd, stdout=PIPE, stderr=PIPE)

            # (lout, lerr) = listFiles.communicate()
            # print lout, '\n'
            # print lerr, '\n'

            filesList = listFiles.stdout
        else:
            filesList = glob(sourceDir + '/*.root')

        nFiles = sum(1 for _ in filesList)
        print 'Found a total of ' + str(nFiles) + ' files.'

        print range(0, nFiles, args.nFiles)

        for nStart in range(0, nFiles, args.nFiles):
            nEnd = nStart + args.nFiles - 1
            nEnd = min(nFiles, nEnd)
            arglist = argList + ['-f', str(nStart), str(nEnd)]
            logname = sname + '_' + str(nStart) + '-' + str(nEnd)

            arguments = ' '.join(arglist)
            argFile.write(arguments + '\n')
        
        argFile.close()

        condor = Popen(condorCmd, stdout=PIPE, stderr=PIPE)
        (cout, cerr) = condor.communicate()
        print cout, '\n'
        print cerr, '\n'
