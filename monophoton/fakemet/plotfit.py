import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas, DataMCCanvas

import ROOT

ROOT.gROOT.SetBatch(True)

fitDiagnostics = sys.argv[1]
plots = sys.argv[2] # plots with random fakemet
name = sys.argv[3]
sigScale = float(sys.argv[4])
fakeNorm = float(sys.argv[5])

originalMu = 0.1
dist = 'mtPhoMet'
signal = 'dph-nlo-125'
region = 'gghg'

canvas = DataMCCanvas()

source = ROOT.TFile.Open(fitDiagnostics)

bkg = source.Get('shapes_fit_s/gghg/total_background')
fake = source.Get('shapes_fit_s/gghg/fakemet')
sig = source.Get('shapes_fit_s/gghg/total_signal')
data = source.Get('shapes_fit_s/gghg/data')

bkg.Add(fake, -1.)

plotsSource = ROOT.TFile.Open(plots)
bkgTrue = plotsSource.Get(dist + '/bkgtotal')
fakeTrue = plotsSource.Get(dist + '/fakemet')
sigTrue = plotsSource.Get(dist + '/samples/' + signal + '_' + region)

canvas.legend.setPosition(0.4, 0.6, 0.9, 0.9)

canvas.addStacked(bkg, title = 'SM Bkgd.', color = ROOT.kGray, drawOpt = 'HIST')
canvas.addStacked(fake, title = 'Fake E_{T}^{miss}', color = ROOT.kRed, drawOpt = 'HIST')
canvas.addStacked(sig, title = 'H(125)', color = ROOT.kBlue, drawOpt = 'HIST')

bkgTrue.Scale(1., 'width')
fakeTrue.Scale(fakeNorm / fakeTrue.GetSumOfWeights(), 'width')
sigTrue.Scale(sigScale, 'width')

canvas.addSignal(bkgTrue, title = 'True SM Bkgd.', color = ROOT.kGreen + 2, drawOpt = 'HIST')
canvas.addSignal(fakeTrue, title = 'True Fake E_{T}^{miss}', color = ROOT.kRed + 2, drawOpt = 'HIST')
canvas.addSignal(sigTrue, title = 'True H(125)', color = ROOT.kBlue + 2, drawOpt = 'HIST')

canvas.addObs(data, drawOpt = 'EP')

canvas.title = '#sigma#timesBR = %.2f, N_{fake} = %.0f' % (originalMu * sigScale, fakeNorm)
canvas.xtitle = 'm_{T} (GeV)'
canvas.ytitle = 'Events / GeV'

canvas.printWeb('monophoton/fakemet', name, logy = False)
