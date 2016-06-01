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
spins = [0., 1., 2.]
mmeds = [10, 20, 50, 100, 200, 500, 1000, 2000]
mdms = [1, 10, 50, 150, 500, 1000, 2000]
processes = []
for sample in allsamples:
    if not sample.name.startswith('dm'):
        continue

    skips = [ 'fs', '10000', 'dma-200-50' ]
    skipp = False
    for skip in skips:
        if skip in sample.name:
            skipp = True
            break
    if skipp:
        continue

    (med, mmed, mdm) = sample.name.split('-')
    mmed = float(mmed)
    mdm = float(mdm)
    if not mmed in mmeds:
        # mmeds.append(mmed)
        continue
    if not mdm in mdms:
        # mdms.append(mdm)
        continue

    processes.append(sample.name)

mmeds = array.array('d', sorted(mmeds))
mdms = array.array('d', sorted(mdms))
spins = array.array('d', sorted(spins))

fastPlot = r.TH3D('fastPlot', ';M_{med} (GeV);M_{DM} (GeV)', len(mmeds)-1, mmeds, len(mdms)-1, mdms, len(spins)-1, spins)
fastPlot.Sumw2()
fullPlot = r.TH3D('fullPlot', ';M_{med} (GeV);M_{DM} (GeV)', len(mmeds)-1, mmeds, len(mdms)-1, mdms, len(spins)-1, spins)
fullPlot.Sumw2()

rcanvas = RatioCanvas(lumi = lumi)

for variable in args.variable:
    xtitle = monophConfig.getVariable(variable).title
    plotDir = 'monophoton/fsValidation/' + args.input.rstrip('.root') + '/' + variable
    
    for iP, proc in enumerate(processes):
        rcanvas.Clear()
        rcanvas.legend.Clear()
        rcanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
        rcanvas.xtitle = xtitle
        rcanvas.ytitle = 'Events / Unit'
        
        fullsim = getHist(proc)
        
        if not fullsim:
            print "FullSim doesn't exist for", proc
            print "Why are you asking for this sample?"
            continue

        if not fullsim.Integral() > 0.:
            print "FullSim integral is 0 for "+proc+". Skipping."
            continue

        (model, med, dm) = proc.split('-')
        fsProc = model+'fs-'+med+'-'+dm
        # print proc, fsProc
        fastsim = getHist(fsProc)

        if not fastsim:
            print "FastSim doesn't exist for", fsProc
            continue

        if not fastsim.Integral() > 0.:
            print "FastSim integral is 0 for "+fsProc+". Skipping."
            continue

        rcanvas.legend.add('fullsim', title = 'FullSim', mcolor = r.kBlack, lcolor = r.kBlack, lwidth = 2)
        rcanvas.legend.apply('fullsim', fullsim)
        fullId = rcanvas.addHistogram(fullsim, drawOpt = 'L')

        rcanvas.legend.add('fastsim', title = 'FastSim', mcolor = r.kRed, lcolor = r.kRed, lwidth = 2)
        rcanvas.legend.apply('fastsim', fastsim)
        fastId = rcanvas.addHistogram(fastsim, drawOpt = 'L')

        rcanvas.printWeb(plotDir+'/raw', proc, hList = [fullId, fastId], rList = [fullId, fastId])

        if variable == "phoPtHighMet":
            (spin, mmed, mdm) = proc.split('-')
            if 'a' in spin:
                spin = 0.5
            elif 'v' in spin:
                spin = 1.5
            mmed = float(mmed)
            mdm = float(mdm)

            fastInt = fastsim.GetEntries() 
            fullInt = fullsim.GetEntries() 

            fastTotal = allsamples[fsProc].nevents
            fullTotal = allsamples[proc].nevents

            fastEff = fastInt / fastTotal
            fullEff = fullInt / fullTotal

            fastEffUp = r.TEfficiency.ClopperPearson(fastTotal, int(fastInt), 0.6827, True)
            fastEffDown = r.TEfficiency.ClopperPearson(fastTotal, int(fastInt), 0.6827, False)
            fastEffErr = (fastEffUp - fastEffDown) / 2.0

            fullEffUp = r.TEfficiency.ClopperPearson(fullTotal, int(fullInt), 0.6827, True)
            fullEffDown = r.TEfficiency.ClopperPearson(fullTotal, int(fullInt), 0.6827, False)
            fullEffErr = (fullEffUp - fullEffDown) / 2.0

            bin = fastPlot.FindBin(mmed, mdm, spin)
            # print spin, mmed, mdm, bin, fastEff, fastEffErr
            fastPlot.SetBinContent(bin, fastEff)
            fastPlot.SetBinError(bin, fastEffErr)
            fullPlot.SetBinContent(bin, fullEff)
            fullPlot.SetBinError(bin, fullEffErr)

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

