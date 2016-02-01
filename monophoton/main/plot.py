#!/usr/bin/env python

import sys
import os
import collections
import array
import math
import ROOT

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
from plotstyle import *
from datasets import allsamples
import config

ROOT.gROOT.SetBatch(True)

MAKEPLOTS = True
if '-C' in sys.argv:
    MAKEPLOTS = False
    sys.argv.remove('-C')

GroupSpec = collections.namedtuple('GroupSpec', ['title', 'samples', 'color'])

class VariableDef(object):
    def __init__(self, title, unit, expr, cut, binning, overflow = False, is2D = False):
        self.title = title
        self.unit = unit
        self.expr = expr
        self.cut = cut
        self.binning = binning
        self.overflow = overflow
        self.is2D = is2D


region = sys.argv[1]

try:
    cutMet = int(sys.argv[2])
except IndexError:
    cutMet = 150

cutHighMet = '(t1Met.met > '+str(cutMet)+')'
baselineCut = 'TMath::Abs(photons.time[0]) < 3. && photons.mipEnergy[0] < 6.3 && photons.s4[0] < 0.95 && tauVeto && t1Met.iso'

if region == 'monoph':
    if baselineCut:
        cutStringHighMet = baselineCut + ' && ' + cutHighMet
    else:
        cutStringHighMet = cutHighMet

    defsel = 'monoph'
    obs = GroupSpec('Observed', ['sph-d3', 'sph-d4'], ROOT.kBlack)
    sigGroups = [GroupSpec('add5-2', ['add5-2'], ROOT.kGreen + 4)]
    bkgGroups = [
        ('minor', GroupSpec('t#bar{t}, Z', ['ttg', 'zg'], ROOT.TColor.GetColor(0x55, 0x44, 0xff))),
        ('g', GroupSpec('#gamma + jets', ['g-40', 'g-100', 'g-200', 'g-400', 'g-600'], ROOT.TColor.GetColor(0xff, 0xaa, 0xcc))),
        ('hfake', GroupSpec('Hadronic fakes', [('sph-d3', 'hfake'), ('sph-d4', 'hfake')], ROOT.TColor.GetColor(0xbb, 0xaa, 0xff))),
        ('efake', GroupSpec('Electron fakes', [('sph-d3', 'efake'), ('sph-d4', 'efake')], ROOT.TColor.GetColor(0xff, 0xee, 0x99))),
        ('wg', GroupSpec('W#rightarrowl#nu+#gamma', ['wg'], ROOT.TColor.GetColor(0x99, 0xee, 0xff))),
        ('zg', GroupSpec('Z#rightarrow#nu#nu+#gamma', ['znng-130'], ROOT.TColor.GetColor(0x99, 0xff, 0xaa)))
    ]
    
    variables = {
        'met': VariableDef('E_{T}^{miss}', 'GeV', 't1Met.met', baselineCut, [40. + 10. * x for x in range(11)] + [150. + 50. * x for x in range(3)] + [300. + 50. * x for x in range(4)] + [500. + 100. * x for x in range(2)], overflow = True),
        'metHighMet'+str(cutMet): VariableDef('E_{T}^{miss}', 'GeV', 't1Met.met', cutStringHighMet, range(cutMet,500,50) + [500. + 100. * x for x in range(2)], overflow = True),
        'phoPt': VariableDef('p_{T}^{#gamma}', 'GeV', 'photons.pt[0]', baselineCut, [175.]+[180. + 10. * x for x in range(12)] + [300. + 50. * x for x in range(4)] + [500. + 100. * x for x in range(6)], overflow = True),
        'phoPtHighMet'+str(cutMet): VariableDef('p_{T}^{#gamma}', 'GeV', 'photons.pt[0]', cutStringHighMet, [175.]+[180. + 10. * x for x in range(12)] + [300. + 50. * x for x in range(4)] + [500. + 100. * x for x in range(2)], overflow = True),
        'phoEta': VariableDef('#eta^{#gamma}', '', 'photons.eta[0]', baselineCut, (20, -1.5, 1.5)),
        'phoEtaHighMet'+str(cutMet): VariableDef('#eta^{#gamma}', '', 'photons.eta[0]', cutStringHighMet, (20, -1.5, 1.5)),
        'phoPhi': VariableDef('#phi^{#gamma}', '', 'photons.phi[0]', baselineCut, (20, -math.pi, math.pi)),
        'phoPhiHighMet'+str(cutMet): VariableDef('#phi^{#gamma}', '', 'photons.phi[0]', cutStringHighMet, (20, -math.pi, math.pi)),
        'dPhiPhoMet': VariableDef('#Delta#phi(#gamma, E_{T}^{miss})', baselineCut, 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)', 't1Met.met > 40.', (20, -math.pi, math.pi)),
        'dPhiPhoMetHighMet'+str(cutMet): VariableDef('#Delta#phi(#gamma, E_{T}^{miss})', '', 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)', cutStringHighMet, (20, -math.pi, math.pi)),
        'metPhi': VariableDef('#phi(E_{T}^{miss})', '', 't1Met.phi', baselineCut, (20, -math.pi, math.pi)),
        'metPhiHighMet'+str(cutMet): VariableDef('#phi(E_{T}^{miss})', '', 't1Met.phi', cutStringHighMet, (20, -math.pi, math.pi)),
        'dPhiJetMet': VariableDef('#Delta#phi(E_{T}^{miss}, j)', '', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi - t1Met.phi))', baselineCut, (30, 0., math.pi)),
        'dPhiJetMetHighMet'+str(cutMet): VariableDef('#Delta#phi(E_{T}^{miss}, j)', '', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi - t1Met.phi))', cutStringHighMet, (30, 0., math.pi)),
        'dPhiJetMetMin': VariableDef('min#Delta#phi(E_{T}^{miss}, j)', '', 't1Met.dPhiJetMetMin', '', (30, 0., math.pi), overflow = True),
        'dPhiJetMetMinHighMet'+str(cutMet): VariableDef('min#Delta#phi(E_{T}^{miss}, j)', '', 't1Met.dPhiJetMetMin', cutHighMet, (30, 0., math.pi), overflow = True),
        'njets': VariableDef('N_{jet}', '', 'jets.size', baselineCut, (6, 0., 6.)),
        'njetsHighMet'+str(cutMet): VariableDef('N_{jet}', '', 'jets.size', cutStringHighMet, (6, 0., 6.)),
        'phoPtOverMet': VariableDef('p_{T}^{#gamma}/E_{T}^{miss}', '', 'photons.pt[0]/t1Met.met', baselineCut, (20,0.,4.)),
        'phoPtOverMetHighMet'+str(cutMet): VariableDef('p_{T}^{#gamma}/E_{T}^{miss}', '', 'photons.pt[0]/t1Met.met', cutStringHighMet, (20,0.,4.)),
        'phoPtOverJetPt': VariableDef('p_{T}^{#gamma}/p_{T}^{jet}', '', 'photons.pt[0]/jets.pt[0]', baselineCut, (20,0.,10.)),
        'phoPtOverJetPtHighMet'+str(cutMet): VariableDef('p_{T}^{#gamma}/p_{T}^{jet}', '', 'photons.pt[0]/jets.pt[0]', cutStringHighMet, (20,0.,10.)),
        'nVertex': VariableDef('N_{vertex}', '', 'npv', baselineCut, (40,0.,40.)),
        'nVertexHighMet'+str(cutMet): VariableDef('N_{vertex}', '', 'npv', cutStringHighMet, (40,0.,40.)),
        'sieie': VariableDef('#sigma_{i#eta i#eta}', '', 'photons.sieie[0]', baselineCut, (16, 0.004, 0.012)),
        'sieieHighMet'+str(cutMet): VariableDef('#sigma_{i#eta i#eta}', '', 'photons.sieie[0]', cutStringHighMet, (16, 0.004, 0.012)),
        'r9': VariableDef('r9', '', 'photons.r9', baselineCut, (50, 0.5, 1.)),
        'r9HighMet'+str(cutMet): VariableDef('r9', '', 'photons.r9', cutStringHighMet, (50, 0.5, 1.)),
        's4': VariableDef('s4', '', 'photons.s4', baselineCut, (50, 0.5, 1.)),
        's4HighMet'+str(cutMet): VariableDef('s4', '', 'photons.s4', cutStringHighMet, (50, 0.5, 1.)),
        's4halo': VariableDef('s4', '', 'photons.s4', cutString+' && (photons[0].mipEnergy > 6.3)', (50, 0.5, 1.)),
        's4haloHighMet'+str(cutMet): VariableDef('s4', '', 'photons.s4', cutStringHighMet+' && (photons[0].mipEnergy > 6.3)', (50, 0.5, 1.)),
        's4nonhalo': VariableDef('s4', '', 'photons.s4', cutString+' && !(photons[0].mipEnergy > 6.3)', (50, 0.5, 1.)),
        's4nonhaloHighMet'+str(cutMet): VariableDef('s4', '', 'photons.s4', cutStringHighMet+' && !(photons[0].mipEnergy > 6.3)', (50, 0.5, 1.)),
        'etaWidth': VariableDef('etaWidth', '', 'photons.etaWidth', cutString, (60, 0.004, .016)),
        'etaWidthHighMet'+str(cutMet): VariableDef('etaWidth', '', 'photons.etaWidth', cutStringHighMet, (60, 0.004, .016)),
        'phiWidth': VariableDef('phiWidth', '', 'photons.phiWidth', baselineCut, (25, 0., .05)),
        'phiWidthHighMet'+str(cutMet): VariableDef('phiWidth', '', 'photons.phiWidth', cutStringHighMet, (25, 0., 0.05)),
        'time': VariableDef('time', '', 'photons.time', baselineCut, (40, -4., 4.)),
        'timeHighMet'+str(cutMet): VariableDef('time', '', 'photons.time', cutStringHighMet, (40, -4., 4.)),
        'timeSpan': VariableDef('timeSpan', '', 'photons.timeSpan', baselineCut, (40, -20., 20.)),
        'timeSpanHighMet'+str(cutMet): VariableDef('timeSpan', '', 'photons.timeSpan', cutStringHighMet, (40, -20., 20.))
        }

