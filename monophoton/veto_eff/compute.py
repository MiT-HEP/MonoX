import sys
import os
import math
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import SimpleCanvas

import ROOT
ROOT.gROOT.SetBatch(True)

dataMumug = ROOT.TChain('skim')
dataMumug.Add(config.histDir + '/veto_eff/mumug_smu*.root')

mcMumug = ROOT.TChain('skim')
mcMumug.Add(config.histDir + '/veto_eff/mumug_zllg-130.root')
mcMumug.Add(config.histDir + '/veto_eff/mumug_tt.root')
mcMumug.Add(config.histDir + '/veto_eff/mumug_ww.root')
mcMumug.Add(config.histDir + '/veto_eff/mumug_wz.root')
mcMumug.Add(config.histDir + '/veto_eff/mumug_zz.root')

mcMonoph = ROOT.TChain('skim')
mcMonoph.Add(config.histDir + '/veto_eff/monoph_znng-130.root')

distCanvas = SimpleCanvas('cdist')
distCanvas.legend.add('data', title = '2#mu data', opt = 'L', color = ROOT.kBlack, fstyle = 0)
distCanvas.legend.add('mumug', title = '2#mu MC', opt = 'L', color = ROOT.kRed, fstyle = 0)
distCanvas.legend.add('monoph', title = 'Z#gamma MC', opt = 'L', color = ROOT.kBlue, fstyle = 0)
distCanvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)

