import sys
import os
import array
needHelp = False
for opt in ['-h', '--help']:
    if opt in sys.argv:
        needHelp = True
        sys.argv.remove(opt)

import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
datadir = basedir + '/data'

if basedir not in sys.path:
    sys.path.append(basedir)

import config

ROOT.gSystem.Load(config.libsimpletree)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')

#ROOT.gROOT.LoadMacro(thisdir + '/jer.cc+')
ROOT.gROOT.LoadMacro(thisdir + '/operators.cc+')
ROOT.gROOT.LoadMacro(thisdir + '/selectors.cc+')

photonFullSelection = [
    'HOverE',
    'Sieie',
    'CHIsoMax',
    'NHIso',
    'PhIso',
    # 'CHIsoMaxS16',
    # 'CHIsoS16',
    # 'NHIsoS16',
    # 'PhIsoS16',
    'EVeto',
    'MIP49',
    'Time',
    'SieieNonzero',
    'SipipNonzero',
#    'E2E995',
    'NoisyRegion'
]

# MEDIUM ID
photonWP = 1

# LOOSE ID
# photonWP = 0

def getFromFile(path, name, newname = ''):
    if newname == '':
        newname = name

    f = ROOT.TFile.Open(path)
    ROOT.gROOT.cd()
    obj = f.Get(name).Clone(newname)
    f.Close()

    return obj

puWeight = getFromFile(datadir + '/pileup.root', 'puweight')

photonSF = getFromFile(datadir + '/photon_id_sf16.root', 'EGamma_SF2D', 'photonSF')

hadproxyWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactNom')
hadproxyupWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactUp')
hadproxydownWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactDown')
hadproxyPurityUpWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactNomPurityUp')
hadproxyPurityDownWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactNomPurityDown')

eleproxyWeight = getFromFile(datadir + '/efake_data_pt.root', 'frate')

muonTightSF = getFromFile(datadir + '/scaleFactor_muon_tightid_12p9.root', 'scaleFactor_muon_tightid_RooCMSShape') # x: abs eta, y: pt
muonLooseSF = getFromFile(datadir + '/scaleFactor_muon_looseid_12p9.root', 'scaleFactor_muon_looseid_RooCMSShape') # x: abs eta, y: pt
muonTrackSF = getFromFile(datadir + '/muonpog_muon_tracking_SF_ichep.root', 'htrack2') # x: npv
muonTrigSF = getFromFile(datadir + '/muonTrigSF.root', 'mutrksfptg10')

electronTightSF = getFromFile(datadir + '/egamma_electron_tight_SF_ichep.root', 'EGamma_SF2D', 'electronTightSF') # x: sc eta, y: pt
electronLooseSF = getFromFile(datadir + '/egamma_electron_loose_SF_ichep.root', 'EGamma_SF2D', 'electronLooseSF') # x: sc eta, y: pt
electronTrackSF = getFromFile(datadir + '/egamma_gsf_tracking_SF_ichep.root', 'EGamma_SF2D', 'electronTrackSF') # x: sc eta, y: npv

##############################################################
# Argument "selector" in all functions below can either be an
# actual Selector object or a name for the selector.
##############################################################

##################
# BASE SELECTORS #
##################