elif region == 'lowmt':
    wenuNoMetCut = baselineCut + ' && photons.pt[0] < 400.'
    wenuCut = wenuNoMetCut + ' && t1Met.met > 100.'

    defsel = 'lowmt'
    obs = GroupSpec('Observed', ['sph-d3', 'sph-d4'], ROOT.kBlack)
    bkgGroups = [
        ('minor', GroupSpec('t#bar{t}, Z', ['ttg', 'zg'], ROOT.TColor.GetColor(0x55, 0x44, 0xff))),
        ('g', GroupSpec('#gamma + jets', ['g-40', 'g-100', 'g-200', 'g-400', 'g-600'], ROOT.TColor.GetColor(0xff, 0xaa, 0xcc))),
        ('hfake', GroupSpec('Hadronic fakes', [('sph-d3', 'hfakelowmt'), ('sph-d4', 'hfakelowmt')], ROOT.TColor.GetColor(0xbb, 0xaa, 0xff))),
        ('efake', GroupSpec('Electron fakes', [('sph-d3', 'efakelowmt'), ('sph-d4', 'efakelowmt')], ROOT.TColor.GetColor(0xff, 0xee, 0x99))),
        ('wg', GroupSpec('W#rightarrowl#nu+#gamma', ['wg'], ROOT.TColor.GetColor(0x99, 0xee, 0xff))),
        ('zg', GroupSpec('Z#rightarrow#nu#nu+#gamma', ['znng-130'], ROOT.TColor.GetColor(0x99, 0xff, 0xaa)))
    ]
    
    variables = {
        'met': VariableDef('E_{T}^{miss}', 'GeV', 't1Met.met', wenuNoMetCut, [40. + 10. * x for x in range(11)] + [150. + 50. * x for x in range(3)] + [300. + 50. * x for x in range(4)] + [500. + 100. * x for x in range(2)], overflow = True),
        'phoPt': VariableDef('p_{T}^{#gamma}', 'GeV', 'photons.pt[0]', wenuCut, [175.] + [180. + 10. * x for x in range(12)] + [300. + 50. * x for x in range(4)] + [500. + 100. * x for x in range(6)], overflow = True),
#        'phoPtHighMet': VariableDef('p_{T}^{#gamma}', 'GeV', 'photons.pt[0]', wenuCut, [175.]+[180. + 10. * x for x in range(12)] + [300. + 50. * x for x in range(4)] + [500. + 100. * x for x in range(2)], overflow = True),
        'phoEta': VariableDef('#eta^{#gamma}', '', 'photons.eta[0]', wenuCut, (20, -1.5, 1.5)),
        'phoPhi': VariableDef('#phi^{#gamma}', '', 'photons.phi[0]', wenuCut, (20, -math.pi, math.pi)),
        'dPhiPhoMet': VariableDef('#Delta#phi(#gamma, E_{T}^{miss})', '', 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)', wenuCut, (20, -1., 1.)),
#        'dPhiPhoMetHighMet': VariableDef('#Delta#phi(#gamma, E_{T}^{miss})', '', 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)', wenuCut, (20, -math.pi, math.pi)),
        'mtPhoMet': VariableDef('M_{T#gamma}', 'GeV', 'TMath::Sqrt(2. * t1Met.met * photons.pt[0] * (1. - TMath::Cos(photons.phi[0] - t1Met.phi)))', wenuCut, (40, 0., 160.)),
#        'mtPhoMetHighMet': VariableDef('M_{T#gamma}', 'GeV', 'TMath::Sqrt(2. * t1Met.met * photons.pt[0] * (1. - TMath::Cos(photons.phi[0] - t1Met.phi)))', wenuCut, (40, 0., 160.)),
        'metPhi': VariableDef('#phi(E_{T}^{miss})', '', 't1Met.phi', wenuCut, (20, -math.pi, math.pi)),
        'njets': VariableDef('N_{jet}', '', 'jets.size', wenuCut, (6, 0., 6.)),
        'jetPt': VariableDef('p_{T}^{j1}', 'GeV', 'jets.pt[0]', wenuCut + ' && jets.size != 0', (30, 30., 800.)),
        'r9': VariableDef('r9', '', 'photons.r9', wenuCut, (50, 0.5, 1.)),
#        'r9HighMet'+str(cutMet): VariableDef('r9', '', 'photons.r9', wenuCut, (50, 0.5, 1.)),
        's4': VariableDef('s4', '', 'photons.s4', wenuCut, (50, 0.5, 1.)),
#        's4HighMet'+str(cutMet): VariableDef('s4', '', 'photons.s4', wenuCut, (50, 0.5, 1.))
    }

