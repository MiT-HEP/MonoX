#!/usr/bin/env python

import sys
import os
import array
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from datasets import allsamples
from plotstyle import SimpleCanvas

import ROOT

dataChain = ROOT.TChain('skimmedEvents')
dataChain.Add('/scratch5/yiiyama/studies/monophoton16/efake_skim_rawE/sel*_eg.root')
mcChain = ROOT.TChain('skimmedEvents')
mcChain.Add('/scratch5/yiiyama/studies/monophoton16/efake_skim_rawE/dy-50_eg.root')

rawPx = 'probes.scRawPt * TMath::Cos(probes.phi)'
rawPy = 'probes.scRawPt * TMath::Sin(probes.phi)'
rawPz = 'TMath::SinH(probes.eta) * probes.scRawPt'
rawE = 'TMath::CosH(probes.eta) * probes.scRawPt'

rawMass = 'TMath::Sqrt(TMath::Power(' + rawE + ' + tags.pt * TMath::CosH(tags.eta), 2.)'
rawMass += ' - TMath::Power(' + rawPx + ' + tags.pt * TMath::Cos(tags.phi), 2.)'
rawMass += ' - TMath::Power(' + rawPy + ' + tags.pt * TMath::Sin(tags.phi), 2.)'
rawMass += ' - TMath::Power(' + rawPz + ' + tags.pt * TMath::SinH(tags.eta), 2.))'

dataCorr = ROOT.TH1D('dataCorr', '', 60, 60., 120.)
dataRaw = ROOT.TH1D('dataRaw', '', 60, 60., 120.)
dataChain.Draw('tp.mass>>dataCorr', 'probes.pt > 100.', 'goff')
dataChain.Draw(rawMass + '>>dataRaw', 'probes.pt > 100.', 'goff')

canvas = SimpleCanvas()
canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
canvas.legend.add('dataCorr', title = 'Corrected', opt = 'LF', color = ROOT.kBlue, fstyle = 3003, lwidth = 2)
canvas.legend.add('dataRaw', title = 'Raw', opt = 'LF', color = ROOT.kRed, fstyle = 3003, lwidth = 2)

canvas.addHistogram(dataCorr)
canvas.addHistogram(dataRaw)

canvas.applyStyles()

canvas.printWeb('rawEScale', 'data', logy = False)

canvas.Clear()

mcCorr = ROOT.TH1D('mcCorr', '', 60, 60., 120.)
mcRaw = ROOT.TH1D('mcRaw', '', 60, 60., 120.)
mcChain.Draw('tp.mass>>mcCorr', 'probes.pt > 100.', 'goff')
mcChain.Draw(rawMass + '>>mcRaw', 'probes.pt > 100.', 'goff')

canvas = SimpleCanvas()
canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
canvas.legend.add('mcCorr', title = 'Corrected', opt = 'LF', color = ROOT.kBlue, fstyle = 3003, lwidth = 2)
canvas.legend.add('mcRaw', title = 'Raw', opt = 'LF', color = ROOT.kRed, fstyle = 3003, lwidth = 2)

canvas.addHistogram(mcCorr)
canvas.addHistogram(mcRaw)

canvas.applyStyles()

canvas.printWeb('rawEScale', 'mc', logy = False)