def monophotonBase(sample, selector):
    """
    Monophoton candidate-like selection (high-pT photon, lepton veto, dphi(photon, MET) and dphi(jet, MET)).
    Base for other selectors.
    """

    if type(selector) is str: # this is a name for the selector
        selector = ROOT.EventSelector(selector)

    if sample.data:
        selector.addOperator(ROOT.HLTFilter('HLT_Photon165_HE10'))

    operators = [
        'MetFilters',
        'PhotonSelection',
        'MuonVeto',
        'ElectronVeto',
        'TauVeto',
        'BjetVeto',
        'JetCleaning',
        'CopyMet'
    ]

    if not sample.data:
        operators.append('MetVariations')
        
    operators += [
        'PhotonMetDPhi',
        'JetMetDPhi',
        'PhotonJetDPhi',
        'HighMet',
        'PhotonMt'
    ]

    for op in operators:
        selector.addOperator(getattr(ROOT, op)())

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.setWP(photonWP)

    if not sample.data:
        metVar = selector.findOperator('MetVariations')
        jetClean = selector.findOperator('JetCleaning')
        metVar.setPhotonSelection(selector.findOperator('PhotonSelection'))

        photonDPhi = selector.findOperator('PhotonMetDPhi')
        photonDPhi.setMetVariations(metVar)
        
        jetDPhi = selector.findOperator('JetMetDPhi')
        jetDPhi.setMetVariations(metVar)

        selector.findOperator('PhotonJetDPhi').setMetVariations(metVar)

        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw, 'crosssection'))
        selector.addOperator(ROOT.PUWeight(puWeight))

    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('BjetVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.kTaus, False)
    selector.findOperator('PhotonMetDPhi').setIgnoreDecision(True)
    selector.findOperator('JetMetDPhi').setIgnoreDecision(True)
    selector.findOperator('HighMet').setIgnoreDecision(True)

    return selector

def purityBase(sample, selector):
    """
    Base selector for EM+Jet control region.
    """

    if type(selector) is str: # this is a name for the selector
        selector = ROOT.EventSelector(selector)

#    if sample.data:
#        selector.addOperator(ROOT.HLTFilter('HLT_Photon165_HE10'))

    operators = [
        'MetFilters',
        'PhotonSelection',
        'MuonVeto',
        'ElectronVeto',
        'TauVeto',
        'BjetVeto',
        'JetCleaning',
        'HighPtJetSelection',
        'CopyMet'
    ]

    operators += [
        'JetMetDPhi',
        'PhotonMetDPhi'
    ]

    for op in operators:
        selector.addOperator(getattr(ROOT, op)())

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.setWP(photonWP)

    if not sample.data:
        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw, 'crosssection'))
        selector.addOperator(ROOT.PUWeight(puWeight))

    selector.findOperator('PhotonSelection').setMinPt(100.)
    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('BjetVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.kTaus, False)
    selector.findOperator('HighPtJetSelection').setJetPtCut(100.)
    selector.findOperator('JetMetDPhi').setIgnoreDecision(True)
    selector.findOperator('PhotonMetDPhi').setIgnoreDecision(True)

    return selector

def leptonBase(sample, selector):
    """
    Base for n-lepton + photon selection
    """

    if type(selector) is str: # this is a name for the selector
        selector = ROOT.EventSelector(selector)

    if sample.data:
        selector.addOperator(ROOT.HLTFilter('HLT_Photon165_HE10'))

    operators = [
        'MetFilters',
        'PhotonSelection',
        'LeptonSelection',
        'TauVeto',
        'BjetVeto',
        'JetCleaning',
        'LeptonRecoil',
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

    jetDPhi = selector.findOperator('JetMetDPhi')
    jetDPhi.setMetSource(ROOT.kInMet)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.setWP(photonWP)

    photonSel.resetSelection()
    photonSel.resetVeto()
    for sel in photonFullSelection:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    if not sample.data:
        metVar = selector.findOperator('MetVariations')
        metVar.setPhotonSelection(photonSel)

        realMetVar = ROOT.MetVariations('RealMetVar')
        realMetVar.setMetSource(ROOT.kInMet)
        realMetVar.setPhotonSelection(photonSel)

        selector.findOperator('PhotonMetDPhi').setMetVariations(metVar)
        
        jetDPhi.setMetVariations(realMetVar)

        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw, 'crosssection'))
        selector.addOperator(ROOT.PUWeight(puWeight))

        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kPhoton, 'photonSF')
        idsf.addFactor(photonSF)
        idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)
        # selector.addOperator(ROOT.ConstantWeight(1.01, 'extraSF'))
        if 'amcatnlo' in sample.fullname or 'madgraph' in sample.fullname: # ouh la la..
            selector.addOperator(ROOT.NNPDFVariation())

    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('BjetVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.kTaus, False)
    selector.findOperator('PhotonMetDPhi').setIgnoreDecision(True)
    selector.findOperator('JetMetDPhi').setIgnoreDecision(True)
    selector.findOperator('HighMet').setIgnoreDecision(True)

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
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.kTaus, False)

    return selector

