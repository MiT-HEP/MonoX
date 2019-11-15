#Direct (without going through purity) computation of hadron fake transfer factors

import os
import sys
import collections
import time
import array
import importlib
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

import config
import utils
from datasets import allsamples
import plotstyle

# Fill plotConfig parameters based on plotutil.confName
params = importlib.import_module('configs.' + config.config + '.params')
fakeParams = importlib.import_module('configs.' + config.config + '.hadron_fake')
selconf = importlib.import_module('configs.' + config.config + '.selectors').selconf

ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gStyle.SetOptStat(0)

MAKE_TEMPLATES = False
SUBDET = 'endcap'

trigger = 'vbfTrigger'
ptBinning = [80, 90, 100, 115, 130, 150, 600]

outputFileName = config.histDir + '/hadron_fake/direct_vbf_' + subdet + '.root'
try:
    os.makedirs(os.path.dirname(outputFileName))
except OSError:
    pass

ROOT.gSystem.Load('libPandaTreeObjects.so')
e = ROOT.panda.Event

idtune = selconf['photonIDTune']
chIsoCuts = ROOT.panda.XPhoton.chIsoCuts[idtune]
nhIsoCuts = ROOT.panda.XPhoton.nhIsoCuts[idtune]
phIsoCuts = ROOT.panda.XPhoton.phIsoCuts[idtune]
hOverECuts = ROOT.panda.XPhoton.hOverECuts[idtune]
sieieCuts = ROOT.panda.XPhoton.sieieCuts[idtune]

targetwp = 1