elif region == 'dimu':
    defsel = 'dimu'
    obs = GroupSpec('Observed', ['smu-d3', 'smu-d4'], ROOT.kBlack)
    bkgGroups = [
        ('ttg', GroupSpec('t#bar{t}#gamma', ['ttg'], ROOT.TColor.GetColor(0x55, 0x44, 0xff))),
        ('zg', GroupSpec('Z#rightarrowll+#gamma', ['zg'], ROOT.TColor.GetColor(0x99, 0xff, 0xaa)))
    ]

    mass = 'TMath::Sqrt(2. * muons.pt[0] * muons.pt[1] * (TMath::CosH(muons.eta[0] - muons.eta[1]) - TMath::Cos(muons.phi[0] - muons.phi[1])))'
    cut = mass + ' > 50.'

    dR2_00 = 'TMath::Power(photons.eta[0] - muons.eta[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi[0]), 2.)'
    dR2_01 = 'TMath::Power(photons.eta[0] - muons.eta[1], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi[1]), 2.)'
    
    variables = {
        'met': VariableDef('E_{T}^{miss}', 'GeV', 't1Met.met', cut, [40. + 10. * x for x in range(12)] + [160. + 40. * x for x in range(3)]),
        'phoPt': VariableDef('p_{T}^{#gamma}', 'GeV', 'photons.pt[0]', cut, [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)]),
        'phoEta': VariableDef('#eta^{#gamma}', '', 'photons.eta[0]', cut, (20, -1.5, 1.5)),
        'phoPhi': VariableDef('#phi^{#gamma}', '', 'photons.phi[0]', cut, (20, -math.pi, math.pi)),
        'dPhiPhoMet': VariableDef('#Delta#phi(#gamma, E_{T}^{miss})', '', 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)', cut, (20, -math.pi, math.pi)),
        'dimumass': VariableDef('M_{#mu#mu}', 'GeV', mass, cut, (30, 50., 200.)),
        'dRPhoMu': VariableDef('#DeltaR(#gamma, #mu)_{min}', '', 'TMath::Sqrt(TMath::Min(%s, %s))' % (dR2_00, dR2_01), '', (20, 0., 4.)),
        'njets': VariableDef('N_{jet}', '', 'jets.size', cut, (10, 0., 10.))
    }