def TagAndProbeBase(sample, selector):
    """
    Base for Z->ll tag and probe stuff.
    """

    if type(selector) is str: # this is a name for the selector
        selector = ROOT.EventSelector(selector)

    operators = [
        'MetFilters',
        'MuonVeto',
        'ElectronVeto',
        'TauVeto',
        'BjetVeto',
        'TagAndProbePairZ',
        'JetCleaning',
        'CopyMet',
        'JetMetDPhi',
        'HighMet'
    ]
    
    for op in operators:
        selector.addOperator(getattr(ROOT, op)())

    if not sample.data:
        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw))
        selector.addOperator(ROOT.PUWeight(puWeight))

    selector.findOperator('MuonVeto').setIgnoreDecision(True)
    selector.findOperator('ElectronVeto').setIgnoreDecision(True)
    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('BjetVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.kTaus, False)
    # selector.findOperator('JetCleaning').setCleanAgainst(ROOT.kElectrons, False)
    # selector.findOperator('JetCleaning').setCleanAgainst(ROOT.kMuons, False)
    selector.findOperator('JetMetDPhi').setIgnoreDecision(True)
    selector.findOperator('HighMet').setThreshold(50.)
    selector.findOperator('HighMet').setIgnoreDecision(True)

    return selector

#####################
# DERIVED SELECTORS #
#####################

def candidate(sample, selector):
    """
    Full monophoton selection.
    """

    selector = monophotonBase(sample, selector)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kPhoton, 'photonSF')
        idsf.addFactor(photonSF)
        idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)
        # selector.addOperator(ROOT.ConstantWeight(1.01, 'extraSF'))
        if 'amcatnlo' in sample.fullname or 'madgraph' in sample.fullname: # ouh la la..
            selector.addOperator(ROOT.NNPDFVariation())

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    for sel in photonFullSelection:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    return selector

def signalRaw(sample, selector):
    """
    Ignore decisions of all cuts to compare shapes for different simulations.
    """

    selector = candidate(sample, selector)

    cuts = [
        'MetFilters',
        'PhotonSelection',
        'ElectronVeto',
        'MuonVeto',
        'TauVeto',
        'PhotonMetDPhi',
        'JetMetDPhi',
        'HighMet'
    ]

    for cut in cuts:
        # print cut
        selector.findOperator(cut).setIgnoreDecision(True)

    return selector

def eleProxy(sample, selector):
    """
    Candidate-like but with inverted electron veto
    """

    selector = monophotonBase(sample, selector)

    weight = ROOT.PhotonPtWeight(eleproxyWeight, 'egfakerate')
    weight.useErrors(True) # use errors of eleproxyWeight as syst. variation
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('EVeto')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.EVeto)
    photonSel.addSelection(False, ROOT.PhotonSelection.CSafeVeto)
    photonSel.addVeto(True, ROOT.PhotonSelection.EVeto)

    return selector

def purity(sample, selector):
    """
    EM Object is baseline photon, used for efficiency and SF measurements as well.
    """

    selector = purityBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = []
    sels.append('Sieie15')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    if not sample.data:
        genPhotonSel = ROOT.GenParticleSelection("GenPhotonSelection")
        genPhotonSel.setPdgId(22)
        genPhotonSel.setMinPt(140.)
        genPhotonSel.setMaxEta(1.7)

        selector.addOperator(genPhotonSel, 1)
        photonSel.setIgnoreDecision(True)
        
        selector.findOperator('HighPtJetSelection').setIgnoreDecision(True)

    return selector

def purityNom(sample, selector):
    """
    EM Object is true photon like, but with inverted sieie and CHIso requirements.
    """

    selector = purityBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
    sels.remove('CHIsoMax')
    sels.append('Sieie15')
    sels.append('CHIsoMax11')
    # sels.append('CHIsoS16VLoose')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIsoMax)
    photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    photonSel.addVeto(True, ROOT.PhotonSelection.CHIsoMax)

    # photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIsoMaxS16)
    # photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    # photonSel.addVeto(True, ROOT.PhotonSelection.CHIsoMaxS16)

    return selector

