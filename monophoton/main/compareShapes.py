#!/usr/bin/env python

import sys

from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Spit out plots showing shape variations.')
argParser.add_argument('input', metavar = 'PATH', help = 'Histogram ROOT file.')
argParser.add_argument('--variable', '-v', action = 'store', metavar = 'VARIABLE(S)', dest = 'variable', nargs = '+', default = ['phoPtHighMet'], help = 'Discriminating variable(s).')
argParser.add_argument('--samples', '-s', action = 'store', metavar = 'SAMPLE(S)', dest = 'samples', nargs = '+', default = [], help = 'Samples to compare. First is used as base for ratios.')
argParser.add_argument('--out-dir', '-o', action = 'store', metavar = 'OUTDIR', dest = 'outdir', default = None, help = 'Output directory name.')
args = argParser.parse_args()
sys.argv = []

import os
import array
import math
import re
import ROOT as r 
from pprint import pprint

# r.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import *
from datasets import allsamples
import config
from main.plotconfig import getConfig

monophConfig = getConfig('nosel')
source = r.TFile.Open(args.input)

colors = [r.kBlack, r.kRed, r.kBlue]

lumi = 0.
for sName in monophConfig.obs.samples:
    lumi += allsamples[sName.name].lumi

def getHist(name, syst = ''):
    if syst:
        return source.Get(variable + '/samples/' + name + '_' + syst)
        
    else:
        return source.Get(variable + '/samples/' + name + '_signalRaw')

rcanvas = RatioCanvas(lumi = lumi, name = 'raw')
scanvas = RatioCanvas(lumi = lumi, name = 'norm')

if args.outdir is None:
    args.outdir = '_'.join(args.samples)

plotDir = 'monophoton/compareShapes/' + args.input.rstrip('.root') + '/' + args.outdir

for variable in args.variable:
    xtitle = monophConfig.getPlot(variable).title
    
    rcanvas.Clear()
    rcanvas.legend.Clear()
    rcanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
    rcanvas.xtitle = xtitle
    rcanvas.ytitle = 'Events / Unit'

    scanvas.Clear()
    scanvas.legend.Clear()
    scanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
    scanvas.xtitle = xtitle
    scanvas.ytitle = 'A.U.'
    
    for iS, sample in enumerate(args.samples):
        print 'Getting', sample
        hist = getHist(sample)
        
        if not hist:
            print "Hist doesn't exist for", sample
            print "Why are you asking for this sample?"
            continue

        if not hist.Integral() > 0.:
            print "Hist integral is 0 for "+sample+". Skipping."
            continue

        rcanvas.legend.add(sample, title = sample, mcolor = colors[iS], lcolor = colors[iS], lwidth = 2)
        rcanvas.legend.apply(sample, hist)
        rID = rcanvas.addHistogram(hist, drawOpt = 'L')

        if hist.Integral():
            hist.Scale( 1. / hist.Integral() )
        scanvas.legend.add(sample, title = sample, mcolor = colors[iS], lcolor = colors[iS], lwidth = 2)
        scanvas.legend.apply(sample, hist)
        sID = scanvas.addHistogram(hist, drawOpt = 'L')

        print rID, sID
        
    rcanvas.printWeb(plotDir, variable + '_raw')
    scanvas.printWeb(plotDir, variable + '_norm')
