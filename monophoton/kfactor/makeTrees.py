import os
import sys
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

sys.path.append(basedir)

from datasets import allsamples
import config as config

ROOT.gSystem.Load('libPandaTreeObjects.so')
e = ROOT.panda.Event

ROOT.gROOT.LoadMacro('GenKinematics.cc+')

snames = ['znng-130', 'znng-130-o', 'wnlg-130', 'wnlg-130-o', 'zllg-130', 'zllg-130-o', 'znng', 'zllg', 'wnlg', 'wnlg-500', 'wglo', 'wglo-130', 'wglo-500']

outputFile = ROOT.TFile.Open(config.histDir + '/kfactor_trees.root', 'recreate')

for sname in snames:
    print sname

    sample = allsamples[sname]

    maker = ROOT.GenKinematics()

    for fname in sample.files():
        maker.addPath(fname)

    outdir = outputFile.mkdir(sname)

    maker.makeTree(outdir)

outputFile.Close()
