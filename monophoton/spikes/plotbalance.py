import sys
import array
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import RatioCanvas

import ROOT

ROOT.gStyle.SetNdivisions(510, 'X')

zsource = ROOT.TFile.Open(config.histDir + '/jetbalance_smu_Z.root')
gsource = ROOT.TFile.Open(config.histDir + '/jetbalance_sph_Photon.root')

binning = array.array('d', [0.1 * x for x in xrange(10)] + [1., 1.2, 1.5, 2., 6.])

ztree = zsource.Get('events')
zhist = ROOT.TH1D('z', ';J/p_{T}^{j}', len(binning) - 1, binning)
zhist.Sumw2()
ztree.Draw('balance / jets.pt_[0]>>z', 'muons.size == 2 && TMath::Abs(TVector2::Phi_mpi_pi(dimu.phi - t1Met.phi)) > 2.6416', 'goff')
zhist.Scale(1. / zhist.GetSumOfWeights())
zhist.Scale(1., 'width')

gtree = gsource.Get('events')
ghist = ROOT.TH1D('g', ';J/p_{T}^{j}', len(binning) - 1, binning)
ghist.Sumw2()
gtree.Draw('balance / jets.pt_[0]>>g', 'TMath::Abs(TVector2::Phi_mpi_pi(photons.phi_[0] - t1Met.phi)) > 2.6416', 'goff')
ghist.Scale(1. / ghist.GetSumOfWeights())
ghist.Scale(1., 'width')

canvas = RatioCanvas()
canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
canvas.legend.add('z', 'Z+jet', opt = 'LF', color = ROOT.kBlue, lwidth = 2, mstyle = 0)
canvas.legend.add('g', '#gamma+jet', opt = 'L', color = ROOT.kRed, lwidth = 2, mstyle = 0)

canvas.legend.apply('z', zhist)
canvas.legend.apply('g', ghist)

zerr = zhist.Clone('zerr')
zerr.SetFillStyle(3003)

rList = [0] * 3

rList[1] = canvas.addHistogram(zerr, drawOpt = 'E2')
rList[0] = canvas.addHistogram(zhist, drawOpt = 'HIST')
rList[2] = canvas.addHistogram(ghist, drawOpt = 'HIST E')

canvas.printWeb('jetbalance', 'zgcomp', rList = rList)
