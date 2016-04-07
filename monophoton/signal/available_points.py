import sys
import os
import re

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas
import config

import ROOT

dma = []
dmv = []

for name in allsamples.names():
    matches = re.match('dm([av])-([0-9]+)-([0-9]+)', name)
    if matches:
        if matches.group(1) == 'a':
            dma.append((float(matches.group(2)), float(matches.group(3))))
        else:
            dmv.append((float(matches.group(2)), float(matches.group(3))))

canvas = SimpleCanvas(cms = False)
canvas.SetGrid(True)

gdma = ROOT.TGraph(len(dma))
for iP, (med, dm) in enumerate(dma):
    gdma.SetPoint(iP, med, dm)

gdma.SetTitle('DMA;M_{med} (GeV);M_{DM} (GeV)')
gdma.SetMarkerStyle(21)

canvas.addHistogram(gdma, drawOpt = 'P')
canvas.printWeb('signal_points', 'dma', logx = True)

canvas.Clear()
canvas.SetGrid(True)

gdmv = ROOT.TGraph(len(dmv))
for iP, (med, dm) in enumerate(dmv):
    gdmv.SetPoint(iP, med, dm)

gdmv.SetTitle('DMV;M_{med} (GeV);M_{DM} (GeV)')
gdmv.SetMarkerStyle(21)

canvas.addHistogram(gdmv, drawOpt = 'P')
canvas.printWeb('signal_points', 'dmv', logx = True)
