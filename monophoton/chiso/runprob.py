import os
import sys
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas, RatioCanvas
import config

import ROOT

tree = ROOT.TChain('events')
tree.Add('/local/yiiyama/skims/sph-16*_hfake.root')

wsource = ROOT.TFile.Open(basedir + '/data/vertex_scores.root')

outputFile = ROOT.TFile.Open('/data/t3home000/yiiyama/pvprob.root', 'recreate')

ROOT.gSystem.Load('libPandaTreeObjects.so')

ROOT.gROOT.LoadMacro('prob.cc+')

ROOT.pvprob(tree, wsource, outputFile)

outputFile.cd()
outputFile.Write()