def purityUp(sample, selector):
    """
    EM Object is true photon like, but with tightened NHIso and PhIso requirements and inverted sieie and CHIso requirements.
    """

    selector = purityBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
    sels.remove('CHIsoMax')
    sels.append('Sieie15')
    sels.append('NHIsoTight')
    sels.append('PhIsoTight')
    sels.append('CHIsoMax11')
    # sels.append('CHIsoS16VLoose')
    # sels.append('NHIsoS16Tight')
    # sels.append('PhIsoS16Tight')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIsoMax)
    photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    photonSel.addVeto(True, ROOT.PhotonSelection.CHIsoMax)

    # photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIsoMaxS16)
    # photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    # photonSel.addVeto(True, ROOT.PhotonSelection.CHIsoMaxS16)

    return selector

def purityDown(sample, selector):
    """
    EM Object is true photon like, but with inverted NHIso and PhIso requirements and loosened sieie and CHIso requirements.
    """

    selector = purityBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('NHIso')
    sels.remove('PhIso')
    sels.remove('Sieie')
    sels.remove('CHIsoMax')
    # sels.remove('NHIsoS16')
    # sels.remove('PhIsoS16')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
    sels.append('Sieie15')
    sels.append('CHIsoMax11')
    sels.append('NHIso11')
    sels.append('PhIso3')
    # sels.append('CHIsoS16VLoose')
    # sels.append('NHIsoS16VLoose')
    # sels.append('PhIsoS16VLoose')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.NHIso, ROOT.PhotonSelection.PhIso)
    photonSel.addVeto(True, ROOT.PhotonSelection.NHIso)
    photonSel.addVeto(True, ROOT.PhotonSelection.PhIso)

    # photonSel.addSelection(False, ROOT.PhotonSelection.NHIsoS16, ROOT.PhotonSelection.PhIsoS16)
    # photonSel.addVeto(True, ROOT.PhotonSelection.NHIsoS16)
    # photonSel.addVeto(True, ROOT.PhotonSelection.PhIsoS16)

    return selector

def hadProxy(sample, selector):
    """
    Candidate-like but with inverted sieie or CHIso.
    """

    if type(selector) is str:
        selector = monophotonBase(sample, selector)

    weight = ROOT.PhotonPtWeight(hadproxyWeight, 'hadProxyWeight')
    weight.setPhotonType(ROOT.PhotonPtWeight.kReco)
    weight.addVariation('purityUp', hadproxyPurityUpWeight)
    weight.addVariation('purityDown', hadproxyPurityDownWeight)
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
    sels.remove('CHIsoMax')
    sels.append('Sieie15')
    sels.append('CHIsoMax11')
    # sels.append('CHIsoS16VLoose')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIsoMax)
    photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    photonSel.addVeto(True, ROOT.PhotonSelection.CHIsoMax)

    # photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIsoMaxS16)
    # photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    # photonSel.addVeto(True, ROOT.PhotonSelection.CHIsoMaxS16)

    return selector

def hadProxyUp(sample, selector):
    """
    Candidate-like with tight NHIso and PhIso, with inverted sieie or CHIso.
    """

    selector = monophotonBase(sample, selector)

    weight = ROOT.PhotonPtWeight(hadproxyupWeight)
    weight.setPhotonType(ROOT.PhotonPtWeight.kReco)
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
    sels.remove('CHIsoMax')
    sels.append('Sieie15')
    sels.append('NHIsoTight')
    sels.append('PhIsoTight')
    sels.append('CHIsoMax11')
    # sels.append('CHIsoS16VLoose')
    # sels.append('NHIsoS16Tight')
    # sels.append('PhIsoS16Tight')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIsoMax)
    photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    photonSel.addVeto(True, ROOT.PhotonSelection.CHIsoMax)

    # photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIsoMaxS16)
    # photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    # photonSel.addVeto(True, ROOT.PhotonSelection.CHIsoMaxS16)

    return selector

