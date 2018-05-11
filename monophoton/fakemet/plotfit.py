import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas

import ROOT

ROOT.gROOT.SetBatch(True)

fitDiagnostics = sys.argv[1]
plots = sys.argv[2] # plots with random fakemet
name = sys.argv[3]

dist = 'mtPhoMet'
signal = 'dph-nlo-125'
region = 'gghg'

canvas = SimpleCanvas()

source = ROOT.TFile.Open(fitDiagnostics)

bkg = source.Get('shapes_fit_s/gghg/total_background')
fake = source.Get('shapes_fit_s/gghg/fakemet')
sig = source.Get('shapes_fit_s/gghg/total_signal')
data = source.Get('shapes_fit_s/gghg/data')

bkg.Add(fake, -1.)

plotsSource = ROOT.TFile.Open(plots)
bkgTrue = source.Get(dist + '/bkgtotal')
fakeTrue = source.Get(dist + '/fakemet')
sigTrue = source.Get(dist + '/samples/' + signal + '_' + region)

bkg.SetFillColor(ROOT.kGray)
bkg.SetLineColor(ROOT.kGray)
bkg.SetLineWidth(2)

fake.SetFillColor(ROOT.kRed)
fake.SetLineColor(ROOT.kRed)
fake.SetLineWidth(2)

sig.SetLineColor(ROOT.kBlue)
sig.SetLineStyle(ROOT.kDashed)
sig.SetLineWidth(2)

stack = ROOT.THStack('stack', 'stack')
stack.Add(bkg)
stack.Add(fake)
stack.Add(sig)

bkgTrue.SetLineColor(ROOT.kGreen + 2)
bkgTrue.SetLineWidth(2)

fakeTrue.SetLineColor(ROOT.kRed + 2)
fakeTrue.SetLineWidth(2)

sigTrue.SetLineColor(ROOT.kBlue + 2)
sigTrue.SetLineWidth(2)

data.SetMarkerStyle(8)
data.SetLineColor(ROOT.kBlack)
data.SetLineWidth(1)

canvas.addHistogram(stack, drawOpt = 'HIST')
canvas.addHistogram(bkgTrue, drawOpt = 'HIST')
canvas.addHistogram(fakeTrue, drawOpt = 'HIST')
canvas.addHistogram(sigTrue, drawOpt = 'HIST')
canvas.addHistogram(data, drawOpt = 'EP')

canvas.printWeb('monophoton/fakemet/fits', name, logy = False)
