import math
import ROOT

class GroupSpec(object):
    def __init__(self, name, title, samples = [], color = ROOT.kBlack):
        self.name = name
        self.title = title
        self.samples = samples
        self.color = color


class VariableDef(object):
    def __init__(self, name, title, expr, binning, unit = '', cut = '', baseline = True, blind = None, overflow = False, is2D = False, logy = True, ymax = -1.):
        self.name = name
        self.title = title
        self.unit = unit
        self.expr = expr
        self.cut = cut
        self.baseline = baseline
        self.binning = binning
        self.blind = blind
        self.overflow = overflow
        self.is2D = is2D
        self.logy = logy
        self.ymax = ymax

    def clone(self, name, binning = None, cut = ''):
        vardef = VariableDef(name, self.title, self.expr, self.binning, unit = self.unit, cut = self.cut, baseline = self.baseline, blind = self.blind, overflow = self.overflow, is2D = self.is2D, logy = self.logy, ymax = self.ymax)
        
        if binning is not None:
            vardef.binning = binning
        if cut != '':
            vardef.cut = cut

        return vardef

class PlotConfig(object):
    def __init__(self, defaultRegion):
        self.defaultRegion = defaultRegion
        self.baseline = '1'
        self.fullSelection = ''
        self.obs = GroupSpec('obs', 'Observed')
        self.sigGroups = []
        self.bkgGroups = []
        self.variables = []
        self.sensitiveVars = []

    def getVariable(self, name):
        return next(variable for variable in self.variables if variable.name == name)

    def countConfig(self):
        return VariableDef('count', '', '0.5', (1, 0., 1.), cut = self.fullSelection)


dPhiPhoMet = 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)'
mtPhoMet = 'TMath::Sqrt(2. * t1Met.met * photons.pt[0] * (1. - TMath::Cos(photons.phi[0] - t1Met.phi)))'
        
