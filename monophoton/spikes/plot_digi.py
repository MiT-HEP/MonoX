import os
import sys
import array
import math

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from plotstyle import WEBDIR

import ROOT
ROOT.gROOT.SetBatch(True)

canvas = ROOT.TCanvas('c1', 'c1', 800, 600)
canvas.SetLeftMargin(0.15)
canvas.SetRightMargin(0.15)

nx = 900
ny = 350

outputFile = ROOT.TFile.Open('/data/t3home000/yiiyama/spike/spikes_sph_wide.root', 'recreate')
#outputFile = ROOT.TFile.Open('/data/t3home000/yiiyama/spike/spikes.root', 'recreate')

hists_list = [
    ROOT.TH2D('pulses', ';time (ns);normalized ADC', nx, -125., 125., ny, -0.1, 1.3),
    ROOT.TH2D('pulses_below10', ';time (ns);normalized ADC', nx, -125., 125., ny, -0.1, 1.3),
    ROOT.TH2D('pulses_above10', ';time (ns);normalized ADC', nx, -125., 125., ny, -0.1, 1.3),
    ROOT.TH2D('pulsesns', ';time (ns);normalized ADC', nx, -125., 125., ny, -0.1, 1.3),
    ROOT.TH2D('pulsesns_below10', ';time (ns);normalized ADC', nx, -125., 125., ny, -0.1, 1.3),
    ROOT.TH2D('pulsesns_above10', ';time (ns);normalized ADC', nx, -125., 125., ny, -0.1, 1.3),
    ROOT.TH1D('alpha', ';#alpha', 100, 0., 2.),
    ROOT.TH1D('beta', ';#beta', 100, 1., 4.),
    ROOT.TH2D('alphabeta', ';#alpha;#beta', 100, 0., 2., 100, 1., 4.),
    ROOT.TH1D('t0', ';t_{0}', 100, -25., 25.)
]

hists = dict((h.GetName(), h) for h in hists_list)

tree = ROOT.TChain('hits')
tree.Add('/data/t3home000/yiiyama/spike/SinglePhoton.root')
#tree.Add('/data/t3home000/yiiyama/spike/JetHT.root')
#tree.Add('/data/t3home000/yiiyama/spike/SingleMuon.root')

sieie = array.array('f', [0.])
sipip = array.array('f', [0.])
ieta = array.array('h', [0])
iphi = array.array('h', [0])
pedestal = array.array('d', [0.])
amps = array.array('d', [0.] * 10)
height = array.array('d', [0.])
alpha = array.array('d', [0.])
beta = array.array('d', [0.])
t0 = array.array('d', [0.])
torig = array.array('f', [0.])

tree.SetBranchAddress('sieie', sieie)
tree.SetBranchAddress('sipip', sipip)
tree.SetBranchAddress('ieta', ieta)
tree.SetBranchAddress('iphi', iphi)
tree.SetBranchAddress('pedestal', pedestal)
tree.SetBranchAddress('amps', amps)
tree.SetBranchAddress('height', height)
tree.SetBranchAddress('alpha', alpha)
tree.SetBranchAddress('beta', beta)
tree.SetBranchAddress('t0', t0)
tree.SetBranchAddress('torig', torig)

iEntry = 0
while tree.GetEntry(iEntry) > 0:
    iEntry += 1

#    if (sieie[0] > 0.001 and sipip[0] > 0.008) or (sieie[0] > 0.008 and sipip[0] > 0.001):
    if sieie[0] < 0.01:
        continue

    for i in xrange(10):
        x0 = (i - t0[0]) * 25.
        y0 = (amps[i] - pedestal[0]) / height[0]
        hists['pulses'].Fill(x0, y0)
        hists['pulsesns'].Fill((i - 5.) * 25., y0)
        if (t0[0] - 5.) * 25. > -10.:
            hists['pulses_above10'].Fill(x0, y0)
            hists['pulsesns_above10'].Fill((i - 5.) * 25., y0)
        else:
            hists['pulses_below10'].Fill(x0, y0)
            hists['pulsesns_below10'].Fill((i - 5.) * 25., y0)

    hists['alpha'].Fill(alpha[0])
    hists['beta'].Fill(beta[0])
    hists['alphabeta'].Fill(alpha[0], beta[0])
    hists['t0'].Fill((t0[0] - 5.) * 25.)

# Clean out bins with contents less than 1% of maximum or just 1 entry
#for hist in [trivial, physical, intime]:
#    hist.SetContour(100)
#    maxcont = hist.GetMaximum()
#    print maxcont
#    for iX in range(1, hist.GetNbinsX() + 1):
#        for iY in range(1, hist.GetNbinsY() + 1):
#            if hist.GetBinContent(iX, iY) < maxcont * 0.01 or hist.GetBinContent(iX, iY) == 1.:
#                hist.SetBinContent(iX, iY, 0.)

#for hist in hists:
#    if hist.IsA() == ROOT.TH2D.Class():
#        hist.Draw('COLZ')
#    else:
#        hist.Draw('HIST')
#
#    canvas.Print(WEBDIR + '/singlemu_digis_shifted/' + hist.GetName() + '.png')
#    canvas.Print(WEBDIR + '/singlemu_digis_shifted/' + hist.GetName() + '.pdf')

outputFile.cd()
outputFile.Write()
outputFile.Close()
