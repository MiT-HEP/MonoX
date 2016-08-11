import os
import sys
import ROOT as r
from pprint import pprint

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas, RatioCanvas

region = sys.argv[1]
samples = sys.argv[2:]

sources = []
trees = []
weights = []
for sample in samples:
    fname = config.skimDir + '/' + sample + '_' + region + '.root'
    print fname
    source = r.TFile.Open(fname)
    tree = source.Get('events')
    sources.append(source)
    trees.append((sample, tree))

    branches = tree.GetListOfBranches()
    for branch in branches:
        name = branch.GetName()
        if not name.startswith('weight'):
            continue
        if not name in weights:
            weights.append(name)

canvas = SimpleCanvas()
canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

for weight in weights:
    print weight
    
    (Xmin, Xmax) = (9999., -1)

    for sample, tree in trees:
        tree.Draw(weight)
        htemp = r.gPad.GetPrimitive("htemp")

        xmin = htemp.GetBinLowEdge(1)
        xmax = htemp.GetBinLowEdge(htemp.GetNbinsX()+1)

        Xmin = min(xmin, Xmin)
        Xmax = max(xmax, Xmax)
        # sys.stdin.readline()

    print Xmin, Xmax
    hbase = r.TH1F("hbase"+weight, weight, 100, Xmin, Xmax)

    
    canvas.Clear()
    canvas.legend.Clear()

    hists = []
    for iS, (sample, tree) in enumerate(trees):
        hsample = hbase.Clone(sample+weight)
        tree.Draw(weight+" >> "+sample+weight, '', "goff")
        # if hsample.Integral():
        print tree.GetEntries()
        print hsample.Integral()
        hsample.Scale(1./tree.GetEntries())

        canvas.legend.add(sample+weight, title = sample, mcolor = iS+1, lcolor = iS+1, lwidth = 2)
        canvas.legend.apply(sample+weight, hsample)
        hists.append(hsample)
        
        canvas.addHistogram(hists[iS])

    canvas.printWeb('monophoton/compWeights', weight, logy = False)
        
    

