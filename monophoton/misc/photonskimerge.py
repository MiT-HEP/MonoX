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

ROOT.gSystem.Load(config.libsimpletree)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')
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

skimmer = ROOT.PhotonSkimmer()

secondary = ROOT.TChain('events')
gsfix = '/data/t3serv014/yiiyama/hist/simpletree19/gsfix'
for fname in os.listdir(gsfix):
    if fname.startswith(sample.fullname):
        print fname
        secondary.Add(gsfix + '/' + fname)
    elif fname.startswith(sample.fullname.replace('-v1', '-v2')):
        print fname
        secondary.Add(gsfix + '/' + fname)
    elif fname.startswith(sample.fullname.replace('-v1', '-v3')):
        print fname
        secondary.Add(gsfix + '/' + fname)

print secondary.GetEntries(), 'secondary entries'
        
skimmer.setSecondaryInput(secondary)

if goodlumi:
    skimmer.run(config.ntuplesDir + '/' + sample.book + '/' + sample.fullname, '/tmp/' + sname + '.root', NENTRIES, goodlumi)
else:
    skimmer.run(config.ntuplesDir + '/' + sample.book + '/' + sample.fullname, '/tmp/' + sname + '.root', NENTRIES)

config.photonSkimDir = '/data/t3home000/yiiyama/simpletree19/photonskim_gsfix'

try:
    os.makedirs(config.photonSkimDir)
except OSError:
    pass

shutil.copyfile('/tmp/' + sname + '.root', config.photonSkimDir + '/' + sname + '.root')