sfPlot = fullPlot.Clone('sfPlot')
sfPlot.Divide(fastPlot)

for iX in range(1, sfPlot.GetNbinsX()+1):
    for iY in range(1, sfPlot.GetNbinsY()+1):
        for iZ in range(1, sfPlot.GetNbinsZ()+1):
            print sfPlot.GetXaxis().GetBinLowEdge(iX), sfPlot.GetYaxis().GetBinLowEdge(iY), sfPlot.GetZaxis().GetBinLowEdge(iZ), sfPlot.GetBinContent(iX, iY, iZ), sfPlot.GetBinError(iX, iY,iZ)

canvas = SimpleCanvas(lumi = lumi, xmax = 0.90)
"""
ncontours = 999
stops = (0.0,1.0)
red   = (1.0,0.0)
green = (1.0,0.0)
blue  = (1.0,1.0)

s = array.array('d', stops)
reds = array.array('d', red)
g = array.array('d', green)
b = array.array('d', blue)

npoints = len(s)
r.TColor.CreateGradientColorTable(npoints, s, reds, g, b, ncontours)
r.gStyle.SetNumberContours(ncontours)
r.gStyle.SetPaintTextFormat(".2f")

canvas.addHistogram(sfPlot, drawOpt = 'BOX')
canvas.printWeb('monophoton/fsValidation/' + args.input.rstrip('.root') + '/scaleFactors', 'scaleFactors', logx = True, logy = True, ymax = 2.)

canvas.Clear(xmax = 0.90)
canvas.addHistogram(fastPlot, drawOpt = 'BOX')
canvas.printWeb('monophoton/fsValidation/' + args.input.rstrip('.root') + '/scaleFactors', 'fastYields', logx = True, logy = True)

canvas.Clear(xmax = 0.90)
canvas.addHistogram(fullPlot, drawOpt = 'BOX')
canvas.printWeb('monophoton/fsValidation/' + args.input.rstrip('.root') + '/scaleFactors', 'fullYields', logx = True, logy = True)

systPlot = sfPlot.Clone('systPlot')
for iX in range(1, sfPlot.GetNbinsX()+1):
    for iY in range(1, sfPlot.GetNbinsY()+1):
        systPlot.SetBinContent(iX, iY, sfPlot.GetBinError(iX, iY))

canvas.Clear(xmax = 0.90)
canvas.addHistogram(systPlot, drawOpt = 'BOX')
canvas.printWeb('monophoton/fsValidation/' + args.input.rstrip('.root') + '/scaleFactors', 'sfSysts', logx = True, logy = True, ymax = 0.1)
"""

spins = [ 'Axial', 'Vector' ]

