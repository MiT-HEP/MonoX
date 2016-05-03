#!/usr/bin/env python

import sys

from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Spit out plots showing shape variations.')
# argParser.add_argument('model', metavar = 'MODEL', help = 'Signal model name. Use "nomodel" for model-independent limits.')
argParser.add_argument('input', metavar = 'PATH', help = 'Histogram ROOT file.')
argParser.add_argument('--variable', '-v', action = 'store', metavar = 'VARIABLE(S)', dest = 'variable', nargs = '+', default = ['phoPtHighMet'], help = 'Discriminating variable(s).')

args = argParser.parse_args()
sys.argv = []

import os
import array
import math
import re
import ROOT as r 
from pprint import pprint

r.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import *
from datasets import allsamples
import config
from main.plotconfig import getConfig

monophConfig = getConfig('monoph')
source = r.TFile.Open(args.input)

lumi = 0.
for sName in monophConfig.obs.samples:
    lumi += allsamples[sName].lumi

def getHist(name, syst = ''):
    if syst:
        return source.Get(variable + '-' + name + '_' + syst)
    else:
        return source.Get(variable + '-' + name)

# gather process names
processes = []
for sample in allsamples:
    if not sample.signal:
        continue
    if not 'dm' in sample.name:
        continue
    if 'fs' in sample.name:
        continue
    processes.append(sample.name)

rcanvas = RatioCanvas(lumi = lumi)

for variable in args.variable:
    xtitle = monophConfig.getVariable(variable).title
    plotDir = 'monophoton/fsValidation/noSel/' + variable
    for proc in processes:
        rcanvas.Clear()
        rcanvas.legend.Clear()
        rcanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
        rcanvas.xtitle = xtitle
        rcanvas.ytitle = 'Events / Unit'
        
        fullsim = getHist(proc)
        (model, med, dm) = proc.split('-')
        fsProc = model+'fs-'+med+'-'+dm
        # print proc, fsProc
        fastsim = getHist(fsProc)

        if not fullsim:
            print "FullSim doesn't exist for", proc
            print "Why are you asking for this sample?"
            continue

        if not fastsim:
            print "FastSim doesn't exist for", fsProc
            continue

        rcanvas.legend.add('fullsim', title = 'FullSim', lcolor = r.kBlack, lwidth = 2)
        rcanvas.legend.apply('fullsim', fullsim)
        fullId = rcanvas.addHistogram(fullsim, drawOpt = 'L')

        rcanvas.legend.add('fastsim', title = 'FastSim', lcolor = r.kRed, lwidth = 2)
        rcanvas.legend.apply('fastsim', fastsim)
        fastId = rcanvas.addHistogram(fastsim, drawOpt = 'L')

        rcanvas.printWeb(plotDir+'/raw', proc, hList = [fullId, fastId], rList = [fullId, fastId])

        rcanvas.Clear()
        rcanvas.legend.Clear()
        rcanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
        rcanvas.xtitle = xtitle
        rcanvas.ytitle = 'A.U.'

        if fullsim.Integral():
            fullsim.Scale( 1. / fullsim.Integral() )
        rcanvas.legend.add('fullsim', title = 'FullSim', lcolor = r.kBlack, lwidth = 2)
        rcanvas.legend.apply('fullsim', fullsim)
        fullId = rcanvas.addHistogram(fullsim, drawOpt = 'L')

        if fastsim.Integral():
            fastsim.Scale( 1. / fastsim.Integral() )
        rcanvas.legend.add('fastsim', title = 'FastSim', lcolor = r.kRed, lwidth = 2)
        rcanvas.legend.apply('fastsim', fastsim)
        fastId = rcanvas.addHistogram(fastsim, drawOpt = 'L')

        rcanvas.printWeb(plotDir+'/norm', proc, hList = [fullId, fastId], rList = [fullId, fastId])
