#Direct (without going through purity) computation of hadron fake transfer factors

import os
import sys
import collections
import time
import array
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

import config
import utils
from datasets import allsamples

ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gStyle.SetOptStat(0)

MAKE_TEMPLATES = True

ptBinning = [80, 90, 100, 115, 130, 150, 600]

ROOT.gSystem.Load('libPandaTreeObjects.so')
e = ROOT.panda.Event

ROOT.gROOT.ProcessLine('int idtune = panda::XPhoton::kSpring16;')
idtune = ROOT.idtune

ROOT.gROOT.ProcessLine('double cut;')
def getCut(expr, wp = 1):
    ROOT.gROOT.ProcessLine('cut = panda::XPhoton::%s[%d][0][%d];' % (expr, idtune, wp))
    return ROOT.cut

if MAKE_TEMPLATES:
    ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')
   
    allsamples['sph-16b-m'].lumi = 4778.
    allsamples['sph-16c-m'].lumi = 2430.
    allsamples['sph-16d-m'].lumi = 4044.
    allsamples['sph-16e-m'].lumi = 3284.
    allsamples['sph-16f-m'].lumi = 2292.
    allsamples['sph-16g-m'].lumi = 5190.
    allsamples['sph-16h-m'].lumi = 5470.
   
    targetSels = [
        'photons.chIsoX[0][%d] < %f' % (idtune, getCut('chIsoCuts')),
        'photons.nhIsoX[0][%d] < %f' % (idtune, getCut('nhIsoCuts')),
        'photons.phIsoX[0][%d] < %f' % (idtune, getCut('phIsoCuts')),
        'photons.hOverE[0] < %f' % getCut('hOverECuts')
    ]
    targetSel = ' && '.join(targetSels)
    
    hadronSels = [
        'photons.chIsoX[0][%d] > 3.5 && photons.chIsoX[0][%d] < 5.' % (idtune, idtune),
        'photons.nhIsoX[0][%d] < %f' % (idtune, getCut('nhIsoCuts')),
        'photons.phIsoX[0][%d] < %f' % (idtune, getCut('phIsoCuts')),
        'photons.hOverE[0] < %f' % getCut('hOverECuts')
    ]
    hadronSel = ' && '.join(hadronSels)

    proxySels = [
        'photons.chIsoX[0][%d] > %f && photons.chIsoX[0][%d] < 11.' % (idtune, getCut('chIsoCuts'), idtune),
        'photons.nhIsoX[0][%d] < %f' % (idtune, getCut('nhIsoCuts', 0)),
        'photons.phIsoX[0][%d] < %f' % (idtune, getCut('phIsoCuts', 0)),
        'photons.hOverE[0] < %f' % getCut('hOverECuts'),
        'photons.sieie[0] < %f' % getCut('sieieCuts')
    ]
    proxySel = ' && '.join(proxySels)

    nminus2 = ' && '.join(targetSels[1:])

    sieieCut = 'photons.sieie[0] < %f' % getCut('sieieCuts')
    
    # garbage collection
    histograms = []
    template = ROOT.TH1D('template', ';#sigma_{i#etai#eta}', 44, 0.004, 0.015)
    ratioTemplate = ROOT.TH1D('ratio', ';I_{CH} (GeV)', 3, array.array('d', [0., getCut('chIsoCuts'), 3.5, 5.]))
    ptTotal = ROOT.TH1D('ptTotal', '', 1, 0., 1.)
    outputFile = ROOT.TFile.Open(basedir + '/hist/hadron_fake/direct_vbf.root', 'recreate')
    
    # target and hadron templates
    dataPlotter = ROOT.MultiDraw()
    
    lumi = 0.
    for sample in allsamples.getmany('sph-16*'):
        dataPlotter.addInputPath(utils.getSkimPath(sample.name, 'vbfem'))
        lumi += sample.lumi

    dataPlotter.setBaseSelection('t1Met.pt < 100.')

    mcPlotter = ROOT.MultiDraw()
    for sample in allsamples.getmany('gj-*'):
        mcPlotter.addInputPath(utils.getSkimPath(sample.name, 'vbfem'))
    
    mcPlotter.setBaseSelection('t1Met.pt < 100.')
    mcPlotter.setConstantWeight(lumi)

    for ipt in range(len(ptBinning) - 1):
        ptlow = ptBinning[ipt]
        pthigh = ptBinning[ipt + 1]

        name = '%d_%d' % (ptlow, pthigh)
    
        ptcut = 'photons.scRawPt[0] > %d && photons.scRawPt[0] < %d' % (ptlow, pthigh)
    
        outputFile.cd()
        target = template.Clone('target_' + name)
        histograms.append(target)
        dataPlotter.addPlot(target, 'photons.sieie[0]', targetSel + ' && ' + ptcut)
    
        outputFile.cd()
        hadron = template.Clone('hadron_' + name)
        histograms.append(hadron)
        dataPlotter.addPlot(hadron, 'photons.sieie[0]', hadronSel + ' && ' + ptcut)

        outputFile.cd()
        targpt = ptTotal.Clone('targpt_' + name)
        histograms.append(targpt)
        dataPlotter.addPlot(targpt, '0.5', targetSel + ' && ' + sieieCut + ' && ' + ptcut, True, False, 'photons.scRawPt[0]')

        outputFile.cd()
        proxypt = ptTotal.Clone('proxypt_' + name)
        histograms.append(proxypt)
        dataPlotter.addPlot(proxypt, '0.5', proxySel + ' && ' + ptcut, True, False, 'photons.scRawPt[0]')

        outputFile.cd()
        photon = template.Clone('photon_' + name)
        histograms.append(photon)
        mcPlotter.addPlot(photon, 'photons.sieie[0]', targetSel + ' && ' + ptcut)

        outputFile.cd()
        sbphoton = template.Clone('sbphoton_' + name)
        histograms.append(sbphoton)
        mcPlotter.addPlot(sbphoton, 'photons.sieie[0]', hadronSel + ' && ' + ptcut)

        outputFile.cd()
        ratio = ratioTemplate.Clone('ratio_' + name)
        histograms.append(ratio)
        mcPlotter.addPlot(ratio, 'TMath::Max(photons.chIsoX[0][%d], 0.)' % idtune, nminus2 + ' && ' + ptcut)

    dataPlotter.fillPlots()
    mcPlotter.fillPlots()
    
    outputFile.cd()
    outputFile.Write()