elif region == 'monomu':
    defsel = 'monomu'
    obs = GroupSpec('Observed', ['smu-d3', 'smu-d4'], ROOT.kBlack)
    bkgGroups = [
        ('wg', GroupSpec('W#gamma', ['wg'], ROOT.TColor.GetColor(0x99, 0xee, 0xff))),
        ('ttg', GroupSpec('t#bar{t}#gamma', ['ttg'], ROOT.TColor.GetColor(0x55, 0x44, 0xff))),
        ('zg', GroupSpec('Z#rightarrowll+#gamma', ['zg'], ROOT.TColor.GetColor(0x99, 0xff, 0xaa)))
    ]
    
    variables = {
        'met': VariableDef('E_{T}^{miss}', 'GeV', 't1Met.met', '', [40. + 10. * x for x in range(12)] + [160. + 40. * x for x in range(3)]),
        'mt': VariableDef('M_{T}', 'GeV', 'TMath::Sqrt(2. * t1Met.met * muons.pt[0] * (1. - TMath::Cos(TVector2::Phi_mpi_pi(t1Met.phi - muons.phi[0]))))', '', [0. + 10. * x for x in range(16)] + [160. + 40. * x for x in range(3)]),
        'phoPt': VariableDef('p_{T}^{#gamma}', 'GeV', 'photons.pt[0]', '', [60.] + [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)]),
        'phoEta': VariableDef('#eta^{#gamma}', '', 'photons.eta[0]', '', (20, -1.5, 1.5)),
        'phoPhi': VariableDef('#phi^{#gamma}', '', 'photons.phi[0]', '', (20, -math.pi, math.pi)),
        'dPhiPhoMet': VariableDef('#Delta#phi(#gamma, E_{T}^{miss})', '', 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)', '', (20, -math.pi, math.pi)),
        'dRPhoMu': VariableDef('#DeltaR(#gamma, #mu)', '', 'TMath::Sqrt(TMath::Power(photons.eta[0] - muons.eta[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi[0]), 2.))', '', (20, 0., 4.)),
        'njets': VariableDef('N_{jet}', '', 'jets.size', '', (10, 0., 10.))
    }

