#!/usr/bin/env python

import os
import sys
import math

from argparse import ArgumentParser

argParser = ArgumentParser(description = 'plot NLO and reco k-factor reweighted distributions from gen level files.')
argParser.add_argument('config', metavar = 'CONFIG', help = 'Plot onfig name.')
argParser.add_argument('--hist-file', '-o', metavar = 'PATH', dest = 'histFile', default = '', help = 'Histogram output file.')
argParser.add_argument('--weight-file', '-w', metavar = 'PATH', dest = 'weightFile', default = '../data/genReweight.root', help = 'File with reweight histograms.')
argParser.add_argument('--grid-dir', '-g', metavar = 'PATH', dest = 'gridDir', default = '/home/ballen/hadoop/monophoton/gengrid', help = 'Location of directories for gen grid.')
argParser.add_argument('--plot', '-p', metavar = 'NAME', dest = 'plots', nargs = '+', default = [], help = 'Limit plotting to specified set of plots.')
argParser.add_argument('--plot-dir', '-d', metavar = 'PATH', dest = 'plotDir', default = '', help = 'Specify a directory under {webdir} to save images. Use "-" for no output.')
argParser.add_argument('--print-level', '-m', metavar = 'LEVEL', dest = 'printLevel', default = 0, help = 'Verbosity of the script.')
argParser.add_argument('--replot', '-P', action = 'store_true', dest = 'replot', default = '', help = 'Do not fill histograms. Need --hist-file.')
argParser.add_argument('--skim-dir', '-i', metavar = 'PATH', dest = 'skimDir', help = 'Input skim directory.')

args = argParser.parse_args()
sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from main.plotconfig import getConfig
from main.plotconfig_vbf import getConfigVBF
from main.plotconfig_ggh import getConfigGGH
import config
import utils
import main.plot
import collections

##################################
## PARSE COMMAND-LINE ARGUMENTS ##
##################################

if args.skimDir:
    localSkimDir = ''
else:
    args.skimDir = config.skimDir
    localSkimDir = config.localSkimDir

plotConfig = getConfig(args.config)
if plotConfig is None:
    plotConfig = getConfigVBF(args.config)
if plotConfig is None:
    plotConfig = getConfigGGH(args.config)
if plotConfig is None:
    print 'Unknown configuration', args.config
    sys.exit(1)

if args.replot:
    histFile = ROOT.TFile.Open(args.histFile)
else:
    histFile = ROOT.TFile.Open(args.histFile, 'update')
    weightFile = ROOT.TFile.Open(args.weightFile)



############################
## SET UP FROM PLOTCONFIG ##
############################

ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')

fullLumi = plotConfig.fullLumi()
effLumi = plotConfig.effLumi()

if 'HighPhi' in args.config:
    phiWeight = (math.pi - 1.) / math.pi
elif 'LowPhi' in args.config:
    phiWeight = 1. / math.pi
else:
    phiWeight = 1.

plotConfig.baseline = 'gammaPt > 130. && met > 170.'
plotConfig.fullSelection = ''

plotdefs = []
ptdef = plotConfig.getPlot('phoPtHighMet')
ptdef.expr = 'gammaPt'
plotdefs.append(ptdef)

vsamples = []
asamples = []

#######################
## LOOP OVER SAMPLES ##
#######################

    ## if keep using plotconfig need to an entry per point to allsamples
    ## need to grab xsec from bhawna's file and number of events (assume 50k for now)
    ## need to override weight function in multidraw as it assumes there is a weight branch
    ## probably need to extract the actual plotting step from fillPlots()

