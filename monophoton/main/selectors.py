import sys
import os
import array
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')

ROOT.gROOT.LoadMacro(thisdir + '/operators.cc+')
ROOT.gROOT.LoadMacro(thisdir + '/selectors.cc+')

photonFullSelection = [
    'HOverE',
    'Sieie',
    'CHIso',
    'CHWorstIso',
    'NHIso',
    'PhIso',
    'EVeto',
    'MIP49',
    'Time',
    'SieieNonzero',
    'NoisyRegion'
]

npvSource = ROOT.TFile.Open(basedir + '/data/npv.root')
npvWeight = npvSource.Get('npvweight')

photonSFSource = ROOT.TFile.Open(basedir + '/data/photon_id_scalefactor.root')
photonSF = photonSFSource.Get('EGamma_SF2D')

hadproxySource = ROOT.TFile.Open(basedir + '/data/hadronTFactor.root')
#hadproxyWeight = hadproxySource.Get('tfact')
#hadproxyupWeight = hadproxySource.Get('tfactUp')
#hadproxydownWeight = hadproxySource.Get('tfactDown')
#hadproxyworstWeight = hadproxySource.Get('tfactWorst')
#hadproxyworstupWeight = hadproxySource.Get('tfactWorstUp')
#hadproxyworstdownWeight = hadproxySource.Get('tfactWorstDown')
hadproxyWeight = hadproxySource.Get('tfactWorst')
hadproxyupWeight = hadproxySource.Get('tfactWorstUp')
hadproxydownWeight = hadproxySource.Get('tfactWorstDown')

eleproxySource = ROOT.TFile.Open(basedir + '/data/egfake_data.root')
eleproxyWeight = eleproxySource.Get('fraction')

def monophotonBase(sample, name, selector = None):
    """
    Monophoton candidate-like selection (high-pT photon, lepton veto, dphi(photon, MET) and dphi(jet, MET)).
    Base for other selectors.
    """

    if selector is None:
        selector = ROOT.EventSelector(name)

    operators = []

    if sample.data:
        operators.append('HLTPhoton165HE10')

    operators += [
        'MetFilters',
        'PhotonSelection',
        'MuonVeto',
        'ElectronVeto',
        'TauVeto',
        'JetCleaning',
        'CopyMet'
    ]

    if not sample.data:
        operators.append('MetVariations')

    operators += [
        'PhotonMetDPhi',
        'JetMetDPhi',
        'HighMet'
    ]

    for op in operators:
        selector.addOperator(getattr(ROOT, op)())

    if not sample.data:
        metVar = selector.findOperator('MetVariations')
        metVar.setPhotonSelection(selector.findOperator('PhotonSelection'))
        selector.addOperator(metVar)

        selector.findOperator('PhotonMetDPhi').setMetVariations(metVar)
        selector.findOperator('JetMetDPhi').setMetVariations(metVar)

        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw, 'crosssection'))
        selector.addOperator(ROOT.NPVWeight(npvWeight))

    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.JetCleaning.kTaus, False)
    selector.findOperator('JetMetDPhi').setIgnoreDecision(True)
    selector.findOperator('HighMet').setIgnoreDecision(True)
    
    return selector

def candidate(sample, name, selector = None):
    """
    Full monophoton selection.
    """

    selector = monophotonBase(sample, name, selector)

    if not sample.data:
        selector.addOperator(ROOT.IDSFWeight(ROOT.IDSFWeight.kPhoton, photonSF, 'PhotonIDSFWeight'))

    photonSel = selector.findOperator('PhotonSelection')

    for sel in photonFullSelection:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    return selector

def eleProxy(sample, name, selector = None):
    """
    Candidate-like but with inverted electron veto
    """

    selector = monophotonBase(sample, name, selector)

    weight = ROOT.ConstantWeight(eleproxyWeight.GetY()[0], 'egfakerate')
    weight.setUncertaintyUp(eleproxyWeight.GetErrorY(0) / eleproxyWeight.GetY()[0])
    weight.setUncertaintyDown(eleproxyWeight.GetErrorY(0) / eleproxyWeight.GetY()[0])
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')

    sels = list(photonFullSelection)
    sels.remove('EVeto')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.EVeto)
    photonSel.addVeto(True, ROOT.PhotonSelection.EVeto)

    return selector