if MAKE_TEMPLATES:
    ROOT.gSystem.Load(config.libmultidraw)

    if trigger in params.effectivelumi:
        for sname, lumi in params.effectivelumi[trigger].iteritems():
            allsamples[sname].lumi = lumi

    if subdet == 'barrel':
        isub = 0
    else:
        isub = 1
   
    targetSels = [
        'photons.chIsoX[0][%d] < %f' % (idtune, chIsoCuts[isub][targetwp]),
        'photons.nhIsoX[0][%d] < %f' % (idtune, nhIsoCuts[isub][targetwp]),
        'photons.phIsoX[0][%d] < %f' % (idtune, phIsoCuts[isub][targetwp]),
        'photons.hOverE[0] < %f' % hOverECuts[isub][targetwp]
    ]
    targetSel = ' && '.join(targetSels)
    
    hadronSels = [
        'photons.chIsoX[0][%d] > 3.5 && photons.chIsoX[0][%d] < 5.' % (idtune, idtune),
        'photons.nhIsoX[0][%d] < %f' % (idtune, nhIsoCuts[isub][targetwp]),
        'photons.phIsoX[0][%d] < %f' % (idtune, phIsoCuts[isub][targetwp]),
        'photons.hOverE[0] < %f' % hOverECuts[isub][targetwp]
    ]
    hadronSel = ' && '.join(hadronSels)

    proxySels = [
        'photons.chIsoX[0][%d] > %f && photons.chIsoX[0][%d] < 11.' % (idtune, chIsoCuts[isub][targetwp], idtune),
        'photons.nhIsoX[0][%d] < %f' % (idtune, nhIsoCuts[isub][0]),
        'photons.phIsoX[0][%d] < %f' % (idtune, phIsoCuts[isub][0]),
        'photons.hOverE[0] < %f' % hOverECuts[isub][targetwp],
        'photons.sieie[0] < %f' % sieieCuts[isub][targetwp]
    ]
    proxySel = ' && '.join(proxySels)

    nminus2 = ' && '.join(targetSels[1:])

    sieieCut = 'photons.sieie[0] < %f' % sieieCuts[isub][targetwp]
    
    # garbage collection
    if subdet == 'barrel':
        template = ROOT.TH1D('template', ';#sigma_{i#etai#eta}', 44, 0.004, 0.015)
    else:
        template = ROOT.TH1D('template', ';#sigma_{i#etai#eta}', 45, 0.015, 0.06)
    ratioTemplate = ROOT.TH1D('ratio', ';I_{CH} (GeV)', 3, array.array('d', [0., chIsoCuts[isub][1], 3.5, 5.]))
    ptTotal = ROOT.TH1D('ptTotal', '', 1, 0., 1.)
    outputFile = ROOT.TFile.Open(outputFileName, 'recreate')
    
    # target and hadron templates
    dataPlotter = ROOT.multidraw.MultiDraw()
    dataPlotter.setWeightBranch('')
    
    lumi = 0.
    for sample in allsamples.getmany(fakeParams.measurementDataset):
        utils.addSkimPaths(dataPlotter, sample.name, fakeParams.measurementSelection)
        lumi += sample.lumi

    if subdet == 'barrel':
        dataPlotter.setFilter('t1Met.pt < 100. && photons.isEB[0]')
    else:
        dataPlotter.setFilter('t1Met.pt < 100. && !photons.isEB[0]')

    mcPlotter = ROOT.multidraw.MultiDraw()
    for sample in allsamples.getmany(fakeParams.measurementMC):
        utils.addSkimPaths(mcPlotter, sample.name, fakeParams.measurementSelection)
    
    if subdet == 'barrel':
        mcPlotter.setFilter('t1Met.pt < 100. && photons.isEB[0]')
    else:
        mcPlotter.setFilter('t1Met.pt < 100. && !photons.isEB[0]')
    mcPlotter.setConstantWeight(lumi)

    # temporary - bug in skimmer weight = 0
    mcPlotter.setWeightBranch('')
    mcPlotter.setReweight('weight_crosssection * weight_PUWeight * weight_ElectronVetoSF * weight_MuonVetoSF * weight_QCDCorrection')

    for plotter in [dataPlotter, mcPlotter]:
        plotter.addCut('target', targetSel)
        plotter.addCut('hadron', hadronSel)

    dataPlotter.addCut('full', ' && '.join([targetSel, sieieCut]))
    dataPlotter.addCut('proxy', proxySel)
    mcPlotter.addCut('nminus2', nminus2)

    targets = []
    hadrons = []
    targpts = []
    proxypts = []
    photons = []
    sbphotons = []
    ratios = []

    categorization = '0'

    for ipt in range(len(ptBinning) - 1):
        ptlow = ptBinning[ipt]
        pthigh = ptBinning[ipt + 1]

        name = '%d_%d' % (ptlow, pthigh)
        if ipt != 0:
            categorization += '+(photons.scRawPt[0] > %f)' % ptlow
    
        outputFile.cd()
        targets.append(template.Clone('target_' + name))
        hadrons.append(template.Clone('hadron_' + name))
        targpts.append(ptTotal.Clone('targpt_' + name))
        proxypts.append(ptTotal.Clone('proxypt_' + name))
        photons.append(template.Clone('photon_' + name))
        sbphotons.append(template.Clone('sbphoton_' + name))
        ratios.append(ratioTemplate.Clone('ratio_' + name))

    for cut in ['target', 'hadron', 'full', 'proxy']:
        dataPlotter.setCategorization(cut, categorization)
    for cut in ['target', 'hadron', 'nminus2']:
        mcPlotter.setCategorization(cut, categorization)

    _arrays = []

    array = ROOT.TObjArray()
    _arrays.append(array)
    for h in targets:
        array.Add(h)
    dataPlotter.addPlotList(array, 'photons.sieie[0]', 'target')

    array = ROOT.TObjArray()
    _arrays.append(array)
    for h in hadrons:
        array.Add(h)
    dataPlotter.addPlotList(array, 'photons.sieie[0]', 'hadron')

    array = ROOT.TObjArray()
    _arrays.append(array)
    for h in targpts:
        array.Add(h)
    dataPlotter.addPlotList(array, '0.5', 'full', 'photons.scRawPt[0]')
    
    array = ROOT.TObjArray()
    _arrays.append(array)
    for h in proxypts:
        array.Add(h)
    dataPlotter.addPlotList(array, '0.5', 'proxy', 'photons.scRawPt[0]')

    array = ROOT.TObjArray()
    _arrays.append(array)
    for h in photons:
        array.Add(h)
    mcPlotter.addPlotList(array, 'photons.sieie[0]', 'target')

    array = ROOT.TObjArray()
    _arrays.append(array)
    for h in sbphotons:
        array.Add(h)
    mcPlotter.addPlotList(array, 'photons.sieie[0]', 'hadron')

    array = ROOT.TObjArray()
    _arrays.append(array)
    for h in ratios:
        array.Add(h)
    mcPlotter.addPlotList(array, 'TMath::Max(photons.chIsoX[0][%d], 0.)' % idtune, 'nminus2')

    dataPlotter.execute()
    mcPlotter.execute()
    
    outputFile.cd()
    outputFile.Write()

else:
    outputFile = ROOT.TFile.Open(outputFileName)

ROOT.gROOT.LoadMacro(basedir + '/purity/SignalSubtraction.cc+')
ssfitter = ROOT.SSFitter.singleton()

canvas = plotstyle.RatioCanvas()
pdir = config.plotDir + '/hadron_fake'

fracs = ROOT.TGraphAsymmErrors(len(ptBinning) - 1)
fracs.SetLineColor(ROOT.kBlack)
fracs.SetLineWidth(2)
fracs.SetMarkerColor(ROOT.kBlack)
fracs.SetMarkerStyle(8)

tfact = ROOT.TGraphAsymmErrors(len(ptBinning) - 1)
tfact.SetLineColor(ROOT.kBlue)
tfact.SetLineWidth(2)
tfact.SetMarkerColor(ROOT.kBlue)
tfact.SetMarkerStyle(8)

