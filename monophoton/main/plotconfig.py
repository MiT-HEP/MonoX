import sys
import os
import math
from pprint import pprint

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from main.plotutil import *

argv = list(sys.argv)
sys.argv = []
import ROOT
black = ROOT.kBlack # need to load something from ROOT to actually import
sys.argv = argv

dPhiPhoMet = 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)'
mtPhoMet = 'TMath::Sqrt(2. * t1Met.met * photons.pt[0] * (1. - TMath::Cos(photons.phi[0] - t1Met.phi)))'
        
def getConfig(confName):

    if confName == 'monoph':
        config = PlotConfig('monoph', ['sph-d3', 'sph-d4'])
        config.baseline = 'photons.pt[0] > 175. && t1Met.photonDPhi > 2. && t1Met.minJetDPhi > 0.5'
        config.fullSelection = 't1Met.met > 170.'
        config.sigGroups = [
#            GroupSpec('add', 'ADD', samples = ['add-*']),
            GroupSpec('dmv', 'DM V', samples = ['dmv-*']),
            GroupSpec('dma', 'DM A', samples = ['dma-*']),
            GroupSpec('dmvfs', 'DM V', samples = ['dmvfs-*']),
            GroupSpec('dmafs', 'DM A', samples = ['dmafs-*'])
        ]            
        config.signalPoints = [
#            SampleSpec('add-5-2', 'ADD n=5 M_{D}=2TeV', group = config.findGroup('add'), color = 41), # 0.07069/pb
            SampleSpec('dmv-1000-150', 'DM V M_{med}=1TeV M_{DM}=150GeV', group = config.findGroup('dmv'), color = 46), # 0.01437/pb
            SampleSpec('dma-500-1', 'DM A M_{med}=500GeV M_{DM}=1GeV', group = config.findGroup('dma'), color = 30) # 0.07827/pb 
        ]
        config.bkgGroups = [
            GroupSpec('spike', 'Spikes', count = 4., color = None),
            GroupSpec('minor', 'Minor SM', samples = ['ttg', 'zllg-130', 'wlnu-100','wlnu-200', 'wlnu-400', 'wlnu-600'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            # GroupSpec('dytt', 'DY, tt', samples = ['tt', 'dy-50-100', 'dy-50-200', 'dy-50-400', 'dy-50-600'], color = ROOT.TColor.GetColor(0xbb, 0x44, 0xCC)), 
            GroupSpec('gjets', '#gamma + jets', samples = ['gj-40', 'gj-100', 'gj-200', 'gj-400', 'gj-600'], color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            # GroupSpec('qcdmc', 'QCD fakes (MC)', samples = ['qcd-200', 'qcd-300', 'qcd-500', 'qcd-700', 'qcd-1000'], region = 'gjets', color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            # GroupSpec('qcddata', 'QCD fakes (Data)', samples = ['sph-d3', 'sph-d4'], region = 'gjets', color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            # GroupSpec('gjetsfake', '#gamma + jets (Fakes)', samples = ['gj-40', 'gj-100', 'gj-200', 'gj-400', 'gj-600'], region = 'gjets', color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            GroupSpec('halo', 'Beam halo', samples = ['sph-d3', 'sph-d4'], region = 'halo', color = ROOT.TColor.GetColor(0xff, 0x99, 0x33)),
            GroupSpec('hfake', 'Hadronic fakes', samples = ['sph-d3', 'sph-d4'], region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = ['sph-d3', 'sph-d4'], region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            # GroupSpec('efake', 'Electron fakes (MC)', samples = ['wlnu-100', 'wlnu-200', 'wlnu-400', 'wlnu-600'], region = 'withel', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('metWide', 'E_{T}^{miss}', 't1Met.met', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('metHigh', 'E_{T}^{miss}', 't1Met.met', [170., 230., 290., 350., 410., 500., 600., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (22, 200., 1300.), unit = 'GeV', overflow = True, blind = (600., 2000.)),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta[0]', (20, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi[0]', (20, -math.pi, math.pi)),
            VariableDef('nphotons', 'N_{#gamma}', 'photons.size', (4, 0., 4.)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', "t1Met.photonDPhi", (30, 0., math.pi), applyBaseline = False, cut = 'photons.pt[0] > 175. && t1Met.minJetDPhi > 0.5 && t1Met.met > 60.', overflow = True),
            VariableDef('dPhiPhoMetCrackVeto', '#Delta#phi(#gamma, E_{T}^{miss})', "t1Met.photonDPhi", (30, 0., math.pi), applyBaseline = False, cut = 'photons.pt[0] > 175. && t1Met.minJetDPhi > 0.5 && t1Met.met > 40. && ecalCrackVeto', overflow = True),
            VariableDef('ecalCrackVeto', 'ECAL Crack Veto', "ecalCrackVeto", (2, -0.5, 1.5), applyBaseline = False, cut = 'photons.pt[0] > 175. && t1Met.minJetDPhi > 0.5 && t1Met.met > 40.'),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt > 30.'),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi), applyBaseline = False, cut = 'photons.pt[0] > 175. && t1Met.photonDPhi > 2.', overflow = True),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.), cut = 'jets.pt > 30.'),
            VariableDef('njetsHightPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (6, 0., 6.), cut = 'jets.pt > 100.'),
            VariableDef('jetPt', 'p_{T}^{jet}', 'jets.pt', (20, 30., 530.) , unit = 'GeV', cut = 'jets.pt > 30', overflow = True),
            VariableDef('jetPtCorrection',  '#Delta p_{T}^{jet} (raw, corrected)', 'jets.pt - jets.ptRaw', (11, -10., 100.), unit = 'GeV', cut = 'jets.pt > 30'),
            VariableDef('phoPtOverMet', 'E_{T}^{#gamma}/E_{T}^{miss}', 'photons.pt[0] / t1Met.met', (20, 0., 4.)),
            VariableDef('phoPtOverJetPt', 'E_{T}^{#gamma}/p_{T}^{jet}', 'photons.pt[0] / jets.pt[0]', (20, 0., 10.)),
            VariableDef('metSignif', 'E_{T}^{miss} Significance', 't1Met.met / TMath::Sqrt(t1Met.sumEt)', (15, 0., 30.)),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.)),
            VariableDef('sieie', '#sigma_{i#eta i#eta}', 'photons.sieie[0]', (30, 0.005, 0.020)),
            VariableDef('r9', 'r9', 'photons.r9[0]', (25, 0.7, 1.2)),
            VariableDef('s4', 's4', 'photons.s4[0]', (25, 0.7, 1.2)),
            VariableDef('etaWidth', 'etaWidth', 'photons.etaWidth[0]', (30, 0.005, .020)),
            VariableDef('phiWidth', 'phiWidth', 'photons.phiWidth[0]', (18, 0., 0.05)),
            VariableDef('timeSpan', 'timeSpan', 'photons.timeSpan[0]', (20, -20., 20.))
            ]

        for variable in list(config.variables): # need to clone the list first!
            if variable.name not in ['met', 'metWide', 'metHigh']:
                config.variables.append(variable.clone(variable.name + 'HighMet', applyFullSel = True))
                config.variables.remove(variable)

        config.getVariable('phoPtHighMet').binning = [175., 190., 250., 400., 700., 1000.]

        config.sensitiveVars = ['met', 'metWide', 'metHigh', 'phoPtHighMet', 'mtPhoMet', 'mtPhoMetHighMet'] # , 'dPhiJetMetMinHighMet'] # , 'dPhiPhoMetHighMet']
        
        config.treeMaker = 'MonophotonTreeMaker'

        # Standard MC systematic variations
        for group in config.bkgGroups + config.sigGroups:
            if group.name in ['efake', 'hfake', 'halo', 'spike', 'qcdmc', 'qcddata', 'gjetsfake']:
                continue

            group.variations.append(Variation('lumi', reweight = 0.027))

            group.variations.append(Variation('totalSF', reweight = 0.06))

            # combined into totalSF
            # group.variations.append(Variation('photonSF', reweight = 'photonSF'))
            # group.variations.append(Variation('worstIsoSF', reweight = 0.05))
            # group.variations.append(Variation('leptonvetoSF', reweight = 0.02))
     
            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECUp'), ('t1Met.met', 't1Met.metCorrUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECDown'), ('t1Met.met', 't1Met.metCorrDown')]
            group.variations.append(Variation('jec', replacements = (replUp, replDown)))

            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECUp'), ('photons.pt', 'photons.ptVarUp'), ('t1Met.met', 't1Met.metGECUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECDown'), ('photons.pt', 'photons.ptVarDown'), ('t1Met.met', 't1Met.metGECDown')]
            group.variations.append(Variation('gec', replacements = (replUp, replDown)))

        # Specific systematic variations
        config.findGroup('halo').variations.append(Variation('haloNorm', reweight = 0.79))
        # config.findGroup('halo').variations.append(Variation('haloShape', region = ('haloUp', 'haloDown')))
        config.findGroup('spike').variations.append(Variation('spikeNorm', reweight = 0.5))
        config.findGroup('hfake').variations.append(Variation('hfakeTfactor', region = ('hfakeUp', 'hfakeDown')))
        config.findGroup('efake').variations.append(Variation('egFakerate', reweight = 0.079))
        config.findGroup('wg').variations.append(Variation('vgPDF', reweight = 'pdf'))
        config.findGroup('wg').variations.append(Variation('vgQCDscale', reweight = 'qcdscale'))
        config.findGroup('wg').variations.append(Variation('wgEWK', reweight = 'ewk'))
        config.findGroup('zg').variations.append(Variation('vgPDF', reweight = 'pdf'))
        config.findGroup('zg').variations.append(Variation('vgQCDscale', reweight = 'qcdscale'))
        config.findGroup('zg').variations.append(Variation('zgEWK', reweight = 'ewk'))
        config.findGroup('minor').variations.append(Variation('minorPDF', reweight = 'pdf'))
        config.findGroup('minor').variations.append(Variation('minorQCDscale', reweight = 0.033))
    
    elif confName == 'lowdphi':
        config = PlotConfig('monoph', ['sph-d3', 'sph-d4'])
        config.baseline = 'photons.pt[0] > 175. && t1Met.minJetDPhi < 0.5'
        config.fullSelection = 't1Met.met > 170.'
        config.bkgGroups = [
            GroupSpec('minor', 'minor SM', samples = ['ttg', 'zllg-130', 'wlnu-100','wlnu-200', 'wlnu-400', 'wlnu-600'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = ['sph-d3', 'sph-d4'], region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            GroupSpec('hfake', 'Hadronic fakes', samples = ['sph-d3', 'sph-d4'], region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('gjets', '#gamma + jets', samples = ['gj-40', 'gj-100', 'gj-200', 'gj-400', 'gj-600'], color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('metWide', 'E_{T}^{miss}', 't1Met.met', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (22, 200., 1300.), unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt > 30.'),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi), overflow = True),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.), cut = 'jets.pt > 30.'),
            VariableDef('njetsHightPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (6, 0., 6.), cut = 'jets.pt > 100.'),
            VariableDef('metSignif', 'E_{T}^{miss} Significance', 't1Met.met / TMath::Sqrt(t1Met.sumEt)', (15, 0., 30.)),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
        ]

        for variable in list(config.variables):
            if variable.name not in ['met', 'metWide']:
                config.variables.append(variable.clone(variable.name + 'HighMet', applyFullSel = True))
                config.variables.remove(variable)
    
    elif confName == 'phodphi':
        metCut = 't1Met.met > 170.'
        
        config = PlotConfig('monoph', ['sph-d3', 'sph-d4'])
        config.baseline = 'photons.pt[0] > 175. && t1Met.photonDPhi < 0.5 && t1Met.minJetDPhi > 0.5'
        config.fullSelection = metCut
        config.sigGroups = [
            # GroupSpec('add', 'ADD', samples = ['add-*']),
            # GroupSpec('dmv', 'DM V', samples = ['dmv-*']),
            # GroupSpec('dma', 'DM A', samples = ['dma-*']),
            # GroupSpec('dmvfs', 'DM V', samples = ['dmvfs-*']),
            # GroupSpec('dmafs', 'DM A', samples = ['dmafs-*'])
        ]
        config.signalPoints = [
            # SampleSpec('add-5-2', 'ADD n=5 M_{D}=2TeV', group = config.findGroup('add'), color = 41), # 0.07069/pb
            # SampleSpec('dmv-1000-150', 'DM V M_{med}=1TeV M_{DM}=150GeV', group = config.findGroup('dmv'), color = 46), # 0.01437/pb
            # SampleSpec('dma-500-1', 'DM A M_{med}=500GeV M_{DM}=1GeV', group = config.findGroup('dma'), color = 30) # 0.07827/pb 
        ]
        config.bkgGroups = [
            GroupSpec('minor', 'minor SM', samples = ['ttg', 'zllg-130', 'wlnu-100','wlnu-200', 'wlnu-400', 'wlnu-600'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('gjets', '#gamma + jets', samples = ['gj-40', 'gj-100', 'gj-200', 'gj-400', 'gj-600'], color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            GroupSpec('halo', 'Beam halo', samples = ['sph-d3', 'sph-d4'], region = 'halo', color = ROOT.TColor.GetColor(0xff, 0x99, 0x33)),
            GroupSpec('hfake', 'Hadronic fakes', samples = ['sph-d3', 'sph-d4'], region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = ['sph-d3', 'sph-d4'], region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('metWide', 'E_{T}^{miss}', 't1Met.met', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('metHigh', 'E_{T}^{miss}', 't1Met.met', [170., 230., 290., 350., 410., 500., 600., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, [0. + 10. * x for x in range(21)], unit = 'GeV', overflow = True, blind = (600., 2000.)),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True), # , ymax = 1.2),
            VariableDef('phoEta', '#eta^{#gamma}', 'TMath::Abs(photons.eta[0])', (10, 0., 1.5)), # , ymax = 250),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi[0]', (20, -math.pi, math.pi)),
            VariableDef('nphotons', 'N_{#gamma}', 'photons.size', (4, 0., 4.)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', "t1Met.photonDPhi", (30, 0., math.pi), applyBaseline = False, cut = 'photons.pt[0] > 175. && t1Met.minJetDPhi > 0.5 && t1Met.met > 40.', overflow = True),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt > 30.'),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi), applyBaseline = False, cut = 'photons.pt[0] > 175. && t1Met.photonDPhi < 2.', overflow = True),
            VariableDef('dPhiPhoJetMin', 'min#Delta#phi(#gamma, j)', 'photons.minJetDPhi[0]', (30, 0., math.pi), overflow = True),
            VariableDef('dPhiJetPho', '#Delta#phi(j, #gamma)', 'jets.photonDPhi', (30, 0., math.pi), cut = 'jets.pt > 30.', overflow = True),
            VariableDef('njets', 'N_{jet}', 'jets.size', (8, 0., 8.), cut = 'jets.pt > 30.'), # , ymax = 1200.),
            VariableDef('njetsHightPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (8, 0., 8.), cut = 'jets.pt > 100.'), # , ymax = 1200.),
            VariableDef('jetPt', 'p_{T}^{jet}', 'jets.pt', (20, 30., 1030.) , unit = 'GeV', cut = 'jets.pt > 30', overflow = True),
            VariableDef('jetPtCorrection',  '#Delta p_{T}^{jet} (raw, corrected)', 'jets.pt - jets.ptRaw', (11, -10., 100.), unit = 'GeV', cut = 'jets.pt > 30'),
            VariableDef('jetEta', '#eta^{j}', 'jets.eta', (40, -5.0, 5.0), cut = 'jets.pt > 30.'), # , ymax = 500.),
            VariableDef('jetPhi', '#phi^{j}', 'jets.phi', (20, -math.pi, math.pi), cut = 'jets.pt > 30'), # , ymax = 250),
            VariableDef('phoPtOverMet', 'E_{T}^{#gamma}/E_{T}^{miss}', 'photons.pt[0] / t1Met.met', (20, 0., 4.)),
            VariableDef('phoPtOverJetPt', 'E_{T}^{#gamma}/p_{T}^{jet}', 'photons.pt[0] / jets.pt[0]', (20, 0., 4.)),
            VariableDef('metSignif', 'E_{T}^{miss} Significance', 't1Met.met / TMath::Sqrt(t1Met.sumEt)', (15, 0., 30.)),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.)),
            VariableDef('sieie', '#sigma_{i#eta i#eta}', 'photons.sieie[0]', (30, 0.005, 0.020)), 
            VariableDef('r9', 'r9', 'photons.r9[0]', (25, 0.7, 1.2)),
            VariableDef('s4', 's4', 'photons.s4[0]', (25, 0.7, 1.2)),
            VariableDef('etaWidth', 'etaWidth', 'photons.etaWidth[0]', (30, 0.005, .020)),
            VariableDef('phiWidth', 'phiWidth', 'photons.phiWidth[0]', (18, 0., 0.05)),
            VariableDef('runNumber', 'Run Number / 1000.', 'run / 1000.', (9, 256.5, 261.0)),
            VariableDef('lumiSection', 'Lumi Section', 'lumi', (10, 0., 2000.))
        ]

        for variable in list(config.variables): # need to clone the list first!
            if variable.name not in ['met', 'metWide', 'metHigh']:
                config.variables.append(variable.clone(variable.name + 'HighMet', applyFullSel = True))
                config.variables.remove(variable)
                
        config.getVariable('phoPtHighMet').binning = [175., 190., 250., 400., 700., 1000.]

        config.sensitiveVars = ['met', 'metWide', 'metHigh', 'phoPtHighMet', 'mtPhoMet', 'mtPhoMetHighMet']
        
        config.treeMaker = 'MonophotonTreeMaker'

        # Standard MC systematic variations
        for group in config.bkgGroups + config.sigGroups:
            if group.name == 'efake' or group.name == 'hfake' or group.name == 'halo':
                continue

            ########################################################
            ### By hand reweights are still broken for plotting. ###
            ########################################################

            # group.variations.append(Variation('lumi', reweight = 0.027))

            # group.variations.append(Variation('totalSF', reweight = 0.06))

            # group.variations.append(Variation('photonSF', reweight = 'photonSF'))

            # group.variations.append(Variation('worstIsoSF', reweight = 0.05))

            # group.variations.append(Variation('leptonvetoSF', reweight = 0.02))

            group.variations.append(Variation('pdf', reweight = 'pdf'))
            
            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECUp'), ('t1Met.met', 't1Met.metCorrUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECDown'), ('t1Met.met', 't1Met.metCorrDown')]
            group.variations.append(Variation('jec', replacements = (replUp, replDown)))

            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECUp'), ('photons.pt', 'photons.ptVarUp'), ('t1Met.met', 't1Met.metGECUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECDown'), ('photons.pt', 'photons.ptVarDown'), ('t1Met.met', 't1Met.metGECDown')]
            group.variations.append(Variation('gec', replacements = (replUp, replDown)))

        # Specific systematic variations
        config.findGroup('halo').variations.append(Variation('haloNorm', reweight = 0.79))
        # config.findGroup('halo').variations.append(Variation('haloShape', region = ('haloUp', 'haloDown')))
        config.findGroup('hfake').variations.append(Variation('hfakeTfactor', region = ('hfakeUp', 'hfakeDown')))
        config.findGroup('efake').variations.append(Variation('egFakerate', reweight = 'egfakerate'))
        config.findGroup('wg').variations.append(Variation('wgQCDscale', reweight = 'qcdscale'))
        config.findGroup('wg').variations.append(Variation('wgEWK', reweight = 'ewk'))
        config.findGroup('zg').variations.append(Variation('zgQCDscale', reweight = 'qcdscale'))
        config.findGroup('zg').variations.append(Variation('zgEWK', reweight = 'ewk'))

    elif confName == 'dimu':
        mass = 'TMath::Sqrt(2. * muons.pt[0] * muons.pt[1] * (TMath::CosH(muons.eta[0] - muons.eta[1]) - TMath::Cos(muons.phi[0] - muons.phi[1])))'
        dR2_00 = 'TMath::Power(photons.eta[0] - muons.eta[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi[0]), 2.)'
        dR2_01 = 'TMath::Power(photons.eta[0] - muons.eta[1], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi[1]), 2.)'

        config = PlotConfig('dimu', ['smu-d3', 'smu-d4'])
        config.baseline = mass + ' > 50. && photons.pt[0] > 140. && t1Met.met > 100.' # met is the recoil (Operator LeptonRecoil)
        config.fullSelection = ''
        config.bkgGroups = [
            GroupSpec('tt', 't#bar{t}#gamma', samples = ['ttg'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('zg', 'Z#rightarrowll+#gamma', samples = ['zllg-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [10. * x for x in range(16)] + [160. + 40. * x for x in range(3)], unit = 'GeV', overflow = True),
            VariableDef('recoil', 'Recoil', 't1Met.recoil', [100. + 10. * x for x in range(6)] + [160. + 40. * x for x in range(3)], unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta[0]', (20, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi[0]', (20, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', 't1Met.photonDPhi', (20, -math.pi, math.pi)),
            VariableDef('dPhiPhoRecoil', '#Delta#phi(#gamma, U)', 'TVector2::Phi_mpi_pi(photons.phi[0] - recoilPhi)', (20, -math.pi, math.pi)),
            VariableDef('dimumass', 'M_{#mu#mu}', mass, (30, 50., 200.), unit = 'GeV'),
            VariableDef('dRPhoMu', '#DeltaR(#gamma, #mu)_{min}', 'TMath::Sqrt(TMath::Min(%s, %s))' % (dR2_00, dR2_01), (20, 0., 4.)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (10, 0., 10.))
        ]

    elif confName == 'monomu':

        dPhiPhoMet = 'TMath::Abs(TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.realPhi))'
        dPhiJetMetMin = '(jets.size == 0) * 4. + (jets.size == 1) * TMath::Abs(TVector2::Phi_mpi_pi(jets.phi[0] - t1Met.realPhi)) + MinIf$(TMath::Abs(TVector2::Phi_mpi_pi(jets.phi - t1Met.realPhi)), jets.size > 1 && Iteration$ < 4)'
        # MinIf$() somehow returns 0 when there is only one jet

        config = PlotConfig('monomu', ['smu-d3', 'smu-d4'])
        config.baseline = 'photons.pt[0] > 140. && ((t1Met.met > 100. && t1Met.photonDPhi > 2. && t1Met.minJetDPhi > 0.5) || (t1Met.realMet > 100. && ' + dPhiPhoMet + ' > 2. && ' + dPhiJetMetMin + ' > 0.5))' # met is the recoil
        config.fullSelection = ''
        config.bkgGroups = [
            GroupSpec('tt', 't#bar{t}#gamma', samples = ['ttg'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('zg', 'Z#rightarrowll+#gamma', samples = ['zllg-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.realMet', [10. * x for x in range(16)] + [160. + 40. * x for x in range(3)], unit = 'GeV', overflow = True),
            VariableDef('recoil', 'Recoil', 't1Met.met', [10. * x for x in range(16)] + [160. + 40. * x for x in range(3)], unit = 'GeV', overflow = True),
            VariableDef('mt', 'M_{T}', 'TMath::Sqrt(2. * t1Met.realMet * muons.pt[0] * (1. - TMath::Cos(TVector2::Phi_mpi_pi(t1Met.realPhi - muons.phi[0]))))', [0. + 10. * x for x in range(16)] + [160. + 40. * x for x in range(3)], unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [60.] + [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta[0]', (20, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi[0]', (20, -math.pi, math.pi)),
            VariableDef('muEta', '#eta^{#mu}', 'muons.eta[0]', (20, -2.4, 2.4)),
            VariableDef('muIso', 'I^{#mu}_{comb.}/p_{T}', 'muons.combRelIso[0]', (20, 0., 0.4)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', dPhiPhoMet, (30, 0., math.pi)),
            VariableDef('dRPhoMu', '#DeltaR(#gamma, #mu)', 'TMath::Sqrt(TMath::Power(photons.eta[0] - muons.eta[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi[0]), 2.))', (20, 0., 4.)),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', dPhiJetMetMin, (30, 0., math.pi), cut = 'jets.size != 0'),
            VariableDef('dPhiJetRecoilMin', 'min#Delta#phi(U, j)', 'TMath::Abs(t1Met.minJetDPhi)', (30, 0., math.pi), cut = 'jets.size != 0'),
            VariableDef('njets', 'N_{jet}', 'jets.size', (10, 0., 10.))
        ]

    elif confName == 'lowmt':
        wenuNoMetCut = baselineCut + ' && photons.pt[0] < 400.'
        wenuNoPtCut = baselineCut + ' && t1Met.met > ' + str(cutMet)
        wenuCut = wenuNoMetCut + ' && t1Met.met > ' + str(cutMet)

        config = PlotConfig('lowmt', ['sph-d3', 'sph-d4'])
        config.baseline = 'photons.pt[0] > 175. && t1Met.photonDPhi < 2. && t1Met.minJetDPhi > 0.5 && ' + mtPhoMet + ' > 40. && ' + mtPhoMet + ' < 150.'
        config.fullSelection = 'photons.pt[0] < 400. && t1Met.met > 170.'
        config.bkgGroups = [
            GroupSpec('minor', 't#bar{t}, Z', samples = ['ttg', 'zg'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('gjets', '#gamma + jets', samples = ['gj-40', 'gj-100', 'gj-200', 'gj-400', 'gj-600'], color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            GroupSpec('hfake', 'Hadronic fakes', samples = [('sph-d3', 'hfakelowmt'), ('sph-d4', 'hfakelowmt')], color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = [('sph-d3', 'efakelowmt'), ('sph-d4', 'efakelowmt')], color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [100. + 10. * x for x in range(5)] + [150. + 50. * x for x in range(6)], cut = 'photons.pt[0] < 400.', unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [175. + 15. * x for x in range(20)], cut = 't1Met.met > 170.', unit = 'GeV', logy = False, ymax = 0.5),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta[0]', (20, -1.5, 1.5), applyFullSel = True),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi[0]', (20, -math.pi, math.pi), applyFullSel = True, logy = False, ymax = 20.),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)', (20, -1., 1.), applyBaseline = False, applyFullSel = True, cut = 'photons.pt[0] > 175. && t1Met.photonDPhi < 2. && t1Met.minJetDPhi > 0.5', logy = False, ymax = 20.),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (11, 40., 150.), applyFullSel = True, unit = 'GeV', logy = False, ymax = 0.6),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi), applyFullSel = True, logy = False, ymax = 20.),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.), applyFullSel = True),
            VariableDef('jetPt', 'p_{T}^{j1}', 'jets.pt[0]', (30, 30., 800.), cut = 'jets.size != 0', applyFullSel = True, unit = 'GeV'),
            VariableDef('r9', 'R_{9}', 'photons.r9', (50, 0.5, 1.), applyFullSel = True),
            VariableDef('s4', 's4', 'photons.s4', (50, 0.5, 1.), applyFullSel = True),
        ]

    elif confName == 'phistack':
        config = PlotConfig('monoph', ['sph-d3', 'sph-d4'])
        config.baseline = 'photons.pt[0] > 175. && t1Met.photonDPhi > 2. && t1Met.minJetDPhi > 0.5'
        config.fullSelection = 't1Met.met > 170.'
        config.signalPoints = [
            GroupSpec('add-5-2', 'ADD n=5 M_{D}=2TeV', color = 41), # 0.07069/pb
            GroupSpec('dmv-1000-150', 'DM V M_{med}=1TeV M_{DM}=150GeV', color = 46), # 0.01437/pb
            GroupSpec('dma-500-1', 'DM A M_{med}=500GeV M_{DM}=1GeV', color = 30) # 0.07827/pb 
        ]
        config.bkgGroups = [
            GroupSpec('minor', 'minor SM', samples = ['ttg', 'zllg-130', 'wlnu-100','wlnu-200', 'wlnu-400', 'wlnu-600'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('gjets', '#gamma + jets', samples = ['gj-40', 'gj-100', 'gj-200', 'gj-400', 'gj-600'], color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
#            GroupSpec('halo', 'Beam halo', samples = ['sph-d3', 'sph-d4'], region = 'halo', color = ROOT.TColor.GetColor(0xff, 0x99, 0x33)),
            GroupSpec('hfake', 'Hadronic fakes', samples = ['sph-d3', 'sph-d4'], region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = ['sph-d3', 'sph-d4'], region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('phoPhiHighMet', '#phi^{#gamma}', 'photons.phi[0]', (20, -math.pi, math.pi), logy = False, applyFullSel = True, blind = (-math.pi, math.pi), ymax = 8.)
        ]

    elif confName == 'nosel':
        metCut = ''
        
        config = PlotConfig('monoph', ['sph-d3', 'sph-d4'])
        config.baseline = ''
        config.fullSelection = metCut

        config.sigGroups = [
            GroupSpec('add', 'ADD', samples = ['add-*']),
            GroupSpec('dmv', 'DM V', samples = ['dmv-*']),
            GroupSpec('dma', 'DM A', samples = ['dma-*']),
            GroupSpec('dmvfs', 'DM V', samples = ['dmvfs-*']),
            GroupSpec('dmafs', 'DM A', samples = ['dmafs-*'])
        ]
        config.signalPoints = [
            SampleSpec('add-5-2', 'ADD n=5 M_{D}=2TeV', group = config.findGroup('add'), color = 41), # 0.07069/pb
            SampleSpec('dmv-1000-150', 'DM V M_{med}=1TeV M_{DM}=150GeV', group = config.findGroup('dmv'), color = 46), # 0.01437/pb
            SampleSpec('dma-500-1', 'DM A M_{med}=500GeV M_{DM}=1GeV', group = config.findGroup('dma'), color = 30) # 0.07827/pb 
        ]

        config.bkgGroups = [
            # GroupSpec('minor', 'minor SM', samples = ['ttg', 'zllg-130', 'wlnu-100','wlnu-200', 'wlnu-400', 'wlnu-600'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            # GroupSpec('gjets', '#gamma + jets', samples = ['gj-40', 'gj-100', 'gj-200', 'gj-400', 'gj-600'], color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            # GroupSpec('halo', 'Beam halo', samples = ['sph-d3', 'sph-d4'], region = 'halo', color = ROOT.TColor.GetColor(0xff, 0x99, 0x33)),
            # GroupSpec('hfake', 'Hadronic fakes', samples = ['sph-d3', 'sph-d4'], region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            # GroupSpec('efake', 'Electron fakes', samples = ['sph-d3', 'sph-d4'], region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            # GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            # GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('metWide', 'E_{T}^{miss}', 't1Met.met', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('metHigh', 'E_{T}^{miss}', 't1Met.met', [170., 230., 290., 350., 410., 500., 600., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (22, 200., 1300.), unit = 'GeV', overflow = True, blind = (600., 2000.)),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta[0]', (20, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi[0]', (20, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', "t1Met.photonDPhi", (30, 0., math.pi), cut = 't1Met.met > 40.'),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt > 30.'),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.)),
            VariableDef('phoPtOverMet', 'E_{T}^{#gamma}/E_{T}^{miss}', 'photons.pt[0] / t1Met.met', (20, 0., 4.)),
            VariableDef('phoPtOverJetPt', 'E_{T}^{#gamma}/p_{T}^{jet}', 'photons.pt[0] / jets.pt[0]', (20, 0., 10.)),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.)),
            VariableDef('sieie', '#sigma_{i#eta i#eta}', 'photons.sieie[0]', (30, 0.005, 0.020)),
            VariableDef('r9', 'r9', 'photons.r9[0]', (50, 0.5, 1.)),
            VariableDef('s4', 's4', 'photons.s4[0]', (50, 0.5, 1.), logy = False),
            VariableDef('etaWidth', 'etaWidth', 'photons.etaWidth[0]', (30, 0.005, .020)),
            VariableDef('phiWidth', 'phiWidth', 'photons.phiWidth[0]', (18, 0., 0.05)),
            VariableDef('timeSpan', 'timeSpan', 'photons.timeSpan[0]', (20, -20., 20.)),
        ]

        for variable in list(config.variables): # need to clone the list first!
            if variable.name not in ['met', 'metWide', 'metHigh']:
                config.variables.append(variable.clone(variable.name + 'HighMet', applyFullSel = True))
                config.variables.remove(variable)

        config.getVariable('phoPtHighMet').binning = [175., 190., 250., 400., 700., 1000.]

        config.sensitiveVars = ['met', 'metWide', 'metHigh', 'phoPtHighMet', 'mtPhoMet', 'mtPhoMetHighMet']
        
        config.treeMaker = 'MonophotonTreeMaker'

        # Standard MC systematic variations
        for group in config.bkgGroups + config.sigGroups:
            if group.name == 'efake' or group.name == 'hfake' or group.name == 'halo':
                continue

            group.variations.append(Variation('lumi', reweight = 0.027))

            group.variations.append(Variation('totalSF', reweight = 0.06))

            # group.variations.append(Variation('photonSF', reweight = 'photonSF'))

            # group.variations.append(Variation('worstIsoSF', reweight = 0.05))

            # group.variations.append(Variation('leptonvetoSF', reweight = 0.02))

            group.variations.append(Variation('pdf', reweight = 'pdf'))
            
            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECUp'), ('t1Met.met', 't1Met.metCorrUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECDown'), ('t1Met.met', 't1Met.metCorrDown')]
            group.variations.append(Variation('jec', replacements = (replUp, replDown)))

            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECUp'), ('photons.pt', 'photons.ptVarUp'), ('t1Met.met', 't1Met.metGECUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECDown'), ('photons.pt', 'photons.ptVarDown'), ('t1Met.met', 't1Met.metGECDown')]
            group.variations.append(Variation('gec', replacements = (replUp, replDown)))

        """
        # Specific systematic variations
        config.findGroup('halo').variations.append(Variation('haloNorm', reweight = 0.79))
        # config.findGroup('halo').variations.append(Variation('haloShape', region = ('haloUp', 'haloDown')))
        config.findGroup('hfake').variations.append(Variation('hfakeTfactor', region = ('hfakeUp', 'hfakeDown')))
        config.findGroup('efake').variations.append(Variation('egFakerate', reweight = 'egfakerate'))
        config.findGroup('wg').variations.append(Variation('wgQCDscale', reweight = 'qcdscale'))
        config.findGroup('wg').variations.append(Variation('wgEWK', reweight = 'ewk'))
        config.findGroup('zg').variations.append(Variation('zgQCDscale', reweight = 'qcdscale'))
        config.findGroup('zg').variations.append(Variation('zgEWK', reweight = 'ewk'))
        """
    
    else:
        print 'Unknown configuration', confName
        return

    return config

