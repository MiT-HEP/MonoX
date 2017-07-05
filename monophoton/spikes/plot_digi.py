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

trivial = ROOT.TH2D('trivial', ';time (ns);normalized ADC', nx, 0., 225., ny, -0.1, 1.3)
physical = ROOT.TH2D('physical', ';time (ns);normalized ADC', nx, 0., 225., ny, -0.1, 1.3)
intime = ROOT.TH2D('intime', ';time (ns);normalized ADC', nx, 0., 225., ny, -0.1, 1.3)

source = ROOT.TFile.Open(sourceName)
tree = source.Get('digiTree')
adc = array.array('d', [0.] * 10)
pedestal = array.array('d', [0.])
amplitude = array.array('d', [0.])
sieie = array.array('d', [0.])
jitter = array.array('d', [0.])
tree.SetBranchAddress('adc', adc)
tree.SetBranchAddress('pedestal', pedestal)
tree.SetBranchAddress('amplitude', amplitude)
tree.SetBranchAddress('sieie', sieie)
tree.SetBranchAddress('jitter', jitter)

iEntry = 0
while tree.GetEntry(iEntry) > 0:
    iEntry += 1

    if amplitude[0] < 3000.:
        continue

    if abs(jitter[0]) < 0.15:
        hist = intime
    elif sieie[0] < 0.001:
        hist = trivial
    else:
        hist = physical

    for i in xrange(9):
        x0 = i * 25.
        x1 = (i + 1) * 25.
        y0 = (adc[i] - pedestal[0]) / amplitude[0]
        y1 = (adc[i + 1] - pedestal[0]) / amplitude[0]
        slope = (y1 - y0) / (x1 - x0)
        for ix in range(nx / 10):
            x = x0 + ix * 25. / (nx / 10)
            y = slope * (x - x0) + y0
            hist.Fill(x, y)

# Clean out bins with contents less than 1% of maximum or just 1 entry
for hist in [trivial, physical, intime]:
    hist.SetContour(100)
    maxcont = hist.GetMaximum()
    print maxcont
#    for iX in range(1, hist.GetNbinsX() + 1):
#        for iY in range(1, hist.GetNbinsY() + 1):
#            if hist.GetBinContent(iX, iY) < maxcont * 0.01 or hist.GetBinContent(iX, iY) == 1.:
#                hist.SetBinContent(iX, iY, 0.)

trivial.Draw('COLZ')
canvas.Print(WEBDIR + '/spike_digis/pulses_trivial.png')
canvas.Print(WEBDIR + '/spike_digis/pulses_trivial.pdf')
physical.Draw('COLZ')
canvas.Print(WEBDIR + '/spike_digis/pulses_physical.png')
canvas.Print(WEBDIR + '/spike_digis/pulses_physical.pdf')
intime.Draw('COLZ')
canvas.Print(WEBDIR + '/spike_digis/pulses_intime.png')
canvas.Print(WEBDIR + '/spike_digis/pulses_intime.pdf')
