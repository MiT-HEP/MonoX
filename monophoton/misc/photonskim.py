#!/usr/bin/env python

import os
import sys
import shutil
import subprocess
import collections
import time
from argparse import ArgumentParser

NENTRIES = -1

padd = os.environ['CMSSW_BASE'] + '/bin/' + os.environ['SCRAM_ARCH'] + '/padd'
condor_run = '/home/yiiyama/bin/condor-run'

argParser = ArgumentParser(description = 'Skim and slim the primary panda files into monophoton format.')
argParser.add_argument('sname', help = 'Sample name.')
argParser.add_argument('--json', '-j', metavar = 'PATH', dest = 'json', default = '', help = 'Good lumi list to apply.')
argParser.add_argument('--catalog', '-c', metavar = 'PATH', dest = 'catalog', default = '/home/cmsprod/catalog/t2mit', help = 'Source file catalog.')
argParser.add_argument('--filesets', '-f', metavar = 'ID', dest = 'filesets', nargs = '+', default = [], help = 'Fileset id (empty => all filesets).')
argParser.add_argument('--split', '-B', action = 'store_true', dest = 'split', help = 'Use condor-run to run the skim in parallel.')
argParser.add_argument('--merge', '-M', action = 'store_true', dest = 'merge', help = 'Run padd at the end of execution to produce a single output.')

args = argParser.parse_args()
argv = list(sys.argv)
sys.argv = []

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
monoxdir = os.path.dirname(basedir)
sys.path.append(basedir)
sys.path.append(monoxdir + '/common')
from datasets import allsamples
import config
from goodlumi import makeGoodLumiFilter

import ROOT
ROOT.gSystem.Load(config.libobjs)
ROOT.gSystem.Load(config.libutils)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats)
ROOT.gSystem.AddIncludePath('-I' + monoxdir + '/common')

ROOT.gROOT.LoadMacro(thisdir + '/PhotonSkim.cc+')
ROOT.PhotonSkimmer # force crash if compilation fails

sample = allsamples[args.sname]

splitOutDir = config.photonSkimDir + '/' + args.sname

if len(args.filesets) != 0:
    outDir = splitOutDir
else:
    outDir = config.photonSkimDir

try:
    os.makedirs(outDir)
except OSError:
    pass

cdir = args.catalog + '/' + sample.book + '/' + sample.fullname

directories = {}
with open(cdir + '/Filesets') as filesetList:
    for line in filesetList:
        fileset, xrdpath = line.split()[:2]
        directories[fileset] = xrdpath.replace('root://xrootd.cmsaf.mit.edu/', '/mnt/hadoop/cms')

if args.split:
    commonArgs = list(argv[1:])
    for a in ['-B', '--split', '-M', '--merge']:
        if a in commonArgs:
            commonArgs.remove(a)

    if len(args.filesets) == 0:
        filesets = directories.keys()
    else:
        filesets = list(args.filesets)

    # remove the output first
    for fileset in filesets:
        path = splitOutDir + '/' + args.sname + '_' + fileset + '.root'
        try:
            os.remove(path)
        except:
            pass

    proc = subprocess.Popen([condor_run, os.path.realpath(__file__), '-H', '-e', ' '.join(commonArgs), '-j'] + ['-f %s' % fileset for fileset in filesets], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = proc.communicate()
    print out.strip()
    print err.strip()

    print 'Waiting for individual skim jobs to complete'

    while True:
        for fileset in filesets:
            path = splitOutDir + '/' + args.sname + '_' + fileset + '.root'
            if not os.path.exists(path) or os.stat(path).st_size == 0:
                break

        else: # all files exist
            break

        time.sleep(10)

else:
    fullpaths = collections.defaultdict(list)
    
    with open(cdir + '/Files') as fileList:
        for line in fileList:
            fileset, fname = line.split()[:2]
    
            fullpath = directories[fileset] + '/' + fname
            if not os.path.exists(fullpath):
                proc = subprocess.Popen(['/usr/local/DynamicData/SmartCache/Client/addDownloadRequest.py', '--file', fname, '--dataset', sample.fullname, '--book', sample.book], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                print proc.communicate()[0].strip()
    
            fullpaths[fileset].append(fullpath)
    
    if len(args.filesets) == 0:
        allpaths = {'': sum(paths for paths in fullpaths.values())}
    else:
        allpaths = {}
        for fileset, paths in fullpaths.items():
            if fileset in args.filesets:
                allpaths['_%s' % fileset] = paths

    for suffix, paths in allpaths.items():
        skimmer = ROOT.PhotonSkimmer()
        for path in paths:
            skimmer.addSourcePath(path)

        if args.json:
            skimmer.setLumiFilter(makeGoodLumiFilter(args.json))

        outputName = args.sname + suffix + '.root'

        skimmer.run('/tmp/' + outputName, True, NENTRIES)

        # shutil.move fails if the destination exists already
        shutil.copy('/tmp/' + outputName, outDir)
        os.remove('/tmp/' + outputName)
    
if args.merge:
    if len(args.filesets) == 0:
        filesets = directories.keys()
    else:
        filesets = args.filesets

    outputName = args.sname + '.root'

    skimmer = ROOT.PhotonSkimmer()
    for fileset in filesets:
        skimmer.addSourcePath(splitOutDir + '/' + args.sname + '_' + fileset + '.root')

    skimmer.run('/tmp/' + outputName, False)

    shutil.copy('/tmp/' + outputName, config.photonSkimDir)
    os.remove('/tmp/' + outputName)
