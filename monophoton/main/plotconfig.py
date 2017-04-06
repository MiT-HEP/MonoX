import sys
import os
import math

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

import config as globalConf
from main.plotutil import *

argv = list(sys.argv)
sys.argv = []
import ROOT
black = ROOT.kBlack # need to load something from ROOT to actually import
sys.argv = argv

photonDataICHEP = ['sph-16b-m', 'sph-16c-m', 'sph-16d-m']
photonData = ['sph-16b-m', 'sph-16c-m', 'sph-16d-m', 'sph-16e-m', 'sph-16f-m', 'sph-16g-m', 'sph-16h-m']
photonDataPrescaled = [
    ('sph-16b-m', 1),
    ('sph-16c-m', 1),
    ('sph-16d-m', 1),
#     ('sph-16e-m', 4),
#     ('sph-16f-m', 4),
#     ('sph-16g-m', 4),
#     ('sph-16h', 4)
]
muonData = ['smu-16b-m', 'smu-16c-m', 'smu-16d-m', 'smu-16e-m', 'smu-16f-m', 'smu-16g-m', 'smu-16h-m']
electronData = ['sel-16b-m', 'sel-16c-m', 'sel-16d-m', 'sel-16e-m', 'sel-16f-m', 'sel-16g-m', 'sel-16h-m']

gj = ['gj-100', 'gj-200', 'gj-400', 'gj-600']
gj04 = ['gj04-100', 'gj04-200', 'gj04-400', 'gj04-600']
wlnu = ['wlnu-100', 'wlnu-200', 'wlnu-400', 'wlnu-600', 'wlnu-800', 'wlnu-1200', 'wlnu-2500']
dy = ['dy-50-100', 'dy-50-200', 'dy-50-400', 'dy-50-600']
qcd = ['qcd-200', 'qcd-300', 'qcd-500', 'qcd-700', 'qcd-1000', 'qcd-1500', 'qcd-2000']

dPhiPhoMet = 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)'
mtPhoMet = 'TMath::Sqrt(2. * t1Met.pt * photons.scRawPt[0] * (1. - TMath::Cos(photons.phi[0] - t1Met.phi)))'
        
# combinedFitPtBinning = [175., 190., 250., 400., 700., 1000.]
# combinedFitPtBinning = [175.0, 200., 225., 250., 275., 300., 325., 350., 400., 450., 500., 600., 800., 1000.0]

combinedFitPtBinning = [175.0, 200., 250., 300., 400., 600., 1000.0]
fitTemplateExpression = '( ( (photons.scRawPt[0] - 175.) * (photons.scRawPt[0] < 1000.) + 800. * (photons.scRawPt[0] > 1000.) ) * TMath::Sign(1, TMath::Abs(TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(photons.phi_[0] + 0.005) - 1.570796)) - 1.570796) - 0.5) )'
fitTemplateBinning = [-1 * (bin - 175.) for bin in reversed(combinedFitPtBinning)] + [bin - 175. for bin in combinedFitPtBinning[1:]]

baseSel = 'photons.scRawPt[0] > 175. && t1Met.pt > 170 && t1Met.photonDPhi > 2.0 && t1Met.minJetDPhi > 0.5' #  && taus.size == 0' # && bjets.size == 0'