def hadProxyDown(sample, selector):
    """
    Candidate-like, but with loosened sieie + CHIso and inverted NHIso or PhIso.
    """

    selector = monophotonBase(sample, selector)

    weight = ROOT.PhotonPtWeight(hadproxydownWeight)
    weight.setPhotonType(ROOT.PhotonPtWeight.kReco)
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('NHIso')
    sels.remove('PhIso')
    sels.remove('Sieie')
    sels.remove('CHIsoMax')
    # sels.remove('NHIsoS16')
    # sels.remove('PhIsoS16')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
    sels.append('Sieie15')
    sels.append('CHIsoMax11')
    sels.append('NHIso11')
    sels.append('PhIso3')
    # sels.append('CHIsoS16VLoose')
    # sels.append('NHIsoS16VLoose')
    # sels.append('PhIsoS16VLoose')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.NHIso, ROOT.PhotonSelection.PhIso)
    photonSel.addVeto(True, ROOT.PhotonSelection.NHIso)
    photonSel.addVeto(True, ROOT.PhotonSelection.PhIso)

    # photonSel.addSelection(False, ROOT.PhotonSelection.NHIsoS16, ROOT.PhotonSelection.PhIsoS16)
    # photonSel.addVeto(True, ROOT.PhotonSelection.NHIsoS16)
    # photonSel.addVeto(True, ROOT.PhotonSelection.PhIsoS16)

    return selector

def gjets(sample, selector):
    """
    Candidate-like, but with a high pT jet and inverted sieie and chIso on the photon.
    """
    
    selector = monophotonBase(sample, selector)
    
    selector.addOperator(ROOT.HighPtJetSelection())
    selector.findOperator('HighPtJetSelection').setJetPtCut(100.)

    selector.addOperator(ROOT.GenPhotonDR())
    
    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
    sels.remove('CHIsoMax')
    sels.append('Sieie15')
    sels.append('CHIsoMax11')
    # sels.append('CHIsoS16VLoose')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))
        photonSel.addVeto(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIsoMax)
    photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    photonSel.addVeto(True, ROOT.PhotonSelection.CHIsoMax)

    # photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIsoMaxS16)
    # photonSel.addVeto(True, ROOT.PhotonSelection.Sieie12)
    # photonSel.addVeto(True, ROOT.PhotonSelection.CHIsoMaxS16)
    
    return selector

def gjSmeared(sample, name):
    """
    Candidate-like, with a smeared MET distribution.
    """

    selector = candidate(sample, ROOT.SmearingSelector(name))

    smearing = ROOT.TF1('smearing', 'TMath::Landau(x, [0], [1])', 0., 40.)
    smearing.SetParameters(-0.7314, 0.5095) # measured in gjets/smearfit.py
    selector.setNSamples(1)
    selector.setFunction(smearing)

    return selector

def halo(sample, selector):
    """
    Candidate sample but with inverted MIP cut and halo tag.
    """

    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    for sel in photonFullSelection:
        if sel == 'MIP49':
            photonSel.addSelection(False, getattr(ROOT.PhotonSelection, sel))
        else:
            photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    selector.findOperator('MetFilters').setFilter(0, -1)

    return selector

def haloMIP(sample, selector):
    """
    Candidate sample but with inverted MIP cut.
    """

    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    for sel in photonFullSelection:
        if sel == 'MIP49':
            photonSel.addSelection(False, getattr(ROOT.PhotonSelection, sel))
        else:
            photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    selector.findOperator('MetFilters').setFilter(0, 0)

    return selector

def haloMET(sample, selector):
    """
    Candidate sample but with inverted MIP cut.
    """

    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('MIP49')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    selector.findOperator('MetFilters').setFilter(0, -1)

    return selector

def haloLoose(sample, selector):
    """
    Candidate sample but with inverted MIP cut and halo tag.
    """

    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.append('Sieie15')

    for sel in sels:
        if sel == 'MIP49':
            photonSel.addSelection(False, getattr(ROOT.PhotonSelection, sel))
        else:
            photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    selector.findOperator('MetFilters').setFilter(0, -1)

    return selector

def haloMIPLoose(sample, selector):
    """
    Candidate sample but with inverted MIP cut.
    """

    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.append('Sieie15')

    for sel in sels:
        if sel == 'MIP49':
            photonSel.addSelection(False, getattr(ROOT.PhotonSelection, sel))
        else:
            photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    selector.findOperator('MetFilters').setFilter(0, 0)

    return selector

def haloMETLoose(sample, selector):
    """
    Candidate sample but with inverted MIP cut.
    """

    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('MIP49')
    sels.remove('Sieie')
    sels.append('Sieie15')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    selector.findOperator('MetFilters').setFilter(0, -1)

    return selector

