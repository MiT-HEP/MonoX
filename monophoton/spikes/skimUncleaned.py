#!/usr/bin/env python

import os
import sys
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

import ROOT

sname = sys.argv[1]

ROOT.gSystem.Load(config.libobjs)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats)

try:
    e = ROOT.panda.Event
except AttributeError:
    pass

ROOT.gROOT.LoadMacro(thisdir + '/skimUncleaned.cc+')

tree = ROOT.TChain('events')

datadir = '/mnt/hadoop/scratch/yiiyama/ftpanda'

# Good lumi JSON already applied at source
if sname == 'sph-16b-m':
    tree.Add(datadir + '/SinglePhoton+Run2016B-23Sep2016-v3+AOD/*.root')
elif sname == 'sph-16c-m':
    tree.Add(datadir + '/SinglePhoton+Run2016C-23Sep2016-v1+AOD/*.root')
elif sname == 'sph-16d-m':
    tree.Add(datadir + '/SinglePhoton+Run2016D-23Sep2016-v1+AOD/*.root')
elif sname == 'sph-16e-m':
    tree.Add(datadir + '/SinglePhoton+Run2016E-23Sep2016-v1+AOD/*.root')
elif sname == 'sph-16f-m':
    tree.Add(datadir + '/SinglePhoton+Run2016F-23Sep2016-v1+AOD/*.root')
elif sname == 'sph-16g-m':
    tree.Add(datadir + '/SinglePhoton+Run2016G-23Sep2016-v1+AOD/*.root')
elif sname == 'sph-16h-m':
    tree.Add(datadir + '/SinglePhoton+Run2016H-23Sep2016-v2+AOD/*.root')
    tree.Add(datadir + '/SinglePhoton+Run2016H-PromptReco-v3+AOD/*.root')
    tree.Add(datadir + '/SinglePhoton+Run2016H-PromptReco-v2+AOD/*.root')

fname = sname + '_offtime.root'
tmpname = '/local/yiiyama/' + sname + '/' + fname
finalname = '/mnt/hadoop/scratch/' + os.environ['USER'] + '/monophoton/skim/' + fname

outputFile = ROOT.TFile.Open(tmpname, 'recreate')

ROOT.skimUncleaned(tree, outputFile)

outputFile.Close()

shutil.copy(tmpname, finalname)
os.remove(tmpname)
