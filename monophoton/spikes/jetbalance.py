import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
import utils
from datasets import allsamples

import ROOT

#sname = 'sph'
#sample = ('sph-16*-m', 'monoph')
#boson = 'Photon'
#sname = 'smu'
#sample = ('smu-16*-m', 'zmumu')
#boson = 'Z'
#sname = 'znng'
#sample = ('znng-130-o', 'monoph')
#boson = 'Photon'
sname = 'wnlg'
sample = ('wnlg-130-o', 'monoph')
boson = 'Photon'

ROOT.gSystem.Load('libPandaTreeObjects.so')
e = ROOT.panda.Event

ROOT.gROOT.LoadMacro('jetbalance.cc+')

print utils.getSkimPath(*sample)

tree = ROOT.TChain('events')
tree.Add(utils.getSkimPath(*sample))

outputFile = ROOT.TFile.Open('/data/t3home000/yiiyama/monophoton/jetbalance_' + sname + '_' + boson + '.root', 'recreate')

ROOT.jetbalance(tree, outputFile, getattr(ROOT, 'b' + boson))

outputFile.Close()