def haloMedium(sample, selector):
    """
    Candidate sample but with inverted MIP cut and halo tag.
    """

    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.append('Sieie12')

    for sel in sels:
        if sel == 'MIP49':
            photonSel.addSelection(False, getattr(ROOT.PhotonSelection, sel))
        else:
            photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    selector.findOperator('MetFilters').setFilter(0, -1)

    return selector

def haloMIPMedium(sample, selector):
    """
    Candidate sample but with inverted MIP cut.
    """

    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.append('Sieie12')

    for sel in sels:
        if sel == 'MIP49':
            photonSel.addSelection(False, getattr(ROOT.PhotonSelection, sel))
        else:
            photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    selector.findOperator('MetFilters').setFilter(0, 0)

    return selector

def haloMETMedium(sample, selector):
    """
    Candidate sample but with inverted MIP cut.
    """

    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('MIP49')
    sels.remove('Sieie')
    sels.append('Sieie12')

    for sel in sels:
        photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    selector.findOperator('MetFilters').setFilter(0, -1)

    return selector


def trivialShower(sample, selector):
    """
    Candidate sample but with inverted sieie cut.
    """

    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    for sel in photonFullSelection:
        if sel == 'SieieNonzero':
            photonSel.addSelection(False, getattr(ROOT.PhotonSelection, sel))
        else:
            photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    return selector

def electronBase(sample, selector):
    selector = leptonBase(sample, selector)
    selector.findOperator('LeptonRecoil').setFlavor(ROOT.kElectron)

    return selector

def muonBase(sample, selector):
    selector = leptonBase(sample, selector)
    selector.findOperator('LeptonRecoil').setFlavor(ROOT.kMuon)

    return selector

def dielectron(sample, selector):
    selector = electronBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(2, 0)

    dielMass = ROOT.Mass()
    dielMass.setPrefix('diel')
    dielMass.setMin(60.)
    dielMass.setMax(120.)
    dielMass.setCollection1(ROOT.kElectrons)
    dielMass.setCollection2(ROOT.kElectrons)
    dielMass.setIgnoreDecision(True)
    selector.addOperator(dielMass)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kElectron, 'ElectronSF')
        idsf.addFactor(electronTightSF)
        idsf.addFactor(electronLooseSF)
        idsf.setNParticles(2)
        idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.IDSFWeight.kElectron, 'GsfTrackSF')
        track.addFactor(electronTrackSF)
        track.addFactor(electronTrackSF)
        track.setNParticles(2)
        track.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)
        

    return selector

def dielectronHadProxy(sample, selector):
    selector = electronBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(2, 0)

    dielMass = ROOT.Mass()
    dielMass.setPrefix('diel')
    dielMass.setMin(60.)
    dielMass.setMax(120.)
    dielMass.setCollection1(ROOT.kElectrons)
    dielMass.setCollection2(ROOT.kElectrons)
    dielMass.setIgnoreDecision(True)
    selector.addOperator(dielMass)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kElectron, 'ElectronSF')
        idsf.addFactor(electronTightSF)
        idsf.addFactor(electronLooseSF)
        idsf.setNParticles(2)
        idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.IDSFWeight.kElectron, 'GsfTrackSF')
        track.addFactor(electronTrackSF)
        track.addFactor(electronTrackSF)
        track.setNParticles(2)
        track.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)
        
    selector = hadProxy(sample, selector)

    return selector

def monoelectron(sample, selector):
    selector = electronBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(1, 0)

    mtCut = ROOT.LeptonMt()
    mtCut.setFlavor(ROOT.kElectron)
    mtCut.setMax(160.)
    mtCut.setIgnoreDecision(True)
    selector.addOperator(mtCut)

    metCut = ROOT.HighMet('RealMetCut')
    metCut.setMetSource(ROOT.kInMet)
    metCut.setThreshold(50.)
    metCut.setIgnoreDecision(True)
    selector.addOperator(metCut)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kElectron, 'ElectronSF')
        idsf.addFactor(electronTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.IDSFWeight.kElectron, 'GsfTrackSF')
        track.addFactor(electronTrackSF)
        track.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    return selector

def monoelectronHadProxy(sample, selector):
    selector = electronBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(1, 0)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kElectron, 'ElectronSF')
        idsf.addFactor(electronTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.IDSFWeight.kElectron, 'GsfTrackSF')
        track.addFactor(electronTrackSF)
        track.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    selector = hadProxy(sample, selector)

    return selector

