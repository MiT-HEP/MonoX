#!/usr/bin/env python

import os
import sys

import ROOT
ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from main.plotconfig import getConfig
import config
import utils
import main.plot
import collections

region = 'monoph'
plotConfig = getConfig(region)
lumi = plotConfig.fullLumi()
outFile = ROOT.TFile.Open('../data/genReweight.root')

ptdef = plotConfig.getPlot('phoPtHighMet')

samples = plotConfig.findGroup('dmvlo').samples + plotConfig.findGroup('dmalo').samples

for sample in samples:
    sourceName = utils.getSkimPath(sample.name, region, config.skimDir, '')

    dname = sample.name + '_' + region

    print '   ', dname, '(%s)' % sourceName
    
    if not os.path.exists(sourceName):
        sys.stderr.write('File ' + sourceName + ' does not exist.\n')
        raise RuntimeError('InvalidSource')

    cuts = []
    if plotConfig.baseline.strip():
        cuts.append('(' + plotConfig.baseline.strip() + ')')

    if plotConfig.fullSelection.strip():
        cuts.append('(' + plotConfig.fullSelection.strip() + ')')

    cuts.append('(genParticles.pt_[photons.matchedGen_[0]] > 170. && genMet.pt > 130.)')

    sel = ' && '.join(cuts)

    weight = '(weight * ' + str(lumi) + ')'

    expr = plotConfig.expr + ':genParticles.pt_[photons.matchedGen_[0]' 