def getConfig(region):

    if region == 'monoph':
        metCut = 't1Met.met > 170.'
        
        config = PlotConfig('monoph')
        config.baseline = 'photons.pt[0] > 175. && t1Met.minJetDPhi > 0.5'
        config.fullSelection = metCut
        config.obs.samples = ['sph-d3', 'sph-d4']
        config.sigGroups = [
            GroupSpec('add5-2', 'ADD n=5 M_{D}=2TeV', ['add5-2'], 41), # 0.07069/pb
            GroupSpec('dmv-1000-150', 'DM V M_{med}=1TeV M_{DM}=150GeV', ['dmv-1000-150'], 46), # 0.01437/pb
            GroupSpec('dma-500-1', 'DM A M_{med}=500GeV M_{DM}=1GeV', ['dma-500-1'], 30) # 0.07827/pb 
        ]
        config.bkgGroups = [
            GroupSpec('minor', 'minor SM', ['ttg', 'zllg-130', 'wlnu-100','wlnu-200', 'wlnu-400', 'wlnu-600'], ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('gjets', '#gamma + jets', ['gj-40', 'gj-100', 'gj-200', 'gj-400', 'gj-600'], ROOT.TColor.GetColor(0xff, 0xaa, 0xcc)),
            GroupSpec('hfake', 'Hadronic fakes', [('sph-d3', 'hfake'), ('sph-d4', 'hfake')], ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('efake', 'Electron fakes', [('sph-d3', 'efake'), ('sph-d4', 'efake')], ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', ['wnlg-130'], ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', ['znng-130'], ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [130., 150., 170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('metWide', 'E_{T}^{miss}', 't1Met.met', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('metHigh', 'E_{T}^{miss}', 't1Met.met', [170., 230., 290., 350., 410., 500., 600., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (22, 200., 1300.), unit = 'GeV', overflow = True, blind = (600., 2000.)),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta[0]', (20, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi[0]', (20, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', dPhiPhoMet, (20, -math.pi, math.pi), cut = 't1Met.met > 40.'),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi - t1Met.phi))', (30, 0., math.pi)),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.)),
            VariableDef('phoPtOverMet', 'E_{T}^{#gamma}/E_{T}^{miss}', 'photons.pt[0] / t1Met.met', (20, 0., 4.)),
            VariableDef('phoPtOverJetPt', 'E_{T}^{#gamma}/p_{T}^{jet}', 'photons.pt[0] / jets.pt[0]', (20, 0., 10.)),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.)),
            VariableDef('sieie', '#sigma_{i#eta i#eta}', 'photons.sieie[0]', (16, 0.004, 0.012)),
            VariableDef('r9', 'r9', 'photons.r9[0]', (50, 0.5, 1.)),
            VariableDef('s4', 's4', 'photons.s4[0]', (50, 0.5, 1.), logy = False),
            VariableDef('etaWidth', 'etaWidth', 'photons.etaWidth[0]', (30, 0.004, .016)),
            VariableDef('phiWidth', 'phiWidth', 'photons.phiWidth[0]', (18, 0., 0.05)),
            VariableDef('timeSpan', 'timeSpan', 'photons.timeSpan[0]', (20, -20., 20.)),
        ]

        for variable in list(config.variables): # need to clone the list first!
            if variable.name not in ['met', 'metWide', 'metHigh']:
                config.variables.append(variable.clone(variable.name + 'HighMet', cut = metCut))

        config.getVariable('phoPtHighMet').binning = [175., 190., 250., 400., 700., 1000.]

        config.sensitiveVars = ['count', 'met', 'metWide', 'metHighMet', 'phoPtHighMet', 'mtPhoMet', 'mtPhoMetHighMet']
    
    elif args.region == 'lowdphi':
        metCut = 't1Met.met > 170.'
        
        config = PlotConfig('monoph')
        config.baseline = 'photons.pt[0] > 175. && t1Met.minJetDPhi < 0.5'
        config.fullSelection = metCut
        config.obs.samples = ['sph-d3', 'sph-d4']
        config.bkgGroups = [
            GroupSpec('minor', 'minor SM', ['ttg', 'zllg-130', 'wlnu-100','wlnu-200', 'wlnu-400', 'wlnu-600'], ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('efake', 'Electron fakes', [('sph-d3', 'efake'), ('sph-d4', 'efake')], ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', ['wnlg-130'], ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', ['znng-130'], ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            GroupSpec('hfake', 'Hadronic fakes', [('sph-d3', 'hfake'), ('sph-d4', 'hfake')], ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('gjets', '#gamma + jets', ['gj-40', 'gj-100', 'gj-200', 'gj-400', 'gj-600'], ROOT.TColor.GetColor(0xff, 0xaa, 0xcc))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [130., 150., 170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (22, 200., 1300.), unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi - t1Met.phi))', (30, 0., math.pi)),
            VariableDef('dPhiJetMetMin', 'min#Delta#phi(E_{T}^{miss}, j)', 't1Met.minJetDPhi', (30, 0., math.pi)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (6, 0., 6.)),
            VariableDef('nVertex', 'N_{vertex}', 'npv', (20, 0., 40.))
        ]

        for variable in list(config.variables):
            if variable.name not in ['met']:
                config.variables.append(variable.clone(variable.name + 'HighMet', cut = metCut))
    
    elif args.region == 'dimu':
        mass = 'TMath::Sqrt(2. * muons.pt[0] * muons.pt[1] * (TMath::CosH(muons.eta[0] - muons.eta[1]) - TMath::Cos(muons.phi[0] - muons.phi[1])))'
        dR2_00 = 'TMath::Power(photons.eta[0] - muons.eta[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi[0]), 2.)'
        dR2_01 = 'TMath::Power(photons.eta[0] - muons.eta[1], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi[1]), 2.)'

        config = PlotConfig('dimu')
        config.baseline = mass + ' > 50. && t1Met.recoil > 100.'
        config.fullSelection = 'photons.pt[0] > 100.'
        config.obs.samples = ['smu-d3', 'smu-d4']
        config.bkgGroups = [
            GroupSpec('ttg', 't#bar{t}#gamma', ['ttg'], ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('zg', 'Z#rightarrowll+#gamma', ['zllg-130'], ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
        ]
        config.variables = [
            VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [10. * x for x in range(16)] + [160. + 40. * x for x in range(3)], unit = 'GeV', overflow = True),
            VariableDef('recoil', 'Recoil', 't1Met.recoil', [100. + 10. * x for x in range(6)] + [160. + 40. * x for x in range(3)], unit = 'GeV', overflow = True),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [80. + 10. * x for x in range(22)] + [300. + 40. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta[0]', (20, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi[0]', (20, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', dPhiPhoMet, (20, -math.pi, math.pi)),
            VariableDef('dPhiPhoRecoil', '#Delta#phi(#gamma, U)', 'TVector2::Phi_mpi_pi(photons.phi[0] - recoilPhi)', (20, -math.pi, math.pi)),
            VariableDef('dimumass', 'M_{#mu#mu}', mass, (30, 50., 200.), unit = 'GeV'),
            VariableDef('dRPhoMu', '#DeltaR(#gamma, #mu)_{min}', 'TMath::Sqrt(TMath::Min(%s, %s))' % (dR2_00, dR2_01), (20, 0., 4.)),
            VariableDef('njets', 'N_{jet}', 'jets.size', (10, 0., 10.))
        ]
    
    else:
        print 'Unknown region', args.region
        return

    return config
