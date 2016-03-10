import math
import array
import ROOT

class GroupSpec(object):
    def __init__(self, name, title, samples = [], region = '', color = ROOT.kBlack):
        self.name = name
        self.title = title
        self.samples = samples
        self.region = region
        self.color = color
        self.variations = []


class VariableDef(object):
    def __init__(self, name, title, expr, binning, unit = '', cut = '', applyBaseline = True, blind = None, overflow = False, logy = True, ymax = -1.):
        self.name = name
        self.title = title
        self.unit = unit
        self.expr = expr
        self.cut = cut
        self.applyBaseline = applyBaseline
        self.binning = binning
        self.blind = blind
        self.overflow = overflow
        self.logy = logy
        self.ymax = ymax

    def clone(self, name, binning = None, cut = ''):
        vardef = VariableDef(name, self.title, self.expr, self.binning, unit = self.unit, cut = self.cut, applyBaseline = self.applyBaseline, blind = self.blind, overflow = self.overflow, logy = self.logy, ymax = self.ymax)
        
        if binning is not None:
            vardef.binning = binning
        if cut != '':
            vardef.cut = cut

        return vardef

    def ndim(self):
        if type(self.expr) is tuple:
            return len(self.expr)
        else:
            return 1

    def makeHist(self, hname, outDir = None):
        """
        Make an empty histogram from the specifications.
        """

        gd = ROOT.gDirectory    
        if outDir:
            outDir.cd()
        else:
            ROOT.gROOT.cd()

        if self.ndim() == 1:
            if type(self.binning) is list:
                nbins = len(self.binning) - 1
                arr = array.array('d', self.binning)
    
            elif type(self.binning) is tuple:
                nbins = self.binning[0]
                arr = array.array('d', [self.binning[1] + (self.binning[2] - self.binning[1]) / nbins * i for i in range(nbins + 1)])
    
            if self.overflow:
                lastbinWidth = (arr[-1] - arr[0]) / 30.
                arr += array.array('d', [self.binning[-1] + lastbinWidth])
    
            hist = ROOT.TH1D(self.name + '-' + hname, '', nbins, arr)
    
        else:
            args = []
    
            for binning in self.binning:
                if type(binning) is list:
                    nbins = len(binning) - 1
                    arr = array.array('d', binning)
    
                elif type(binning) is tuple:
                    nbins = binning[0]
                    arr = array.array('d', [binning[1] + (binning[2] - binning[1]) / nbins * i for i in range(nbins + 1)])
                    
                args += [nbins, arr]
    
            if ndim == 2:
                hist = ROOT.TH2D(self.name + '-' + hname, '', *tuple(args))
            elif ndim == 3:
                # who would do this??
                hist = ROOT.TH3D(self.name + '-' + hname, '', *tuple(args))
            else:
                raise RuntimeError('What are you thinking')

        gd.cd()

        hist.Sumw2()
        return hist


class PlotConfig(object):
    def __init__(self, name, obsSamples):
        self.name = name # name serves as the default region selection (e.g. monoph)
        self.baseline = '1'
        self.fullSelection = '1'
        self.obs = GroupSpec('data_obs', 'Observed', samples = obsSamples)
        self.sigGroups = []
        self.bkgGroups = []
        self.variables = []
        self.sensitiveVars = []
        self.treeMaker = ''

    def getVariable(self, name):
        return next(variable for variable in self.variables if variable.name == name)

    def countConfig(self):
        return VariableDef('count', '', '0.5', (1, 0., 1.), cut = self.fullSelection)

    def findGroup(self, name):
        return next(g for g in self.sigGroups + self.bkgGroups if g.name == name)

    def samples(self):
        snames = set(self.obs.samples)

        for group in self.bkgGroups:
            for s in group.samples:
                if type(s) is tuple:
                    snames.add(s[0])
                else:
                    snames.add(s)

        for group in self.sigGroups:
            snames.add(group.name)

        return list(snames)


class Variation(object):
    """
    Specifies alternative samples and cuts for systematic variation.
    Must specify either region or replacements or both as a two-component tuple corresponding to up and down variations.
    """

    def __init__(self, name, region = None, replacements = None):
        self.name = name
        self.region = region
        self.replacements = replacements


dPhiPhoMet = 'TVector2::Phi_mpi_pi(photons.phi[0] - t1Met.phi)'
mtPhoMet = 'TMath::Sqrt(2. * t1Met.met * photons.pt[0] * (1. - TMath::Cos(photons.phi[0] - t1Met.phi)))'
        
