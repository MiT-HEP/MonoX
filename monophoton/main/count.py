#!/usr/bin/env python

import sys
import os
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

sname = sys.argv[1]

source = ROOT.TFile.Open(config.skimDir + '/' + sname + '_monoph.root')
tree = source.Get('events')

counter = ROOT.TH1D('counter', '', 1, 0., 1.)
tree.Draw('0.5>>counter', 'weight * (photons.pt[0] > 175 && t1Met.met > 170 && t1Met.photonDPhi > 2 && t1Met.minJetDPhi > 0.5)', 'goff')

print sname, counter.GetBinContent(1)
