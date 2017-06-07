"""
This script does two things:
 - Draw the distributions of variables given in configs.
 - Draw the electron & muon veto efficiencies as functions of variables given in configs.
Data and MC are compared in Z->mumug events. The "data efficiency" for monophoton events
is computed by convoluting the data efficiency in Z->mumug with the HT distribution from
MC monophoton events.
"""

import sys
import os
import math
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas

import ROOT
ROOT.gROOT.SetBatch(True)

# data tree
dataMumug = ROOT.TChain('events')
dataMumug.Add(config.skimDir + '/smu-16*-m_tpmmg.root')

# MC mumug tree
mcMumug = ROOT.TChain('events')
mcMumug.Add(config.skimDir + '/zllg_tpmmg.root')
mcMumug.Add(config.skimDir + '/tt_tpmmg.root')
mcMumug.Add(config.skimDir + '/ww_tpmmg.root')
mcMumug.Add(config.skimDir + '/wz_tpmmg.root')
mcMumug.Add(config.skimDir + '/zz_tpmmg.root')

# MC znng tree
mcMonoph = ROOT.TChain('events')
mcMonoph.Add(config.skimDir + '/znng-130-o_monophNoLVeto.root')

# canvases
distCanvas = SimpleCanvas('cdist')
distCanvas.legend.add('data', title = '2#mu data', opt = 'L', color = ROOT.kBlack, fstyle = 0)
distCanvas.legend.add('mumug', title = '2#mu MC', opt = 'L', color = ROOT.kRed, fstyle = 0)
distCanvas.legend.add('monoph', title = 'Z#gamma MC', opt = 'L', color = ROOT.kBlue, fstyle = 0)
distCanvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)

effCanvas = SimpleCanvas('ceff')
effCanvas.legend.add('data', title = '2#mu data', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
effCanvas.legend.add('mumug', title = '2#mu MC', opt = 'LP', color = ROOT.kRed, mstyle = 8)
effCanvas.legend.add('monoph', title = 'Z#gamma MC', opt = 'LP', color = ROOT.kBlue, mstyle = 4)
effCanvas.legend.add('sf', title = '2#mu data/MC', opt = 'LP', color = ROOT.kBlack, mstyle = 34, lwidth = 2)
effCanvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
effCanvas.ylimits = (0.9, 1.05)
effCanvas.SetGrid(True)

# plot configs
configs = {
    'incl': ('0.5', '', (1, 0., 1.)),
    'njet': ('jets.size', 'N_{jet}', (8, 0., 8.)),
    'ht': ('Sum$(jets.pt_)', 'H_{T} (GeV)', [100. * x for x in range(5)] + [500., 700., 900., 1200., 2000.]),
    'npv': ('npv', 'N_{vtx}', (20, 0., 40.))
}

outputFile = ROOT.TFile.Open(config.histDir + '/veto_eff/veto_eff.root', 'recreate')

for name, config in configs.items():
    expr, title, binning = config

    # create the distribution and efficiency plot templates
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

    weight = 'weight_Input'

    # plot the data distribution
    dataDist = dist.Clone('data_' + dist.GetName())
    distCanvas.legend.apply('data', dataDist)
    dataMumug.Draw(expr + '>>' + dataDist.GetName(), weight, 'goff')
    dataDist.Scale(1. / dataDist.GetSumOfWeights(), scaleopt)

    # plot the data efficiency
    dataEff = eff.Clone('data_' + eff.GetName())
    effCanvas.legend.apply('data', dataEff)
    dataMumug.Draw('1. - (electrons.size != 0 || muons.size != 0):' + expr + '>>' + dataEff.GetName(), weight, 'prof goff')
    
    # plot the MC distribution
    mumugDist = dist.Clone('mumug_' + dist.GetName())
    distCanvas.legend.apply('mumug', mumugDist)
    mcMumug.Draw(expr + '>>' + mumugDist.GetName(), weight, 'goff')
    mumugDist.Scale(1. / mumugDist.GetSumOfWeights(), scaleopt)

    # plot the MC efficiency
    mumugEff = eff.Clone('mumug_' + eff.GetName())
    effCanvas.legend.apply('mumug', mumugEff)
    mcMumug.Draw('1. - (electrons.size != 0 || muons.size != 0):' + expr + '>>' + mumugEff.GetName(), weight, 'prof goff')

    # we will use the efficiency-HT plots to derive the "data monophoton efficiency"
    if name == 'ht':
        dataEffHt = dataEff
        mumugEffHt = mumugEff

    # efficiency scale factors
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

    # additional measurement with a jet, just to demonstrate the robustness of the scale factor
    if name == 'incl':
        effCanvas.legend.add('datajet', title = '2#mu+jet data', opt = 'LP', color = ROOT.kBlack, mstyle = 25, lstyle = ROOT.kDashed)
        effCanvas.legend.add('mumugjet', title = '2#mu+jet MC', opt = 'LP', color = ROOT.kRed, mstyle = 25, lstyle = ROOT.kDashed)
        effCanvas.legend.construct()

        weight = 'weight_Input * (jets.pt_[0] > 175.)'
    
        datajetEff = eff.Clone('datajet_' + eff.GetName())
        effCanvas.legend.apply('datajet', datajetEff)
        dataMumug.Draw('electrons.size == 0 && muons.size == 0:' + expr + '>>' + datajetEff.GetName(), weight, 'prof goff')
    
        mumugjetEff = eff.Clone('mumugjet_' + eff.GetName())
        effCanvas.legend.apply('mumugjet', mumugjetEff)
        mcMumug.Draw('electrons.size == 0 && muons.size == 0:' + expr + '>>' + mumugjetEff.GetName(), weight, 'prof goff')

    weight = 'weight_Input'

    # znng (monophoton) distributions
    monophDist = dist.Clone('monoph_' + dist.GetName())
    distCanvas.legend.apply('monoph', monophDist)
    mcMonoph.Draw(expr + '>>' + monophDist.GetName(), weight, 'goff')
    monophDist.Scale(1. / monophDist.GetSumOfWeights(), scaleopt)

    # this distribution will be convoluted with mumug efficiency
    if name == 'ht':
        monophHt = monophDist

    # znng efficiency
    monophEff = eff.Clone('monoph_' + eff.GetName())
    effCanvas.legend.apply('monoph', monophEff)
    mcMonoph.Draw('electrons.size == 0 && muons.size == 0:' + expr + '>>' + monophEff.GetName(), weight, 'prof goff')

    # print plots
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

    # save histograms
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

print 'Histograms saved to', outputFile.GetName()

if 'ht' in configs:
    # convolution with HT
    data = 0.
    mc = 0.
    for iX in range(1, monophHt.GetNbinsX() + 1):
        data += dataEffHt.GetBinContent(iX) * monophHt.GetBinContent(iX)
        mc += mumugEffHt.GetBinContent(iX) * monophHt.GetBinContent(iX)
    
    data /= monophHt.GetSumOfWeights()
    mc /= monophHt.GetSumOfWeights()
    
    print data, mc, data / mc