elif region == 'diel':
    defsel = 'diel'
    obs = GroupSpec('Observed', ['sel-d3', 'sel-d4'], ROOT.kBlack)
    bkgGroups = [
        ('ttg', GroupSpec('t#bar{t}#gamma', ['ttg'], ROOT.TColor.GetColor(0x55, 0x44, 0xff))),
        ('zg', GroupSpec('Z#rightarrowll+#gamma', ['zg'], ROOT.TColor.GetColor(0x99, 0xff, 0xaa)))
    ]

    mass = 'TMath::Sqrt(2. * electrons.pt[0] * electrons.pt[1] * (TMath::CosH(electrons.eta[0] - electrons.eta[1]) - TMath::Cos(electrons.phi[0] - electrons.phi[1])))'
    cut = mass + ' > 50.'

    dR2_00 = 'TMath::Power(photons.eta[0] - electrons.eta[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - electrons.phi[0]), 2.)'
    dR2_01 = 'TMath::Power(photons.eta[0] - electrons.eta[1], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - electrons.phi[1]), 2.)'
    
    variables = {
        'met': VariableDef('E_{T}^{miss}', 'GeV', 't1Met.met', cut, [40. + 10. * x for x in range(12)] + [160. + 40. * x for x in range(3)]),
        'phoPt': VariableDef('p_{T}^{#gamma}', 'GeV', 'photons.pt[0]', cut, [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)]),
        'phoEta': VariableDef('#eta^{#gamma}', '', 'photons.eta[0]', cut, (20, -1.5, 1.5)),
        'phoPhi': VariableDef('#phi^{#gamma}', '', 'photons.phi[0]', cut, (20, -math.pi, math.pi)),
        'dPhiPhoMet': VariableDef('#Delta#phi(#gamma, E_{T}^{miss})', '', 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)', cut, (20, -math.pi, math.pi)),
        'dielmass': VariableDef('M_{ee}', 'GeV', mass, cut, (30, 50., 200.)),
        'dRPhoEl': VariableDef('#DeltaR(#gamma, e)_{min}', '', 'TMath::Sqrt(TMath::Min(%s, %s))' % (dR2_00, dR2_01), '', (20, 0., 4.)),
        'njets': VariableDef('N_{jet}', '', 'jets.size', cut, (10, 0., 10.)),
    }

