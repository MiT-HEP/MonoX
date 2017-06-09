import os
import sys
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from datasets import allsamples

import ROOT

ROOT.gSystem.Load('libPandaTreeObjects.so')
e = ROOT.panda.Event

ROOT.gROOT.LoadMacro('randomcone.cc+')

outputFile = ROOT.TFile.Open(basedir + '/data/randomcone.root', 'recreate')
hist = None

# to save time, we collect 10 * lumi * pb from each sample
for run in ['b', 'c', 'd', 'e', 'f', 'g', 'h']:
    calc = ROOT.RandomConeIso()
    calc.addPath(config.skimDir + '/smu-16' + run + '-m_zmumu.root')

    sample = allsamples['sph-16' + run + '-m']

    h = calc.run(int(10 * sample.lumi), False)
    if hist is None:
        outputFile.cd()
        hist = h.Clone()
    else:
        hist.Add(h)

    h.Delete()

for iX in range(1, hist.GetNbinsX() + 1):
    sliceTotal = 0.
    for iY in range(1, hist.GetNbinsY() + 1):
        sliceTotal += hist.GetBinContent(iX, iY)

    for iY in range(1, hist.GetNbinsY() + 1):
        hist.SetBinContent(iX, iY, hist.GetBinContent(iX, iY) / sliceTotal)

outputFile.cd()
hist.Write()
