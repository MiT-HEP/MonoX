#!/usr/bin/env python

import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

from subprocess import Popen, PIPE
from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Plot and count')
argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '*', help = 'Sample names to skim.')
argParser.add_argument('--plot-config', '-p', metavar = 'PLOTCONFIG', dest = 'plotConfig', default = '', help = 'Run on samples used in PLOTCONFIG.')
argParser.add_argument('--nero-input', '-n', action = 'store_true', dest = 'neroInput', help = 'Specify that input is Nero instead of simpletree.')
argParser.add_argument('--files', '-f', metavar = 'nFilesPerJob', dest = 'nFiles', type = int, default = -1, help = 'Number of files to run on')

args = argParser.parse_args()
sys.argv = []

queue = '1nh' # '2nw4cores'

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

if not os.path.exists(config.skimDir):
    os.makedirs(config.skimDir)

logDir = config.skimDir + '/logs'
if not os.path.exists(logDir):
    os.makedirs(logDir)

for sname in snames:
    sample = allsamples[sname]
    print 'Starting sample %s (%d/%d)' % (sname, snames.index(sname) + 1, len(snames))

    stdOut = logDir + '/' + sname + '.out'
    stdErr = logDir + '/' + sname + '.err'

    cmdList = ['bsub','-o',stdOut,'-e',stdErr,'-q',queue,'ssw2.py',sname]
    if args.neroInput:
        cmdList.append('-n')

    if os.path.exists(config.photonSkimDir + '/' + sname + '.root'):
        print 'Using photon skim.'
        submit = Popen(mdList, stdout=PIPE, stderr=PIPE)
        (lout, lerr) = submit.communicate()
        print lout, '\n'
        print lerr, '\n'
        continue

    elif args.nFiles < 0:
        print 'Not splitting into smaller jobs.'
        submit = Popen(cmdList, stdout=PIPE, stderr=PIPE)
        (lout, lerr) = submit.communicate()
        print lout, '\n'
        print lerr, '\n'
        continue

    else:
        if sample.data:
            sourceDir = config.dataNtuplesDir + sample.book + '/' + sample.fullname
        elif 'dm' in sample.name:
            sourceDir = config.ntuplesDir.replace('tree18', 'tree18a') + sample.book + '/' + sample.fullname
        else:
            sourceDir = config.ntuplesDir + sample.book + '/' + sample.fullname
            
        print 'Reading', sname, 'from', sourceDir

        if args.neroInput:
            lsCmd = ['/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select']
            pathPrefix = 'root:://eoscms/'
        else:
            lsCmd = []
            pathPrefix = ''

        lsCmd += ['ls', sourceDir + '/*.root']
        listFiles = Popen(lsCmd, stdout=PIPE, stderr=PIPE)

        # (lout, lerr) = listFiles.communicate()
        # print lout, '\n'
        # print lerr, '\n'

        nFiles = sum(1 for _ in listFiles.stdout)
        print 'Found a total of ' + str(nFiles) + ' files.'

        print range(0, nFiles, args.nFiles)

        for nStart in range(0, nFiles, args.nFiles):
            nEnd = nStart + args.nFiles - 1
            nEnd = min(nFiles, nEnd)
            stdOut = logDir + '/' + sname + '_' + str(nStart) + '-' + str(nEnd) + '.out'
            stdErr = logDir + '/' + sname + '_' + str(nStart) + '-' + str(nEnd) + '.err'

            cmdList = ['bsub','-o',stdOut,'-e',stdErr,'-q',queue,'ssw2.py',sname, '-f', str(nStart), str(nEnd)]
            if args.neroInput:
                cmdList.append('-n')

            print cmdList
            submit = Popen(cmdList, stdout=PIPE, stderr=PIPE)
            (lout, lerr) = submit.communicate()
            # print lout, '\n'
            # print lerr, '\n'
