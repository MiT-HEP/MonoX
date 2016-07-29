import os
import sys
import ROOT as r
from pprint import pprint

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import RatioCanvas

region = sys.argv[1]
samples = sys.argv[2:]

trees = []
weights = []
for sample in samples:
    fname = config.skimDir + '/' + sample + '_' + region + '.root'
    print fname
    source = r.TFile.Open(fname)
    tree = source.Get('events')
    trees.append((sample, tree))

    branches = tree.GetListOfBranches()
    for branch in branches:
        name = branch.GetName()
        if not name.startswith('weight'):
            continue
        if not name in weights:
            weights.append(name)

canvas = RatioCanvas()

for weight in weights:
    canvas.Clear()
    canvas.legend.Clear()
    
    (Xmin, Xmax) = (9999., -1)

    for sample, tree in trees:
        tree.Draw(weight)
        htemp = r.gPad.GetPrimitive("htemp")

        xmin = htemp.GetBinLowEdge(1)
        xmax = htemp.GetBinLowEdge(htemp.GetNbinsX()+1)

        Xmin = min(xmin, Xmin)
        Xmax = max(xmax, Xmax)

    hbase = r.TH1F("hbase", weight, 20, Xmin, Xmax)
    
    hists = []
    for iS, (sample, tree) in enumerate(trees):
        hsample = hbase.Clone(sample)
        tree.Draw(weight+">>"+sample)
        if hsample.Integral():
            hsample.Scale(1/hsample.Integral())
        hists.append(hsample)

        canvas.legend.add(sample, title = sample, mcolor = iS+1, lcolor = iS+1, lwidth = 2)
        canvas.legend.apply(sample, hsample)
        
    ids = []
    for iS, hist in enumerate(hists):
        hId = canvas.addHistogram(hists[iS])
        ids.append(hId)
    
    canvas.ylimits = (0., 1.2)
    canvas.printWeb('monophoton/compWeights', weight, hList = ids, rList = ids, logy = False)
        
    