count = 0
for pname in os.listdir(args.gridDir):
    try:
        (_, _, spin, dm, med) = pname.split('-')[0].split('_')
    except:
        continue

    dm = dm.strip('Mx')
    med = med.strip('Mv')

    if float(med) != 1800.:
        continue

    if spin == 'V':
        sname = 'dmvgen-' + med + '-' + dm
        vsamples.append(sname)
        group = plotConfig.findGroup('dmvlo')
        nloGroup = plotConfig.findGroup('dmvh')
        xsecFile = open(args.gridDir + '/xsec_V_interpolated.txt', 'r')

    elif spin == 'AV':
        sname = 'dmagen-' + med + '-' + dm
        asamples.append(sname)
        group = plotConfig.findGroup('dmalo')
        nloGroup = plotConfig.findGroup('dmah')
        xsecFile = open(args.gridDir + '/xsec_AV_interpolated.txt', 'r')

    xsec = None
    while True:
        line = xsecFile.readline()
        if dm + ',' + med in line:
            xsec = xsecFile.readline()
            xsec = float(xsec)
            break
        if not line:
            break
    
    sample = None
    nloSample = None
    mindist = 1.0e12
    nlodist = 1.0e12
    for s in group.samples:
        try:
            (_, smed, sdm) = s.name.split('-')
        except:
            continue

        distance = (2*float(sdm) - 2*float(dm))**2 + (float(smed) - float(med))**2

        print '%20s, %20f' % (s.name, distance)

        if distance <= mindist:
            mindist = distance 
            sample = s

        if not s.name.replace('lo', 'h') in [r.name for r in nloGroup.samples]:
            continue

        if distance <= nlodist:
            nlodist = distance 
            nloSample = s
        
    sourceName = args.gridDir + '/' + pname + '/merged.root'
    dname = sname + '_' + args.config
    print '   ', dname, '(%s)' % sourceName
    print '   using %20s for reco reweight' % sample.name
    print '   using %20s for nlo  reweight' % nloSample.name

    if not os.path.exists(sourceName):
        sys.stderr.write('File ' + sourceName + ' does not exist.\n')
        raise RuntimeError('InvalidSource')

    plotter = main.plot.makePlotter(sourceName, plotConfig, group, sample, fullLumi, args.printLevel)
    plotter.setWeightBranch('')

    histograms = collections.OrderedDict() # {(sample, plotdef, variation, direction): histogram}
    for plotdef in plotdefs:
        if not histFile.GetDirectory(plotdef.name):
            sys.stderr.write('File ' + args.histFile + ' does not contain phoPtHighMet.\n')
            raise RuntimeError('InvalidSource')

        outDir = histFile.GetDirectory(plotdef.name + '/samples')
        if not outDir:
            outDir = outFile.GetDirectory(plotdef.name).mkdir('samples')

        # clean up
        for key in outDir.GetListOfKeys():
            if dname in key.GetName():
                outDir.Delete(key.GetName() + ';*')

        hist = plotdef.makeHist(dname, outDir = outDir)
        histograms[(sample, plotdef, None, None)] = hist

        plotCuts = []

        if plotdef.cut.strip():
            plotCuts.append('(' + plotdef.cut.strip() + ')')

        if group.cut.strip():
            plotCuts.append('(' + group.cut.strip() + ')' )

        cut = ' && '.join(plotCuts)

        if plotdef.overflow:
            overflowMode = ROOT.Plot.kMergeLast
        else:
            overflowMode = ROOT.Plot.kNoOverflowBin

        # nominal distribution
        plotter.addPlot(
            hist,
            plotdef.formExpression(),
            cut.strip(),
            plotdef.applyBaseline,
            plotdef.applyFullSel,
            '',
            overflowMode
        )

    # setup complete. Fill all plots in one go
    if plotter.numObjs() != 0:
        plotter.fillPlots()
        xsecWeight = xsec / plotter.getTotalEvents()

    for (sample, plotdef, variation, _), hist in histograms.items():
        # ad-hoc scaling
        hist.Scale(xsecWeight)

        # zero out negative bins 
        hist, horig = main.plot.cleanHist(hist)

        # save histograms
        main.plot.writeHist(hist)
        if horig is not None:
            horig.SetDirectory(hist.GetDirectory())
            main.plot.writeHist(horig)

    count = count + 1
    # if count > 10:
    #     break
    
