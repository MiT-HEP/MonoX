#!/usr/bin/env python

import os
import sys
import shutil
import ROOT

NENTRIES = -1

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
monoxdir = os.path.dirname(basedir)
sys.path.append(basedir)
sys.path.append(monoxdir + '/common')
from datasets import allsamples
import config
from goodlumi import makeGoodLumiFilter

ROOT.gSystem.Load(config.libobjs)
ROOT.gSystem.Load(config.libutils)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats)
ROOT.gSystem.AddIncludePath('-I' + monoxdir + '/common')

ROOT.gROOT.LoadMacro(thisdir + '/PhotonSkim.cc+')

sname = sys.argv[1]
goodlumi = None
try:
    json = sys.argv[2]
    goodlumi = makeGoodLumiFilter(json)
except:
    pass

sample = allsamples[sname]

sample.book = ''

print config.ntuplesDir + '/' + sample.book + '/' + sample.fullname

ROOT.PhotonSkim(config.ntuplesDir + '/' + sample.book + '/' + sample.fullname, '/tmp/' + sname + '.root', NENTRIES, goodlumi)

try:
    os.makedirs(config.photonSkimDir)
except OSError:
    pass

shutil.copyfile('/tmp/' + sname + '.root', config.photonSkimDir + '/' + sname + '.root')
