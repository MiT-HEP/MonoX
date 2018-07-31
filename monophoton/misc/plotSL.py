#!/usr/bin/env python

import os
import sys
sys.dont_write_bytecode = True
import ROOT

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)

from plotstyle import TwoDimCanvas

ROOT.gROOT.SetBatch(True)

inName = sys.argv[1]

inFile = ROOT.TFile.Open(inName)

covar = inFile.Get('shapes_fit_b').Get('total_covar')
covar.SetTitle('')
covar.SetMarkerSize(0.7)

for iX in range(1, covar.GetNbinsX() + 1):
    for iY in range(1, covar.GetNbinsY() + 1):
        if iY > iX:
            covar.SetBinContent(iX, iY, 0.)
            covar.SetBinError(iX, iY, 0.)

text = covar.Clone('total_covar_text')

canvas = TwoDimCanvas(lumi = 35900., xmax = 0.85, prelim = False)

ROOT.gStyle.SetPaintTextFormat("7.2e");

canvas.addHistogram(covar, drawOpt = 'colz text')

canvas.zlimits = (1.0e-7, 1.0)
canvas.xtitle = 'Bin name'
canvas.ytitle = 'Bin name'

canvas.printWeb('EXO16053/fit/', 'signal_covar', logz = True)
