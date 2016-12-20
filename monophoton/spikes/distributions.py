import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas
from datasets import allsamples

lumi = sum(s.lumi for s in allsamples.getmany('sph-16*'))

canvas = SimpleCanvas(lumi = lumi)

import ROOT

spikeTree = ROOT.TChain('events')
spikeTree.Add('/data/t3home000/yiiyama/simpletree/uncleanedSkimmed/sph-16*.root')

#uncleanedTime = ROOT.TH1D('uncleanedTime', ';seed time (ns)', 100, -25., 25.)
#spikeTree.Draw('superClusters.time>>uncleanedTime', 'superClusters.rawPt > 175 && superClusters.sieie < 0.0102')
#
#uncleanedTime.SetLineColor(ROOT.kBlack)
#
#canvas.addHistogram(uncleanedTime)
#
#canvas.printWeb('spike', 'uncleanedTime')
#canvas.Clear()

ROOT.gStyle.SetNdivisions(210, 'X')

uncleanedShower = ROOT.TH1D('uncleanedShower', ';#sigma_{i#etai#eta}', 102, 0., 0.0102)
spikeTree.Draw('superClusters.sieie>>uncleanedShower', 'superClusters.rawPt > 175 && superClusters.time > -15. && superClusters.time < -10.')

uncleanedShower.SetLineColor(ROOT.kBlack)

canvas.addHistogram(uncleanedShower)

canvas.printWeb('spike', 'uncleanedShower')
