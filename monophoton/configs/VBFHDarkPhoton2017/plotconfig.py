import os
import math

import main.plotutil as pu
import configs.common.plotconfig_2017 as common

import ROOT

config = pu.plotConfig

if pu.confName in ['vbfg', 'vbfglo']:
    config.name = pu.confName
    config.addObs(common.photonData)
    config.obs.region = 'vbfg'

    for sample in config.obs.samples:
        sample.lumi = common.vbfTriggerLumi[sample.name]

    config.baseline = 'photons.scRawPt[0] > 80.'
    config.fullSelection = 't1Met.pt > 110. && t1Met.minJetDPhi > 1. && photons.mt[0] < 300.'

    config.addSig('dph', 'Dark Photon', samples=['dphv-*'], scale=0.03)
    config.addSig('dphg', 'Dark Photon (ggH)', samples=['dph-*'], scale=0.03)

    config.addSigPoint('dphv-nlo-125', 'H_{125}(#gamma, #gamma_{D})', color=ROOT.kGreen)
    config.addSigPoint('dph-nlo-125', 'H_{125}(#gamma, #gamma_{D}) (ggH)', color=ROOT.kCyan)

    if confName == 'vbfg':
        gjsamples = ['gjn']
        gjscale = 1.
    elif confName == 'vbfglo':
        gjsamples = gj04
        gjscale = 1.3

    config.addBkg('top', 't#bar{t}#gamma/t#gamma', samples=['ttg', 'tg'], color=ROOT.TColor.GetColor(0x55, 0x44, 0xff))
    config.addBkg('gjets', '#gamma + jets', samples=gjsamples, color=ROOT.TColor.GetColor(0xff, 0xaa, 0xcc), scale=gjscale)
    config.addBkg('hfake', 'Hadronic fakes', samples=photonData, region='vbfgHfake', color=ROOT.TColor.GetColor(0xbb, 0xaa, 0xff))
    config.addBkg('zg', 'Z#rightarrow#nu#nu+#gamma', samples=['znng'], color=ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
    config.addBkg('wg', 'W#rightarrowl#nu+#gamma', samples=['wglo'], color=ROOT.TColor.GetColor(0x99, 0xee, 0xff))
    config.addBkg('efake', 'Electron fakes', samples=photonData, region='vbfgEfake', color=ROOT.TColor.GetColor(0xff, 0xee, 0x99))

    jetPtBinning = [x * 10. for x in range(20)] + [200. + x * 20. for x in range(10)] + [400. + x * 50. for x in range(9)]
    jetPtFullSelBinning = [0., 40., 80., 120., 160., 200., 240., 280., 320., 360., 400., 500., 600., 700., 800.]

    config.cut['jetAwayFromMet'] = 't1Met.minJetDPhi > 1.'
    config.cut['metGreater'] = 't1Met.pt > photons.scRawPt[0]'
    config.cut['jets30'] = 'jets.pt_ > 30.'
    config.cut['jets100'] = 'jets.pt_ > 100.'
    config.cut['met100'] = 't1Met.pt > 100.'

    # only used once - no need to alias
    ptjj = 'TMath::Sqrt('
    ptjj += 'TMath::Power(jets.pt_[pdijet.ij1[0]] * TMath::Cos(jets.phi_[pdijet.ij1[0]]) + jets.pt_[pdijet.ij2[0]] * TMath::Cos(jets.phi_[pdijet.ij2[0]]), 2.) +'
    ptjj += 'TMath::Power(jets.pt_[pdijet.ij1[0]] * TMath::Sin(jets.phi_[pdijet.ij1[0]]) + jets.pt_[pdijet.ij2[0]] * TMath::Sin(jets.phi_[pdijet.ij2[0]]), 2.)'
    ptjj += ')'

    mgg = 'TMath::Sqrt(2. * photons.pt_[0] * photons.pt_[1] * (TMath::CosH(photons.eta_[0] - photons.eta_[1]) - TMath::Cos(photons.phi_[0] - photons.phi_[1])))'

    config.addPlot('met', 'E_{T}^{miss}', 't1Met.pt', [10. * x for x in range(10)] + [100. + 20. * x for x in range(20)], unit='GeV', overflow=True, sensitive=True, blind=(100., 'inf'))
    config.addPlot('metHigh', 'E_{T}^{miss}', 't1Met.pt', [100. + 40. * x for x in range(20)], unit='GeV', overflow=True, sensitive=True)
    config.addPlot('metLargeDPhi', 'E_{T}^{miss}', 't1Met.pt', [10. * x for x in range(10)] + [100. + 20. * x for x in range(20)], unit='GeV', cutName='metAwayFromJet', overflow=True, sensitive=True, blind=(100., 'inf'))
    config.addPlot('mt', 'M_{T}^{#gamma}', 'photons.mt[0]', (50, 0., 500.), unit='GeV', overflow=True)
    config.addPlot('mtFullSel', 'M_{T}^{#gamma}', 'photons.mt[0]', [20. * x for x in range(5)] + [100 + 25. * x for x in range(9)], unit='GeV', cutName='fullSelection', sensitive=True)
    config.addPlot('mtMetGreater', 'M_{T}^{#gamma}', 'photons.mt[0]', (8, 0., 300.), unit='GeV', cutName='metGreater')
    config.addPlot('phoPt', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', (80, 0., 1000.), unit='GeV', overflow=True)
    config.addPlot('phoPtFullSel', 'E_{T}^{#gamma}', 'photons.scRawPt[0]', (20, 0., 1000.), unit='GeV', overflow=True, cutName='fullSelection', sensitive=True)
    config.addPlot('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (20, -1.5, 1.5))
    config.addPlot('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (20, -math.pi, math.pi))
    config.addPlot('nphotons', 'N_{#gamma}', 'photons.size', (4, 0., 4.))
    config.addPlot('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi))
    config.addPlot('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', "t1Met.photonDPhi", (20, 0., math.pi))
    config.addPlot('dPhiPhoMetFullSel', '#Delta#phi(#gamma, E_{T}^{miss})', "t1Met.photonDPhi", (8, 0., 3.25), cutName='fullSelection', sensitive=True)
    config.addPlot('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (13, 0., 3.25), cutName='jets30')
    config.addPlot('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (20, 0., math.pi))
    config.addPlot('dPhiJetMetMinHighMet', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (20, 0., math.pi), cutName='met100', sensitive=True, blind =(1., math.pi))
    config.addPlot('dPhiPhoJetMin', 'min#Delta#phi(#gamma, j)', 'photons.minJetDPhi[0]', (20, 0., math.pi))
    config.addPlot('njets', 'N_{jet}', 'jets.size', (6, 0., 6.))
    config.addPlot('njetsFullSel', 'N_{jet}', 'jets.size', (6, 0., 6.), cutName='fullSelection', sensitive=True)
    config.addPlot('njetsHighPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (10, 0., 10.), cutName='jets100')
    config.addPlot('jetPt', 'p_{T}^{jet}', 'jets.pt_', jetPtBinning, unit='GeV', cutName='jets30', overflow=True)
    config.addPlot('jet1Pt', 'p_{T}^{j1}', 'jets.pt_[pdijet.ij1[0]]', jetPtBinning, unit='GeV', overflow=True)
    config.addPlot('jet1PtFullSel', 'p_{T}^{j1}', 'jets.pt_[pdijet.ij1[0]]', jetPtFullSelBinning, unit='GeV', cutName='fullSelection', sensitive=True, overflow=True)
    config.addPlot('jet1Eta', '#eta^{j1}', 'jets.eta_[pdijet.ij1[0]]', (40, -5., 5.))
    config.addPlot('jet2Pt', 'p_{T}^{j2}', 'jets.pt_[pdijet.ij2[0]]', jetPtBinning, unit='GeV', overflow=True)
    config.addPlot('jet2PtFullSel', 'p_{T}^{j2}', 'jets.pt_[pdijet.ij2[0]]', jetPtFullSelBinning, unit='GeV', cutName='fullSelection', sensitive=True, overflow=True)
    config.addPlot('jet2Eta', '#eta^{j2}', 'jets.eta_[pdijet.ij2[0]]', (40, -5., 5.))
    config.addPlot('detajj', '#Delta#eta^{jj}', 'pdijet.dEtajj[0]', (40, 0., 10.))
    config.addPlot('detajjFullSel', '#Delta#eta^{jj}', 'pdijet.dEtajj[0]', (10, 0., 10.), cutName='fullSelection', sensitive=True)
    config.addPlot('dphijj', '#Delta#phi^{jj}', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[pdijet.ij1[0]] - jets.phi_[pdijet.ij2[0]]))', (40, 0., math.pi))
    config.addPlot('dphijjFullSel', '#Delta#phi^{jj}', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[pdijet.ij1[0]] - jets.phi_[pdijet.ij2[0]]))', (15, 0., math.pi), cutName='fullSelection', sensitive=True)
    config.addPlot('mjj', 'm^{jj}', 'pdijet.mjj[0]', (40, 0., 5000.), unit='GeV')
    config.addPlot('mjjFullSel', 'm^{jj}', 'pdijet.mjj[0]', (10, 0., 5000.), unit='GeV', cutName='fullSelection', sensitive=True)
    config.addPlot('ptjj', 'p_{T}^{jj}', ptjj, (40, 0., 600.), unit='GeV')
    config.addPlot('phoPtOverMet', 'E_{T}^{#gamma}/E_{T}^{miss}', 'photons.scRawPt[0] / t1Met.pt', (30, 0., 3.))
    config.addPlot('phoPtOverMetFullSel', 'E_{T}^{#gamma}/E_{T}^{miss}', 'photons.scRawPt[0] / t1Met.pt', (10, 0., 3.), cutName='fullSelection', sensitive=True)
    config.addPlot('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
    config.addPlot('sieie', '#sigma_{i#eta i#eta}', 'photons.sieie[0]', (40, 0., 0.020))
    config.addPlot('sipip', '#sigma_{i#phi i#phi}', 'photons.sipip[0]', (40, 0., 0.020))
    config.addPlot('r9', 'r9', 'photons.r9[0]', (25, 0.7, 1.2))
    config.addPlot('etaWidth', 'etaWidth', 'photons.etaWidth[0]', (30, 0.005, .020))
    config.addPlot('phiWidth', 'phiWidth', 'photons.phiWidth[0]', (18, 0., 0.05))
    config.addPlot('npartons', 'N_{q,g}', 'Sum$(TMath::Abs(partons.pdgid) < 7 || partons.pdgid == 21)', (5, 0., 5.), sensitive=True, mcOnly=True)
    config.addPlot('npartonsFullSel', 'N_{q,g}', 'Sum$(TMath::Abs(partons.pdgid) < 7 || partons.pdgid == 21)', (5, 0., 5.), cutName='fullSelection', sensitive=True, mcOnly=True)
    config.addPlot('mgg', 'm^{#gamma#gamma}', mgg, (50, 100., 200.), unit='GeV', cutName='fullSelection')

    # Standard MC systematic variations
    for group in config.bkgGroups + config.sigGroups:
        if group.name in ['efake', 'hfake']:
            continue

        group.addVariation('lumi', reweight=0.027)

        group.addVariation('triggerSF', reweight=0.005)
        group.addVariation('photonSF', reweight='photonSF')
        group.addVariation('customIDSF', reweight=0.055)
        group.addVariation('leptonVetoSF', reweight=0.02)

        replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECUp'), ('t1Met.pt', 't1Met.ptCorrUp')]
        replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECDown'), ('t1Met.pt', 't1Met.ptCorrDown')]
        group.addVariation('jec', replacements=(replUp, replDown))

        replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECUp'), ('photons.scRawPt', 'photons.ptVarUp'), ('t1Met.pt', 't1Met.ptGECUp')]
        replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECDown'), ('photons.scRawPt', 'photons.ptVarDown'), ('t1Met.pt', 't1Met.ptGECDown')]
        group.addVariation('gec', replacements=(replUp, replDown))

    for gname in ['zg', 'wg']:
        group = config.findGroup(gname)
        group.addVariation('vgPDF', reweight='pdf')
        group.addVariation('vgQCDscale', reweight='qcdscale') # temporary off until figure out how to apply
        group.addVariation('EWKoverall', reweight='ewkstraight')
        group.addVariation('EWKshape', reweight='ewktwisted')
        group.addVariation('EWKgamma', reweight='ewkgamma')

    # Specific systematic variations
    proxyDefCuts = (
        'photons.nhIso < 0.264 && photons.phIso < 2.362',
        'photons.nhIso < 10.910 && photons.phIso < 3.630'
    )
    config.findGroup('hfake').addVariation('hfakeTfactor', reweight='proxyDef', cuts=proxyDefCuts)
    config.findGroup('hfake').addVariation('purity', reweight='purity')
    config.findGroup('efake').addVariation('egfakerate', reweight='egfakerate')
    config.findGroup('gjets').addVariation('gjetsNorm', reweight=0.3 / 1.3)

elif pu.confName == 'vbfgCtrl':
    config.name = pu.confName
    config.addObs(common.photonData)
    config.obs.region = pu.confName

    for sample in config.obs.samples:
        sample.lumi = common.ph75TriggerLumi[sample.name]

    #config.addBkg('wg', 'W#gamma', samples = ['wglo'], region = 'vbfgWHadCtrl', color = ROOT.TColor.GetColor(0x99, 0xee, 0xff))
    #config.addBkg('hfake', 'QCD', samples = photonData, region = 'vbfgHfakeCtrl', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff))
    config.addBkg('gjets', '#gamma+jets', samples = ['gj04*'], color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc))

    config.addSig('gjetsUNLOPS', '#gamma+jets (UNLOPS)', samples=['gju'])
    config.addSigPoint('gju', '#gamma+jets (UNLOPS)', color=ROOT.kGreen)

    config.baseline = 'photons.scRawPt[0] > 80. && dijet.size != 0'

    config.cuts['mjj400LowMet'] = 'dijet.mjj[0] > 400. && t1Met.pt < 50.'
    config.cuts['dijetWideDEta'] = 'TMath::Abs(dijet.dEtajj) > 2.'
    config.cuts['dijetNarrowDEta'] = 'TMath::Abs(dijet.dEtajj) < 2.'
    config.cuts['lowMet'] = 't1Met.pt < 50.'
    config.cuts['lowMetLowPU'] = 't1Met.pt < 50. && vertices.size < 9.'
    config.cuts['lowMetJet1Pt80'] = 't1Met.pt < 50. && jets.pt_[dijet.ij2[0]] > 80.'
    config.cuts['lowMetJet2Pt80'] = 't1Met.pt < 50. && jets.pt_[dijet.ij1[0]] > 80.'

    config.addPlot('phoPt', 'p_{T}^{#gamma}', 'photons.scRawPt[0]', (20, 80., 280.), unit='GeV')
    config.addPlot('phoEta', '#eta^{#gamma}', 'photons.eta_[0]', (20, -1.5, 1.5))
    config.addPlot('phoPhi', '#phi^{#gamma}', 'photons.phi_[0]', (20, -math.pi, math.pi))
    config.addPlot('phoDRJet1', '#DeltaR^{#gamma,j1}', 'TMath::Sqrt(TMath::Power(photons.eta_[0] - jets.eta_[dijet.ij1[0]], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi_[0] - jets.phi_[dijet.ij1[0]]), 2.))', (20, 0., 5.))
    config.addPlot('phoDRJet2', '#DeltaR^{#gamma,j2}', 'TMath::Sqrt(TMath::Power(photons.eta_[0] - jets.eta_[dijet.ij2[0]], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi_[0] - jets.phi_[dijet.ij2[0]]), 2.))', (20, 0., 5.))
    config.addPlot('detajjAll', '#Delta#eta^{jj}', 'TMath::Abs(dijet.dEtajj[0])', (20, 0., 8.5), rmax=4.)
    config.addPlot('detajjMjj400LowMet', '#Delta#eta^{jj}', 'TMath::Abs(dijet.dEtajj[0])', (10, 0., 8.5), cutName='mjj400LowMet', rmax=4.)
    config.addPlot('dphijjAll', '#Delta#phi^{jj}', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[dijet.ij1[0]] - jets.phi_[dijet.ij2[0]]))', (20, 0., math.pi), logy=False)
    config.addPlot('mjjAll', 'm^{jj}', 'dijet.mjj[0]', (20, 0., 5000.), unit='GeV')
    config.addPlot('mjjLow', 'm^{jj}', 'dijet.mjj[0]', (20, 0., 500.), unit='GeV')
    config.addPlot('met', 'E_{T}^{miss}', 't1Met.pt', (20, 0., 200.), unit='GeV')
    config.addPlot('dphijjDEtaGt2', '#Delta#phi^{jj}', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[dijet.ij1[0]] - jets.phi_[dijet.ij2[0]]))', (20, 0., math.pi), cutName='dijetWideDEta', logy=False)
    config.addPlot('dphijjDEtaLt2', '#Delta#phi^{jj}', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[dijet.ij1[0]] - jets.phi_[dijet.ij2[0]]))', (20, 0., math.pi), cutName='dijetNarrowDEta', logy=False)
    config.addPlot('jet1Pt', 'p_{T}^{j1}', 'jets.pt_[dijet.ij1[0]]', (20, 0., 1000.), unit='GeV', overflow=True)
    config.addPlot('jet2Pt', 'p_{T}^{j2}', 'jets.pt_[dijet.ij2[0]]', (20, 0., 1000.), unit='GeV', overflow=True)
    config.addPlot('jet1PtLowMet', 'p_{T}^{j1}', 'jets.pt_[dijet.ij1[0]]', (20, 0., 1000.), unit='GeV', cutName='lowMet')
    config.addPlot('jet2PtLowMet', 'p_{T}^{j2}', 'jets.pt_[dijet.ij2[0]]', (20, 0., 1000.), unit='GeV', cutName='lowMet')
    config.addPlot('jet1PtLow', 'p_{T}^{j1}', 'jets.pt_[dijet.ij1[0]]', (20, 0., 200.), unit='GeV')
    config.addPlot('jet2PtLow', 'p_{T}^{j2}', 'jets.pt_[dijet.ij2[0]]', (20, 0., 200.), unit='GeV')
    config.addPlot('jet1PtLowAll', 'p_{T}^{j1}', 'jets.pt_[dijet.ij1[0]]', (20, 0., 200.), unit='GeV', cutName='lowMet')
    config.addPlot('jet2PtLowAll', 'p_{T}^{j2}', 'jets.pt_[dijet.ij2[0]]', (20, 0., 200.), unit='GeV', cutName='lowMet')
    config.addPlot('jet1PtLowJ280', 'p_{T}^{j1}', 'jets.pt_[dijet.ij1[0]]', (20, 0., 200.), unit='GeV', cutName='lowMetJet2Pt80')
    config.addPlot('jet2PtLowJ180', 'p_{T}^{j2}', 'jets.pt_[dijet.ij2[0]]', (20, 0., 200.), unit='GeV', cutName='lowMetJet1Pt80')
    config.addPlot('jet2PtLowLowPU', 'p_{T}^{j2}', 'jets.pt_[dijet.ij2[0]]', (20, 0., 200.), unit='GeV', cutName='lowMetLowPU')
    config.addPlot('jet2EtaJ180', '#eta^{j2}', 'jets.eta_[dijet.ij2[0]]', (20, -5., 5.), cutName='lowMetJet1Pt80')
    config.addPlot('jetDPt', 'p_{T}^{j1} - p_{T}^{j2}', 'jets.pt_[dijet.ij1[0]] - jets.pt_[dijet.ij2[0]]', (20, -100., 1000.), unit='GeV')
    config.addPlot('jet1Eta', '#eta^{j1}', 'jets.eta_[dijet.ij1[0]]', (20, -5., 5.))
    config.addPlot('jet2Eta', '#eta^{j2}', 'jets.eta_[dijet.ij2[0]]', (20, -5., 5.))
    config.addPlot('jet1Phi', '#phi^{j1}', 'jets.phi_[dijet.ij1[0]]', (20, -math.pi, math.pi), logy=False)
    config.addPlot('jet2Phi', '#phi^{j2}', 'jets.phi_[dijet.ij2[0]]', (20, -math.pi, math.pi), logy=False)
    config.addPlot('jet1PUID', 'puid(j1)', 'jets.puid[dijet.ij1[0]]', (20, 0., 1.))
    config.addPlot('jet2PUID', 'puid(j2)', 'jets.puid[dijet.ij2[0]]', (20, 0., 1.))
    config.addPlot('njets', 'N_{jet}', 'jets.size', (6, 2., 8.))
    config.addPlot('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
    config.addPlot('ht', 'H_{T}', 'Sum$(jets.pt_)', (20, 100., 2100.), unit='GeV', overflow=True)
    config.addPlot('genHt', 'H_{T}^{gen}', 'Sum$(partons.pt_ * (TMath::Abs(partons.pdgid) < 6 || partons.pdgid == 21))', (40, 40., 2040.), overflow=True, mcOnly=True)
    config.addPlot('genNjets', 'N_{jet}^{gen}', 'Sum$(genJets.pt_ > 30.)', (8, 0., 8.), mcOnly=True)
    config.addPlot('genNpartons', 'N_{parton}^{gen}', 'Sum$(TMath::Abs(partons.pdgid) < 7 || partons.pdgid == 21)', (8, 0., 8.), mcOnly=True)

    for plot in config.plots:
        plot.sensitive = True

#elif pu.confName in ['vbfe', 'vbfelo']:
#    config = PlotConfig(confName, ['sel-16*'])
#
#    config.baseline = 'electrons.pt_[0] > 40.'
#
#    config.fullSelection = ''
#
#    mt = 'TMath::Sqrt(2. * t1Met.pt * electrons.pt_[0] * (1. - TMath::Cos(TVector2::Phi_mpi_pi(t1Met.phi - electrons.phi_[0]))))'
#
#    if confName == 'vbfe':
#        main = wlnun
#        wscale = 1.
#    elif confName == 'vbfelo':
#        main = wlnu
#        wscale = 6.153 / 4.997
#
#    config.addBkg('top', 't#bar{t}/t', samples=['tt', 'sttbar', 'stt', 'stwbar', 'stw'], color=ROOT.TColor.GetColor(0x55, 0x44, 0xff))
#    config.addBkg('w', 'W#rightarrowl#nu', samples=main, color=ROOT.TColor.GetColor(0x99, 0xee, 0xff), scale=wscale)
#    config.addBkg('wewk', 'W#rightarrowl#nu (EWK)', samples=['wmlnuewk', 'wplnuewk'], color=ROOT.TColor.GetColor(0x77, 0xcc, 0xff))
#    config.addBkg('z', 'Z#rightarrowll', samples=dy, color=ROOT.TColor.GetColor(0x99, 0xff, 0xaa), scale=6025. / 4975.)
#    config.addBkg('zewk', 'Z#rightarrowll (EWK)', samples=['zewk'], color=ROOT.TColor.GetColor(0x77, 0xff, 0x99))
#
#    config.obs.region = 'vbfe'
#    for group in config.bkgGroups:
#        if not group.region:
#            group.region = 'vbfe'
#
#    config.addPlot('met', 'E_{T}^{miss}', 't1Met.pt', [10. * x for x in range(10)] + [100. + 20. * x for x in range(20)], unit='GeV', overflow=True)
#    config.addPlot('metHigh', 'E_{T}^{miss}', 't1Met.pt', [100. + 40. * x for x in range(20)], unit='GeV', overflow=True)
#    config.addPlot('mt', 'M_{T}^{e}', mt, (50, 0., 500.), unit='GeV', overflow=True)
#    config.addPlot('elPt', 'p_{T}^{e}', 'electrons.pt_[0]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('elEta', '#eta^{e}', 'electrons.eta_[0]', (20, -1.5, 1.5))
#    config.addPlot('elPhi', '#phi^{e}', 'electrons.phi_[0]', (20, -math.pi, math.pi))
#    config.addPlot('nelectrons', 'N_{e}', 'electrons.size', (4, 0., 4.))
#    config.addPlot('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi))
#    config.addPlot('dPhiElMet', '#Delta#phi(e, E_{T}^{miss})', "TMath::Abs(TVector2::Phi_mpi_pi(electrons.phi_[0] - t1Met.phi))", (20, 0., math.pi))
#    config.addPlot('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (13, 0., 3.25), cut='jets.pt_ > 30.')
#    config.addPlot('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (20, 0., math.pi))
#    config.addPlot('njets', 'N_{jet}', 'jets.size', (6, 0., 6.))
#    config.addPlot('njetsHighPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (10, 0., 10.), cut='jets.pt_ > 100.')
#    config.addPlot('jetPt', 'p_{T}^{jet}', 'jets.pt_', (40, 0., 1000.), unit='GeV', cut='jets.pt_ > 30', overflow=True)
#    config.addPlot('jet1Pt', 'p_{T}^{j1}', 'jets.pt_[0]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('jet1Eta', '#eta^{j1}', 'jets.eta_[0]', (40, -5., 5.))
#    config.addPlot('jet2Pt', 'p_{T}^{j2}', 'jets.pt_[1]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('jet2Eta', '#eta^{j2}', 'jets.eta_[1]', (40, -5., 5.))
#    config.addPlot('ht', 'H_{T}', 'Sum$(jets.pt_)', (50, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('detajj', '#Delta#eta^{jj}', 'pdijet.dEtajj[0]', (40, 0., 10.))
#    config.addPlot('dphijj', '#Delta#phi^{jj}', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[pdijet.ij1[0]] - jets.phi_[pdijet.ij2[0]]))', (40, 0., math.pi))
#    config.addPlot('mjj', 'm^{jj} (GeV)', 'pdijet.mjj[0]', (40, 0., 5000.), sensitive=True)
#    config.addPlot('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
#
#    for plot in list(config.plots):
#        if plot.name not in ['met', 'metHigh']:
#            cut = 't1Met.pt > 100.'
#            if plot.cut:
#                cut += ' && (%s)' % plot.cut
#
#            config.plots.append(plot.clone(plot.name + 'HighMet', cut=cut))
#
#    # Standard MC systematic variations
#    for group in config.bkgGroups + config.sigGroups:
#        group.addVariation('lumi', reweight=0.027)
#
#elif confName == 'vbfm' or confName == 'vbfmlo':
#    config = PlotConfig(confName, ['smu-16*-m'])
#
#    config.baseline = 'pdijet.size != 0 && muons.pt_[0] > 40.'
#
#    config.fullSelection = ''
#
#    mt = 'TMath::Sqrt(2. * t1Met.pt * muons.pt_[0] * (1. - TMath::Cos(TVector2::Phi_mpi_pi(t1Met.phi - muons.phi_[0]))))'
#
#    if confName == 'vbfm':
#        main = wlnun
#        wscale = 1.
#    elif confName == 'vbfmlo':
#        main = wlnu
#        wscale = 6.153 / 4.997
#
#    config.addBkg('top', 't#bar{t}/t', samples=['tt', 'sttbar', 'stt', 'stwbar', 'stw'], color=ROOT.TColor.GetColor(0x55, 0x44, 0xff))
#    config.addBkg('w', 'W#rightarrowl#nu', samples=main, color=ROOT.TColor.GetColor(0x99, 0xee, 0xff), scale=wscale)
#    config.addBkg('wewk', 'W#rightarrowl#nu (EWK)', samples=['wmlnuewk', 'wplnuewk'], color=ROOT.TColor.GetColor(0x77, 0xcc, 0xdd))
#    config.addBkg('z', 'Z#rightarrowll', samples=dy, color=ROOT.TColor.GetColor(0x99, 0xff, 0xaa), scale=6025. / 4975.)
#    config.addBkg('zewk', 'Z#rightarrowll (EWK)', samples=['zewk'], color=ROOT.TColor.GetColor(0x77, 0xdd, 0x99))
#
#    config.obs.region = 'vbfm'
#    for group in config.bkgGroups:
#        if not group.region:
#            group.region = 'vbfm'
#
#    config.addPlot('met', 'E_{T}^{miss}', 't1Met.pt', [10. * x for x in range(10)] + [100. + 20. * x for x in range(20)], unit='GeV', overflow=True)
#    config.addPlot('metHigh', 'E_{T}^{miss}', 't1Met.pt', [100. + 40. * x for x in range(20)], unit='GeV', overflow=True)
#    config.addPlot('mt', 'M_{T}^{#mu}', mt, (50, 0., 500.), unit='GeV', overflow=True)
#    config.addPlot('muPt', 'p_{T}^{#mu}', 'muons.pt_[0]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('muEta', '#eta^{#mu}', 'muons.eta_[0]', (20, -1.5, 1.5))
#    config.addPlot('muPhi', '#phi^{#mu}', 'muons.phi_[0]', (20, -math.pi, math.pi))
#    config.addPlot('nmuons', 'N_{#mu}', 'muons.size', (4, 0., 4.))
#    config.addPlot('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi))
#    config.addPlot('dPhiMuMet', '#Delta#phi(#mu, E_{T}^{miss})', "TMath::Abs(TVector2::Phi_mpi_pi(muons.phi_[0] - t1Met.phi))", (20, 0., math.pi))
#    config.addPlot('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (13, 0., 3.25), cut='jets.pt_ > 30.')
#    config.addPlot('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (20, 0., math.pi))
#    config.addPlot('njets', 'N_{jet}', 'jets.size', (6, 0., 6.))
#    config.addPlot('njetsHighPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (10, 0., 10.), cut='jets.pt_ > 100.')
#    config.addPlot('jetPt', 'p_{T}^{jet}', 'jets.pt_', (40, 0., 1000.), unit='GeV', cut='jets.pt_ > 30', overflow=True)
#    config.addPlot('jet1Pt', 'p_{T}^{j1}', 'jets.pt_[0]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('jet1Eta', '#eta^{j1}', 'jets.eta_[0]', (40, -5., 5.))
#    config.addPlot('jet2Pt', 'p_{T}^{j2}', 'jets.pt_[1]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('jet2Eta', '#eta^{j2}', 'jets.eta_[1]', (40, -5., 5.))
#    config.addPlot('ht', 'H_{T}', 'Sum$(jets.pt_)', (50, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('detajj', '#Delta#eta^{jj}', 'pdijet.dEtajj[0]', (40, 0., 10.))
#    config.addPlot('dphijj', '#Delta#phi^{jj}', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[pdijet.ij1[0]] - jets.phi_[pdijet.ij2[0]]))', (40, 0., math.pi))
#    config.addPlot('mjj', 'm^{jj}', 'pdijet.mjj[0]', (40, 0., 5000.), unit='GeV', sensitive=True)
#    config.addPlot('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
#    config.addPlot('genht', 'H_{T}^{gen}', 'Sum$(partons.pt_ * (TMath::Abs(partons.pdgid) < 7 || partons.pdgid == 21))', (100, 0., 3000), unit='GeV', blind='full')
#    config.addPlot('genhtLow', 'H_{T}^{gen}', 'Sum$(partons.pt_ * (TMath::Abs(partons.pdgid) < 7 || partons.pdgid == 21))', (100, 0., 200), unit='GeV', blind='full')
#    bosonPt='TMath::Sqrt(TMath::Power(Sum$(partons.pt_ * TMath::Cos(partons.phi_) * (TMath::Abs(partons.pdgid) == 13 || TMath::Abs(partons.pdgid) == 14)), 2.)'
#    bosonPt += ' + TMath::Power(Sum$(partons.pt_ * TMath::Sin(partons.phi_) * (TMath::Abs(partons.pdgid) == 13 || TMath::Abs(partons.pdgid) == 14)), 2.))'
#    config.addPlot('genpt', 'p_{T}^{V,gen}', bosonPt, (100, 0., 800), unit='GeV', blind='full')
#
#    for plot in list(config.plots):
#        if plot.name not in ['met', 'metHigh']:
#            cut = 't1Met.pt > 100.'
#            if plot.cut:
#                cut += ' && (%s)' % plot.cut
#
#            config.plots.append(plot.clone(plot.name + 'HighMet', cut=cut))
#
#    # Standard MC systematic variations
#    for group in config.bkgGroups + config.sigGroups:
#        group.addVariation('lumi', reweight=0.027)
#
#elif confName == 'vbfee' or confName == 'vbfeelo':
#    config = PlotConfig(confName, ['sel-16*'])
#
#    config.baseline = 'electrons.pt_[0] > 40.'
#
#    config.fullSelection = ''
#
#    if confName == 'vbfee':
#        main = dyn
#        zscale = 1.
#    elif confName == 'vbfeelo':
#        main = dy
#        zscale = 6025. / 4975.
#
#    mt = 'TMath::Sqrt(2. * t1Met.pt * electrons.pt_[0] * (1. - TMath::Cos(TVector2::Phi_mpi_pi(t1Met.phi - electrons.phi_[0]))))'
#
#    config.addBkg('top', 't#bar{t}', samples=['tt'], color=ROOT.TColor.GetColor(0x55, 0x44, 0xff))
#    config.addBkg('z', 'Z#rightarrowll', samples=main, color=ROOT.TColor.GetColor(0x99, 0xff, 0xaa), scale=zscale)
#    config.addBkg('zewk', 'Z#rightarrowll (EWK)', samples=['zewk'], color=ROOT.TColor.GetColor(0x77, 0xff, 0x99))
#    config.addBkg('vv', 'VV', samples=['ww', 'wz', 'zz'], color=ROOT.TColor.GetColor(0xff, 0x44, 0x99))
#
#    config.obs.region = 'vbfee'
#    for group in config.bkgGroups:
#        if not group.region:
#            group.region = 'vbfee'
#
#    config.addPlot('met', 'E_{T}^{miss}', 't1Met.pt', [10. * x for x in range(10)] + [100. + 20. * x for x in range(20)], unit='GeV', overflow=True)
#    config.addPlot('el1Pt', 'p_{T}^{e1}', 'electrons.pt_[0]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('el1Eta', '#eta^{e1}', 'electrons.eta_[0]', (20, -1.5, 1.5))
#    config.addPlot('el1Phi', '#phi^{e1}', 'electrons.phi_[0]', (20, -math.pi, math.pi))
#    config.addPlot('el2Pt', 'p_{T}^{e2}', 'electrons.pt_[1]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('el2Eta', '#eta^{e2}', 'electrons.eta_[1]', (20, -1.5, 1.5))
#    config.addPlot('el2Phi', '#phi^{e2}', 'electrons.phi_[1]', (20, -math.pi, math.pi))
#    config.addPlot('nelectrons', 'N_{e}', 'electrons.size', (4, 0., 4.))
#    config.addPlot('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi))
#    config.addPlot('dPhiElMet', '#Delta#phi(e, E_{T}^{miss})', "TMath::Abs(TVector2::Phi_mpi_pi(electrons.phi_[0] - t1Met.phi))", (20, 0., math.pi))
#    config.addPlot('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (13, 0., 3.25), cut='jets.pt_ > 30.')
#    config.addPlot('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (20, 0., math.pi))
#    config.addPlot('njets', 'N_{jet}', 'jets.size', (6, 0., 6.))
#    config.addPlot('njetsHighPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (10, 0., 10.), cut='jets.pt_ > 100.')
#    config.addPlot('jetPt', 'p_{T}^{jet}', 'jets.pt_', (40, 0., 1000.), unit='GeV', cut='jets.pt_ > 30', overflow=True)
#    config.addPlot('jet1Pt', 'p_{T}^{j1}', 'jets.pt_[0]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('jet1Eta', '#eta^{j1}', 'jets.eta_[0]', (40, -5., 5.))
#    config.addPlot('jet2Pt', 'p_{T}^{j2}', 'jets.pt_[1]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('jet2Eta', '#eta^{j2}', 'jets.eta_[1]', (40, -5., 5.))
#    config.addPlot('ht', 'H_{T}', 'Sum$(jets.pt_)', (50, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('detajj', '#Delta#eta^{jj}', 'pdijet.dEtajj[0]', (40, 0., 10.))
#    config.addPlot('dphijj', '#Delta#phi^{jj}', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[pdijet.ij1[0]] - jets.phi_[pdijet.ij2[0]]))', (40, 0., math.pi))
#    config.addPlot('mjj', 'm^{jj}', 'pdijet.mjj[0]', (40, 0., 5000.), sensitive=True)
#    config.addPlot('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
#
#    # Standard MC systematic variations
#    for group in config.bkgGroups + config.sigGroups:
#        group.addVariation('lumi', reweight=0.027)
#
#elif confName == 'vbfmm' or confName == 'vbfmmlo':
#    config = PlotConfig(confName, ['smu-16*'])
#
#    config.baseline = 'muons.pt_[0] > 40.'
#
#    config.fullSelection = ''
#
#    mt = 'TMath::Sqrt(2. * t1Met.pt * muons.pt_[0] * (1. - TMath::Cos(TVector2::Phi_mpi_pi(t1Met.phi - muons.phi_[0]))))'
#
#    if confName == 'vbfmm':
#        main = dyn
#        zscale = 1.
#    elif confName == 'vbfmmlo':
#        main = dy
#        zscale = 6025. / 4975.
#
#    config.addBkg('top', 't#bar{t}', samples=['tt'], color=ROOT.TColor.GetColor(0x55, 0x44, 0xff))
#    config.addBkg('z', 'Z#rightarrowll', samples=main, color=ROOT.TColor.GetColor(0x99, 0xff, 0xaa), scale=zscale)
#    config.addBkg('zewk', 'Z#rightarrowll (EWK)', samples=['zewk'], color=ROOT.TColor.GetColor(0x77, 0xdd, 0x99))
#    config.addBkg('vv', 'VV', samples=['ww', 'wz', 'zz'], color=ROOT.TColor.GetColor(0xff, 0x44, 0x99))
#
#    config.obs.region = 'vbfmm'
#    for group in config.bkgGroups:
#        if not group.region:
#            group.region = 'vbfmm'
#
#    config.addPlot('met', 'E_{T}^{miss}', 't1Met.pt', [10. * x for x in range(10)] + [100. + 20. * x for x in range(20)], unit='GeV', overflow=True)
#    config.addPlot('mu1Pt', 'p_{T}^{#mu}', 'muons.pt_[0]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('mu1Eta', '#eta^{#mu}', 'muons.eta_[0]', (20, -1.5, 1.5))
#    config.addPlot('mu1Phi', '#phi^{#mu}', 'muons.phi_[0]', (20, -math.pi, math.pi))
#    config.addPlot('mu2Pt', 'p_{T}^{#mu}', 'muons.pt_[1]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('mu2Eta', '#eta^{#mu}', 'muons.eta_[1]', (20, -1.5, 1.5))
#    config.addPlot('mu2Phi', '#phi^{#mu}', 'muons.phi_[1]', (20, -math.pi, math.pi))
#    config.addPlot('nmuons', 'N_{#mu}', 'muons.size', (4, 0., 4.))
#    config.addPlot('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi))
#    config.addPlot('dPhiMuMet', '#Delta#phi(#mu, E_{T}^{miss})', "TMath::Abs(TVector2::Phi_mpi_pi(muons.phi_[0] - t1Met.phi))", (20, 0., math.pi))
#    config.addPlot('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_ - t1Met.phi))', (13, 0., 3.25), cut='jets.pt_ > 30.')
#    config.addPlot('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (20, 0., math.pi))
#    config.addPlot('njets', 'N_{jet}', 'jets.size', (6, 0., 6.))
#    config.addPlot('njetsHighPt', 'N_{jet} (p_{T} > 100 GeV)', 'jets.size', (10, 0., 10.), cut='jets.pt_ > 100.')
#    config.addPlot('jetPt', 'p_{T}^{jet}', 'jets.pt_', (40, 0., 1000.), unit='GeV', cut='jets.pt_ > 30', overflow=True)
#    config.addPlot('jet1Pt', 'p_{T}^{j1}', 'jets.pt_[0]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('jet1Eta', '#eta^{j1}', 'jets.eta_[0]', (40, -5., 5.))
#    config.addPlot('jet2Pt', 'p_{T}^{j2}', 'jets.pt_[1]', (40, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('jet2Eta', '#eta^{j2}', 'jets.eta_[1]', (40, -5., 5.))
#    config.addPlot('ht', 'H_{T}', 'Sum$(jets.pt_)', (50, 0., 1000.), unit='GeV', overflow=True)
#    config.addPlot('detajj', '#Delta#eta^{jj}', 'pdijet.dEtajj[0]', (40, 0., 10.))
#    config.addPlot('dphijj', '#Delta#phi^{jj}', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi_[pdijet.ij1[0]] - jets.phi_[pdijet.ij2[0]]))', (40, 0., math.pi))
#    config.addPlot('mjj', 'm^{jj}', 'pdijet.mjj[0]', (40, 0., 5000.), unit='GeV', sensitive=True)
#    config.addPlot('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
#
#    # Standard MC systematic variations
#    for group in config.bkgGroups + config.sigGroups:
#        group.addVariation('lumi', reweight=0.027)
#
#elif confName == 'vbfzee':
#    allsamples['sph-16b-m'].lumi = 4778.
#    allsamples['sph-16c-m'].lumi = 2430.
#    allsamples['sph-16d-m'].lumi = 4044.
#    allsamples['sph-16e-m'].lumi = 3284.
#    allsamples['sph-16f-m'].lumi = 2292.
#    allsamples['sph-16g-m'].lumi = 5190.
#    allsamples['sph-16h-m'].lumi = 5470.
#
#    meg = 'TMath::Sqrt(TMath::Power(photons.scRawPt[0] * TMath::CosH(photons.eta_[0]) + electrons.pt_[0] * TMath::CosH(electrons.eta_[0]), 2.)'
#    meg += ' - TMath::Power(photons.scRawPt[0] * TMath::Cos(photons.phi_[0]) + electrons.pt_[0] * TMath::Cos(electrons.phi_[0]), 2.)'
#    meg += ' - TMath::Power(photons.scRawPt[0] * TMath::Sin(photons.phi_[0]) + electrons.pt_[0] * TMath::Sin(electrons.phi_[0]), 2.)'
#    meg += ' - TMath::Power(photons.scRawPt[0] * TMath::SinH(photons.eta_[0]) + electrons.pt_[0] * TMath::SinH(electrons.eta_[0]), 2.))'
#
#    config = PlotConfig('vbfzee', photonData)
#
#    config.baseline = 'photons.scRawPt[0] > 80.'
#
#    config.fullSelection = 'electrons.pt_[0] > 110.'
#
#    config.addBkg('wg', 'W#rightarrowl#nu+#gamma', samples=['wglo'], color=ROOT.TColor.GetColor(0x99, 0xee, 0xff))
#    config.addBkg('top', 't#bar{t}#gamma/t#gamma', samples=['ttg', 'tg'], color=ROOT.TColor.GetColor(0x55, 0x44, 0xff))
#    config.addBkg('zg', 'Z#rightarrow#nu#nu+#gamma', samples=['zllg'], color=ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
#    config.addBkg('efake', 'Electron fakes', samples=photonData, region='vbfzeeEfake', color=ROOT.TColor.GetColor(0xff, 0xee, 0x99))
#
#    config.addPlot('met', 'E_{T}^{miss}', 't1Met.pt', [10. * x for x in range(10)] + [100. + 20. * x for x in range(20)], unit='GeV', overflow=True)
#    config.addPlot('metHigh', 'E_{T}^{miss}', 't1Met.pt', [100. + 40. * x for x in range(20)], unit='GeV', overflow=True,)
#    config.addPlot('mt', 'M_{T}^{#gamma}', 'photons.mt[0]', (50, 0., 500.), unit='GeV', overflow=True)
#     config.addPlot('mtFullSel', 'M_{T}^{#gamma}', 'photons.mt[0]', [20. * x for x in range(5)] + [100 + 25. * x for x in range(9)], unit='GeV', cutName='fullSelection')
#    config.addPlot('mtFullSel', 'M_{T}^{#gamma}', 'photons.mt[0]', (12, 0., 300.), unit='GeV', cutName='fullSelection')
#    config.addPlot('meg', 'M_{e#gamma}', meg, (50, 0., 200.), unit='GeV')

else:
    raise RuntimeError('Unknown configuration ' + pu.confName)
