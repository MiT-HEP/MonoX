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
from tp.efake_conf import lumiSamples, outputName, outputDir, roofitDictsDir, getBinning

binningName = sys.argv[1]

ADDFIT = False

binningTitle, binning, fitBins = getBinning(binningName)

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
canvas.ylimits = (0.9, 1.10)

canvas.legend.apply('sf', scaleFactor)
canvas.addHistogram(scaleFactor, drawOpt = 'EP')

canvas.legend.apply('sf_truth', sfTruth)
canvas.addHistogram(sfTruth, drawOpt = 'EP')

if ADDFIT:
    power = ROOT.TF1('power', '[0] + [1] / (x - [2])', scaleFactor.GetXaxis().GetXmin(), scaleFactor.GetXaxis().GetXmax())
    power.SetParameters(0.02, 1., 0.)
    power.SetParLimits(2, -175., 10000.)

    quad = ROOT.TF1('quad', '[0] + [1] * x + [2] * x**2', scaleFactor.GetXaxis().GetXmin(), scaleFactor.GetXaxis().GetXmax())
    quad.SetParameters(1., 0.001, 0.00001)

    function = quad

    scaleFactor.Fit(function)
    canvas.addObject(function)

    """
    text = 'f = %.4f + #frac{%.3f}{p_{T}' % (function.GetParameter(0), function.GetParameter(1))
    if function.GetParameter(2) >= 0.:
        text += ' - %.2f}' % function.GetParameter(2)
    else:
        text += ' + %.2f}' % (-function.GetParameter(2))
    """
    text = 'f = %.4f + %.4f * p_{T} + %.4f * p_{T}^{2}' % (function.GetParameter(0), function.GetParameter(1), function.GetParameter(2))

    canvas.addText(text, 0.3, 0.3, 0.5, 0.2)

canvas.xtitle = binningTitle
canvas.printWeb(outputName, 'scaleFactor_' + binningName, logy = False)

print 'Fit Results:'
for iBin, (bin, _) in enumerate(fitBins):
    print '%15s [%.3f +- %.3f]' % (bin, scaleFactor.GetBinContent(iBin + 1), scaleFactor.GetBinError(iBin + 1))

print '\nTruth Results:'
for iBin, (bin, _) in enumerate(fitBins):
    print '%15s [%.3f +- %.3f]' % (bin, sfTruth.GetBinContent(iBin + 1), sfTruth.GetBinError(iBin + 1))

outputFile.Close()