else:
    outputFile = ROOT.TFile.Open(basedir + '/hist/hadron_fake/direct_vbf.root')

ROOT.gROOT.LoadMacro(basedir + '/purity/SignalSubtraction.cc+')
ssfitter = ROOT.SSFitter.singleton()

canvas = ROOT.TCanvas('c1', 'c1', 600, 600)
pdir = '/home/yiiyama/public_html/cmsplots/monophoton/hadronTFactorVBF'

text = ROOT.TLatex()
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

    cut = getCut('sieieCuts')
    cutBin = target.FindFixBin(cut)
    if target.GetXaxis().GetBinLowEdge(cutBin) == cut:
        cutBin -= 1

    purity = ssfitter.getPurity(cutBin)
    nReal = ssfitter.getNsig(cutBin)
    nFake = ssfitter.getNbkg(cutBin)

    ssfitter.plotOn(canvas)
    text.DrawLatexNDC(0.525, 0.8, "Fake frac.: %.3f" % (1. - purity))

    canvas.SetLogy(False)
    canvas.Print(pdir + '/ssfit_' + name + '.png')
    canvas.Print(pdir + '/ssfit_' + name + '.pdf')
    canvas.SetLogy(True)
    canvas.Print(pdir + '/ssfit_' + name + '_log.png')
    canvas.Print(pdir + '/ssfit_' + name + '_log.pdf')

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

fracs.SetMinimum(0.)
fracs.SetMaximum(0.08)
fracs.GetXaxis().SetRangeUser(ptBinning[0], ptBinning[-1])
fracs.Draw('APE')

fracs.GetXaxis().SetTitle('E_{T}^{#gamma} (GeV)')
fracs.SetTitle('Fake fraction')

#powerlaw = ROOT.TF1('powerlaw', '[0] + [1] / (x - [2])', ptBinning[0], ptBinning[-1])
#powerlaw.SetParameters(0., 6., 50.)
#fracs.Fit(powerlaw)
fracs.Fit('expo')

canvas.SetLogy(False)
canvas.Print(pdir + '/fakefrac.png')
canvas.Print(pdir + '/fakefrac.pdf')

tfact.SetMinimum(0.)
tfact.SetMaximum(0.25)
tfact.GetXaxis().SetRangeUser(ptBinning[0], ptBinning[-1])
tfact.Draw('APE')

tfact.GetXaxis().SetTitle('E_{T}^{#gamma} (GeV)')
tfact.SetTitle('Transfer factor')

#powerlaw = ROOT.TF1('powerlaw', '[0] + [1] / (x - [2])', ptBinning[0], ptBinning[-1])
#powerlaw.SetParameters(0., 6., 50.)
#tfact.Fit(powerlaw)
tfact.Fit('expo')

canvas.SetLogy(False)
canvas.Print(pdir + '/tfactor.png')
canvas.Print(pdir + '/tfactor.pdf')
