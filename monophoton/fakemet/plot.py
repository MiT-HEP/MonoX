import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas

import ROOT

ROOT.gROOT.SetBatch(True)

sourceDir = sys.argv[1]
originalName = sys.argv[2]

# Original injection in plot.py is 0.05 times sigma_SM
originalMu = 0.05
signal = 'dph-nlo-125'
region = 'gghg'

original = ROOT.TFile.Open(originalName)
originalSig = original.Get('mtPhoMet/samples/' + signal + '_' + region).GetSumOfWeights()
original.Close()

data = {}
fakens = []

for fname in os.listdir(sourceDir):
    if not fname.startswith('norms'):
        continue

    with open(sourceDir + '/' + fname) as source:
        for line in source:
            words = line.split()
            if len(words) < 4:
                continue

            sigs = words[0]
            faken = words[1]
   
            if sigs not in data:
                data[sigs] = {}

            if faken not in data[sigs]:
                data[sigs][faken] = []

            if int(faken) not in fakens:
                fakens.append(int(faken))

            data[sigs][faken].append(tuple(map(float, words[2:])))

try:
    os.makedirs(config.histDir + '/fakemet')
except OSError:
    pass

fakens.sort()

outputFile = ROOT.TFile.Open(config.histDir + '/fakemet/injection_results.root', 'recreate')

canvas = SimpleCanvas()
canvas.legend.setPosition(0.8, 0.7, 0.9, 0.9)
canvas.legend.SetFillStyle(1001)
canvas.legend.SetBorderSize(1)

n = 0
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
for faken in fakens:
    canvas.legend.add('n%d' % faken, title = 'N_{f}=%d' % faken, opt = 'P', color = ROOT.TColor.GetColor(colors[n]), mstyle = 24 + n)
    n += 1
        
for sigs in data.keys():
    mu = float(sigs) * originalMu
    sign = float(sigs) * originalSig

    graphs = []

    for faken in data[sigs].keys():
        points = data[sigs][faken]
        graph = ROOT.TGraph(len(points))

        for ip, point in enumerate(points):
            try:
                sig, fake = point
            except:
                print point
                raise

            x = fake / float(faken)
            y = sig / sign
            if x > 2.:
                x = 2.
            if y > 2.:
                y = 2.

            graph.SetPoint(ip, x, y)

        graph.SetTitle('')

        outputFile.cd()
        graph.Write('%s_%s' % (sigs, faken))

        graphs.append(graph)

        canvas.legend.apply('n%s' % faken, graph)
        canvas.addHistogram(graph, drawOpt = 'P')

    canvas.addLine(0., 1., 2., 1., style = ROOT.kDashed)
    canvas.addLine(1., 0., 1., 2., style = ROOT.kDashed)
    canvas.xlimits = (0., 2.)
    canvas.ylimits = (0., 2.)

    canvas.title = '#sigma#timesBR = %.2f' % mu
    canvas.xtitle = 'Fake E_{T}^{miss} extracted / injected'
    canvas.ytitle = 'Signal extracted / injected'
    
    canvas.printWeb('monophoton/fakemet', sigs, logy = False)
    canvas.Clear()

outputFile.Close()
