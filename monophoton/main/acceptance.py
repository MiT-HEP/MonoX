import sys
import os
import array
import math
import re
import ROOT

ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import *
from datasets import allsamples
import config
from main.plotconfig import getConfig
from main.plot import getHist, formatHist, printBinByBin

varname = sys.argv[1]

plotConfig = getConfig('monoph')
vardef = next(v for v in plotConfig.variables if v.name == varname)

stack = {}

for group in plotConfig.bkgGroups:
    totalw = 0.
    for sname in group.samples:
        if group.region:
            region = group.region
            hname = sname + '_' + group.region
        else:
            region = plotConfig.name
            hname = ''

        hist = getHist(sname, region, vardef, plotConfig.baseline, hname = hname, acceptance = True)
        hist.Scale(allsamples[sname].nevents)

        totalw += allsamples[sname].nevents
        try:
            stack[group.name].Add(hist)
        except KeyError:
            stack[group.name] = hist.Clone(group.name)

    stack[group.name].Scale(1. / totalw)
    formatHist(stack[group.name], vardef)

totalw = 0.
for sname in plotConfig.obs.samples:
    hist = getHist(sname, plotConfig.name, vardef, plotConfig.baseline, acceptance = True)
    try:
        stack['data_obs'].Add(hist)
    except KeyError:
        stack['data_obs'] = hist.Clone('data_obs')

    totalw += allsamples[sname].nevents

stack['data_obs'].Scale(1. / totalw)
formatHist(stack['data_obs'], vardef)

printBinByBin(stack, plotConfig, precision = '.2e')
