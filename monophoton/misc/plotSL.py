#!/usr/bin/env python

import os
import sys
sys.dont_write_bytecode = True
import ROOT

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)

from plotstyle import SimpleCanvas

ROOT.gROOT.SetBatch(True)

inName = sys.argv[1]

inFile = ROOT.TFile.Open(inName)

covar = inFile.Get('shapes_fit_b').Get('total_covar')
covar.GetZaxis().SetLimits(1.0e-6, 0.5)
covar.SetTitle('')
# covar.GetZaxis().SetMinimum(0.)
# covar.SetLogz(True)
text = covar.Clone('total_covar_text')

canvas = SimpleCanvas(lumi = 35900., xmax = 0.90)

ROOT.gStyle.SetPaintTextFormat("7.2e");
ROOT.gStyle.SetTextSize(0.05)

canvas.addHistogram(covar, drawOpt = 'colz text')

# canvas.zlimits = (0., 1.)
canvas.xtitle = 'Bin name'
canvas.ytitle = 'Bin name'

# canvas.SetLogz(True)

canvas.printWeb('EXO16053/fit/', 'signal_covar', logy = False)