elif region == 'monoel':
    defsel = 'monoel'
    obs = GroupSpec('Observed', ['sel-d3', 'sel-d4'], ROOT.kBlack)
    bkgGroups = [
        ('wg', GroupSpec('W#gamma', ['wg'], ROOT.TColor.GetColor(0x99, 0xee, 0xff))),
        ('ttg', GroupSpec('t#bar{t}#gamma', ['ttg'], ROOT.TColor.GetColor(0x55, 0x44, 0xff))),
        ('zg', GroupSpec('Z#rightarrowll+#gamma', ['zg'], ROOT.TColor.GetColor(0x99, 0xff, 0xaa))),
        ('eefake', GroupSpec('Electron fakes', [('sel-d3', 'eefake'), ('sel-d4', 'eefake')], ROOT.TColor.GetColor(0xff, 0xee, 0x99)))
    ]
    
    variables = {
        'met': VariableDef('E_{T}^{miss}', 'GeV', 't1Met.met', '', [40. + 10. * x for x in range(12)] + [160. + 40. * x for x in range(3)]),
        'mt': VariableDef('M_{T}', 'GeV', 'TMath::Sqrt(2. * t1Met.met * electrons.pt[0] * (1. - TMath::Cos(TVector2::Phi_mpi_pi(t1Met.phi - electrons.phi[0]))))', '', [0. + 10. * x for x in range(16)] + [160. + 40. * x for x in range(3)]),
        'phoPt': VariableDef('p_{T}^{#gamma}', 'GeV', 'photons.pt[0]', '', [60.] + [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)]),
        'phoEta': VariableDef('#eta^{#gamma}', '', 'photons.eta[0]', '', (20, -1.5, 1.5)),
        'phoPhi': VariableDef('#phi^{#gamma}', '', 'photons.phi[0]', '', (20, -math.pi, math.pi)),
        'dPhiPhoMet': VariableDef('#Delta#phi(#gamma, E_{T}^{miss})', '', 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)', '', (20, -math.pi, math.pi)),
        'dRPhoEl': VariableDef('#DeltaR(#gamma, #mu)', '', 'TMath::Sqrt(TMath::Power(photons.eta[0] - electrons.eta[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - electrons.phi[0]), 2.))', '', (20, 0., 4.)),
        'njets': VariableDef('N_{jet}', '', 'jets.size', '', (10, 0., 10.))
    }

elif region == 'elmu':
    defsel = 'elmu'
    obs = GroupSpec('Observed', ['smu-d3', 'smu-d4'], ROOT.kBlack)
    bkgGroups = [
        ('ttg', GroupSpec('t#bar{t}#gamma', ['ttg'], ROOT.TColor.GetColor(0x55, 0x44, 0xff))),
        ('zg', GroupSpec('Z#rightarrowll+#gamma', ['zg'], ROOT.TColor.GetColor(0x99, 0xff, 0xaa)))
    ]
    
    variables = {
        'met': VariableDef('E_{T}^{miss}', 'GeV', 't1Met.met', '', [40. + 10. * x for x in range(12)] + [160. + 40. * x for x in range(3)]),
        'phoPt': VariableDef('p_{T}^{#gamma}', 'GeV', 'photons.pt[0]', '', [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)]),
        'phoEta': VariableDef('#eta^{#gamma}', '', 'photons.eta[0]', '', (20, -1.5, 1.5)),
        'phoPhi': VariableDef('#phi^{#gamma}', '', 'photons.phi[0]', '', (20, -math.pi, math.pi)),
        'dPhiPhoMet': VariableDef('#Delta#phi(#gamma, E_{T}^{miss})', '', 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)', '', (20, -math.pi, math.pi)),
        'njets': VariableDef('N_{jet}', '', 'jets.size', '', (10, 0., 10.))
    }

else:
    print 'Unknown region', region
    sys.exit(0)

