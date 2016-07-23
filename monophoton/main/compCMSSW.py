#!/usr/bin/env python

import sys

from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Spit out plots showing shape variations.')
argParser.add_argument('input', metavar = 'PATH', nargs = 2, help = 'Histogram ROOT files.')
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
source80 = r.TFile.Open(args.input[0])
source74 = r.TFile.Open(args.input[1]) 

lumi = 0.
for sName in monophConfig.obs.samples:
    lumi += allsamples[sName].lumi

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

plot74 = r.TH3D('plot74', ';M_{med} (GeV);M_{DM} (GeV)', len(mmeds)-1, mmeds, len(mdms)-1, mdms, len(spins)-1, spins)
plot74.Sumw2()
plot80 = r.TH3D('plot80', ';M_{med} (GeV);M_{DM} (GeV)', len(mmeds)-1, mmeds, len(mdms)-1, mdms, len(spins)-1, spins)
plot80.Sumw2()

rcanvas = RatioCanvas(lumi = lumi)

for variable in args.variable:
    xtitle = monophConfig.getVariable(variable).title
    plotDir = 'monophoton/cmsswValidation/' + args.input[0].rstrip('.root') + '/' + variable
    
    for iP, proc in enumerate(processes):
        rcanvas.Clear()
        rcanvas.legend.Clear()
        rcanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
        rcanvas.xtitle = xtitle
        rcanvas.ytitle = 'Events / Unit'
        
        dist80 = source80.Get(variable + '-' + proc)
        
        if not dist80:
            print "Dist80 doesn't exist for", proc
            print "Why are you asking for this sample?"
            continue

        if not dist80.Integral() > 0.:
            print "Dist80 integral is 0 for "+proc+". Skipping."
            continue

        dist74 = source74.Get(variable + '-' + proc)

        if not dist74:
            print "Dist74 doesn't exist for", proc
            continue

        if not dist74.Integral() > 0.:
            print "Dist74 integral is 0 for "+proc+". Skipping."
            continue

        rcanvas.legend.add('dist80', title = '80X', mcolor = r.kBlack, lcolor = r.kBlack, lwidth = 2)
        rcanvas.legend.apply('dist80', dist80)
        id80 = rcanvas.addHistogram(dist80, drawOpt = 'L')

        rcanvas.legend.add('dist74', title = '74X', mcolor = r.kRed, lcolor = r.kRed, lwidth = 2)
        rcanvas.legend.apply('dist74', dist74)
        id74 = rcanvas.addHistogram(dist74, drawOpt = 'L')

        rcanvas.printWeb(plotDir+'/raw', proc, hList = [id80, id74], rList = [id80, id74])

        if variable == "phoPtHighMet":
            (spin, mmed, mdm) = proc.split('-')
            if 'a' in spin:
                spin = 0.5
            elif 'v' in spin:
                spin = 1.5
            mmed = float(mmed)
            mdm = float(mdm)

            int74 = dist74.GetEntries() 
            int80 = dist80.GetEntries() 

            total74 = 50000. # allsamples[proc].nevents # hacky because it is hard to read 74X 
            total80 = allsamples[proc].nevents

            eff74 = int74 / total74
            eff80 = int80 / total80

            eff74Up = r.TEfficiency.ClopperPearson(total74, int(int74), 0.6827, True)
            eff74Down = r.TEfficiency.ClopperPearson(total74, int(int74), 0.6827, False)
            eff74Err = (eff74Up - eff74Down) / 2.0

            eff80Up = r.TEfficiency.ClopperPearson(total80, int(int80), 0.6827, True)
            eff80Down = r.TEfficiency.ClopperPearson(total80, int(int80), 0.6827, False)
            eff80Err = (eff80Up - eff80Down) / 2.0

            bin = plot74.FindBin(mmed, mdm, spin)
            # print spin, mmed, mdm, bin, eff74, eff74Err
            plot74.SetBinContent(bin, eff74)
            plot74.SetBinError(bin, eff74Err)
            plot80.SetBinContent(bin, eff80)
            plot80.SetBinError(bin, eff80Err)

        rcanvas.Clear()
        rcanvas.legend.Clear()
        rcanvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
        rcanvas.xtitle = xtitle
        rcanvas.ytitle = 'A.U.'

        if dist80.Integral():
            dist80.Scale( 1. / dist80.Integral() )
        rcanvas.legend.add('dist80', title = 'Dist80', lcolor = r.kBlack, lwidth = 2)
        rcanvas.legend.apply('dist80', dist80)
        id80 = rcanvas.addHistogram(dist80, drawOpt = 'L')

        if dist74.Integral():
            dist74.Scale( 1. / dist74.Integral() )
        rcanvas.legend.add('dist74', title = 'Dist74', lcolor = r.kRed, lwidth = 2)
        rcanvas.legend.apply('dist74', dist74)
        id74 = rcanvas.addHistogram(dist74, drawOpt = 'L')

        rcanvas.printWeb(plotDir+'/norm', proc, hList = [id80, id74], rList = [id80, id74])

sfPlot = plot80.Clone('sfPlot')
sfPlot.Divide(plot74)

for iX in range(1, sfPlot.GetNbinsX()+1):
    for iY in range(1, sfPlot.GetNbinsY()+1):
        for iZ in range(1, sfPlot.GetNbinsZ()+1):
            print sfPlot.GetXaxis().GetBinLowEdge(iX), sfPlot.GetYaxis().GetBinLowEdge(iY), sfPlot.GetZaxis().GetBinLowEdge(iZ), sfPlot.GetBinContent(iX, iY, iZ), sfPlot.GetBinError(iX, iY,iZ)

canvas = SimpleCanvas(lumi = lumi, xmax = 0.90)

spins = [ 'Axial', 'Vector' ]

for iS, spin in enumerate(spins):
    flat = r.TF1('Flat'+spin, '[0]', 0., 2000.)
    flat.SetParameter(0, 1.)
    flat.SetParLimits(0, 0., 2.)

    sfMDM1 = sfPlot.ProjectionX('sfMDM1'+spin, 1, 1, iS+1, iS+1, 'e')
    sfMDM1.SetTitle('')
    sfMDM1.GetYaxis().SetTitle('80X/74X Scale Factor')
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

    flat.SetParameter(0, mean)

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

    canvas.printWeb('monophoton/cmsswValidation/' + args.input[0].rstrip('.root') + '/scaleFactors', 'sfMDM1'+spin, logx = True, logy = False)

    flat2 = r.TF1('Flat2'+spin, '[0]', 0., 2000.)
    flat2.SetParameter(0, 1.)
    flat2.SetParLimits(0, 0., 2.)

    sfMMED10 = sfPlot.ProjectionY('sfMMED10'+spin, 1, 1, iS+1, iS+1, 'e')
    sfMMED10.SetTitle('')
    sfMMED10.GetYaxis().SetTitle('80X/74X Scale Factor')
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

    # if iS == 0:
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

    canvas.printWeb('monophoton/cmsswValidation/' + args.input[0].rstrip('.root') + '/scaleFactors', 'sfMMED10'+spin, logx = True, logy = False)
