import os
import sys
import array
import math

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

hists_trivial = [
    ROOT.TH2D('pulses_trivial', ';time (ns);normalized ADC', nx, 0., 225., ny, -0.1, 1.3),
    ROOT.TH1D('alpha_trivial', ';#alpha', 100, 0., 2.),
    ROOT.TH1D('beta_trivial', ';#beta', 100, 1., 4.),
    ROOT.TH2D('alphabeta_trivial', ';#alpha;#beta', 100, 0., 2., 100, 1., 4.),
    ROOT.TH1D('t0_trivial', ';t_{0}', 100, 0., 10.)
]

hists_physical = [
    ROOT.TH2D('pulses_physical', ';time (ns);normalized ADC', nx, 0., 225., ny, -0.1, 1.3),
    ROOT.TH1D('alpha_physical', ';#alpha', 100, 0., 2.),
    ROOT.TH1D('beta_physical', ';#beta', 100, 1., 4.),
    ROOT.TH2D('alphabeta_physical', ';#alpha;#beta', 100, 0., 2., 100, 1., 4.),
    ROOT.TH1D('t0_physical', ';t_{0}', 100, 0., 10.)
]

source = ROOT.TFile.Open(sourceName)
tree = source.Get('digiTree')
amplitude = array.array('d', [4000.])
adc = array.array('d', [0.] * 10)
sieie = array.array('d', [0.])
tree.SetBranchAddress('amplitude', amplitude)
tree.SetBranchAddress('adc', adc)
tree.SetBranchAddress('sieie', sieie)

func = ROOT.TF1('pulse', '[0] * TMath::Power(TMath::Max(0., 1. + (x - [3]) / [1] / [2]), [1]) * TMath::Exp(-(x - [3]) / [2])')

iEntry = 8
while tree.GetEntry(iEntry) > 0:
    iEntry += 1

    if amplitude[0] < 3000.:
        continue

    pmin = min(adc[:3])
    pmax = max(adc[:3])
    if pmax - pmin > 5.:
        continue

    pedestal = sum(adc[:3]) / 3.

    graph = ROOT.TGraphErrors(7)
    #graph.SetMarkerStyle(34)

    for i in xrange(3, 10):
        graph.SetPoint(i - 3, float(i), max(0., adc[i] - pedestal))
        graph.SetPointError(i - 3, 0., 3.)

    func.SetParameters(amplitude[0], 1., 1.7, 4.5)

    graph.Fit(func)

#    graph.GetXaxis().SetLimits(2.5, 9.5)
#    func.SetRange(2.5, 9.5)
#
#    graph.Draw('AP')
#    func.Draw('SAME')
#
#    canvas.Update()
#    
#    r = sys.stdin.readline().strip()
#    if r == 'q':
#        sys.exit(0)
#    else:
#        continue

    amp = func.GetParameter(0)
    alpha = func.GetParameter(1)
    beta = func.GetParameter(2)
    t0 = func.GetParameter(3)

    if sieie[0] < 0.001:
        hists = hists_trivial
    else:
        hists = hists_physical

    for i in xrange(10):
        x0 = (i - t0 + 4.) * 25.
        y0 = (adc[i] - pedestal) / amp
        hists[0].Fill(x0, y0)

    hists[1].Fill(alpha)
    hists[2].Fill(beta)
    hists[3].Fill(alpha, beta)
    hists[4].Fill(t0)

# Clean out bins with contents less than 1% of maximum or just 1 entry
#for hist in [trivial, physical, intime]:
#    hist.SetContour(100)
#    maxcont = hist.GetMaximum()
#    print maxcont
#    for iX in range(1, hist.GetNbinsX() + 1):
#        for iY in range(1, hist.GetNbinsY() + 1):
#            if hist.GetBinContent(iX, iY) < maxcont * 0.01 or hist.GetBinContent(iX, iY) == 1.:
#                hist.SetBinContent(iX, iY, 0.)

for hists in [hists_trivial, hists_physical]:
    for hist in hists:
        if hist.IsA() == ROOT.TH2D.Class():
            hist.Draw('COLZ')
        else:
            hist.Draw('HIST')

        canvas.Print(WEBDIR + '/normal_digis_shifted/' + hist.GetName() + '.png')
        canvas.Print(WEBDIR + '/normal_digis_shifted/' + hist.GetName() + '.pdf')