def dimuon(sample, selector):
    selector = muonBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(0, 2)

    dimuMass = ROOT.Mass()
    dimuMass.setPrefix('dimu')
    dimuMass.setMin(60.)
    dimuMass.setMax(120.)
    dimuMass.setCollection1(ROOT.kMuons)
    dimuMass.setCollection2(ROOT.kMuons)
    dimuMass.setIgnoreDecision(True)
    selector.addOperator(dimuMass)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kMuon, 'MuonSF')
        idsf.addFactor(muonTightSF)
        idsf.addFactor(muonLooseSF)
        idsf.setNParticles(2)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.IDSFWeight.kMuon, 'MuonTrackSF')
        track.addFactor(muonTrackSF)
        track.addFactor(muonTrackSF)
        track.setNParticles(2)
        track.setVariable(ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    return selector

def dimuonHadProxy(sample, selector):
    selector = muonBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(0, 2)

    dimuMass = ROOT.Mass()
    dimuMass.setPrefix('dimu')
    dimuMass.setMin(60.)
    dimuMass.setMax(120.)
    dimuMass.setCollection1(ROOT.kMuons)
    dimuMass.setCollection2(ROOT.kMuons)
    dimuMass.setIgnoreDecision(True)
    selector.addOperator(dimuMass)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kMuon, 'MuonSF')
        idsf.addFactor(muonTightSF)
        idsf.addFactor(muonLooseSF)
        idsf.setNParticles(2)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.IDSFWeight.kMuon, 'MuonTrackSF')
        track.addFactor(muonTrackSF)
        track.addFactor(muonTrackSF)
        track.setNParticles(2)
        track.setVariable(ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    selector = hadProxy(sample, selector)

    return selector

def monomuon(sample, selector):
    selector = muonBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(0, 1)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kMuon, 'MuonSF')
        idsf.addFactor(muonTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.IDSFWeight.kMuon, 'MuonTrackSF')
        track.addFactor(muonTrackSF)
        track.setVariable(ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    return selector

def monomuonHadProxy(sample, selector):
    selector = muonBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(0, 1)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kMuon, 'MuonSF')
        idsf.addFactor(muonTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.IDSFWeight.kMuon, 'MuonTrackSF')
        track.addFactor(muonTrackSF)
        track.setVariable(ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    selector = hadProxy(sample, selector)

    return selector

def oppflavor(sample, selector):
    selector = muonBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(1, 1)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kElectron, 'ElectronSF')
        idsf.addFactor(electronTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.IDSFWeight.kElectron, 'GsfTrackSF')
        track.addFactor(electronTrackSF)
        track.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

        ### might not be 100% correct because there is no check 
        ### that both electron and muon are tight >.>

        idsf = ROOT.IDSFWeight(ROOT.IDSFWeight.kMuon, 'MuonSF')
        idsf.addFactor(muonTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.IDSFWeight.kMuon, 'MuonTrackSF')
        track.addFactor(muonTrackSF)
        track.setVariable(ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    return selector

def wenuall(sample, name):
    """
    Candidate-like selection but for W->enu, no pixel veto on the photon.
    """

    selector = monophotonBase(sample, ROOT.WenuSelector(name))

    # selector.addOperator(ROOT.IDSFWeight(ROOT.IDSFWeight.kPhoton, photonSF, 'photonSF'))
    # selector.addOperator(ROOT.ConstantWeight(1.01, 'extraSF'))
    if 'amcatnlo' in sample.fullname or 'madgraph' in sample.fullname: # ouh la la..
        selector.addOperator(ROOT.NNPDFVariation())

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    for sel in photonFullSelection:
        if sel != 'EVeto':
            photonSel.addSelection(True, getattr(ROOT.PhotonSelection, sel))

    photonSel.setMinPt(15.)

    return selector


def zeeBase(sample, selector):
    """
    Select Z->ee events.
    """
    selector = TagAndProbeBase(sample, selector)
#    if sample.data:
#        selector.addOperator(ROOT.HLTFilter('HLT_Ele27_WPTight_Gsf'), 0)

    tnp = selector.findOperator('TagAndProbePairZ')
    tnp.setTagSpecies(ROOT.TagAndProbePairZ.kElectron)
    tnp.setProbeSpecies(ROOT.TagAndProbePairZ.kElectron)

    return selector

def zeeJets(sample, selector):
    """
    Require Z->ee plus at least one high pt jet.
    """
    selector = zeeBase(sample, selector)

    b2b = ROOT.ZJetBackToBack()
    b2b.setTagAndProbePairZ(selector.findOperator('TagAndProbePairZ'))
    b2b.setMinJetPt(100.)
    b2b.setMinDeltaPhi(3.)
    selector.addOperator(b2b)

    return selector

def zmmBase(sample, selector):
    """
    Select Z->mumu events.
    """
    selector = TagAndProbeBase(sample, selector)
#    if sample.data:
#        selector.addOperator(ROOT.HLTFilter('HLT_IsoMu20_OR_HLT_IsoTkMu20'), 0)

    tnp = selector.findOperator('TagAndProbePairZ')
    tnp.setTagSpecies(ROOT.TagAndProbePairZ.kMuon)
    tnp.setProbeSpecies(ROOT.TagAndProbePairZ.kMuon)
    
    return selector

def zmmJets(sample, selector):
    """
    Require Z->mumu plus at least one high pt jet.
    """
    selector = TagAndProbeBase(sample, selector)

    b2b = ROOT.ZJetBackToBack()
    b2b.setTagAndProbePairZ(selector.findOperator('TagAndProbePairZ'))
    b2b.setMinJetPt(100.)
    b2b.setMinDeltaPhi(3.)
    selector.addOperator(b2b)

    return selector

if needHelp:
    sys.argv.append('--help')


#####################
# SELECTOR WRAPPERS #
#####################

def kfactor(generator):
    """
    Wrapper for applying the k-factor corrections to the selector returned by the generator in the argument.
    """

    def scaled(sample, name):
        selector = generator(sample, name)

        sname = sample.name.replace('gj04', 'gj').replace('znng-d', 'znng-130').replace('wnlg-d', 'wnlg-130').replace('0-d', '0').replace('zllg', 'znng')

        qcdSource = ROOT.TFile.Open(datadir + '/kfactor.root')
        corr = qcdSource.Get(sname)

        qcd = ROOT.PhotonPtWeight(corr, 'QCDCorrection')
        qcd.setPhotonType(ROOT.PhotonPtWeight.kPostShower) # if possible
        # qcd.setPhotonType(ROOT.PhotonPtWeight.kReco) # because nero doesn't have gen info saved

        for variation in ['renUp', 'renDown', 'facUp', 'facDown', 'scaleUp', 'scaleDown']:
            vcorr = qcdSource.Get(sname + '_' + variation)
            if vcorr:
                # print 'applying qcd var', variation, sample.name
                qcd.addVariation('qcd' + variation, vcorr)

        selector.addOperator(qcd)

        ewkSource = ROOT.TFile.Open(datadir + '/ewk_corr.root')
        corr = ewkSource.Get(sname)
        if corr:
            # print 'applying ewk', sample.name
            ewk = ROOT.PhotonPtWeight(corr, 'EWKNLOCorrection')
            ewk.setPhotonType(ROOT.PhotonPtWeight.kParton)

            for variation in ['Up', 'Down']:
                vcorr = ewkSource.Get(sname + '_' + variation)
                if vcorr:
                    # print 'applying ewk var', variation, sample.name
                    ewk.addVariation('ewk' + variation, vcorr)

            selector.addOperator(ewk)

        return selector

    return scaled

def genveto(generator):
    """
    Wrapper for vetoing gen-level photons.
    """

    def vetoed(sample, name):
        selector = generator(sample, name)

        veto = ROOT.GenPhotonVeto()

        selector.addOperator(veto, 0)

        return selector

    return vetoed

def wlnu(generator):
    """
    Wrapper for W->lnu sample to pick out non-electron decays only.
    """

    def filtered(sample, name):
        return generator(sample, ROOT.WlnuSelector(name))

    return filtered

def wglo(generator):
    """
    Wrapper for adding an LHE photon pT cut.
    """

    def truncated(sample, name):
        selector = generator(sample, name)

        truncator = ROOT.PhotonPtTruncator()
        truncator.setPtMax(500.)
        selector.addOperator(truncator, 0)

        return selector

    return truncated