for ipt in range(len(ptBinning) - 1):
    ptlow = ptBinning[ipt]
    pthigh = ptBinning[ipt + 1]

    name = '%d_%d' % (ptlow, pthigh)

    target = outputFile.Get('target_' + name)
    hadron = outputFile.Get('hadron_' + name)
    photon = outputFile.Get('photon_' + name)
    sbphoton = outputFile.Get('sbphoton_' + name)
    ratio = outputFile.Get('ratio_' + name)
    targpt = outputFile.Get('targpt_' + name)
    proxypt = outputFile.Get('proxypt_' + name)

    ssfitter.initialize(target, photon, hadron, sbphoton, ratio.GetBinContent(3) / ratio.GetBinContent(1))
    ssfitter.fit()

    cut = sieieCuts[0][targetwp]
    cutBin = target.FindFixBin(cut)
    if target.GetXaxis().GetBinLowEdge(cutBin) == cut:
        cutBin -= 1

    purity = ssfitter.getPurity(cutBin)
    nReal = ssfitter.getNsig(cutBin)
    nFake = ssfitter.getNbkg(cutBin)

    ssfitter.preparePlot()

    plots = [
        ssfitter.getTotal(),
        ssfitter.getSignal(),
        ssfitter.getBackground(),
        ssfitter.getSubtractedBackground(),
        ssfitter.getTarget()
    ]
    for plot in plots:
        for iX in range(1, plot.GetNbinsX() + 1):
            if plot.GetBinContent(iX) < 0.:
                plot.SetBinContent(iX, 1.e-6)

    idxTotal = canvas.addHistogram(plots[0])
    for plot in plots[1:-1]:
        canvas.addHistogram(plot)
    idxTarget = canvas.addHistogram(plots[-1], drawOpt='EP')

    canvas.addText("Fake frac.: %.3f" % (1. - purity), 0.525, 0.8, 0.55, 0.9)

    canvas.printWeb(pdir, 'ssfit_' + name, rList=[idxTotal, idxTarget], logy=False)
    canvas.ylimits = (0.1, max(plots[0].GetMaximum(), plots[-1].GetMaximum()) * 2.)
    canvas.printWeb(pdir, 'ssfit_' + name + '_log', rList=[idxTotal, idxTarget], logy=True)
    canvas.ylimits = (0., -1.)
    canvas.Clear(full=True)

    print (ptlow, pthigh), purity, nReal, nFake

    nTotal = nReal + nFake
    stat = purity - ROOT.TEfficiency.ClopperPearson(int(nTotal), int(nReal), 0.6827, False)

    ntarg = targpt.GetEntries()

    x = targpt.GetBinContent(1) / ntarg
    fracs.SetPoint(ipt, x, 1. - purity)
    fracs.SetPointError(ipt, x - ptBinning[ipt], ptBinning[ipt + 1] - x, stat, stat)

    nproxy = proxypt.GetEntries()

    x = proxypt.GetBinContent(1) / nproxy
    tfact.SetPoint(ipt, x, (1. - purity) * ntarg / nproxy)
    tfact.SetPointError(ipt, x - ptBinning[ipt], ptBinning[ipt + 1] - x, stat * ntarg / nproxy, stat * ntarg / nproxy)

scanvas = plotstyle.SimpleCanvas()

fracs.SetMinimum(0.)
fracs.SetMaximum(0.08)
fracs.GetXaxis().SetRangeUser(ptBinning[0], ptBinning[-1])

fracs.GetXaxis().SetTitle('E_{T}^{#gamma} (GeV)')
fracs.SetTitle('Fake fraction')

#fracfit = ROOT.TF1('fracfit', '[0] + [1] / (x - [2])', ptBinning[0], ptBinning[-1)]
#fracfit.SetParameters(0., 6., 50.)
fracfit = ROOT.TF1('fracfit', '[0] * TMath::Exp([1] * (x - %f))' % ptBinning[0], ptBinning[0], ptBinning[-1])
fracfit.SetParameters(0.1, -0.01)
fitres = fracs.Fit(fracfit, 'S').Get()
sfitres = '[%.2f#pm%.2f] exp([%.4f#pm%.4f]x)' % (fitres.Value(0), fitres.Error(0), fitres.Value(1), fitres.Error(1))

scanvas.addHistogram(fracs)
scanvas.addText(sfitres, 0.5, 0.7, 0.9, 0.8)

scanvas.printWeb(pdir, 'fakefrac', logy=False)
scanvas.Clear(full=True)

tfact.SetMinimum(0.)
tfact.SetMaximum(0.25)
tfact.GetXaxis().SetRangeUser(ptBinning[0], 300.)

tfact.GetXaxis().SetTitle('E_{T}^{#gamma} (GeV)')
tfact.SetTitle('Transfer factor')

#tfactfit = ROOT.TF1('tfactfit', '[0] + [1] / (x - [2])', ptBinning[0], ptBinning[-1])
#tfactfit.SetParameters(0., 6., 50.)
tfactfit = ROOT.TF1('tfactfit', '[0] * TMath::Exp([1] * (x - %f))' % ptBinning[0], ptBinning[0], ptBinning[-1])
tfactfit.SetParameters(0.2, -0.001)
fitres = tfact.Fit(tfactfit, 'S').Get()
sfitres = '[%.2f#pm%.2f] exp([%.4f#pm%.4f]x)' % (fitres.Value(0), fitres.Error(0), fitres.Value(1), fitres.Error(1))

scanvas.addHistogram(tfact)
scanvas.addText(sfitres, 0.5, 0.7, 0.9, 0.8)

scanvas.printWeb(pdir, 'tfactor', logy=False)