countDef = VariableDef('N_{cand}', '', '0.5', baselineCut + ' && ' + cutHighMet, (1, 0., 1.))
limitDef = VariableDef( ('p_{T}^{#gamma}','E_{T}^{miss}'), ('GeV','GeV'), 't1Met.met:photons.pt[0]', '',
                        ( [175. + 25. * x for x in range(18)], [0. + 50. * x for x in range(13)]), is2D = True)

sensitive = {'monoph': ['met', 'metHighMet'+str(cutMet), 'phoPtHighMet'+str(cutMet)]}
blind = 1

lumi = sum([allsamples[s].lumi for s in obs.samples])

def getHist(sampledef, selection, varname, vardef, isSensitive = False):
    source = ROOT.TFile.Open(config.skimDir + '/' + sampledef.name + '_' + selection + '.root')
    tree = source.Get('events')

    if vardef.is2D:
        nbins = []
        arr = []
        for binning in vardef.binning:
            if type(binning) is list:
                nbins_ = len(binning) - 1
                binning_ = list(binning)
            elif type(binning) is tuple:
                nbins_ = binning[0]
                binning_ = [binning[1] + (binning[2] - binning[1]) / nbins * i for i in range(nbins + 1)]
                
            arr_ = array.array('d', binning_)
            nbins.append(nbins_)
            arr.append(arr_)

        hist = ROOT.TH2D(varname + '-' + sampledef.name, '', nbins[0], arr[0], nbins[1], arr[1]) 
    else:
        if type(vardef.binning) is list:
            nbins = len(vardef.binning) - 1
            binning = list(vardef.binning)
        elif type(vardef.binning) is tuple:
            nbins = vardef.binning[0]
            binning = [vardef.binning[1] + (vardef.binning[2] - vardef.binning[1]) / nbins * i for i in range(nbins + 1)]

        arr = array.array('d', binning)

        hist = ROOT.TH1D(varname + '-' + sampledef.name, '', nbins, arr)

    cut = vardef.cut
    if isSensitive and blind > 1:
        if cut:
            cut += ' && event % {blind} == 0'.format(blind = blind)
        else:
            cut = ' event % {blind} == 0'.format(blind = blind)

    if cut:
        weightexpr = 'weight * (%s)' % cut
    else:
        weightexpr = 'weight'

    hist.Sumw2()
    if sampledef.data:
        tree.Draw(vardef.expr + '>>' + varname + '-' + sampledef.name, weightexpr, 'goff')
    else:
        tree.Draw(vardef.expr + '>>' + varname + '-' + sampledef.name, str(lumi) + ' * ' + weightexpr, 'goff')

    if vardef.overflow:
        binning += [binning[-1] + (binning[1] - binning[0])]
        arr = array.array('d', binning)
        hist.SetBins(len(binning) - 1, arr)

    hist.SetDirectory(0)
    if vardef.is2D:
        xtitle = vardef.title[0]
        ytitle = vardef.title[1]
        ztitle = 'Events'
    else:
        for iX in range(1, nbins + 1):
            cont = hist.GetBinContent(iX)
            err = hist.GetBinError(iX)
            w = hist.GetXaxis().GetBinWidth(iX)
            if vardef.unit:
                hist.SetBinContent(iX, cont / w)
                hist.SetBinError(iX, err / w)
            else:
                if iX == 1:
                    wnorm = w
                hist.SetBinContent(iX, cont / (w / wnorm))
                hist.SetBinError(iX, err / (w / wnorm))

        xtitle = vardef.title
        if vardef.unit:
            xtitle += '(%s)' % vardef.unit

        ytitle = 'Events'
        if hist.GetXaxis().GetBinWidth(1) != 1.:
            ytitle += ' / '
            if vardef.unit:
                ytitle += vardef.unit
            else:
                ytitle += '%.2f' % hist.GetXaxis().GetBinWidth(1)

    hist.GetXaxis().SetTitle(xtitle)
    hist.GetYaxis().SetTitle(ytitle)
    if vardef.is2D:
        hist.GetZaxis().SetTitle(ztitle)
        hist.SetMinimum(0.)

    return hist