effCanvas = SimpleCanvas('ceff')
effCanvas.legend.add('data', title = '2#mu data', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
effCanvas.legend.add('mumug', title = '2#mu MC', opt = 'LP', color = ROOT.kRed, mstyle = 8)
effCanvas.legend.add('monoph', title = 'Z#gamma MC', opt = 'LP', color = ROOT.kBlue, mstyle = 4)
effCanvas.legend.add('sf', title = '2#mu data/MC', opt = 'LP', color = ROOT.kBlack, mstyle = 25, lwidth = 2)
effCanvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
effCanvas.ylimits = (0.9, 1.05)
effCanvas.SetGrid(True)

configs = {
    'incl': ('0.5', '', (1, 0., 1.)),
    'njet': ('njet', 'N_{jet}', (8, 0., 8.)),
    'ht': ('ht', 'H_{T} (GeV)', [100. * x for x in range(5)] + [500., 700., 900., 1200., 2000.]),
    'npv': ('npv', 'N_{vtx}', (20, 0., 40.))
}

outputFile = ROOT.TFile.Open(config.histDir + '/veto_eff/veto_eff.root', 'recreate')

for name, config in configs.items():
    expr, title, binning = config

    if type(binning) is tuple:
        dist = ROOT.TH1D('dist_' + name, ';' + title, *binning)
        eff = ROOT.TProfile('eff_' + name, ';' + title, *binning)
        sf = ROOT.TGraphErrors(binning[0])
        scaleopt = ''
    else:
        dist = ROOT.TH1D('dist_' + name, ';' + title, len(binning) - 1, array.array('d', binning))
        eff = ROOT.TProfile('eff_' + name, ';' + title, len(binning) - 1, array.array('d', binning))
        sf = ROOT.TGraphErrors(len(binning) - 1)
        scaleopt = 'width'

    dist.Sumw2()

    weight = 'weight'

    dataDist = dist.Clone('data_' + dist.GetName())
    distCanvas.legend.apply('data', dataDist)
    dataMumug.Draw(expr + '>>' + dataDist.GetName(), weight, 'goff')
    dataDist.Scale(1. / dataDist.GetSumOfWeights(), scaleopt)

    dataEff = eff.Clone('data_' + eff.GetName())
    effCanvas.legend.apply('data', dataEff)
    dataMumug.Draw('1. - (eleveto || muveto):' + expr + '>>' + dataEff.GetName(), weight, 'prof goff')
    
    mumugDist = dist.Clone('mumug_' + dist.GetName())
    distCanvas.legend.apply('mumug', mumugDist)
    mcMumug.Draw(expr + '>>' + mumugDist.GetName(), weight, 'goff')
    mumugDist.Scale(1. / mumugDist.GetSumOfWeights(), scaleopt)

    mumugEff = eff.Clone('mumug_' + eff.GetName())
    effCanvas.legend.apply('mumug', mumugEff)
    mcMumug.Draw('1. - (eleveto || muveto):' + expr + '>>' + mumugEff.GetName(), weight, 'prof goff')

    if name == 'ht':
        dataEffHt = dataEff
        mumugEffHt = mumugEff

    for iX in range(1, dataEff.GetNbinsX() + 1):
        x = dataEff.GetXaxis().GetBinCenter(iX)
        data = dataEff.GetBinContent(iX)
        mc = mumugEff.GetBinContent(iX)
        if data > 0.:
            dataerr = dataEff.GetBinError(iX) / data
        else:
            dataerr = 0.

        if mc > 0.:
            mcerr = mumugEff.GetBinError(iX) / mc
            sf.SetPoint(iX - 1, x, data / mc)
            sf.SetPointError(iX - 1, 0., data / mc * math.sqrt(dataerr * dataerr + mcerr * mcerr))
        else:
            sf.SetPoint(iX - 1, x, 1.)

    effCanvas.legend.apply('sf', sf)

    if name == 'incl':
        effCanvas.legend.add('datajet', title = '2#mu+jet data', opt = 'LP', color = ROOT.kBlack, mstyle = 25, lstyle = ROOT.kDashed)
        effCanvas.legend.add('mumugjet', title = '2#mu+jet MC', opt = 'LP', color = ROOT.kRed, mstyle = 25, lstyle = ROOT.kDashed)
        effCanvas.legend.construct()

        weight = 'weight * (leadjetpt > 175.)'
    
        datajetEff = eff.Clone('datajet_' + eff.GetName())
        effCanvas.legend.apply('datajet', datajetEff)
        dataMumug.Draw('1. - (eleveto || muveto):' + expr + '>>' + datajetEff.GetName(), weight, 'prof goff')
    
        mumugjetEff = eff.Clone('mumugjet_' + eff.GetName())
        effCanvas.legend.apply('mumugjet', mumugjetEff)
        mcMumug.Draw('1. - (eleveto || muveto):' + expr + '>>' + mumugjetEff.GetName(), weight, 'prof goff')

    weight = 'weight'

    monophDist = dist.Clone('monoph_' + dist.GetName())
    distCanvas.legend.apply('monoph', monophDist)
    mcMonoph.Draw(expr + '>>' + monophDist.GetName(), weight, 'goff')
    monophDist.Scale(1. / monophDist.GetSumOfWeights(), scaleopt)

    if name == 'ht':
        monophHt = monophDist

    monophEff = eff.Clone('monoph_' + eff.GetName())
    effCanvas.legend.apply('monoph', monophEff)
    mcMonoph.Draw('1. - (eleveto || muveto):' + expr + '>>' + monophEff.GetName(), weight, 'prof goff')

    distCanvas.addHistogram(dataDist, drawOpt = 'HIST')
    distCanvas.addHistogram(mumugDist, drawOpt = 'HIST')
    distCanvas.addHistogram(monophDist, drawOpt = 'HIST')
    distCanvas.printWeb('veto_eff', 'dist_' + name)
    distCanvas.Clear()

    effCanvas.addHistogram(dataEff, drawOpt = 'EP')
    effCanvas.addHistogram(mumugEff, drawOpt = 'EP')
    if name == 'incl':
        effCanvas.addHistogram(datajetEff, drawOpt = 'EP')
        effCanvas.addHistogram(mumugjetEff, drawOpt = 'EP')
    effCanvas.addHistogram(monophEff, drawOpt = 'EP')
    effCanvas.addHistogram(sf, drawOpt = 'P')
    effCanvas.printWeb('veto_eff', 'eff_' + name, logy = False)
    effCanvas.Clear()
    effCanvas.SetGrid(True)

    outputFile.cd()

    dataDist.Write()
    mumugDist.Write()
    monophDist.Write()
    dataEff.Write()
    mumugEff.Write()
    monophEff.Write()
    sf.Write('sf_' + name)

    if name == 'incl':
        datajetEff.Write()
        mumugjetEff.Write()
        effCanvas.legend.remove('datajet')
        effCanvas.legend.remove('mumugjet')
        effCanvas.legend.construct()

data = 0.
mc = 0.
for iX in range(1, monophHt.GetNbinsX() + 1):
    data += dataEffHt.GetBinContent(iX) * monophHt.GetBinContent(iX)
    mc += mumugEffHt.GetBinContent(iX) * monophHt.GetBinContent(iX)

data /= monophHt.GetSumOfWeights()
mc /= monophHt.GetSumOfWeights()

print data, mc, data / mc
