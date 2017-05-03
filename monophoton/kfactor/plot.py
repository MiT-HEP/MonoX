import os
import sys
import math
import array
import ROOT

ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

sys.path.append(basedir)

import config
from datasets import allsamples
from plotstyle import RatioCanvas

plots = [
    ('gammaPt', 'Photon p_{T};p_{T}^{#gamma} (GeV);pb / GeV', (45, 100., 1000.), 'hasMatchingPhoton', True),
    ('gammaEta', 'Photon #eta;#eta^{#gamma};pb / 0.2', (50, -5., 5.), 'hasMatchingPhoton', False),
    ('jet1Pt', 'Leading jet p_{T};p_{T}^{j1} (GeV);pb / GeV', (50, 0., 1000.), 'jet1Pt > 0.', True),
    ('jet1Eta', 'Leading jet #eta;#eta^{j1};pb / 0.2', (50, -5., 5.), 'jet1Pt > 0.', False),
    ('jet2Pt', 'Trailing jet p_{T};p_{T}^{j2} (GeV);pb / GeV', (50, 0., 1000.), 'jet2Pt > 0.', True),
    ('jet2Eta', 'Trailing jet #eta;#eta^{j2};pb / 0.2', (50, -5., 5.), 'jet2Pt > 0.', False),
    ('vPt', 'Vector boson p_{T};p_{T}^{V} (GeV);pb / GeV', (50, 0., 1000.), 'hasBoson', True),
    ('vEta', 'Vector boson #eta;#eta^{V};pb / 0.2', (50, -5., 5.), 'hasBoson', False),
    ('vM', 'Vector boson mass;m^{V} (GeV);pb / GeV', (50, 0., 200.), 'hasBoson', False),
    ('vgammaDPhi', '#Delta#phi(#gamma, V);#Delta#phi;pb / (#pi/30)', (30, 0., math.pi), 'hasMatchingPhoton && hasBoson', False),
    ('vgammaPt', 'V#gamma p_{T};p_{T} (GeV);pb / GeV', (50, 0., 1000.), 'hasMatchingPhoton && hasBoson', True),
    ('vgammaEta', 'V#gamma #eta;#eta;pb / 0.2', (50, -5., 5.), 'hasMatchingPhoton && hasBoson', False),
    ('vgammaM', 'V#gamma mass;m_{V#gamma} (GeV);pb / GeV', (50, 0., 500.), 'hasMatchingPhoton && hasBoson', True),
    ('pgammaPt', '#gamma p_{T} (parton level);p_{T} (GeV);pb / GeV', (50, 0., 1000.), '1', True),
    ('pgammaEta', '#gamma #eta (parton level);#eta;pb / 0.2', (50, -5., 5.), '1', False),
    ('jgammaDPhi', '#Delta#phi(#gamma, j1);#Delta#phi;pb / (#pi/30)', (30, 0., math.pi), 'hasMatchingPhoton && jet1Pt > 0.', False)
]

samples = [
    ('znng130MP', ('znng-130', 'znng-130-o'), 'pgammaPt > 140.'),
    ('wnlg130MP', ('wnlg-130', 'wnlg-130-o'), 'pgammaPt > 140.'),
    ('zllg130MP', ('zllg-130', 'zllg-130-o'), 'pgammaPt > 140.'),
    ('wnlg', ('wnlg', 'wglo'), 'pgammaPt > 0.'),
    ('zllg', ('zllg', None), 'pgammaPt > 0.'),
    ('znng', ('znng', None), 'pgammaPt > 0.'),
    ('wnlg130', ('wnlg-130', 'wglo-130'), 'pgammaPt > 140.'),
    ('wlng500', ('wnlg-500', 'wglo-500'), 'pgammaPt > 510.')
]

source = ROOT.TFile.Open(config.histDir + '/kfactor_trees.root')

canvas = RatioCanvas(sim = True)
canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
canvas.legend.add('lo', 'LO', opt = 'L', color = ROOT.kBlue, lwidth = 2, lstyle = ROOT.kSolid)
canvas.legend.add('nlo', 'NLO', opt = 'L', color = ROOT.kRed, lwidth = 2, lstyle = ROOT.kSolid)

for name, (nlo, lo), baseline in samples:
    nloTree = source.Get(nlo + '/genkine')
    nloSample = allsamples[nlo]

    counter = ROOT.TH1D('counter', '', 1, 0., 1.)
    nloTree.Draw('0.5>>counter', 'weight', 'goff')
    nloSumw = counter.GetBinContent(1)
    counter.Delete()

    if lo is not None:
        loTree = source.Get(lo + '/genkine')
        loSample = allsamples[lo]
        loSumw = loTree.GetEntries()

    for vname, title, binning, cond, logy in plots:
        if type(binning) is tuple:
            hlo = ROOT.TH1D('lo', title, *binning)
            hnlo = ROOT.TH1D('nlo', title, *binning)
        else:
            hlo = ROOT.TH1D('lo', title, len(binning) - 1, array.array('d', binning))
            hnlo = ROOT.TH1D('nlo', title, len(binning) - 1, array.array('d', binning))

        nloTree.Draw(vname + '>>nlo', 'weight * ((%s) && (%s))' % (baseline, cond), 'goff')
        hnlo.Scale(nloSample.crosssection / nloSumw, 'width')
        canvas.addHistogram(hnlo)

        if lo is not None:
            loTree.Draw(vname + '>>lo', '(%s) && (%s)' % (baseline, cond), 'goff')
            hlo.Scale(loSample.crosssection / loSumw, 'width')
            canvas.addHistogram(hlo)

        canvas.applyStyles()

        canvas.printWeb('kfactor', name + '_' + vname, logy = logy)

        canvas.Clear()

        hnlo.Delete()
        hlo.Delete()
