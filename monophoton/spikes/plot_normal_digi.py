import os
import sys
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from plotstyle import WEBDIR

sourceName = sys.argv[1]

import ROOT
ROOT.gROOT.SetBatch(True)

canvas = ROOT.TCanvas('c1', 'c1', 800, 600)
canvas.SetLeftMargin(0.15)
canvas.SetRightMargin(0.15)

nx = 900
ny = 350

hist = ROOT.TH2D('pulses', ';time (ns);normalized ADC', nx, 0., 225., ny, -2., 25.)

source = ROOT.TFile.Open(sourceName)
tree = source.Get('digiTree')
adc = array.array('d', [0.] * 10)
energy = array.array('d', [0.])
tree.SetBranchAddress('adc', adc)
tree.SetBranchAddress('energy', energy)

iEntry = 0
while tree.GetEntry(iEntry) > 0:
    iEntry += 1

    if energy[0] < 150.:
        continue

    pedestal = 0.
    for i in xrange(3):
        pedestal += adc[i]

    pedestal /= 3.

    for i in xrange(9):
        x0 = i * 25.
        x1 = (i + 1) * 25.
        y0 = (adc[i] - pedestal) / energy[0]
        y1 = (adc[i + 1] - pedestal) / energy[0]
        slope = (y1 - y0) / (x1 - x0)
        for ix in range(nx / 10):
            x = x0 + ix * 25. / (nx / 10)
            y = slope * (x - x0) + y0
            hist.Fill(x, y)

# Clean out bins with contents less than 1% of maximum or just 1 entry
hist.SetContour(100)
maxcont = hist.GetMaximum()
print maxcont
#for iX in range(1, hist.GetNbinsX() + 1):
#    for iY in range(1, hist.GetNbinsY() + 1):
#        if hist.GetBinContent(iX, iY) < maxcont * 0.01 or hist.GetBinContent(iX, iY) == 1.:
#            hist.SetBinContent(iX, iY, 0.)

hist.Draw('COLZ')
canvas.Print(WEBDIR + '/spike_digis/pulses_normal.png')
canvas.Print(WEBDIR + '/spike_digis/pulses_normal.pdf')
