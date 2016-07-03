#!/usr/bin/env python

import os
import sys
import shutil
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

ROOT.gSystem.Load(config.libsimpletree)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')

ROOT.gROOT.LoadMacro(thisdir + '/PhotonSkim.cc+')

sname = sys.argv[1]

sample = allsamples[sname]

ROOT.PhotonSkim(config.ntuplesDir + '/' + sample.book + '/' + sample.fullname, '/tmp/' + sname + '.root', -1)

shutil.copyfile('/tmp/' + sname + '.root', config.photonSkimDir + '/' + sname + '.root')