def getConfig(confName):

    if confName == 'monoph':
        config = PlotConfig('monoph')
        config.blind = True

        for sname, prescale in photonDataPrescaled:
            config.addObs(sname, prescale = prescale)

        spikeSource = ROOT.TFile.Open(globalConf.histDir + '/spikes.root')
        spikePt = spikeSource.Get('uncleanedPt')
        spikeTemplate = spikeSource.Get('fitTemplate')

        spikeDir = ROOT.gROOT.mkdir('spike')
        spikePt.SetName('phoPtHighMet')
        spikePt.SetDirectory(spikeDir)
        spikeTemplate.SetName('spikeFitTemplate')
        spikeTemplate.SetName('fitTemplate')
        spikeTemplate.SetDirectory(spikeDir)

        spikeSource.Close()

        config.baseline = baseSel
        config.fullSelection = ''
        config.sigGroups = [
            GroupSpec('dmv', 'DM V', samples = ['dmv-500-1', 'dmv-1000-1', 'dmv-2000-1']),
            GroupSpec('dma', 'DM A', samples = ['dma-500-1', 'dmv-1000-1', 'dmv-2000-1']),
            GroupSpec('dph', 'Dark Photon', samples = ['dph-125', 'dph-1000']),
#            GroupSpec('dmewk', 'DM EWK', samples = ['dmewk-*']),
            GroupSpec('dmvlo', 'DM V', samples = ['dmvlo-500-1', 'dmvlo-1000-1', 'dmvlo-2000-1']),
            GroupSpec('dmalo', 'DM A', samples = ['dmalo-1000-1', 'dmvlo-2000-1'])
        ]            
        config.signalPoints = [
            # SampleSpec('dmv-500-1', 'DMV500', group = config.findGroup('dmv'), color = 46), 
            SampleSpec('dmv-1000-1', 'DMV1000', group = config.findGroup('dmv'), color = 30), 
            # SampleSpec('dmv-2000-1', 'DMV2000', group = config.findGroup('dmv'), color = 50),
            # SampleSpec('dmvlo-1000-1', 'DMV1000', group = config.findGroup('dmvlo'), color = 30), 
            # SampleSpec('dma-1000-1', 'DMA1000', group = config.findGroup('dma'), color = 31), 
            # SampleSpec('dmalo-1000-1', 'DMA1000', group = config.findGroup('dmalo'), color = 31), 
            SampleSpec('dph-125', 'DPH125', group = config.findGroup('dph'), color = 77),
            SampleSpec('dph-1000', 'DPH1000', group = config.findGroup('dph'), color = 98), 
        ]
        config.bkgGroups = [
            GroupSpec('minor', 'Minor SM', samples = ['ttg', 'tg', 'zllg-130', 'gg-40', 'gg-80'] + wlnu, color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('gjets', '#gamma + jets', samples = gj04, color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            GroupSpec('vvg', 'VV#gamma', samples = ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            GroupSpec('spike', 'Spikes', samples = [], color = ROOT.TColor.GetColor(0xbb, 0x66, 0xff), norm = 30.5 * 12.9 / 36.4, templateDir = spikeDir), # norm set here
            GroupSpec('halo', 'Beam halo', samples = photonData, region = 'haloMETLoose', color = ROOT.TColor.GetColor(0xff, 0x99, 0x33), norm = 15.), # norm set here
            GroupSpec('hfake', 'Hadronic fakes', samples = photonDataICHEP, region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = photonDataICHEP, region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130-o'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            # GroupSpec('wgnlo', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130-o'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            # GroupSpec('zgnlo', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('fitTemplate', 'E_{T}^{#gamma}', fitTemplateExpression, fitTemplateBinning, unit = 'GeV', applyFullSel = True, overflow = False),
            VariableDef('met', 'E_{T}^{miss}', 't1Met.pt', [170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),            
            VariableDef('metWide', 'E_{T}^{miss}', 't1Met.pt', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.photonDPhi > 2. && t1Met.minJetDPhi > 0.5', overflow = True),
            VariableDef('metHigh', 'E_{T}^{miss}', 't1Met.pt', combinedFitPtBinning, unit = 'GeV', overflow = True),
            VariableDef('metScan', 'E_{T}^{miss}', 't1Met.pt', [175. + 25. * x for x in range(14)], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (22, 200., 1300.), unit = 'GeV', overflow = True), # blind = (600., 2000.)),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoPtHighMet', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', combinedFitPtBinning, unit = 'GeV', overflow = True, applyFullSel = True),
            VariableDef('phoPtScan', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175.] + [200. + 10. * x for x in range(40)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (20, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (20, -math.pi, math.pi)),
            VariableDef('nphotons', 'N_{#gamma}', 'photons.size', (4, 0., 4.)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', "t1Met.photonDPhi", (30, 0., math.pi), applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.minJetDPhi > 0.5', overflow = True),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt_ > 30.'),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi), applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170 && t1Met.photonDPhi > 2.', overflow = True),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.), ymax = 5.e+3),
            VariableDef('njetsHighPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (10, 0., 10.), cut = 'jets.pt_ > 100.'),
            VariableDef('jetPt', 'p_{T}^{jet}', 'jets.pt_', (20, 30., 530.) , unit = 'GeV', cut = 'jets.pt_ > 30', overflow = True),
            VariableDef('jetPtCorrection',  '#Delta p_{T}^{jet} (raw, corrected)', 'jets.pt_ - jets.ptRaw', (11, -10., 100.), unit = 'GeV', cut = 'jets.pt_ > 30'),
            VariableDef('phoPtOverMet', 'E_{T}^{#gamma}/E_{T}^{miss}', 'photons.scRawPt[0] / t1Met.pt', (30, 0., 3.)),
            VariableDef('phoPtOverJetPt', 'E_{T}^{#gamma}/p_{T}^{jet}', 'photons.scRawPt[0] / jets.pt_[0]', (20, 0., 10.)),
            VariableDef('metSignif', 'E_{T}^{miss} Significance', 't1Met.pt / TMath::Sqrt(t1Met.sumEt)', (15, 0., 30.)),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.)),
            VariableDef('sieie', '#sigma_{i#eta i#eta}', 'photons.sieie[0]', (40, 0., 0.020)),
            VariableDef('sipip', '#sigma_{i#phi i#phi}', 'photons.sipip[0]', (40, 0., 0.020)),
            VariableDef('r9', 'r9', 'photons.r9[0]', (25, 0.7, 1.2)),
            VariableDef('e2e9', 'E2/E9', '(photons.emax[0] + photons.e2nd[0]) / photons.e33[0]', (25, 0.7, 1.2)),
            VariableDef('eStripe9', 'E_{Strip}/E9', 'photons.e15[0] / photons.e33[0]', (40, 0.4, 1.4)),
            VariableDef('etaWidth', 'etaWidth', 'photons.etaWidth[0]', (30, 0.005, .020)),
            VariableDef('phiWidth', 'phiWidth', 'photons.phiWidth[0]', (18, 0., 0.05)),
            VariableDef('time', 'time', 'photons.time[0]', (20, -5., 5.), unit = 'ns'),
            VariableDef('timeSpan', 'timeSpan', 'photons.timeSpan[0]', (20, -20., 20.), unit = 'ns')
        ]

        """
        for variable in list(config.variables): # need to clone the list first!
            if variable.name not in ['met', 'metWide', 'metHigh', 'metScan']:
                config.variables.append(variable.clone(variable.name + 'HighMet', applyFullSel = True))
                config.variables.remove(variable)
        """

        config.sensitiveVars = [v.name for v in config.variables]
        
        config.treeMaker = 'MonophotonTreeMaker'

        # Standard MC systematic variations
        for group in config.bkgGroups + config.sigGroups:
            if group.name in ['efake', 'hfake', 'halo', 'spike']:
                continue

            group.variations.append(Variation('lumi', reweight = 0.027))

            group.variations.append(Variation('photonSF', reweight = 'photonSF'))
            group.variations.append(Variation('customIDSF', reweight = 0.055))
            group.variations.append(Variation('leptonVetoSF', reweight = 0.02))

            if group.name in ['vvg']:
                continue
            
            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECUp'), ('t1Met.pt', 't1Met.ptCorrUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECDown'), ('t1Met.pt', 't1Met.ptCorrDown')]
            group.variations.append(Variation('jec', replacements = (replUp, replDown)))

            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECUp'), ('photons.scRawPt', 'photons.ptVarUp'), ('t1Met.pt', 't1Met.ptGECUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECDown'), ('photons.scRawPt', 'photons.ptVarDown'), ('t1Met.pt', 't1Met.ptGECDown')]
            group.variations.append(Variation('gec', replacements = (replUp, replDown)))

        for gname in ['zg', 'wg']:
            group = config.findGroup(gname)
            group.variations.append(Variation('vgPDF', reweight = 'pdf'))
            # group.variations.append(Variation('vgQCDscale', reweight = 'qcdscale')) # temporary off until figure out how to apply

        # Specific systematic variations
        config.findGroup('spike').variations.append(Variation('spikeNorm', reweight = 1.0))
        config.findGroup('halo').variations.append(Variation('haloShape', region = ('haloMIPLoose', 'haloLoose'))) 
        config.findGroup('halo').variations.append(Variation('haloNorm', reweight = 1.0))
        config.findGroup('hfake').variations.append(Variation('hfakeTfactor', region = ('hfakeTight', 'hfakeLoose')))
        config.findGroup('hfake').variations.append(Variation('purity', reweight = 'purity'))
        config.findGroup('efake').variations.append(Variation('egfakerate', reweight = 'egfakerate'))
        config.findGroup('wg').variations.append(Variation('EWK', reweight = 'ewk'))
        config.findGroup('zg').variations.append(Variation('EWK', reweight = 'ewk'))
        config.findGroup('minor').variations.append(Variation('minorQCDscale', reweight = 0.033))


    elif confName == 'dimu':
        mass = 'TMath::Sqrt(2. * muons.pt_[0] * muons.pt_[1] * (TMath::CosH(muons.eta_[0] - muons.eta_[1]) - TMath::Cos(muons.phi_[0] - muons.phi_[1])))'
        dR2_00 = 'TMath::Power(photons.eta_[0] - muons.eta_[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi_[0]), 2.)'
        dR2_01 = 'TMath::Power(photons.eta_[0] - muons.eta_[1], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi_[1]), 2.)'
        ### need to add formulas for z pt, eta, and phi

        config = PlotConfig('dimu', photonData)
        config.baseline = baseSel.replace('minJetDPhi', 'realMinJetDPhi') + ' && dimu.oppSign && dimu.mass[0] > 60. && dimu.mass[0] < 120.'  # met is the recoil (Operator LeptonRecoil)
        config.fullSelection = ''
        config.bkgGroups = [
            GroupSpec('vvg', 'VV#gamma', samples = ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            GroupSpec('hfake', 'Hadronic fakes', samples = photonData, region = 'dimuHfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('top', 't#bar{t}#gamma', samples = ['ttg'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('zg', 'Z#rightarrowll+#gamma', samples = ['zllg-130-o'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            # GroupSpec('zgnlo', 'Z#rightarrowll+#gamma', samples = ['zllg-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('fitTemplate', 'E_{T}^{#gamma}', fitTemplateExpression, fitTemplateBinning, unit = 'GeV', overflow = False),
            VariableDef('met', 'E_{T}^{miss}', 't1Met.realMet', [10. * x for x in range(6)] + [60. + 20. * x for x in range(4)], unit = 'GeV', overflow = True),
            VariableDef('recoil', 'Recoil', 't1Met.pt', combinedFitPtBinning, unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (10, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', 't1Met.realPhotonDPhi', (10, 0., math.pi)),
            VariableDef('dPhiPhoRecoil', '#Delta#phi(#gamma, U)', 't1Met.photonDPhi', (10, 0., math.pi), applyBaseline = False, cut = mass + ' > 60. && ' + mass + ' < 120. && photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.realMinJetDPhi > 0.5'),
            VariableDef('dRPhoMu', '#DeltaR(#gamma, #mu)_{min}', 'TMath::Sqrt(TMath::Min(%s, %s))' % (dR2_00, dR2_01), (10, 0., 4.)),
            VariableDef('dimumass', 'M_{#mu#mu}', 'dimu.mass[0]', (12, 60., 120.), unit = 'GeV', overflow = True),
            VariableDef('zPt', 'p_{T}^{Z}', 'dimu.pt[0]', combinedFitPtBinning, unit = 'GeV'),
            VariableDef('zEta', '#eta_{Z}', 'dimu.eta[0]', (10, -5., 5.)),
            VariableDef('zPhi', '#phi_{Z}', 'dimu.phi[0]', (10, -math.pi, math.pi)),
            VariableDef('mu0Pt', 'p_{T}^{leading #mu}', 'muons.pt_[0]', [100., 125., 150., 175., 200., 250., 300., 400., 500.], unit = 'GeV', overflow = True),
            VariableDef('mu0Eta', '#eta_{leading #mu}', 'muons.eta_[0]', (10, -2.5, 2.5)),
            VariableDef('mu0Phi', '#phi_{leading #mu}', 'muons.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('mu1Pt', 'p_{T}^{trailing #mu}', 'muons.pt_[1]', [0. + 10 * x for x in range(5)] + [50., 75., 100., 150., 200.], unit = 'GeV', overflow = True),
            VariableDef('mu1Eta', '#eta_{trailing #mu}', 'muons.eta_[1]', (10, -2.5, 2.5)),
            VariableDef('mu1Phi', '#phi_{trailing #mu}', 'muons.phi_[1]', (10, -math.pi, math.pi)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.)),
            VariableDef('jetPt', 'p_{T}^{j}', 'jets.pt_[0]', [0., 50., 100.]  + [200. + 200. * x for x in range(5)], unit = 'GeV', overflow = True),
            VariableDef('jetEta', '#eta_{j}', 'jets.eta_[0]', (10, -5., 5.)),
            VariableDef('jetPhi', '#phi_{j}', 'jets.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.realMinJetDPhi', (10, 0., math.pi), applyBaseline = False, cut = mass + ' > 60. && ' + mass + ' < 120. && photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.photonDPhi > 2. && jets.size != 0'),
            VariableDef('dPhiJetRecoilMin', 'min#Delta#phi(U, j)', 'TMath::Abs(t1Met.minJetDPhi)', (10, 0., math.pi), cut = 'jets.size != 0'),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.)),
            # VariableDef('partonID', 'PGD ID', 'TMath::Abs(photons.matchedGen[0])', (31, 0., 31.), overflow = True)
        ]

        config.variables.append(config.getVariable('phoPt').clone('phoPtHighMet'))
        config.getVariable('phoPtHighMet').binning = combinedFitPtBinning

        # Standard MC systematic variations
        for group in config.bkgGroups:
            if group.name == 'hfake':
                continue

            group.variations.append(Variation('lumi', reweight = 0.027))

            group.variations.append(Variation('photonSF', reweight = 'photonSF'))
            group.variations.append(Variation('customIDSF', reweight = 0.055))
            # group.variations.append(Variation('muonSF', reweight = 'MuonSF')) # only statistical from current estimates
            group.variations.append(Variation('muonSF', reweight = 0.02)) # apply flat for now

            if group.name in ['vvg']:
                continue;

            replUp = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiJECUp'), ('t1Met.realMet', 't1Met.ptCorrUp')]
            replDown = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiJECDown'), ('t1Met.realMet', 't1Met.ptCorrDown')]
            group.variations.append(Variation('jec', replacements = (replUp, replDown)))

            replUp = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiGECUp'), ('photons.scRawPt', 'photons.ptVarUp'), ('t1Met.pt', 't1Met.ptGECUp')]
            replDown = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiGECDown'), ('photons.scRawPt', 'photons.ptVarDown'), ('t1Met.pt', 't1Met.ptGECDown')]
            group.variations.append(Variation('gec', replacements = (replUp, replDown)))

        for gname in ['zg']:
            group = config.findGroup(gname)
            group.variations.append(Variation('vgPDF', reweight = 'pdf'))
            # group.variations.append(Variation('vgQCDscale', reweight = 'qcdscale'))

        config.findGroup('zg').variations.append(Variation('EWK', reweight = 'ewk'))
        config.findGroup('hfake').variations.append(Variation('purity', reweight = 'purity'))
        config.findGroup('top').variations.append(Variation('topQCDscale', reweight = 0.033))


    elif confName == 'diel':
        mass = 'TMath::Sqrt(2. * electrons.pt_[0] * electrons.pt_[1] * (TMath::CosH(electrons.eta_[0] - electrons.eta_[1]) - TMath::Cos(electrons.phi_[0] - electrons.phi_[1])))'
        dR2_00 = 'TMath::Power(photons.eta_[0] - electrons.eta_[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - electrons.phi_[0]), 2.)'
        dR2_01 = 'TMath::Power(photons.eta_[0] - electrons.eta_[1], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - electrons.phi_[1]), 2.)'

        config = PlotConfig('diel', photonData)
        config.baseline = baseSel.replace('minJetDPhi', 'realMinJetDPhi') + ' && diel.oppSign && diel.mass[0] > 60. && diel.mass[0] < 120.' # met is the recoil (Operator LeptonRecoil)
        config.fullSelection = ''
        config.bkgGroups = [
            GroupSpec('vvg', 'VV#gamma', samples = ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            GroupSpec('hfake', 'Hadronic fakes', samples = photonData, region = 'dielHfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('top', 't#bar{t}#gamma', samples = ['ttg'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('zg', 'Z#rightarrowll+#gamma', samples = ['zllg-130-o'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            # GroupSpec('zgnlo', 'Z#rightarrowll+#gamma', samples = ['zllg-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
            ]
        config.variables = [
            VariableDef('fitTemplate', 'E_{T}^{#gamma}', fitTemplateExpression, fitTemplateBinning, unit = 'GeV', overflow = False),
            VariableDef('met', 'E_{T}^{miss}', 't1Met.realMet', [10. * x for x in range(6)] + [60. + 20. * x for x in range(4)], unit = 'GeV', overflow = True),
            VariableDef('recoil', 'Recoil', 't1Met.pt', combinedFitPtBinning, unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (10, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', 't1Met.realPhotonDPhi', (10, 0., math.pi)),
            VariableDef('dPhiPhoRecoil', '#Delta#phi(#gamma, U)', 't1Met.photonDPhi', (10, 0., math.pi), applyBaseline = False, cut = mass + ' > 60. && ' + mass + ' < 120. && photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.realMinJetDPhi > 0.5'),
            VariableDef('dRPhoEl', '#DeltaR(#gamma, e)_{min}', 'TMath::Sqrt(TMath::Min(%s, %s))' % (dR2_00, dR2_01), (10, 0., 4.)),
            VariableDef('dielmass', 'M_{ee}', 'diel.mass[0]', (12, 60., 120.), unit = 'GeV', overflow = True),
            VariableDef('zPt', 'p_{T}^{Z}', 'diel.pt[0]', combinedFitPtBinning, unit = 'GeV'),
            VariableDef('zEta', '#eta_{Z}', 'diel.eta[0]', (10, -5., 5.)),
            VariableDef('zPhi', '#phi_{Z}', 'diel.phi[0]', (10, -math.pi, math.pi)),
            VariableDef('el0Pt', 'p_{T}^{leading e}', 'electrons.pt_[0]', [100., 125., 150., 175., 200., 250., 300., 400., 500.], unit = 'GeV', overflow = True),
            VariableDef('el0Eta', '#eta_{leading e}', 'electrons.eta_[0]', (10, -2.5, 2.5)),
            VariableDef('el0Phi', '#phi_{leading e}', 'electrons.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('el1Pt', 'p_{T}^{trailing e}', 'electrons.pt_[1]', [0. + 10 * x for x in range(5)] + [50., 75., 100., 150., 200.], unit = 'GeV', overflow = True),
            VariableDef('el1Eta', '#eta_{trailing e}', 'electrons.eta_[1]', (10, -2.5, 2.5)),
            VariableDef('el1Phi', '#phi_{trailing e}', 'electrons.phi_[1]', (10, -math.pi, math.pi)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.)),
            VariableDef('jetPt', 'p_{T}^{j}', 'jets.pt_[0]', [0., 50., 100.]  + [200. + 200. * x for x in range(5)], unit = 'GeV', overflow = True),
            VariableDef('jetEta', '#eta_{j}', 'jets.eta_[0]', (10, -5., 5.)),
            VariableDef('jetPhi', '#phi_{j}', 'jets.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.realMinJetDPhi', (10, 0., math.pi), applyBaseline = False, cut = mass + ' > 60. && ' + mass + ' < 120. && photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.photonDPhi > 2. && jets.size != 0'),
            VariableDef('dPhiJetRecoilMin', 'min#Delta#phi(U, j)', 'TMath::Abs(t1Met.minJetDPhi)', (10, 0., math.pi), cut = 'jets.size != 0'),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.)),
            # VariableDef('partonID', 'PGD ID', 'TMath::Abs(photons.matchedGen[0])', (31, 0., 31.), overflow = True)
            ]

        config.variables.append(config.getVariable('phoPt').clone('phoPtHighMet'))
        config.getVariable('phoPtHighMet').binning = combinedFitPtBinning

        # Standard MC systematic variations
        for group in config.bkgGroups:
            if group.name == 'hfake':
                continue

            group.variations.append(Variation('lumi', reweight = 0.027))

            group.variations.append(Variation('photonSF', reweight = 'photonSF'))
            group.variations.append(Variation('customIDSF', reweight = 0.055))
            # group.variations.append(Variation('electronSF', reweight = 'ElectronSF')) # only statistical from current estimates
            group.variations.append(Variation('electronSF', reweight = 0.04)) # apply flat for now

            if group.name in ['vvg']:
                continue;

            replUp = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiJECUp'), ('t1Met.realMet', 't1Met.ptCorrUp')]
            replDown = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiJECDown'), ('t1Met.realMet', 't1Met.ptCorrDown')]
            group.variations.append(Variation('jec', replacements = (replUp, replDown)))

            replUp = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiGECUp'), ('photons.scRawPt', 'photons.ptVarUp'), ('t1Met.pt', 't1Met.ptGECUp')]
            replDown = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiGECDown'), ('photons.scRawPt', 'photons.ptVarDown'), ('t1Met.pt', 't1Met.ptGECDown')]
            group.variations.append(Variation('gec', replacements = (replUp, replDown)))
       
        for gname in ['zg']:
            group = config.findGroup(gname)
            group.variations.append(Variation('vgPDF', reweight = 'pdf'))
            # group.variations.append(Variation('vgQCDscale', reweight = 'qcdscale'))

        config.findGroup('zg').variations.append(Variation('EWK', reweight = 'ewk'))
        config.findGroup('top').variations.append(Variation('topQCDscale', reweight = 0.033))
        config.findGroup('hfake').variations.append(Variation('purity', reweight = 'purity'))


    elif confName == 'monomu':

        dPhiPhoMet = 'TMath::Abs(TVector2::Phi_mpi_pi(photons.phi_[0] - t1Met.realPhi))'
        dPhiJetMetMin = '((jets.size == 0) * 4. + (jets.size == 1) * TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[0] - t1Met.realPhi)) + MinIf$(TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.realPhi)), jets.size > 1 && Iteration$ < 4))'
        dRPhoParton  = 'TMath::Sqrt(TMath::Power(photons.eta_[0] - promptFinalStates.eta_, 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi_[0] - promptFinalStates.phi_), 2.))'
        # MinIf$() somehow returns 0 when there is only one jet
        mt = 'TMath::Sqrt(2. * t1Met.realMet * muons.pt_[0] * (1. - TMath::Cos(TVector2::Phi_mpi_pi(t1Met.realPhi - muons.phi_[0]))))'

        config = PlotConfig('monomu', photonData)
        config.baseline = baseSel.replace('minJetDPhi', 'realMinJetDPhi') + ' && ' + mt + ' < 160.' # met is the recoil, mt cut to synch with monoel region

        config.fullSelection = ''
        config.bkgGroups = [
            GroupSpec('vvg', 'VV#gamma', samples = ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            GroupSpec('gg', '#gamma#gamma', samples = ['gg-40', 'gg-80'], color = ROOT.TColor.GetColor(0xbb, 0x66, 0xff)),
            GroupSpec('hfake', 'Hadronic fakes', samples = photonData, region = 'monomuHfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('zg', 'Z#rightarrowll+#gamma', samples = ['zllg-130-o'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            GroupSpec('top', 't#bar{t}#gamma/t#gamma', samples = ['ttg', 'tg'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130-o'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            # GroupSpec('wglo', 'W#rightarrowl#nu+#gamma', samples = ['wglo-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            # GroupSpec('wgnlo', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff))
        ]
        config.variables = [
            VariableDef('fitTemplate', 'E_{T}^{#gamma}', fitTemplateExpression, fitTemplateBinning, unit = 'GeV', overflow = False),
            VariableDef('met', 'E_{T}^{miss}', 't1Met.realMet', [50. * x for x in range(6)] + [300., 400., 500.], unit = 'GeV', overflow = True),
            VariableDef('recoil', 'Recoil', 't1Met.pt', combinedFitPtBinning, unit = 'GeV', overflow = True),
            VariableDef('mt', 'M_{T}', mt, [0. + 20. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('mtNMinusOne', 'M_{T}', mt, [0. + 20. * x for x in range(9)] + [200., 300., 400., 500.], unit = 'GeV', overflow = True, applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.photonDPhi > 2. && t1Met.realMinJetDPhi > 0.5'),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [60.] + [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (10, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', 't1Met.realPhotonDPhi', (10, 0., math.pi)),
            VariableDef('dPhiPhoRecoil', '#Delta#phi(#gamma, U)', 't1Met.photonDPhi', (10, 0., math.pi), applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.realMinJetDPhi > 0.5 && ' + mt + ' < 160.'),
            VariableDef('dRPhoMu', '#DeltaR(#gamma, #mu)', 'TMath::Sqrt(TMath::Power(photons.eta_[0] - muons.eta_[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi_[0] - muons.phi_[0]), 2.))', (10, 0., 4.)),
            VariableDef('muPt', 'p_{T}^{#mu}', 'muons.pt_[0]', [0., 50., 100., 150., 200., 250., 300., 400., 500.], unit = 'GeV', overflow = True),
            VariableDef('muEta', '#eta_{#mu}', 'muons.eta_[0]', (10, -2.5, 2.5)),
            VariableDef('muPhi', '#phi_{#mu}', 'muons.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiMuMet', '#Delta#phi(#mu, E_{T}^{miss})', 'TMath::Abs(TVector2::Phi_mpi_pi(muons.phi_[0] - t1Met.realPhi))', (10, 0., math.pi)),
            VariableDef('muIso', 'I^{#mu}_{comb.}/p_{T}', 'muons.combRelIso[0]', (20, 0., 0.4)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.)),
            VariableDef('jetPt', 'p_{T}^{leading j}', 'jets.pt_[0]', [0., 50., 100.]  + [200. + 200. * x for x in range(5)], unit = 'GeV', overflow = True),
            VariableDef('jetEta', '#eta_{leading j}', 'jets.eta_[0]', (10, -5., 5.)),
            VariableDef('jetPhi', '#phi_{leading j}', 'jets.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.realMinJetDPhi', (10, 0., math.pi), applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.photonDPhi > 2. && ' + mt + ' < 160. && jets.size != 0'),
            VariableDef('dPhiJetRecoilMin', 'min#Delta#phi(U, j)', 'TMath::Abs(t1Met.minJetDPhi)', (10, 0., math.pi), cut = 'jets.size != 0'),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.)),
            # VariableDef('partonID', 'PGD ID', 'TMath::Abs(photons.matchedGen[0])', (31, 0., 31.), overflow = True)
        ]

        config.variables.append(config.getVariable('phoPt').clone('phoPtHighMet'))
        config.getVariable('phoPtHighMet').binning = combinedFitPtBinning

        # Standard MC systematic variations
        for group in config.bkgGroups:
            if group.name == 'hfake':
                continue

            group.variations.append(Variation('lumi', reweight = 0.027))
            
            group.variations.append(Variation('photonSF', reweight = 'photonSF'))
            group.variations.append(Variation('customIDSF', reweight = 0.055))
            # group.variations.append(Variation('muonSF', reweight = 'MuonSF')) # only statistical from current estimates
            group.variations.append(Variation('muonSF', reweight = 0.01)) # apply flat for now

            if group.name in ['vvg']:
                continue;

            replUp = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiJECUp'), ('t1Met.realMet', 't1Met.ptCorrUp')]
            replDown = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiJECDown'), ('t1Met.realMet', 't1Met.ptCorrDown')]
            group.variations.append(Variation('jec', replacements = (replUp, replDown)))

            replUp = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiGECUp'), ('photons.scRawPt', 'photons.ptVarUp'), ('t1Met.pt', 't1Met.ptGECUp')]
            replDown = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiGECDown'), ('photons.scRawPt', 'photons.ptVarDown'), ('t1Met.pt', 't1Met.ptGECDown')]
            group.variations.append(Variation('gec', replacements = (replUp, replDown)))

        for gname in ['zg', 'wg']:
            group = config.findGroup(gname)
            group.variations.append(Variation('vgPDF', reweight = 'pdf'))
            # group.variations.append(Variation('vgQCDscale', reweight = 'qcdscale'))

        config.findGroup('zg').variations.append(Variation('EWK', reweight = 'ewk'))
        config.findGroup('wg').variations.append(Variation('EWK', reweight = 'ewk'))
        config.findGroup('top').variations.append(Variation('topQCDscale', reweight = 0.033))
        config.findGroup('hfake').variations.append(Variation('purity', reweight = 'purity'))


    elif confName == 'monoel':

        dPhiPhoMet = 'TMath::Abs(TVector2::Phi_mpi_pi(photons.phi_[0] - t1Met.realPhi))'
        dPhiJetMetMin = '(jets.size == 0) * 4. + (jets.size == 1) * TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[0] - t1Met.realPhi)) + MinIf$(TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.realPhi)), jets.size > 1 && Iteration$ < 4)'
        dRPhoParton  = 'TMath::Sqrt(TMath::Power(photons.eta_[0] - promptFinalStates.eta_, 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi_[0] - promptFinalStates.phi_), 2.))'
        # MinIf$() somehow returns 0 when there is only one jet
        mt = 'TMath::Sqrt(2. * t1Met.realMet * electrons.pt_[0] * (1. - TMath::Cos(TVector2::Phi_mpi_pi(t1Met.realPhi - electrons.phi_[0]))))'

        config = PlotConfig('monoel', photonData)
        config.baseline = baseSel.replace('minJetDPhi', 'realMinJetDPhi') + ' && ' + mt + ' < 160. && t1Met.realMet > 50.' # met is the recoil, real MET cut to reject QCD, mt cut to reject QCD

        config.fullSelection = ''
        config.bkgGroups = [
            GroupSpec('vvg', 'VV#gamma', samples = ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            GroupSpec('gg', '#gamma#gamma', samples = ['gg-40', 'gg-80'], color = ROOT.TColor.GetColor(0xbb, 0x66, 0xff)),
            GroupSpec('hfake', 'Hadronic fakes', samples = photonData, region = 'monoelHfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('zg', 'Z#rightarrowll+#gamma', samples = ['zllg-130-o'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            GroupSpec('top', 't#bar{t}#gamma/t#gamma', samples = ['ttg', 'tg'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130-o'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            # GroupSpec('wglo', 'W#rightarrowl#nu+#gamma', samples = ['wglo-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            # GroupSpec('wgnlo', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff))
        ]
        config.variables = [
            VariableDef('fitTemplate', 'E_{T}^{#gamma}', fitTemplateExpression, fitTemplateBinning, unit = 'GeV', overflow = False),
            VariableDef('met', 'E_{T}^{miss}', 't1Met.realMet', [0., 10., 20., 30., 40.] + [50. + 50. * x for x in range(5)] + [300., 400., 500.], unit = 'GeV', overflow = True, applyBaseline = False, cut ='photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.photonDPhi > 2. && t1Met.realMinJetDPhi > 0.5  && ' + mt + ' < 160.'),
            VariableDef('recoil', 'Recoil', 't1Met.pt', combinedFitPtBinning, unit = 'GeV', overflow = True),
            VariableDef('mt', 'M_{T}', mt, [0. + 20. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('mtNMinusOne', 'M_{T}', mt, [0. + 20. * x for x in range(9)] + [200., 300., 400., 500.], unit = 'GeV', overflow = True, applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.photonDPhi > 2 && t1Met.realMinJetDPhi > 0.5 && t1Met.realMet > 50.'),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [60.] + [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (10, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', 't1Met.realPhotonDPhi', (10, 0., math.pi)),
            VariableDef('dPhiPhoRecoil', '#Delta#phi(#gamma, U)', 't1Met.photonDPhi', (10, 0., math.pi), applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170  && t1Met.realMinJetDPhi > 0.5 && t1Met.realMet > 50. && ' + mt + ' < 160.'),
            VariableDef('dRPhoEl', '#DeltaR(#gamma, e)', 'TMath::Sqrt(TMath::Power(photons.eta_[0] - electrons.eta_[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi_[0] - electrons.phi_[0]), 2.))', (10, 0., 4.)),
            VariableDef('elPt', 'p_{T}^{e}', 'electrons.pt_[0]', [0., 50., 100., 150., 200., 250., 300., 400., 500.], unit = 'GeV', overflow = True),
            VariableDef('elEta', '#eta_{e}', 'electrons.eta_[0]', (10, -2.5, 2.5)),
            VariableDef('elPhi', '#phi_{e}', 'electrons.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiElMet', '#Delta#phi(e, E_{T}^{miss})', 'TMath::Abs(TVector2::Phi_mpi_pi(electrons.phi_[0] - t1Met.realPhi))', (10, 0., math.pi)),
            VariableDef('elIso', 'I^{e}_{comb.}/p_{T}', 'electrons.combRelIso[0]', (20, 0., 0.4)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.)),
            VariableDef('jetPt', 'p_{T}^{leading j}', 'jets.pt_[0]', [0., 50., 100.]  + [200. + 200. * x for x in range(5)], unit = 'GeV', overflow = True),
            VariableDef('jetEta', '#eta_{leading j}', 'jets.eta_[0]', (10, -5., 5.)),
            VariableDef('jetPhi', '#phi_{leading j}', 'jets.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.realMinJetDPhi', (10, 0., math.pi), applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.photonDPhi > 2. && t1Met.realMet > 50. && ' + mt + ' < 160. && jets.size != 0'),
            VariableDef('dPhiJetRecoilMin', 'min#Delta#phi(U, j)', 'TMath::Abs(t1Met.minJetDPhi)', (10, 0., math.pi), cut = 'jets.size != 0'),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.)),
            # VariableDef('partonID', 'PGD ID', 'TMath::Abs(photons.matchedGen[0])', (31, 0., 31.), overflow = True)
        ]

        config.variables.append(config.getVariable('phoPt').clone('phoPtHighMet'))
        config.getVariable('phoPtHighMet').binning = combinedFitPtBinning

        # Standard MC systematic variations
        for group in config.bkgGroups:
            if group.name == 'hfake':
                continue

            group.variations.append(Variation('lumi', reweight = 0.027))
            
            group.variations.append(Variation('photonSF', reweight = 'photonSF'))
            group.variations.append(Variation('customIDSF', reweight = 0.055))
            # group.variations.append(Variation('electronSF', reweight = 'ElectronSF')) # only statistical from current estimates
            group.variations.append(Variation('electronSF', reweight = 0.02)) # apply flat for now

            if group.name in ['vvg']:
                continue;

            replUp = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiJECUp'), ('t1Met.realMet', 't1Met.ptCorrUp')]
            replDown = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiJECDown'), ('t1Met.realMet', 't1Met.ptCorrDown')]
            group.variations.append(Variation('jec', replacements = (replUp, replDown)))

            replUp = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiGECUp'), ('photons.scRawPt', 'photons.ptVarUp'), ('t1Met.pt', 't1Met.ptGECUp')]
            replDown = [('t1Met.realMinJetDPhi', 't1Met.realMinJetDPhiGECDown'), ('photons.scRawPt', 'photons.ptVarDown'), ('t1Met.pt', 't1Met.ptGECDown')]
            group.variations.append(Variation('gec', replacements = (replUp, replDown)))

        for gname in ['zg', 'wg']:
            group = config.findGroup(gname)
            group.variations.append(Variation('vgPDF', reweight = 'pdf'))
            # group.variations.append(Variation('vgQCDscale', reweight = 'qcdscale'))

        config.findGroup('zg').variations.append(Variation('EWK', reweight = 'ewk'))
        config.findGroup('wg').variations.append(Variation('EWK', reweight = 'ewk'))
        config.findGroup('top').variations.append(Variation('topQCDscale', reweight = 0.033))
        config.findGroup('hfake').variations.append(Variation('purity', reweight = 'purity'))
        
    
    elif confName == 'lowdphi':
        config = PlotConfig('monoph', photonData)
        config.baseline = 'photons.scRawPt[0] > 175. && t1Met.minJetDPhi < 0.5 && t1Met.photonDPhi > 2. && t1Met.pt > 100.'
        config.fullSelection = 't1Met.pt > 170.'
        config.bkgGroups = [
#            GroupSpec('minor', 'minor SM', samples = ['ttg', 'tg', 'zllg-130', 'wlnu', 'gg-80'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('minor', 'minor SM', samples = ['ttg', 'tg', 'zllg-130', 'gg-80'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('vvg', 'VV#gamma', samples = ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            GroupSpec('halo', 'Beam halo', samples = photonData, region = 'halo', color = ROOT.TColor.GetColor(0xff, 0x99, 0x33)),
            GroupSpec('efake', 'Electron fakes', samples = photonData, region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            GroupSpec('hfake', 'Hadronic fakes', samples = photonData, region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('gjets', '#gamma + jets', samples = gj, color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.pt', [170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('metWide', 'E_{T}^{miss}', 't1Met.pt', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (22, 200., 1300.), unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt_ > 30.'),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi), overflow = True),
            VariableDef('njets', 'N_{jet}', 'jets.size', (10, 0., 10.)),
            VariableDef('njetsHightPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (10, 0., 10.), cut = 'jets.pt_ > 100.'),
            VariableDef('metSignif', 'E_{T}^{miss} Significance', 't1Met.pt / TMath::Sqrt(t1Met.sumEt)', (15, 0., 30.)),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
        ]

        for variable in list(config.variables):
            if variable.name not in ['met', 'metWide']:
                config.variables.append(variable.clone(variable.name + 'HighMet', applyFullSel = True))
#                config.variables.remove(variable)

        config.getVariable('phoPtHighMet').binning = combinedFitPtBinning

    elif confName == 'gjets':
        config = PlotConfig('monoph', photonData)
        config.baseline = 'photons.scRawPt[0] > 175. && (t1Met.minJetDPhi < 0.5 || t1Met.photonDPhi < 0.5) && t1Met.pt > 100. && TMath::Abs(TVector2::Phi_mpi_pi(photons.phi_[0] - jets.phi_[0])) > 3. && jets.size == 1 && jets.pt_[0] > 100.'
        config.fullSelection = 'photons.scRawPt[0] > 350.'
        config.bkgGroups = [
#            GroupSpec('minor', 'minor SM', samples = ['ttg', 'tg', 'zllg-130', 'wlnu', 'gg-80'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('minor', 'minor SM', samples = ['ttg', 'tg', 'zllg-130', 'gg-80'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            # GroupSpec('vvg', 'VV#gamma', samples = ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            # GroupSpec('halo', 'Beam halo', samples = photonData, region = 'halo', color = ROOT.TColor.GetColor(0xff, 0x99, 0x33)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('hfake', 'Hadronic fakes', samples = photonData, region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = photonData, region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('gjets', '#gamma + jets', samples = gj04, color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc), scale = 1.5)
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.pt', combinedFitPtBinning, unit = 'GeV', overflow = True),
            VariableDef('metWide', 'E_{T}^{miss}', 't1Met.pt', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('metDPhiWeighted', 'E_{T}^{miss}', '(t1Met.pt) * TMath::Sign(1, (t1Met.photonDPhi - 1.570796))', list(reversed([-200. - 50. * x for x in range(9)])) + list(reversed([-120 - 20. * x for x in range(4)])) +[ -100., 0.] +  [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (22, 200., 1300.), unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt_ > 30.'),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi), overflow = True),
            VariableDef('njets', 'N_{jet}', 'jets.size', (10, 0., 10.)),
            VariableDef('njetsHightPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (10, 0., 10.), cut = 'jets.pt_ > 100.'),
            VariableDef('metSignif', 'E_{T}^{miss} Significance', 't1Met.pt / TMath::Sqrt(t1Met.sumEt)', (15, 0., 30.)),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
        ]

        for variable in list(config.variables):
            """
            if variable.name not in ['met', 'metWide', 'metDPhiWeighted']:
                config.variables.append(variable.clone(variable.name + 'HighMet', applyFullSel = True))
#                config.variables.remove(variable)
            """
            if variable.name not in ['phoPt']:
                config.variables.append(variable.clone(variable.name + 'HighPhoPt', applyFullSel = True))
#                config.variables.remove(variable)

            # config.getVariable('phoPtHighMet').binning = combinedFitPtBinning
            # config.getVariable('phoPtHighMet').binning = combinedFitPtBinning


    elif confName == 'lowmt':
        config = PlotConfig('monoph', photonData)
        config.baseline = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.photonDPhi < 2. && t1Met.minJetDPhi > 0.5'
        config.fullSelection = ''
        config.bkgGroups = [
            GroupSpec('minor', 't#bar{t}, Z, #gamma#gamma', samples = ['ttg', 'zllg-130', 'gg-80'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('qcd', 'QCD', samples = qcd, color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            GroupSpec('multiboson', 'multiboson', samples = ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            GroupSpec('gjets', '#gamma + jets', samples = gj, color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            GroupSpec('hfake', 'Hadronic fakes', samples = photonData, region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = photonData, region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.pt', [100. + 10. * x for x in range(5)] + [150. + 50. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('metLowSx', 'E_{T}^{miss}', 't1Met.pt', [100. + 10. * x for x in range(5)] + [150. + 50. * x for x in range(6)], cut = 'photons.e4[0] / photons.emax[0] > 0.5', unit = 'GeV', overflow = True),
            VariableDef('metHighSx', 'E_{T}^{miss}', 't1Met.pt', [100. + 10. * x for x in range(5)] + [150. + 50. * x for x in range(6)], cut = 'photons.e4[0] / photons.emax[0] < 0.5', unit = 'GeV', overflow = True),
            VariableDef('sumEt', '#SigmaE_{T}', 't1Met.sumEt', [1000. + 50. * x for x in range(40)], unit = 'GeV', overflow = True),
            VariableDef('sumEtHighSx', '#SigmaE_{T}', 't1Met.sumEt', [1000. + 50. * x for x in range(40)], cut = 'photons.e4[0] / photons.emax[0] < 0.5', unit = 'GeV', overflow = True),
            VariableDef('significance', 'E_{T}^{miss} / #SigmaE_{T}', 't1Met.pt / TMath::Sqrt(t1Met.sumEt)', (20, 0., 20.), unit = '#sqrt{GeV}', overflow = True),
            VariableDef('significanceHighSx', 'E_{T}^{miss} / #SigmaE_{T}', 't1Met.pt / TMath::Sqrt(t1Met.sumEt)', (20, 0., 20.), cut = 'photons.e4[0] / photons.emax[0] < 0.5', unit = '#sqrt{GeV}', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175. + 15. * x for x in range(20)], unit = 'GeV', logy = False),
            VariableDef('phoPtLowSx', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175. + 15. * x for x in range(20)], cut = 'photons.e4[0] / photons.emax[0] > 0.5', unit = 'GeV', logy = False),
            VariableDef('phoPtHighSx', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175. + 30. * x for x in range(25)], cut = 'photons.e4[0] / photons.emax[0] < 0.5', unit = 'GeV', overflow = True),
            VariableDef('phoPtHighMet', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175. + 15. * x for x in range(20)], cut = 't1Met.pt > 170.', unit = 'GeV', logy = False),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (20, -1.5, 1.5), applyFullSel = True),
            VariableDef('phoEtaLowSx', '#eta^{#gamma}', 'photons.eta_[0]', (20, -1.5, 1.5), cut = 'photons.e4[0] / photons.emax[0] > 0.5', applyFullSel = True),
            VariableDef('phoEta2Jets', '#eta^{#gamma}', 'photons.eta_[0]', (20, -1.5, 1.5), cut = 'jets.size == 2', applyFullSel = True),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (20, -math.pi, math.pi), applyFullSel = True, logy = False),
#            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', 'TVector2::Phi_mpi_pi(photons.phi_[0] - t1Met.phi)', (20, -math.pi, math.pi), cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.minJetDPhi > 0.5', applyBaseline = False, logy = False),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', 'TVector2::Phi_mpi_pi(photons.phi_[0] - t1Met.phi)', (20, -math.pi, math.pi), logy = False),
            VariableDef('dPhiPhoMetHighSx', '#Delta#phi(#gamma, E_{T}^{miss})', 'TVector2::Phi_mpi_pi(photons.phi_[0] - t1Met.phi)', (20, -math.pi, math.pi), cut = 'photons.e4[0] / photons.emax[0] < 0.5', logy = False),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt_ > 30.'),
            VariableDef('dPhiJet1Met', '#Delta#phi(E_{T}^{miss}, j1)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[0] - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt_[0] > 30.'),
            VariableDef('dPhiJet2Met', '#Delta#phi(E_{T}^{miss}, j2)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[1] - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt_[1] > 30.'),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi), overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', 'photons.mt[0]', (30, 0., 300.), applyFullSel = True, unit = 'GeV', logy = False),
            VariableDef('mtPhoMetHighSx', 'M_{T#gamma}', 'photons.mt[0]', (30, 0., 300.), cut = 'photons.e4[0] / photons.emax[0] < 0.5', applyFullSel = True, unit = 'GeV'),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi_', (20, -math.pi, math.pi), applyFullSel = True, logy = False),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.), applyFullSel = True),
            VariableDef('jetPt', 'p_{T}^{j1}', 'jets.pt_[0]', (30, 30., 800.), cut = 'jets.size != 0', applyFullSel = True, unit = 'GeV'),
            VariableDef('jetPtHighSx', 'p_{T}^{j1}', 'jets.pt_[0]', (30, 30., 1600.), cut = 'jets.size != 0 && photons.e4[0] / photons.emax[0] < 0.5', overflow = True, unit = 'GeV'),
            VariableDef('jetPtLowSx', 'p_{T}^{j1}', 'jets.pt_[0]', (30, 30., 1600.), cut = 'jets.size != 0 && photons.e4[0] / photons.emax[0] > 0.5', overflow = True, unit = 'GeV'),
            VariableDef('jetEta', '#eta^{j1}', 'jets.eta_[0]', (30, -5., 5.), cut = 'jets.size != 0', applyFullSel = True),
            VariableDef('jet2Pt', 'p_{T}^{j2}', 'jets.pt_[1]', (30, 30., 800.), cut = 'jets.size > 1', applyFullSel = True, unit = 'GeV'),
            VariableDef('jet2Eta', '#eta^{j2}', 'jets.eta_[1]', (30, -5., 5.), cut = 'jets.size > 1', applyFullSel = True),
            VariableDef('r9', 'R_{9}', 'photons.r9', (50, 0.5, 1.), applyFullSel = True),
            VariableDef('r9HighSx', 'R_{9}', 'photons.r9', (50, 0.5, 1.), cut = 'photons.e4[0] / photons.emax[0] < 0.5', applyFullSel = True),
            VariableDef('swissCross', '1-S4/S1', '1. - photons.e4[0] / photons.emax[0]', (50, 0., 1.)),
            VariableDef('sipip', '#sigma_{i#phii#phi}', 'photons.sipip[0]', (50, 0., 0.02)),
            VariableDef('sipipLowSx', '#sigma_{i#phii#phi}', 'photons.sipip[0]', (50, 0., 0.02), cut = 'photons.e4[0] / photons.emax[0] > 0.5')
        ]


    elif confName == 'zmmJets':
        config = PlotConfig('zmmJets', muonData)
        config.baseline = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi_[0])) > 3. && TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi)) < 0.5 && z.mass > 81. && z.mass < 101. && z.oppSign == 1 && jets.size == 1 && jets.pt_[0] > 100. && t1Met.pt > 50. && t1Met.minJetDPhi > 0.5'
        config.fullSelection = ''
        config.bkgGroups = [
            GroupSpec('wjets', 'W+jets', samples = ['wlnu-100', 'wlnu-200', 'wlnu-400', 'wlnu-800', 'wlnu-1200', 'wlnu-2500'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            GroupSpec('diboson', 'Diboson', samples =  ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)), 
            GroupSpec('tt', 'Top', samples = ['tt'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('zjets', 'Z+jets', samples = ['dy-50'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)) # ['dy-50-100', 'dy-50-200', 'dy-50-400', 'dy-50-600', 'dy-50-800', 'dy-50-1200', 'dy-50-2500']
            ]
        config.variables = [ 
            VariableDef('met', 'E_{T}^{miss}', 't1Met.pt', [25 * x for x in range(2, 4)] + [100 + 50 * x for x in range(0, 8)], unit = 'GeV', overflow = True),
            VariableDef('dPhi', '#Delta#phi(Z, jet)', 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi_))', (15, 0., math.pi), applyBaseline = False, cut = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi)) < 0.5 && z.mass > 81. && z.mass < 101. && z.oppSign == 1 && jets.size == 1 && jets.pt[0] > 100. && t1Met.pt > 50. && t1Met.minJetDPhi > 0.5'),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, jet)', 'TMath::Abs(TVector2::Phi_mpi_pi(t1Met.phi - jets.phi_))', (15, 0., math.pi), applyBaseline = False, cut = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi)) < 0.5 && z.mass > 81. && z.mass < 101. && z.oppSign == 1 && jets.size == 1 && jets.pt_[0] > 100. && t1Met.pt > 50. && t1Met.minJetDPhi > 0.5'),
            VariableDef('dPhiZMet', '#Delta#phi(Z, E_{T}^{miss})', 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi))', (15, 0., math.pi), applyBaseline = False, cut = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi_[0])) > 3. && z.mass > 81. && z.mass < 101. && z.oppSign == 1 && jets.size == 1 && jets.pt_[0] > 100. && t1Met.pt > 50. && t1Met.minJetDPhi > 0.5'),
            VariableDef('jetPt', 'p_{T}^{j}', 'jets.pt_[0]', (20, 0., 1000.), unit = 'GeV'),
            VariableDef('jetEta', '#eta_{j}', 'jets.eta_[0]', (10, -5., 5.)),
            VariableDef('jetPhi', '#phi_{j}', 'jets.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('tagPt', 'p_{T}^{tag}', 'tag.pt_[0]', (20, 0., 200.), unit = 'GeV'),
            VariableDef('tagEta', '#eta_{tag}', 'tag.eta_[0]', (10, -2.5, 2.5)),
            VariableDef('tagPhi', '#phi_{tag}', 'tag.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('probePt', 'p_{T}^{probe}', 'probe.pt_[0]', (10, 0., 100.), unit = 'GeV'),
            VariableDef('probeEta', '#eta_{probe}', 'probe.eta_[0]', (10, -2.5, 2.5)),
            VariableDef('probePhi', '#phi_{probe}', 'probe.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('metPhi', '#phi_{E_{T}^{miss}}', 't1Met.phi', (10, -math.pi, math.pi)),
            VariableDef('zPt', 'p_{T}^{Z}', 'z.pt[0]', (20, 0., 1000.), unit = 'GeV'),
            VariableDef('zEta', '#eta_{Z}', 'z.eta[0]', (10, -5., 5.)),
            VariableDef('zPhi', '#phi_{Z}', 'z.phi[0]', (10, -math.pi, math.pi)),
            VariableDef('zMass', 'm_{Z}', 'z.mass[0]', (10, 81., 101.), unit = 'GeV')
            ]


    elif confName == 'zeeJets':
        config = PlotConfig('zeeJets', electronData)
        config.baseline = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi_[0])) > 3. && TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi)) < 0.5 && z.mass > 81. && z.mass < 101. && z.oppSign == 1 && jets.size == 1 && jets.pt_[0] > 100. && t1Met.pt > 50. && t1Met.minJetDPhi > 0.5'
        config.fullSelection = ''
        config.bkgGroups = [
            GroupSpec('wjets', 'W+jets', samples = ['wlnu-100', 'wlnu-200', 'wlnu-400', 'wlnu-800', 'wlnu-1200', 'wlnu-2500'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            GroupSpec('diboson', 'Diboson', samples =  ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)), 
            GroupSpec('tt', 'Top', samples = ['tt'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('zjets', 'Z+jets', samples = ['dy-50'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)) # ['dy-50-100', 'dy-50-200', 'dy-50-400', 'dy-50-600', 'dy-50-800', 'dy-50-1200', 'dy-50-2500']
            ]
        config.variables = [ 
            VariableDef('met', 'E_{T}^{miss}', 't1Met.pt', [25 * x for x in range(2, 4)] + [100 + 50 * x for x in range(0, 8)], unit = 'GeV', overflow = True),
            VariableDef('dPhi', '#Delta#phi(Z, jet)', 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi_))', (15, 0., math.pi), applyBaseline = False, cut = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi)) < 0.5 && z.mass > 81. && z.mass < 101. && z.oppSign == 1 && jets.size == 1 && jets.pt_[0] > 100. && t1Met.pt > 50. && t1Met.minJetDPhi > 0.5'),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, jet)', 'TMath::Abs(TVector2::Phi_mpi_pi(t1Met.phi - jets.phi_))', (15, 0., math.pi), applyBaseline = False, cut = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi)) < 0.5 && z.mass > 81. && z.mass < 101. && z.oppSign == 1 && jets.size == 1 && jets.pt_[0] > 100. && t1Met.pt > 50. && t1Met.minJetDPhi > 0.5'),
            VariableDef('dPhiZMet', '#Delta#phi(Z, E_{T}^{miss})', 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi))', (15, 0., math.pi), applyBaseline = False, cut = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi_[0])) > 3. && z.mass > 81. && z.mass < 101. && z.oppSign == 1 && jets.size == 1 && jets.pt_[0] > 100. && t1Met.pt > 50. && t1Met.minJetDPhi > 0.5'),
            VariableDef('jetPt', 'p_{T}^{j}', 'jets.pt_[0]', (20, 0., 1000.), unit = 'GeV'),
            VariableDef('jetEta', '#eta_{j}', 'jets.eta_[0]', (10, -5., 5.)),
            VariableDef('jetPhi', '#phi_{j}', 'jets.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('tagPt', 'p_{T}^{tag}', 'tag.pt_[0]', (20, 0., 200.), unit = 'GeV'),
            VariableDef('tagEta', '#eta_{tag}', 'tag.eta_[0]', (10, -2.5, 2.5)),
            VariableDef('tagPhi', '#phi_{tag}', 'tag.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('probePt', 'p_{T}^{probe}', 'probe.pt_[0]', (10, 0., 100.), unit = 'GeV'),
            VariableDef('probeEta', '#eta_{probe}', 'probe.eta_[0]', (10, -2.5, 2.5)),
            VariableDef('probePhi', '#phi_{probe}', 'probe.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('metPhi', '#phi_{E_{T}^{miss}}', 't1Met.phi', (10, -math.pi, math.pi)),
            VariableDef('zPt', 'p_{T}^{Z}', 'z.pt[0]', (20, 0., 1000.), unit = 'GeV'),
            VariableDef('zEta', '#eta_{Z}', 'z.eta[0]', (10, -5., 5.)),
            VariableDef('zPhi', '#phi_{Z}', 'z.phi[0]', (10, -math.pi, math.pi)),
            VariableDef('zMass', 'm_{Z}', 'z.mass[0]', (10, 81., 101.), unit = 'GeV')
            ]


    elif confName == 'phistack':
        config = PlotConfig('monoph', photonData)
        config.baseline = 'photons.scRawPt[0] > 175. && t1Met.photonDPhi > 2. && t1Met.minJetDPhi > 0.5'
        config.fullSelection = 't1Met.pt > 170.'
        config.signalPoints = [
            GroupSpec('add-5-2', 'ADD n=5 M_{D}=2TeV', color = 41), # 0.07069/pb
            GroupSpec('dmv-1000-150', 'DM V M_{med}=1TeV M_{DM}=150GeV', color = 46), # 0.01437/pb
            GroupSpec('dma-500-1', 'DM A M_{med}=500GeV M_{DM}=1GeV', color = 30) # 0.07827/pb 
        ]
        config.bkgGroups = [
            GroupSpec('minor', 'minor SM', samples = ['ttg', 'tg', 'zllg-130', 'wlnu', 'gg-80'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('vvg', 'VV#gamma', samples = ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            GroupSpec('gjets', '#gamma + jets', samples = gj, color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            # GroupSpec('halo', 'Beam halo', samples = photonData, region = 'halo', color = ROOT.TColor.GetColor(0xff, 0x99, 0x33)),
            GroupSpec('hfake', 'Hadronic fakes', samples = photonData, region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = photonData, region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('phoPhiHighMet', '#phi^{#gamma}', 'photons.phi_[0]', (20, -math.pi, math.pi), logy = False, applyFullSel = True, blind = (-math.pi, math.pi), ymax = 8.)
        ]

    elif confName == 'invChIsoMax':
        config = PlotConfig('monoph', photonDataICHEP)
        config.baseline = 'photons.scRawPt[0] > 175. && photons.chIsoMax > 0.441 && t1Met.minJetDPhi > 0.5 && t1Met.photonDPhi > 2. && t1Met.pt > 170.'
        config.fullSelection = 't1Met.pt > 170.'
        config.bkgGroups = [
            GroupSpec('minor', 'Minor SM', samples = ['ttg', 'tg', 'zllg-130'] + wlnu + ['gg-80'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('gjets', '#gamma + jets', samples = gj, color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            GroupSpec('vvg', 'VV#gamma', samples = ['ww', 'wz', 'zz'], color = ROOT.TColor.GetColor(0xff, 0x44, 0x99)),
            # GroupSpec('spike', 'Spikes', samples = [], color = ROOT.TColor.GetColor(0xbb, 0x66, 0xff), norm = 30.5 * 12.9 / 36.4, templateDir = spikeDir), # norm set here
            # GroupSpec('halo', 'Beam halo', samples = photonData, region = 'halo', color = ROOT.TColor.GetColor(0xff, 0x99, 0x33), norm = 15.), # norm set here
            GroupSpec('hfake', 'Hadronic fakes', samples = photonDataICHEP, region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = photonDataICHEP, region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.pt', [170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (20, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (20, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', "t1Met.photonDPhi", (30, 0., math.pi), applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.minJetDPhi > 0.5', overflow = True),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt_ > 30.'),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi), applyBaseline = False, cut = 'photons.scRawPt[0] > 175. && t1Met.pt > 170 && t1Met.photonDPhi > 2.', overflow = True),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.), overflow = True),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.)),
            VariableDef('chIso', 'CH Iso', 'photons.chIsoS16[0]', (10, 0., 1.0), overflow = True),
            VariableDef('chIsoMax', 'Max CH Iso', 'photons.chIsoMax[0]', (20, 0., 10.), overflow = True),
            VariableDef('sieie', '#sigma_{i#eta i#eta}', 'photons.sieie[0]', (40, 0., 0.020)),
            VariableDef('sipip', '#sigma_{i#phi i#phi}', 'photons.sipip[0]', (40, 0., 0.020)),
            VariableDef('r9', 'r9', 'photons.r9[0]', (25, 0.7, 1.2)),
            VariableDef('swissCross', '1-S4/S1', '1. - photons.e4[0] / photons.emax[0]', (50, 0., 1.)),
            VariableDef('e2e9', 'E2/E9', '(photons.emax[0] + photons.e2nd[0]) / photons.e33[0]', (25, 0.7, 1.2))
        ]

        for variable in list(config.variables):
            if variable.name not in ['met', 'metWide']:
                config.variables.append(variable.clone(variable.name + 'HighMet', applyFullSel = True))
                config.variables.remove(variable)

        config.getVariable('phoPtHighMet').binning = combinedFitPtBinning


    elif confName == 'diph':
        config = PlotConfig('monoph', photonData)
        config.baseline = 'photons.size == 2 && photons.scRawPt[0] > 175. && photons.loose[1] && photons.scRawPt[1] > 170. && TMath::Abs(TVector2::Phi_mpi_pi(photons.phi_[0] - photons.phi_[1])) > 2. && t1Met.minJetDPhi > 0.5'
        config.fullSelection = ''
        config.bkgGroups = [
            GroupSpec('minor', 'Minor SM', samples = ['ttg', 'tg', 'zllg-130'] + wlnu, color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('hfake', 'Hadronic fakes', samples = photonData, region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('gjets', '#gamma + jets', samples = gj04, color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            GroupSpec('efake', 'Electron fakes', samples = photonData, region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('gg', '#gamma#gamma', samples = ['gg-40', 'gg-80'], color = ROOT.TColor.GetColor(0xbb, 0x66, 0xff))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.pt', [10. * x for x in range(6)] + [60. + 20. * x for x in range(4)], unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (10, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('recoil', 'Recoil', 'photons.scRawPt[1]', combinedFitPtBinning, unit = 'GeV', overflow = True),
            VariableDef('recoilEta', '#eta^{recoil}', 'photons.eta_[1]', (10, -1.5, 1.5)),
            VariableDef('recoilPhi', '#phi^{recoil}', 'photons.phi_[1]', (10, -math.pi, math.pi)),
            VariableDef('dPhiPhoRecoil', '#Delta#phi(#gamma, U)', 'TMath::Abs(TVector2::Phi_mpi_pi(photons.phi_[0] - photons.phi_[1]))', (10, 0., math.pi), applyBaseline = False, cut = 'photons.size == 2 && photons.scRawPt[0] > 175. && photons.loose[1] && photons.scRawPt[1] > 170. && t1Met.minJetDPhi > 0.5'),
            VariableDef('sieie', '#sigma_{i#eta i#eta}', 'photons.sieie[0]', (10, 0., 0.020)),
            VariableDef('sipip', '#sigma_{i#phi i#phi}', 'photons.sipip[0]', (10, 0., 0.020)),
            VariableDef('r9', 'r9', 'photons.r9[0]', (25, 0.7, 1.2)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.)),
            VariableDef('jetPt', 'p_{T}^{leading j}', 'jets.pt_[0]', [0., 50., 100.]  + [200. + 200. * x for x in range(5)], unit = 'GeV', overflow = True),
            VariableDef('jetEta', '#eta_{leading j}', 'jets.eta_[0]', (10, -5., 5.)),
            VariableDef('jetPhi', '#phi_{leading j}', 'jets.phi_[0]', (10, -math.pi, math.pi)),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (10, 0., math.pi), applyBaseline = False, cut = 'photons.size == 2 && photons.scRawPt[0] > 175. && photons.loose[1] && photons.scRawPt[1] > 170. && TMath::Abs(TVector2::Phi_mpi_pi(photons.phi_[0] - photons.phi_[1])) > 2.', overflow = True),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
        ]

        config.variables.append(config.getVariable('phoPt').clone('phoPtHighMet'))
        config.getVariable('phoPtHighMet').binning = combinedFitPtBinning

        # Standard MC systematic variations
        for group in config.bkgGroups + config.sigGroups:
            if group.name in ['efake', 'hfake']:
                continue

            group.variations.append(Variation('lumi', reweight = 0.027))

            group.variations.append(Variation('photonSF', reweight = 'photonSF'))
            group.variations.append(Variation('customIDSF', reweight = 0.055))
            group.variations.append(Variation('leptonVetoSF', reweight = 0.02))
     
            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECUp'), ('t1Met.pt', 't1Met.ptCorrUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECDown'), ('t1Met.pt', 't1Met.ptCorrDown')]
            group.variations.append(Variation('jec', replacements = (replUp, replDown)))

            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECUp'), ('photons.scRawPt', 'photons.ptVarUp'), ('t1Met.pt', 't1Met.ptGECUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECDown'), ('photons.scRawPt', 'photons.ptVarDown'), ('t1Met.pt', 't1Met.ptGECDown')]
            group.variations.append(Variation('gec', replacements = (replUp, replDown)))

        for group in config.bkgGroups:
            if group.name in ['efake', 'hfake']:
                continue

#            group.variations.append(Variation('minorPDF', reweight = 'pdf'))
            group.variations.append(Variation('minorQCDscale', reweight = 0.033))

        # Specific systematic variations
        config.findGroup('hfake').variations.append(Variation('hfakeTfactor', region = ('hfakeTight', 'hfakeLoose')))
        config.findGroup('hfake').variations.append(Variation('purity', reweight = 'purity'))
        config.findGroup('efake').variations.append(Variation('egFakerate', reweight = 0.079))


    elif confName == 'nosel':
        metCut = ''
        
        config = PlotConfig('monoph', photonData)
        config.baseline = '1'
        config.fullSelection = '1'

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

        config.bkgGroups = []
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.pt', [170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('metWide', 'E_{T}^{miss}', 't1Met.pt', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('metHigh', 'E_{T}^{miss}', 't1Met.pt', [170., 230., 290., 350., 410., 500., 600., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (22, 200., 1300.), unit = 'GeV', overflow = True, blind = (600., 2000.)),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (20, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (20, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', "t1Met.photonDPhi", (30, 0., math.pi), cut = 't1Met.pt > 40.'),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt_ > 30.'),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.)),
            VariableDef('phoPtOverMet', 'E_{T}^{#gamma}/E_{T}^{miss}', 'photons.scRawPt[0] / t1Met.pt', (20, 0., 4.)),
            VariableDef('phoPtOverJetPt', 'E_{T}^{#gamma}/p_{T}^{jet}', 'photons.scRawPt[0] / jets.pt_[0]', (20, 0., 10.)),
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

        config.getVariable('phoPtHighMet').binning = combinedFitPtBinning
    
    else:
        print 'Unknown configuration', confName
        return

    return config

