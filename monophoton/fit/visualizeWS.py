import sys
sys.dont_write_bytecode = True
import os
import array
import math
from argparse import ArgumentParser

import parameters

plotDir = 'workspace'

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import SimpleCanvas, RatioCanvas

import ROOT

canvas1 = SimpleCanvas(name = 'canvas1')
canvas1.legend.setPosition(0.7, 0.7, 0.9, 0.9)
# a very ugly hack - somehow cannot plot two types (with and without uncertainty) of plots..
canvas2 = SimpleCanvas(name = 'canvas2')

canvas1.legend.add('total', 'stat. + syst.', opt = 'F', color = ROOT.kOrange + 1, fstyle = 1001)
canvas1.legend.add('stat', 'stat.', opt = 'L', color = ROOT.kBlack, mstyle = 8)

source = ROOT.TFile.Open(parameters.plotsOutname)

tfList = ['tf_' + target[0] + '_' + target[1] + '_' + base[0] + '_' + base[1]  for (target, base) in parameters.links]
print tfList
procList = parameters.processes + parameters.signals + tfList

for region in parameters.regions:
    for proc in procList:
        if 'tf_' in proc:
            hnominal = source.Get(proc)
            huncert = source.Get(proc + '_uncertainties')
        else:
            hnominal = source.Get(proc + '_' + region)
            huncert = source.Get(proc + '_' + region + '_uncertainties')
        if not hnominal:
            continue
    
        canvas1.legend.apply('stat', hnominal)
    
        if huncert:
            canvas1.Clear()
            canvas1.legend.apply('total', huncert)
    
            canvas1.addHistogram(huncert, drawOpt = 'E2')
            canvas1.addHistogram(hnominal, drawOpt = 'EP')
            canvas1.printWeb(plotDir, hnominal.GetName(), logy = not proc.startswith('tf_'))
        else:
            canvas2.Clear()
            canvas2.addHistogram(hnominal, drawOpt = 'EP')
            canvas2.printWeb(plotDir, hnominal.GetName(), logy = not proc.startswith('tf_'))

rcanvas = RatioCanvas(name = 'datamc', lumi = 36400)
rcanvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)

for lep in ['mu', 'el']:
    for tf in tfList:
        if lep in tf:
            hMcRatio = source.Get(tf)
            hMcRatioUnc = source.Get(tf + '_uncertainties')

    hDilepData = source.Get('data_obs_di' + lep + '__x')
    hMonolepData = source.Get('data_obs_mono' + lep + '__x')
    
    hDataRatio = hDilepData.Clone('tf_data_'+lep)
    hDataRatio.Divide(hMonolepData)

    rcanvas.Clear()
    rcanvas.legend.Clear()
    rcanvas.legend.add('mc', 'Z/W MC', opt = 'L', color = ROOT.kBlue + 1)
    rcanvas.legend.add('mcUnc', 'Z/W MC Uncertainty', opt = 'F', color = ROOT.kOrange + 1, fstyle = 1001)
    rcanvas.legend.add('data', 'Z/W Data', opt = 'L', color = ROOT.kBlack, mstyle = 8)

    rcanvas.legend.apply('mc', hMcRatio)
    rcanvas.legend.apply('mcUnc', hMcRatioUnc)
    rcanvas.legend.apply('data', hDataRatio)

    iMc = rcanvas.addHistogram(hMcRatio, drawOpt = 'HIST')
    iUnc = rcanvas.addHistogram(hMcRatioUnc, drawOpt = 'E2')
    iData = rcanvas.addHistogram(hDataRatio, drawOpt = 'EP')
    
    outName = 'tf_ratio_'+lep
    rcanvas.printWeb(plotDir, outName, hList = [iUnc, iMc, iData], rList = [iMc, iUnc, iData], logy = False)
