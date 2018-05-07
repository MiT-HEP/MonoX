#!/usr/bin/env python

import os
import sys

from argparse import ArgumentParser

argParser = ArgumentParser(description = 'plot NLO and reco k-factor reweighted distributions from gen level files.')
argParser.add_argument('config', metavar = 'CONFIG', help = 'Plot onfig name.')
argParser.add_argument('--hist-file', '-o', metavar = 'PATH', dest = 'histFile', default = '', help = 'Histogram output file.')
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

if args.histFile:
    if args.replot:
        histFile = ROOT.TFile.Open(args.histFile)
    else:
        histFile = ROOT.TFile.Open(args.histFile, 'update')

else:
    if args.replot:
        print '--replot requires a --hist-file.'
        sys.exit(1)

############################
## SET UP FROM PLOTCONFIG ##
############################

fullLumi = plotConfig.fullLumi()
effLumi = plotConfig.effLumi()

plotdefs = []

ptdef = plotConfig.getPlot('phoPtHighMet')
ptdef.expr = 'gammaPt'
ptdef.baseline = 'gammaPt > 130. && met > 170.'
plotdefs.append(ptdef)

vsamples = []
asamples = []

for pname in os.listdir(args.gridDir):
    (_, _, spin, dm, med) = pname.split('-')[0].split('_')
    dm = dm.strip('Mx')
    med = med.strip('Mv')

    if spin == 'V':
        sname = 'dmvgen-%s-%s'.format(med, dm)
        vsamples.append(sname)
    elif spin == 'AV':
        sname = 'dmagen-%s-%s'.format(med, dm)
        asamples.append(sname)
    
plotConfig.addSig('dmvgen', 'DM V', samples = vsamples)
plotConfig.addSig('dmagen', 'DM A', samples = asamples)    

groups = [plotConfig.findGroup('dmvgen'), plotConfig.findGroup('dmagen')]

#####################################
## FILL HISTOGRAMS FROM SKIM TREES ##
#####################################

# if not args.replot:
ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')

print 'Filling plots for %s..' % plotConfig.name

# for data-driven background estimates under presence of prescales
# multiply the yields by postscale
postscale = effLumi / fullLumi

for group in groups:
    print ' ', group.name

    fillPlots(plotConfig, group, plotdefs, args.skimDir, histFile, lumi = effLumi, postscale = postscale, printLevel = args.printLevel, altSourceDir = localSkimDir)

# Save a background total histogram (for display purpose) for each plotdef
for plotdef in plotdefs:
    outDir = histFile.GetDirectory(plotdef.name)

    if args.asimov:
        asimov = bkghist.Clone('asimov')

        # generate the "observed" distribution from background total
        for varspec in args.asimov_variation:
            # example: fakemet:fakemetShapeUp:5
            words = varspec.split(':')
            gname, varname = words[:2]
            if len(words) > 2:
                scale = float(words[2])
            else:
                scale = 1.

            nominal = outDir.Get(gname)
            if varname:
                varhist = outDir.Get(gname + '_' + varname)
            else:
                varhist = nominal

            if not nominal or not varhist:
                print 'Invalid variation specified for pseudo-data:', varspec
                continue

            asimov.Add(nominal, -1.)
            asimov.Add(varhist, scale)

        if args.asimov != 'background':
            sighist = outDir.Get('samples/' + args.asimov + '_' + plotConfig.name)
            asimov.Add(sighist)

        # make data_obs here
        obshist = plotdef.makeHist('data_obs', outDir = outDir)

        for iBin in xrange(1, asimov.GetNbinsX() + 1):
            x = asimov.GetXaxis().GetBinCenter(iBin)
            for _ in xrange(int(round(asimov.GetBinContent(iBin)))):
                obshist.Fill(x)

        writeHist(obshist)

if args.histFile:
    # close and reopen the output file
    histFile.Close()
    histFile = ROOT.TFile.Open(args.histFile)

# closes if not args.replot