def purity(sample, name, selector = None):
    """
    Candidate-like but with loosened sieie or CHIso.
    """

    selector = monophotonBase(sample, name, selector)

    photonSel = selector.findOperator('PhotonSelection')

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.remove('CHIso')
    sels.remove('CHWorstIso')
    sels.append('Sieie15')
    sels.append('CHIso11')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    return selector

def hadProxy(sample, name, selector = None):
    """
    Candidate-like but with inverted sieie or CHIso.
    """

    selector = monophotonBase(sample, name, selector)

    weight = ROOT.PhotonPtWeight(hadproxyWeight)
    weight.setPhotonType(ROOT.PhotonPtWeight.kReco)
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.remove('CHIso')
    sels.remove('CHWorstIso')
    sels.append('Sieie15')
    sels.append('CHWorstIso11')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHWorstIso)
    photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    photonSel.addVeto(True, ROOT.PhotonSelection.CHWorstIso)

    return selector

def hadProxyUp(sample, name, selector = None):
    """
    Candidate-like with tight NHIso and PhIso, with inverted sieie or CHIso.
    """

    selector = monophotonBase(sample, name, selector)

    weight = ROOT.PhotonPtWeight(hadproxyupWeight)
    weight.setPhotonType(ROOT.PhotonPtWeight.kReco)
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.remove('CHIso')
    sels.remove('CHWorstIso')
    sels.append('NHIsoTight')
    sels.append('PhIsoTight')
    sels.append('Sieie15')
    sels.append('CHWorstIso11')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHWorstIso)
    photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    photonSel.addVeto(True, ROOT.PhotonSelection.CHWorstIso)

    return selector

def hadProxyDown(sample, name, selector = None):
    """
    Candidate-like, but with loosened sieie + CHIso and inverted NHIso or PhIso.
    """

    selector = monophotonBase(sample, name, selector)

    weight = ROOT.PhotonPtWeight(hadproxydownWeight)
    weight.setPhotonType(ROOT.PhotonPtWeight.kReco)
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.remove('CHIso')
    sels.remove('CHWorstIso')
    sels.remove('NHIso')
    sels.remove('PhIso')
    sels.append('Sieie15')
    sels.append('CHWorstIso11')
    sels.append('NHIso11')
    sels.append('PhIso3')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.NHIso, ROOT.PhotonSelection.PhIso)
    photonSel.addVeto(True, ROOT.PhotonSelection.NHIso)
    photonSel.addVeto(True, ROOT.PhotonSelection.PhIso)

    return selector

def gammaJets(sample, name, selector = None):
    """
    Candidate-like, but with inverted jet-met dPhi cut.
    """

    selector = candidate(sample, name, selector)

    selector.findOperator('JetMetDPhi').setPassIfIsolated(False)

    return selector

def halo(norm):
    """
    Wrapper to return the generator for the halo proxy sample normalized to norm.
    """

    def normalized(sample, name):
        """
        Candidate-like, but with inverted MIP tag and CSC filter.
        """
    
        selector = ROOT.NormalizingSelector(name)
        selector.setNormalization(norm)
    
        selector = monophotonBase(sample, name, selector)
    
        # 0->CSC halo tagger
    #    selector.findOperator('MetFilters').setFilter(0, -1)
    
        photonSel = selector.findOperator('PhotonSelection')
    
        sels = list(photonFullSelection)
        sels.remove('Sieie')
        sels.remove('MIP49')
        sels.append('Sieie15')
    
        for sel in sels:
            photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
    
        photonSel.addSelection(False, ROOT.PhotonSelection.MIP49)
    
        return selector

    return normalized

