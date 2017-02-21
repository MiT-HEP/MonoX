#!/usr/bin/env python

import os
import sys
import shutil
import subprocess
import collections
import time
from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Skim and slim the primary panda files into monophoton format.')
argParser.add_argument('sname', help = 'Sample name.')
argParser.add_argument('--json', '-j', metavar = 'PATH', dest = 'json', default = '', help = 'Good lumi list to apply.')
argParser.add_argument('--catalog', '-c', metavar = 'PATH', dest = 'catalog', default = '/home/cmsprod/catalog/t2mit', help = 'Source file catalog.')
argParser.add_argument('--filesets', '-f', metavar = 'ID', dest = 'filesets', nargs = '+', default = [], help = 'Fileset id (empty => all filesets).')
argParser.add_argument('--batch', '-B', action = 'store_true', dest = 'batch', help = 'Use condor-run to run the skim in parallel.')
argParser.add_argument('--merge', '-M', action = 'store_true', dest = 'merge', help = 'Run padd at the end of execution to produce a single output.')

args = argParser.parse_args()
argv = list(sys.argv)
sys.argv = []

NENTRIES = -1

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

sample = allsamples[args.sname]

try:
    os.makedirs(config.photonSkimDir)
except OSError:
    pass

outnameBase = config.photonSkimDir + '/' + args.sname

cdir = args.catalog + '/' + sample.book + '/' + sample.fullname

directories = {}
with open(cdir + '/Filesets') as filesetList:
    for line in filesetList:
        fileset, xrdpath = line.split()[:2]
        directories[fileset] = xrdpath.replace('root://xrootd.cmsaf.mit.edu/', '/mnt/hadoop/cms')

if args.batch:
    commonArgs = list(argv[1:])
    for a in ['-B', '--batch', '-M', '--merge']:
        if a in commonArgs:
            commonArgs.remove(a)

    if len(args.filesets) == 0:
        filesets = directories.keys()
    else:
        filesets = list(args.filesets)

    proc = subprocess.Popen(['/home/yiiyama/bin/condor-run', os.path.realpath(__file__), '-H', '-e', ' '.join(commonArgs), '-j'] + ['-f %s' % fileset for fileset in filesets], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = proc.communicate()
    print out.strip()
    print err.strip()

    print 'Waiting for individual skim jobs to complete'

    while True:
        for fileset in filesets:
            if not os.path.exists(outnameBase + '_' + fileset + '.root'):
                break

        else: # all files exist
            break

        time.sleep(10)

else:
    goodlumi = None
    if args.json:
        goodlumi = makeGoodLumiFilter(args.json)
    
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
        skimmer = ROOT.PhotonSkimmer()
        for fileset, paths in fullpaths.items():
            for path in paths:
                skimmer.addSourcePath(path)

        outputName = args.sname + '.root'
    
        skimmer.run('/tmp/' + args.sname + '.root', NENTRIES, goodlumi)
    
        shutil.copyfile('/tmp/' + outputName, config.photonSkimDir + '/' + outputName)
        os.remove('/tmp/' + outputName)
    
    else:
        filesets = list(args.filesets)
    
        for fileset in filesets:
            skimmer = ROOT.PhotonSkimmer()
    
            for path in fullpaths[fileset]:
                skimmer.addSourcePath(path)
    
            outputName = args.sname + '_' + fileset + '.root'
    
            skimmer.run('/tmp/' + outputName, NENTRIES, goodlumi)
    
            shutil.copyfile('/tmp/' + outputName, config.photonSkimDir + '/' + outputName)
            os.remove('/tmp/' + outputName)

if args.merge:
    proc = subprocess.Popen([os.environ['CMSSW_BASE'] + '/bin/' + os.environ['SCRAM_ARCH'] + '/padd', '/tmp/' + args.sname + '.root'] + [outnameBase + '_' + fileset + '.root' for fileset in filesets], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = proc.communicate()
    print out.strip()
    print err.strip()

    shutil.copyfile('/tmp/' + args.sname + '.root', outnameBase + '.root')
    os.remove('/tmp/' + args.sname + '.root')
