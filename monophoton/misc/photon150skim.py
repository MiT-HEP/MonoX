#!/usr/bin/env python

import os
import sys
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

sname = sys.argv[1]

sample = allsamples[sname]

source = ROOT.TChain('events')
source.Add(config.ntuplesDir + '/' + sample.directory + '/simpletree_*.root')

print 'Sample ' + sname + ': ' + str(source.GetEntries()) + ' events'

output = ROOT.TFile.Open(config.phskimDir + '/' + sname + '.root', 'recreate')
outtree = source.CopyTree('Sum$(photons.pt > 150.) != 0')
output.Write()

print ' Reduced to ' + str(outtree.GetEntries()) + ' events'
