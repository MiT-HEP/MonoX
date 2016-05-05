# Trigger efficiency measurement using X+photon events

import os
import sys
import array

import ROOT
ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas

tree = ROOT.TChain('events')

tree.Add('/scratch5/yiiyama/hist/triggertree/t2mit/filefi/042/' + allsamples['sph-d3'].directory + '/l1t_*.root')
tree.Add('/scratch5/yiiyama/hist/triggertree/t2mit/filefi/042/' + allsamples['sph-d4'].directory + '/l1t_*.root')

binning = array.array('d', [30. + 5. * x for x in range(14)] + [100. + 10. * x for x in range(10)] + [200. + 20. * x for x in range(5)])

passing = ROOT.TH1D('passing', ';p_{T}^{#gamma} (GeV)', len(binning) - 1, binning)
denom = ROOT.TH1D('denom', ';p_{T}^{#gamma} (GeV)', len(binning) - 1, binning)

tree.Draw('pt>>denom')
tree.Draw('pt>>passing', 'l1dr2 < 0.25')

eff = ROOT.TGraphAsymmErrors(passing, denom)

canvas = SimpleCanvas(lumi = allsamples['sph-d3'].lumi + allsamples['sph-d4'].lumi)
canvas.legend.setPosition(0.7, 0.3, 0.9, 0.5)
canvas.legend.add('eff', title = 'L1 seed', opt = 'LP', color = ROOT.kBlack, mstyle = 8)

canvas.SetGrid()

canvas.legend.apply('eff', eff)

canvas.addHistogram(eff, drawOpt = 'EP')
canvas.addLine(0., 1., 300., 1.)
eff.GetXaxis().SetLimits(0., 300.)

canvas.xtitle = 'p_{T}^{#gamma} (GeV)'
canvas.ytitle = 'L1 seed eff.'

canvas.ylimits = (0., 1.2)

canvas.printWeb('trigger', 'l1seed', logy = False)
