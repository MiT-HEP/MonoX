import sys
import os
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas
import tp.efake_conf as efake
import config

variable = sys.argv[1]
sys.argv = []

if variable == 'eta':
    pname = 'TMath::Abs(photons.eta[0])'
    tname = 'TMath::Abs(probes.eta)'
elif variable == 'njet':
    pname = 'jets.size'
    tname = 'jets.size'
elif variable == 'npv':
    pname = 'npv'
    tname = 'npv'
else:
    print 'Unknown variable ' + variable
    sys.exit(1)


import ROOT
ROOT.gROOT.SetBatch(True)

proxyTree = ROOT.TChain('events')
proxyTree.Add(config.skimDir + '/wlnu-100_wenu.root')
proxyTree.Add(config.skimDir + '/wlnu-200_wenu.root')
proxyTree.Add(config.skimDir + '/wlnu-400_wenu.root')
proxyTree.Add(config.skimDir + '/wlnu-600_wenu.root')

tpTree = ROOT.TChain('skimmedEvents')
tpTree.Add(efake.skimDir + '/dy-50_eg.root')

title, binningList, fitBins = efake.getBinning(variable)
binning = array.array('d', binningList)

source = ROOT.TFile.Open(efake.outputDir + '/results_data_' + variable + '.root')
frate = source.Get(variable + '_frate')

# pixel seeding efficiency for electrons
efficiency = ROOT.TH1D('efficiency', '', len(binning) - 1, binning)
inefficiency = ROOT.TH1D('inefficiency', '', len(binning) - 1, binning)

for iX in range(1, frate.GetNbinsX() + 1):
    f = frate.GetBinContent(iX)
    eff = 1. / (1. + f)
    err = eff * frate.GetBinError(iX) / (1. + f)
    efficiency.SetBinContent(iX, eff)
    efficiency.SetBinError(iX, err)
    inefficiency.SetBinContent(iX, (1. - eff) * 100.)
    inefficiency.SetBinError(iX, err * 100.)


proxyDist = ROOT.TH1D('proxy', '', len(binning) - 1, binning)
proxyDist.Sumw2()
proxyTree.Draw(pname + '>>proxy', 'weight * (photons.pt[0] > 80. && t1Met.met > 80. && t1Met.photonDPhi > 2. && t1Met.minJetDPhi > 0.5)')

tpDist = ROOT.TH1D('tp', '', len(binning) - 1, binning)

original = 0.
reweighted = 0.

counter = ROOT.TH1D('counter', '', 1, 0., 1.)

for iX in range(1, len(binning)):
    # cut is defined for each bin
    # more efficient workflow is to make a histogram from tp tree in one call, but this is easier
    cut = fitBins[iX - 1][1]
    counter.Reset()
    tpTree.Draw('0.5>>counter', 'weight * (%s)' % cut)
    ntp = counter.GetBinContent(1)

    nproxy = proxyDist.GetBinContent(iX)

    original += efficiency.GetBinContent(iX) * ntp
    reweighted += efficiency.GetBinContent(iX) * nproxy

    tpDist.SetBinContent(iX, ntp)

original /= tpDist.GetSumOfWeights() # should in principle match the nominal pT > 40 GeV efficiency
reweighted /= proxyDist.GetSumOfWeights()

print 'Original fake rate =', 1. / original - 1.
print 'Reweighted fake rate =', 1. / reweighted - 1.

proxyDist.Scale(1., 'width')
tpDist.Scale(1., 'width')
proxyDist.Scale(8. / proxyDist.GetSumOfWeights())
tpDist.Scale(8. / tpDist.GetSumOfWeights())

canvas = SimpleCanvas()
canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
canvas.legend.add('inefficiency', title = '1 - #epsilon_{e}', opt = 'LP', mstyle = 8, color = ROOT.kBlack)
canvas.legend.add('tp', title = 'T&P sample', opt = 'LF', color = ROOT.kRed - 7, fstyle = 3003, lwidth = 2)
canvas.legend.add('proxy', title = 'W#rightarrowe#nu', opt = 'LF', color = ROOT.kBlue - 7, fstyle = 3003, lwidth = 2)

canvas.addHistogram(inefficiency, drawOpt = 'EP')
canvas.addHistogram(tpDist)
canvas.addHistogram(proxyDist)
canvas.applyStyles()

canvas.ytitle = '1 - #epsilon (%)'
canvas.xtitle = title

canvas.printWeb('efake', 'convolution_' + variable, logy = False)