if MAKEPLOTS:

    canvas = DataMCCanvas(lumi = lumi)
    simpleCanvas = SimpleCanvas(lumi = lumi, sim = True)
    
    print "Starting plot making."
    
    for varname, vardef in variables.items():
        isSensitive = region in sensitive and varname in sensitive[region]
    
        canvas.Clear(full = True)
        canvas.legend.setPosition(0.6, 0.55, 0.92, SimpleCanvas.YMAX - 0.01)
    
        if isSensitive:
            canvas.lumi = lumi / blind
    
        for gName, group in bkgGroups:
            idx = -1
            for sName in group.samples:
                if type(sName) is tuple:
                    selection = sName[1]
                    sName = sName[0]
                else:
                    selection = defsel
    
                hist = getHist(allsamples[sName], selection, varname, vardef)
    
                for iX in range(1, hist.GetNbinsX() + 1):
                    if hist.GetBinContent(iX) < 0.:
                        hist.SetBinContent(iX, 0.)
    
                if isSensitive and blind > 1:
                    hist.Scale(1. / blind)
    
                idx = canvas.addStacked(hist, title = group.title, color = group.color, idx = idx)
                
        if isSensitive:
            for sGroup in sigGroups:
                idx = -1
                for sName in sGroup.samples:
                    hist = getHist(allsamples[sName], defsel, varname, vardef)
                    if blind > 1:
                        hist.Scale(1. / blind)
    
                    idx = canvas.addSignal(hist, title = sGroup.title, color = sGroup.color, idx = idx)
    
        for sName in obs.samples:
            hist = getHist(allsamples[sName], defsel, varname, vardef, isSensitive)
            canvas.addObs(hist, title = obs.title)
    
        canvas.xtitle = canvas.obsHistogram().GetXaxis().GetTitle()
        canvas.ytitle = canvas.obsHistogram().GetYaxis().GetTitle()
    
        canvas.printWeb('monophoton/' + region, varname)
        # canvas.printWeb('monophoton/' + region, varname + '-linear', logy = False)

print "Finished plotting."
print "Counting yields and preparing limits file."

#canvas = simpleCanvas # this line causes segfault somewhere down the line of DataMCCanvas destruction
hists = {}
counts = {}
for gName, group in bkgGroups:
    counts[gName] = 0.
    for sName in group.samples:
        if type(sName) is tuple:
            selection = sName[1]
            sName = sName[0]
        else:
            selection = defsel

        hist = getHist(allsamples[sName], selection, 'count', countDef)
        counts[gName] += hist.GetBinContent(1) / blind

        hist2D = getHist(allsamples[sName], selection, 'limit', limitDef, isSensitive = True)
        if gName in hists.keys():
            hists[gName].Add(hist2D)
        else:
            hists[gName] = hist2D
            hists[gName].SetName(gName)

if region == 'monoph':
    for sGroup in sigGroups:
        for sName in sGroup.samples:
            hist = getHist(allsamples[sName], defsel, 'count', countDef)
            counts[sName] = hist.GetBinContent(1) / blind

            hist2D = getHist(allsamples[sName], selection, 'limit', limitDef, isSensitive = True)
            if sName in hists.keys():
                hists[sName].Add(hist2D)
            else:
                hists[sName] = hist2D
                hists[sName].SetName(sName)

counts['obs'] = 0.
for sName in obs.samples:
    hist = getHist(allsamples[sName], defsel, 'count', countDef, isSensitive = True)
    counts['obs'] += hist.GetBinContent(1)

    hist2D = getHist(allsamples[sName], selection, 'limit', limitDef, isSensitive = True)
    if 'obs' in hists.keys():
        hists['obs'].Add(hist2D)
    else:
        hists['obs'] = hist2D
        hists['obs'].SetName('data_obs')

limitFile = ROOT.TFile(config.histDir + "/monoph.root", "RECREATE")
limitFile.cd()

for name, hist in hists.iteritems():
    hist.Write()

bkgTotal = 0.
print 'Yields for MET > '+str(cutMet)
for gName, group in reversed(bkgGroups):
    bkgTotal += counts[gName]
    print '%+10s  %.1f' % (gName, counts[gName])

print '---------------------'
print '%+10s  %.1f' % ('bkg', bkgTotal)

print '====================='

if region == 'monoph':
    for sGroup in sigGroups:
        for sName in sGroup.samples:
            print '%+10s  %.1f' % (sName, counts[sName])

print '====================='
print '%+10s  %.1f' % ('obs', counts['obs'])
