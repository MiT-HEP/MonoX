import os
import sys
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import SimpleCanvas

ROOT.gStyle.SetTitleOffset(1.6, 'Y')

source = ROOT.TFile.Open(basedir + '/data/kfactor.root')

canvas = SimpleCanvas(sim = True)
canvas.legend.setPosition(0.8, 0.7, 0.9, 0.9)
canvas.legend.add('znng-130-o', 'Z#gamma', opt = 'LFP', color = ROOT.kBlue, fstyle = 3003, lwidth = 2, mstyle = 8)
canvas.legend.add('wnlg-130-o', 'W#gamma', opt = 'LFP', color = ROOT.kMagenta, fstyle = 3003, lwidth = 2, mstyle = 8)

for hname in ['znng-130-o', 'wnlg-130-o']:
    cent = source.Get(hname)
    up = source.Get(hname + '_scaleUp')
    down = source.Get(hname + '_scaleDown')

    graph = ROOT.TGraphAsymmErrors(cent.GetNbinsX())
    bars = ROOT.TGraphErrors(cent.GetNbinsX())
    for iX in range(1, cent.GetNbinsX() + 1):
        binw = cent.GetXaxis().GetBinWidth(iX)
        y = cent.GetBinContent(iX)
        graph.SetPoint(iX - 1, cent.GetXaxis().GetBinCenter(iX), y)
        graph.SetPointError(iX - 1, binw * 0.5, binw * 0.5, up.GetBinContent(iX) - y, y - down.GetBinContent(iX))
        bars.SetPoint(iX - 1, cent.GetXaxis().GetBinCenter(iX), y)
        bars.SetPointError(iX - 1, binw * 0.5, 0.)

        cent.SetBinError(iX, 0.)

    canvas.legend.apply(hname, cent)
    canvas.legend.apply(hname, bars)
    canvas.legend.apply(hname, graph)

    cent.GetXaxis().SetTitle('p_{T}^{#gamma} (GeV)')
    cent.GetYaxis().SetTitle('#sigma_{QCD}^{NNLO} / #sigma^{LO}')

    canvas.addHistogram(cent, drawOpt = 'EP')
    canvas.addHistogram(graph, drawOpt = '2')
    canvas.addHistogram(bars, drawOpt = 'EZ')

canvas.addLine(cent.GetXaxis().GetXmin(), 1., cent.GetXaxis().GetXmax(), 1., style = ROOT.kDashed)

canvas.ylimits = (0.8, 1.8)

canvas.printWeb('kfactor', 'zgwg', logy = False)
canvas.Clear()
