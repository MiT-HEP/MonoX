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

sname = sys.argv[1]

sample = allsamples[sname]

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')

ROOT.gROOT.LoadMacro(thisdir + '/PhotonSkim.cc+')

ROOT.PhotonSkim(config.ntuplesDir + '/' + sample.book + '/' + sample.fullname, '/tmp/' + sname + '.root', -1)

shutil.copyfile('/tmp/' + sname + '.root', '/scratch5/yiiyama/hist/simpletree18/photonskim/' + sname + '.root')