for iS, spin in enumerate(spins):
    flat = r.TF1('Flat'+spin, '[0]', 0., 2000.)
    flat.SetParameter(0, 1.)
    flat.SetParLimits(0, 0., 2.)

    sfMDM1 = sfPlot.ProjectionX('sfMDM1'+spin, 1, 1, iS+1, iS+1, 'e')
    sfMDM1.SetTitle('')
    sfMDM1.GetYaxis().SetTitle('FullSim/FastSim Scale Factor')
    fitMDM1 = sfMDM1.Clone('fitMDM1'+spin)
    fitMDM1.Fit(flat, "M WL B", "goff", 0., 2000.)

    nbins = 0.
    mean = 0.
    error = 0.
    for iX in range(1,sfMDM1.GetNbinsX()+1):
        eff = sfMDM1.GetBinContent(iX)
        err = sfMDM1.GetBinError(iX)

        if eff == 0:
            continue

        nbins += 1.
        mean += eff
        error += err*err

    mean = mean / nbins
    error = math.sqrt(error) / nbins

    # flat.SetParameter(0, mean)

    canvas.Clear()
    canvas.legend.Clear()
    canvas.legend.setPosition(0.5, 0.7, 0.9, 0.9)
    canvas.ylimits = (0.8, 1.2)

    canvas.legend.add('data', title = spin+' M_{DM} = 1 GeV', mcolor = r.kBlack, lcolor = r.kBlack, lwidth = 1)
    canvas.legend.apply('data', sfMDM1)
    canvas.addHistogram(sfMDM1, drawOpt = 'EP')

    titleMDM1 = 'Fit: SF = '+str(round(flat.GetParameter(0),2))+'#pm'+str(round(flat.GetParError(0),2))
    # titleMDM1 = 'Fit: SF = '+str(round(mean,2))+'#pm'+str(round(error,2))
    canvas.legend.add('fit', title = titleMDM1, mcolor = r.kRed, lcolor = r.kRed, lwidth = 2)
    canvas.legend.apply('fit', flat)
    canvas.addHistogram(flat, drawOpt = 'L')

    canvas.printWeb('monophoton/fsValidation/' + args.input.rstrip('.root') + '/scaleFactors', 'sfMDM1'+spin, logx = True, logy = False)

    flat2 = r.TF1('Flat2'+spin, '[0]', 0., 2000.)
    flat2.SetParameter(0, 1.)
    flat2.SetParLimits(0, 0., 2.)

    sfMMED10 = sfPlot.ProjectionY('sfMMED10'+spin, 1, 1, iS+1, iS+1, 'e')
    sfMMED10.SetTitle('')
    sfMMED10.GetYaxis().SetTitle('FullSim/FastSim Scale Factor')
    fitMMED10 = sfMMED10.Clone('fitMMED10'+spin)
    fitMMED10.Fit(flat2, "M WL B", "goff", 0., 2000.)

    nbins = 0.
    mean = 0.
    error = 0.
    for iX in range(1,sfMMED10.GetNbinsX()+1):
        eff = sfMMED10.GetBinContent(iX)
        err = sfMMED10.GetBinError(iX)

        if eff == 0:
            continue

        nbins += 1.
        mean += eff
        error += err*err

    mean = mean / nbins
    error = math.sqrt(error) / nbins

    if iS == 0:
        flat2.SetParameter(0, mean)

    canvas.Clear()
    canvas.legend.Clear()
    canvas.legend.setPosition(0.5, 0.7, 0.9, 0.9)
    canvas.ylimits = (0.8, 1.2)

    canvas.legend.add('data', title = spin+' M_{MED} = 10 GeV', mcolor = r.kBlack, lcolor = r.kBlack, lwidth = 1)
    canvas.legend.apply('data', sfMMED10)
    canvas.addHistogram(sfMMED10, drawOpt = 'EP')

    titleMMED10 = 'Fit: SF = '+str(round(flat2.GetParameter(0),2))+'#pm'+str(round(flat2.GetParError(0),2))
    # titleMMED10 = 'Fit: SF = '+str(round(mean,2))+'#pm'+str(round(error,2))
    canvas.legend.add('fit', title = titleMMED10, mcolor = r.kRed, lcolor = r.kRed, lwidth = 2)
    canvas.legend.apply('fit', flat2)
    canvas.addHistogram(flat2, drawOpt = 'L')

    canvas.printWeb('monophoton/fsValidation/' + args.input.rstrip('.root') + '/scaleFactors', 'sfMMED10'+spin, logx = True, logy = False)