def leptonBase(sample, name, selector = None):
    """
    Base for n-lepton + photon selection
    """

    if selector is None:
        selector = ROOT.EventSelector(name)

    for op in [
        'MetFilters',
        'PhotonSelection',
        'LeptonSelection',
        'TauVeto',
        'JetCleaning',
        'CopyMet',
        'LeptonRecoil'
    ]:
        selector.addOperator(getattr(ROOT, op)())

    if not sample.data:
        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw))
        selector.addOperator(ROOT.NPVWeight(npvWeight))

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.setMinPt(30.)
    for sel in photonFullSelection:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.JetCleaning.kTaus, False)

    return selector

def electronBase(sample, name, selector = None):
    selector = leptonBase(sample, name, selector)
    selector.addOperator(ROOT.HLTEle27eta2p1WPLooseGsf(), 0)

    return selector

def muonBase(sample, name, selector = None):
    selector = leptonBase(sample, name, selector)
    selector.addOperator(ROOT.HLTIsoMu27(), 0)

    return selector

def dielectron(sample, name, selector = None):
    selector = electronBase(sample, name, selector)
    selector.findOperator('LeptonSelection').setN(2, 0)

    return selector

def monoelectron(sample, name, selector = None):
    selector = electronBase(sample, name, selector)
    selector.findOperator('LeptonSelection').setN(1, 0)

    return selector

def dimuon(sample, name, selector = None):
    selector = muonBase(sample, name, selector)
    selector.findOperator('LeptonSelection').setN(0, 2)

    return selector

def monomuon(sample, name, selector = None):
    selector = muonBase(sample, name, selector)
    selector.findOperator('LeptonSelection').setN(0, 1)

    return selector

def oppflavor(sample, name, selector = None):
    selector = muonBase(sample, name, selector)
    selector.findOperator('LeptonSelection').setN(1, 1)

    return selector

def zee(sample, name):
    selector = ROOT.ZeeEventSelector(name)

    eeSel = selector.findOperator('EEPairSelection')
    eeSel.setMinPt(140.)

    sels = list(photonFullSelection)
    sels.remove('EVeto')

    for sel in sels:
        eeSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    eeSel.addSelection(False, ROOT.PhotonSelection.EVeto)

    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.JetCleaning.kTaus, False)

    return selector

def kfactor(generator):
    """
    Wrapper for applying the k-factor corrections to the selector returned by the generator in the argument.
    """

    def scaled(sample, name):
        selector = generator(sample, name)

        qcdSource = ROOT.TFile.Open(basedir + '/data/kfactor.root')
        corr = qcdSource.Get(sample.name)

        qcd = ROOT.PhotonPtWeight(corr, 'QCDCorrection')
        qcd.setPhotonType(ROOT.PhotonPtWeight.kPostShower)

        for variation in ['renUp', 'renDown', 'facUp', 'facDown', 'pdfUp', 'pdfDown', 'scaleUp', 'scaleDown']:
            vcorr = qcdSource.Get(sample.name + '_' + variation)
            if vcorr:
                qcd.addVariation('qcd' + variation, vcorr)

        selector.addOperator(qcd)
    
        ewkSource = ROOT.TFile.Open(basedir + '/data/ewk_corr.root')
        corr = ewkSource.Get(sample.name)
        if corr:
            ewk = ROOT.PhotonPtWeight(corr, 'EWKNLOCorrection')
            ewk.setPhotonType(ROOT.PhotonPtWeight.kParton)
    
            for variation in ['Up', 'Down']:
                vcorr = ewkSource.Get(sample.name + '_' + variation)
                if vcorr:
                    ewk.addVariation('ewk' + variation, vcorr)

            selector.addOperator(ewk)
    
        return selector

    return scaled

def wlnu(generator):
    """
    Wrapper for W->lnu sample to pick out non-electron decays only.
    """

    def filtered(sample, name):
        return generator(sample, name, ROOT.WlnuSelector(name))

    return filtered
