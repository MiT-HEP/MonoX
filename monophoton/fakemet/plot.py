import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas

import ROOT
import math

ROOT.gROOT.SetBatch(True)

sourceName = sys.argv[1]
originalName = sys.argv[2]

# Original injection in plot.py is 0.1 times sigma_SM
originalMu = 0.1
signal = 'dph-nlo-125'
region = 'gghg'

original = ROOT.TFile.Open(originalName)
originalSig = original.Get('mtPhoMet/samples/' + signal + '_' + region).GetSumOfWeights()
original.Close()

data = {}
fakens = []

sourceDir = '/data/t3home000/' + os.environ['USER'] + '/monophoton/fakemet/' + sourceName
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
canvas.legend.setPosition(0.6, 0.6, 0.9, 0.9)
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
                sig, esig, fake, efake = point
            except:
                print point
                raise

            if efake == 0:
                if fake == 0:
                    if float(faken) == 0:
                        x = 0.
                    else:
                        x = (fake - float(faken)) / math.sqrt(float(faken))
                else:
                    x = (fake - float(faken)) / math.sqrt(fake)
            else:
                x = (fake - float(faken)) / efake

            if esig == 0:
                if sig == 0:
                    if float(sign) == 0:
                        y = 0.
                    else:
                        y = (sig - float(sign)) / math.sqrt(float(sign))
                else:
                    y = (sig - float(sign)) / math.sqrt(sig)
            else:
                y = (sig  - sign) / esig
            
            if x > 5.:
                x = 5.
            if x < -5.:
                x = -5.
            if y > 5.:
                y = 5.
            if y < -5.:
                y = -5.

            graph.SetPoint(ip, x, y)

        graph.SetTitle('')

        outputFile.cd()
        graph.Write('%s_%s' % (sigs, faken))

        graphs.append(graph)

        canvas.legend.apply('n%s' % faken, graph)
        canvas.addHistogram(graph, drawOpt = 'P')

    canvas.addLine(-5., 0., 5., 0., style = ROOT.kDashed)
    canvas.addLine(0., -5., 0., 5., style = ROOT.kDashed)
    canvas.xlimits = (-5., 5.)
    canvas.ylimits = (-5., 5.)

    canvas.title = '#sigma#timesBR = %.2f' % mu
    canvas.xtitle = 'Fake E_{T}^{miss}: (N_{fit} - N_{true})/#sigma_{fit}'
    canvas.ytitle = 'Signal: (N_{fit} - N_{true})/#sigma_{fit}'
    
    canvas.printWeb('monophoton/fakemet', sourceName + '_' + sigs, logy = False)
    canvas.Clear()

outputFile.Close()