def getConfig(confName):

    if confName == 'monoph':
        metCut = 't1Met.met > 170.'
        
        config = PlotConfig('monoph', ['sph-d3', 'sph-d4'])
        config.baseline = 'photons.pt[0] > 175. && t1Met.photonDPhi > 2. && t1Met.minJetDPhi > 0.5'
        config.fullSelection = metCut
        config.sigGroups = [
            GroupSpec('add5-2', 'ADD n=5 M_{D}=2TeV', color = 41), # 0.07069/pb
            GroupSpec('dmv-1000-150', 'DM V M_{med}=1TeV M_{DM}=150GeV', color = 46), # 0.01437/pb
            GroupSpec('dma-500-1', 'DM A M_{med}=500GeV M_{DM}=1GeV', color = 30) # 0.07827/pb 
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
            VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [130., 150., 170., 190., 250., 400., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('metWide', 'E_{T}^{miss}', 't1Met.met', [0. + 10. * x for x in range(10)] + [100. + 20. * x for x in range(5)] + [200. + 50. * x for x in range(9)], unit = 'GeV', overflow = True),
            VariableDef('metHigh', 'E_{T}^{miss}', 't1Met.met', [170., 230., 290., 350., 410., 500., 600., 700., 1000.], unit = 'GeV', overflow = True),
            VariableDef('mtPhoMet', 'M_{T#gamma}', mtPhoMet, (22, 200., 1300.), unit = 'GeV', overflow = True, blind = (600., 2000.)),
            VariableDef('phoPt', 'E_{T}^{#gamma}', 'photons.pt[0]', [175.] + [180. + 10. * x for x in range(12)] + [300., 350., 400., 450.] + [500. + 100. * x for x in range(6)], unit = 'GeV', overflow = True),
            VariableDef('phoEta', '#eta^{#gamma}', 'photons.eta[0]', (20, -1.5, 1.5)),
            VariableDef('phoPhi', '#phi^{#gamma}', 'photons.phi[0]', (20, -math.pi, math.pi)),
            VariableDef('dPhiPhoMet', '#Delta#phi(#gamma, E_{T}^{miss})', dPhiPhoMet, (20, -math.pi, math.pi), cut = 't1Met.met > 40.'),
            VariableDef('metPhi', '#phi(E_{T}^{miss})', 't1Met.phi', (20, -math.pi, math.pi)),
            VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, j)', 'TMath::Abs(TVector2::Phi_mpi_pi(jets.phi - t1Met.phi))', (30, 0., math.pi), cut = 'jets.pt > 30.'),
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

        config.sensitiveVars = ['met', 'metWide', 'metHigh', 'phoPtHighMet', 'mtPhoMet', 'mtPhoMetHighMet']
        
        config.treeMaker = 'MonophotonTreeMaker'

        # Standard MC systematic variations
        for group in config.bkgGroups + config.sigGroups:
            if group.name == 'efake' or group.name == 'hfake' or group.name == 'halo':
                continue
            
            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECUp'), ('t1Met.met', 't1Met.metCorrUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiJECDown'), ('t1Met.met', 't1Met.metCorrDown')]
            group.variations.append(Variation('jec', replacements = (replUp, replDown)))

            replUp = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECUp'), ('photons.pt', 'photons.ptVarUp'), ('t1Met.met', 't1Met.metGECUp')]
            replDown = [('t1Met.minJetDPhi', 't1Met.minJetDPhiGECDown'), ('photons.pt', 'photons.ptVarDown'), ('t1Met.met', 't1Met.metGECDown')]
            group.variations.append(Variation('gec', replacements = (replUp, replDown)))

        # Specific systematic variations
        config.findGroup('hfake').variations.append(Variation('tfactor', region = ('hfakeUp', 'hfakeDown')))
    
    elif confName == 'lowdphi':
        metCut = 't1Met.met > 170.'
        
        config = PlotConfig('monoph', ['sph-d3', 'sph-d4'])
        config.baseline = 'photons.pt[0] > 175. && t1Met.minJetDPhi < 0.5'
        config.fullSelection = metCut
        config.bkgGroups = [
            GroupSpec('minor', 'minor SM', samples = ['ttg', 'zllg-130', 'wlnu-100','wlnu-200', 'wlnu-400', 'wlnu-600'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('efake', 'Electron fakes', samples = ['sph-d3', 'sph-d4'], region = 'efake', color = ROOT.TColor.GetColor(0xff, 0xee, 0x99)),
            GroupSpec('wg', 'W#rightarrowl#nu+#gamma', samples = ['wnlg-130'], color = ROOT.TColor.GetColor(0x99, 0xee, 0xff)),
            GroupSpec('zg', 'Z#rightarrow#nu#nu+#gamma', samples = ['znng-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa)),
            GroupSpec('hfake', 'Hadronic fakes', samples = ['sph-d3', 'sph-d4'], region = 'hfake', color = ROOT.TColor.GetColor(0xbb, 0xaa, 0xff)),
            GroupSpec('gjets', '#gamma + jets', samples = ['gj-40', 'gj-100', 'gj-200', 'gj-400', 'gj-600'], color = ROOT.TColor.GetColor(0xff, 0xaa, 0xcc))
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
    
    elif confName == 'dimu':
        mass = 'TMath::Sqrt(2. * muons.pt[0] * muons.pt[1] * (TMath::CosH(muons.eta[0] - muons.eta[1]) - TMath::Cos(muons.phi[0] - muons.phi[1])))'
        dR2_00 = 'TMath::Power(photons.eta[0] - muons.eta[0], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi[0]), 2.)'
        dR2_01 = 'TMath::Power(photons.eta[0] - muons.eta[1], 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi[0] - muons.phi[1]), 2.)'

        config = PlotConfig('dimu', ['smu-d3', 'smu-d4'])
        config.baseline = mass + ' > 50. && t1Met.recoil > 100.'
        config.fullSelection = 'photons.pt[0] > 100.'
        config.bkgGroups = [
            GroupSpec('ttg', 't#bar{t}#gamma', samples = ['ttg'], color = ROOT.TColor.GetColor(0x55, 0x44, 0xff)),
            GroupSpec('zg', 'Z#rightarrowll+#gamma', samples = ['zllg-130'], color = ROOT.TColor.GetColor(0x99, 0xff, 0xaa))
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
        print 'Unknown configuration', confName
        return

    return config
