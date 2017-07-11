#!/usr/bin/env python

import sys
import os
import array
import math
import collections

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas
from tp.efake_conf import lumiSamples, outputDir, roofitDictsDir, getBinning

binningName = sys.argv[1]

binningTitle, binning, fitBins = getBinning(binningName)

if binningName == 'pt':
    binning[-1] = binning[-2] + 20.

binLabels = False
if len(binning) == 0:
    binLabels = True
    binning = range(len(fitBins) + 1)

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load(roofitDictsDir + '/libCommonRooFit.so') # defines KeysShape

ROOT.gStyle.SetNdivisions(510, 'X')

dataSource = ROOT.TFile.Open(outputDir + '/eff_data_' + binningName + '.root')
mcSource = ROOT.TFile.Open(outputDir + '/eff_mc_' + binningName + '.root')

outputFile = ROOT.TFile.Open(outputDir + '/scaleFactor_' + binningName + '.root', 'RECREATE')

dataEff = dataSource.Get('eff')
mcEff = mcSource.Get('eff')
mcTruthEff = mcSource.Get('eff_truth')

scaleFactor = dataEff.Clone('scaleFactor')
scaleFactor.Divide(mcEff)

sfTruth = dataEff.Clone('sf_truth')
sfTruth.Divide(mcTruthEff)

outputFile.cd()
scaleFactor.Write()
sfTruth.Write()
dataEff.Write('dataEff')
mcEff.Write('mcEff')
mcTruthEff.Write('mcTruthEff')

### Visualize

lumi = sum(allsamples[s].lumi for s in lumiSamples)

# scaleFactor.SetMaximum(1.05)

canvas = SimpleCanvas(lumi = lumi)
canvas.SetGrid(False, True)
canvas.legend.setPosition(0.7, 0.8, 0.9, 0.9)

canvas.legend.add('sf', 'Scale Factor', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
canvas.legend.add('sf_truth', 'MC truth', opt = 'LP', color = ROOT.kGreen, mstyle = 4)
canvas.ylimits = (0.8, 1.20)

canvas.legend.apply('sf', scaleFactor)
canvas.addHistogram(scaleFactor, drawOpt = 'EP')

canvas.legend.apply('sf_truth', sfTruth)
canvas.addHistogram(sfTruth, drawOpt = 'EP')

canvas.xtitle = binningTitle
canvas.printWeb('efake', 'scaleFactor_' + binningName, logy = False)

print 'Fit Results:'
for iBin, (bin, _) in enumerate(fitBins):
    print '%15s [%.3f +- %.3f]' % (bin, scaleFactor.GetBinContent(iBin + 1), scaleFactor.GetBinError(iBin + 1))

print '\nTruth Results:'
for iBin, (bin, _) in enumerate(fitBins):
    print '%15s [%.3f +- %.3f]' % (bin, sfTruth.GetBinContent(iBin + 1), sfTruth.GetBinError(iBin + 1))

outputFile.Close()
