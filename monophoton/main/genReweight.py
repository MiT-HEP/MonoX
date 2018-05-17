#!/usr/bin/env python

import os
import sys
import array

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

outFile = ROOT.TFile.Open('../data/genReweight.root', 'recreate')

region = 'monoph'
plotConfig = getConfig(region)

lumi = plotConfig.fullLumi()
samples = plotConfig.findGroup('dmvlo').samples + plotConfig.findGroup('dmalo').samples
nloSamples = [s.name for s in plotConfig.findGroup('dmvh').samples + plotConfig.findGroup('dmah').samples]

ptdef = plotConfig.getPlot('phoPtHighMet')
xbins = array.array('d', [130] + ptdef.binning)
ybins = array.array('d', ptdef.binning)

cuts = []
if plotConfig.baseline.strip():
    cuts.append('(' + plotConfig.baseline.strip() + ')')

if plotConfig.fullSelection.strip():
    cuts.append('(' + plotConfig.fullSelection.strip() + ')')

if ptdef.cut.strip():
    cuts.append('(' + ptdef.cut.strip() + ')')

recoSel = ' && '.join(cuts)

cuts.append('(genPhoton.pt > 170. && genMet.pt > 130.)')

genSel = ' && '.join(cuts)

weight = '(weight * ' + str(lumi) + ')'
genSelString = weight + ' * ' + genSel
recoSelString = weight + ' * ' + recoSel

expr = ptdef.expr + ':genPhoton.pt' 

print expr
print genSelString
print recoSelString

for sample in samples:
    sourceName = utils.getSkimPath(sample.name, region, config.skimDir, '')
    dname = sample.name + '_' + region

    print '   ', dname, '(%s)' % sourceName
    
    if not os.path.exists(sourceName):
        sys.stderr.write('File ' + sourceName + ' does not exist.\n')
        raise RuntimeError('InvalidSource')

    source = ROOT.TFile.Open(sourceName)
    events = source.Get('events')
    hist = ROOT.TH2D(dname, dname, len(xbins)-1, xbins, len(ybins)-1, ybins)

    events.Draw(expr + '>>' + dname, genSelString, 'colz')

    outFile.cd()
    hist.Write()

for sample in samples:
    nloname = sample.name.replace('lo', 'h')
    if nloname not in nloSamples:
        continue

    sourceName = utils.getSkimPath(sample.name, region, config.skimDir, '')
    dname = sample.name + '_' + region

    print '   ', dname, '(%s)' % sourceName
    
    if not os.path.exists(sourceName):
        sys.stderr.write('File ' + sourceName + ' does not exist.\n')
        raise RuntimeError('InvalidSource')

    nloSourceName = utils.getSkimPath(sample.name.replace('lo', 'h'), region, config.skimDir, '')
    sname = nloname + '_' + region

    print '   ', sname, '(%s)' % nloSourceName

    if not os.path.exists(nloSourceName):
        sys.stderr.write('File ' + nloSourceName + ' does not exist.\n')
        raise RuntimeError('InvalidSource')


    source = ROOT.TFile.Open(sourceName)
    events = source.Get('events')

    nloSource = ROOT.TFile.Open(nloSourceName)
    nloEvents = nloSource.Get('events')

    loHist = ROOT.TH1D(sample.name, sample.name, len(ybins)-1, ybins)
    nloHist = ROOT.TH1D(nloname, nloname, len(ybins)-1, ybins)
    hist = ROOT.TH1D(sname, sname, len(ybins)-1, ybins)

    events.Draw(ptdef.expr + '>>' + sample.name, recoSelString)
    nloEvents.Draw(ptdef.expr + '>>' + nloname, recoSelString)

    hist.Divide(nloHist, loHist)

    outFile.cd()
    loHist.Write()
    nloHist.Write()
    hist.Write()

outFile.Close()
