import sys
import os
import array
import logging

needHelp = False
for opt in ['-h', '--help']:
    if opt in sys.argv:
        needHelp = True
        sys.argv.remove(opt)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
datadir = basedir + '/data'

if basedir not in sys.path:
    sys.path.append(basedir)

import config

logger = logging.getLogger(__name__)
logger.setLevel(config.printLevel)

import ROOT

ROOT.gSystem.Load(config.libobjs)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats)

ROOT.gROOT.LoadMacro(thisdir + '/operators.cc+')
ROOT.gROOT.LoadMacro(thisdir + '/selectors.cc+')

photonFullSelection = [
    'HOverE',
    'Sieie',
    'NHIso',
    'PhIso',
    'CHIsoMax',
    # 'CHIsoMaxS16',
    # 'CHIsoS16',
    # 'NHIsoS16',
    # 'PhIsoS16',
    'EVeto',
    'MIP49',
    'Time',
    'SieieNonzero',
    'SipipNonzero',
    'NoisyRegion',
    # 'E2E995',
]

# MEDIUM ID
photonWP = 1

# LOOSE ID
# photonWP = 0

# PU reweight
puWeights = []
f = ROOT.TFile.Open(datadir + '/pileup.root')
for k in f.GetListOfKeys():
    if k.GetName().startswith('puweight_'):
        ROOT.gROOT.cd()
        logger.debug('Loading PU weights %s', k.GetName())
        puWeights.append((k.GetName().replace('puweight_', ''), k.ReadObj().Clone()))

f.Close()

def addPUWeight(sample, selector):
    for name, hist in puWeights:
        if name in sample.fullname:
            logger.debug('Using PU weights %s for %s', name, sample.name)
            selector.addOperator(ROOT.PUWeight(hist))
            break
    else:
        raise RuntimeError('Pileup profile for ' + sample.name + ' not defined')

# Other weights
def getFromFile(path, name, newname = ''):
    if newname == '':
        newname = name

    f = ROOT.TFile.Open(path)
    ROOT.gROOT.cd()
    obj = f.Get(name).Clone(newname)
    f.Close()

    logger.debug('Picked up %s from %s', name, path)

    return obj

photonSF = getFromFile(datadir + '/photon_id_sf16.root', 'EGamma_SF2D', 'photonSF')

hadproxyWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactNom')
hadproxyTightWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactTight')
hadproxyLooseWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactLoose')
hadproxyVLooseWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactVLoose')
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

gjSmearParams = {}
gjSmearParamsFile = file(datadir + '/gjSmearParams_linear.txt', 'r')
for line in gjSmearParamsFile:
    param = line.split()
    gjSmearParams[param[0]] = (param[1], param[2])
gjSmearParamsFile.close()

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
    # else:
    #     operators.append('EGCorrection')
        
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
        metVar.setPhotonSelection(selector.findOperator('PhotonSelection'))

        photonDPhi = selector.findOperator('PhotonMetDPhi')
        photonDPhi.setMetVariations(metVar)
        
        jetDPhi = selector.findOperator('JetMetDPhi')
        jetDPhi.setMetVariations(metVar)

        selector.findOperator('PhotonJetDPhi').setMetVariations(metVar)

        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw, 'crosssection'))

        addPUWeight(sample, selector)

    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('BjetVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.cTaus, False)
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
        'HighPtJetSelection',
        'CopyMet'
    ]

    # if sample.data:
    #     operators.append('EGCorrection')

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

        addPUWeight(sample, selector)

    selector.findOperator('PhotonSelection').setMinPt(100.)
    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('BjetVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.cTaus, False)
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
        'CopyMet',
    ]

    # if sample.data:
    #     operators.append('EGCorrection')

    operators += [
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

        addPUWeight(sample, selector)

        idsf = ROOT.IDSFWeight(ROOT.cPhotons, 'photonSF')
        idsf.addFactor(photonSF)
        idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)
        # selector.addOperator(ROOT.ConstantWeight(1.01, 'extraSF'))
        if 'amcatnlo' in sample.fullname or 'madgraph' in sample.fullname: # ouh la la..
            selector.addOperator(ROOT.NNPDFVariation())

    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('BjetVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.cTaus, False)
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
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.cTaus, False)

    return selector

def zmumu(sample, name):
    """
    Just dimuon. 
    """

    selector = ROOT.EventSelector(name)
    selector.setCanPhotonSkim(False)

    selector.addOperator(ROOT.MetFilters())

    leptons = ROOT.LeptonSelection()
    leptons.setN(0, 2)
    leptons.setStrictMu(False)
    leptons.setRequireTight(False)
    selector.addOperator(leptons)

    mass = ROOT.Mass()
    mass.setPrefix('dimu')
    mass.setMin(60.)
    mass.setMax(120.)
    mass.setCollection1(ROOT.cMuons)
    mass.setCollection2(ROOT.cMuons)
    selector.addOperator(mass)

    if not sample.data:
        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw, 'crosssection'))

        addPUWeight(sample, selector)

        if 'amcatnlo' in sample.fullname or 'madgraph' in sample.fullname: # ouh la la..
            selector.addOperator(ROOT.NNPDFVariation())

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
    ]

    # if sample.data:
    #     operators.append('EGCorrection')

    operators += [ 
        'JetMetDPhi',
        'HighMet'
    ]
    
    for op in operators:
        selector.addOperator(getattr(ROOT, op)())

    if not sample.data:
        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw))

        addPUWeight(sample, selector)

    selector.findOperator('MuonVeto').setIgnoreDecision(True)
    selector.findOperator('ElectronVeto').setIgnoreDecision(True)
    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('BjetVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.cTaus, False)
    # selector.findOperator('JetCleaning').setCleanAgainst(ROOT.cElectrons, False)
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
        idsf = ROOT.IDSFWeight(ROOT.cPhotons, 'photonSF')
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

    selector.findOperator('PhotonSelection').setMinPt(30.)
    
    dimuMass = ROOT.Mass()
    dimuMass.setPrefix('dimu')
    dimuMass.setMin(60.)
    dimuMass.setMax(120.)
    dimuMass.setCollection1(ROOT.cMuons)
    dimuMass.setCollection2(ROOT.cMuons)
    dimuMass.setIgnoreDecision(True)
    selector.addOperator(dimuMass)

    dielMass = ROOT.Mass()
    dielMass.setPrefix('diel')
    dielMass.setMin(60.)
    dielMass.setMax(120.)
    dielMass.setCollection1(ROOT.cElectrons)
    dielMass.setCollection2(ROOT.cElectrons)
    dielMass.setIgnoreDecision(True)
    selector.addOperator(dielMass)

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

        # GenParticles not being filled currently
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

def purityTight(sample, selector):
    """
    EM Object is true photon like, but with tightened NHIso and PhIso requirements and inverted sieie and CHIso requirements.
    """

    selector = purityBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.remove('CHIsoMax')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
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

def purityLoose(sample, selector):
    """
    EM Object is true photon like, but with loosened NHIso and PhIso requirements and inverted sieie and CHIso requirements.
    """

    selector = purityBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.remove('NHIso')
    sels.remove('PhIso')
    sels.remove('CHIsoMax')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
    # sels.remove('NHIsoS16')
    # sels.remove('PhIsoS16')
    sels.append('Sieie15')
    sels.append('NHIsoLoose')
    sels.append('PhIsoLoose')
    sels.append('CHIsoMax11')
    # sels.append('CHIsoS16VLoose')
    # sels.append('NHIsoS16Loose')
    # sels.append('PhIsoS16Loose')

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

def hadProxyTight(sample, selector):
    """
    Candidate-like with tight NHIso and PhIso, with inverted sieie or CHIso.
    """

    selector = monophotonBase(sample, selector)

    weight = ROOT.PhotonPtWeight(hadproxyTightWeight)
    weight.setPhotonType(ROOT.PhotonPtWeight.kReco)
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.remove('CHIsoMax')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
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

def hadProxyLoose(sample, selector):
    """
    Candidate-like with Loose NHIso and PhIso, with inverted sieie or CHIso.
    """

    selector = monophotonBase(sample, selector)

    weight = ROOT.PhotonPtWeight(hadproxyLooseWeight)
    weight.setPhotonType(ROOT.PhotonPtWeight.kReco)
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    sels = list(photonFullSelection)
    sels.remove('Sieie')
    sels.remove('NHIso')
    sels.remove('PhIso')
    sels.remove('CHIsoMax')
    # sels.remove('CHIsoMaxS16')
    # sels.remove('CHIsoS16')
    sels.append('Sieie15')
    sels.append('NHIsoLoose')
    sels.append('PhIsoLoose')
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

    smearing = ROOT.TF1('smearing', 'TMath::Landau(x, [0], [1]*(1. + [2]*x))', 0., 100.)
    mean = gjSmearParams['mean'][0]
    sigmar = gjSmearParams['sigmar'][0]
    alpha = gjSmearParams['alpha'][0]
    smearing.SetParameters(mean, sigmar, alpha) # measured in gjets/smearfit.py
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

def haloNoShowerCut(sample, selector):
    selector = monophotonBase(sample, selector)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.resetSelection()
    photonSel.resetVeto()

    for sel in photonFullSelection:
        if sel == 'MIP49':
            photonSel.addSelection(False, getattr(ROOT.PhotonSelection, sel))
        elif sel == 'Sieie':
            continue
        else:
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
    selector.findOperator('LeptonRecoil').setFlavor(ROOT.lElectron)

    return selector

def muonBase(sample, selector):
    selector = leptonBase(sample, selector)
    selector.findOperator('LeptonRecoil').setFlavor(ROOT.lMuon)

    return selector

def dielectron(sample, selector):
    selector = electronBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(2, 0)
    # selector.findOperator('LeptonSelection').setStrictEl(False)

    dielMass = ROOT.Mass()
    dielMass.setPrefix('diel')
    dielMass.setMin(60.)
    dielMass.setMax(120.)
    dielMass.setCollection1(ROOT.cElectrons)
    dielMass.setCollection2(ROOT.cElectrons)
    dielMass.setIgnoreDecision(True)
    selector.addOperator(dielMass)

    dielSign = ROOT.OppositeSign()
    dielSign.setPrefix('diel')
    dielSign.setCollection1(ROOT.cElectrons)
    dielSign.setCollection2(ROOT.cElectrons)
    dielSign.setIgnoreDecision(True)
    selector.addOperator(dielSign)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.cElectrons, 'ElectronSF')
        idsf.addFactor(electronTightSF)
        idsf.addFactor(electronLooseSF)
        idsf.setNParticles(2)
        idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.cElectrons, 'GsfTrackSF')
        track.addFactor(electronTrackSF)
        track.addFactor(electronTrackSF)
        track.setNParticles(2)
        track.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)
        

    return selector

def dielectronHadProxy(sample, selector):
    selector = electronBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(2, 0)
    # selector.findOperator('LeptonSelection').setStrictEl(False)

    dielMass = ROOT.Mass()
    dielMass.setPrefix('diel')
    dielMass.setMin(60.)
    dielMass.setMax(120.)
    dielMass.setCollection1(ROOT.cElectrons)
    dielMass.setCollection2(ROOT.cElectrons)
    dielMass.setIgnoreDecision(True)
    selector.addOperator(dielMass)

    dielSign = ROOT.OppositeSign()
    dielSign.setPrefix('diel')
    dielSign.setCollection1(ROOT.cElectrons)
    dielSign.setCollection2(ROOT.cElectrons)
    dielSign.setIgnoreDecision(True)
    selector.addOperator(dielSign)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.cElectrons, 'ElectronSF')
        idsf.addFactor(electronTightSF)
        idsf.addFactor(electronLooseSF)
        idsf.setNParticles(2)
        idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.cElectrons, 'GsfTrackSF')
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
    mtCut.setFlavor(ROOT.lElectron)
    mtCut.setMax(160.)
    mtCut.setIgnoreDecision(True)
    selector.addOperator(mtCut)

    metCut = ROOT.HighMet('RealMetCut')
    metCut.setMetSource(ROOT.kInMet)
    metCut.setThreshold(50.)
    metCut.setIgnoreDecision(True)
    selector.addOperator(metCut)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.cElectrons, 'ElectronSF')
        idsf.addFactor(electronTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.cElectrons, 'GsfTrackSF')
        track.addFactor(electronTrackSF)
        track.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    return selector

def monoelectronHadProxy(sample, selector):
    selector = electronBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(1, 0)

    mtCut = ROOT.LeptonMt()
    mtCut.setFlavor(ROOT.lElectron)
    mtCut.setMax(160.)
    mtCut.setIgnoreDecision(True)
    selector.addOperator(mtCut)

    metCut = ROOT.HighMet('RealMetCut')
    metCut.setMetSource(ROOT.kInMet)
    metCut.setThreshold(50.)
    metCut.setIgnoreDecision(True)
    selector.addOperator(metCut)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.cElectrons, 'ElectronSF')
        idsf.addFactor(electronTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.cElectrons, 'GsfTrackSF')
        track.addFactor(electronTrackSF)
        track.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    selector = hadProxy(sample, selector)

    return selector

def dimuon(sample, selector):
    selector = muonBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(0, 2)
    # selector.findOperator('LeptonSelection').setStrictMu(False)

    dimuMass = ROOT.Mass()
    dimuMass.setPrefix('dimu')
    dimuMass.setMin(60.)
    dimuMass.setMax(120.)
    dimuMass.setCollection1(ROOT.cMuons)
    dimuMass.setCollection2(ROOT.cMuons)
    dimuMass.setIgnoreDecision(True)
    selector.addOperator(dimuMass)

    dimuSign = ROOT.OppositeSign()
    dimuSign.setPrefix('dimu')
    dimuSign.setCollection1(ROOT.cMuons)
    dimuSign.setCollection2(ROOT.cMuons)
    dimuSign.setIgnoreDecision(True)
    selector.addOperator(dimuSign)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.cMuons, 'MuonSF')
        idsf.addFactor(muonTightSF)
        idsf.addFactor(muonLooseSF)
        idsf.setNParticles(2)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.cMuons, 'MuonTrackSF')
        track.addFactor(muonTrackSF)
        track.addFactor(muonTrackSF)
        track.setNParticles(2)
        track.setVariable(ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    return selector

def dimuonAllPhoton(sample, selector):
    selector = dimuon(sample, selector)

    muons = selector.findOperator('LeptonSelection')
    muons.setStrictMu(False)
    muons.setRequireTight(False)

    photons = selector.findOperator('PhotonSelection')
    photons.resetSelection()
    photons.addSelection(True, ROOT.PhotonSelection.HOverE)

    return selector

def dimuonHadProxy(sample, selector):
    selector = muonBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(0, 2)
    # selector.findOperator('LeptonSelection').setStrictMu(False)

    dimuMass = ROOT.Mass()
    dimuMass.setPrefix('dimu')
    dimuMass.setMin(60.)
    dimuMass.setMax(120.)
    dimuMass.setCollection1(ROOT.cMuons)
    dimuMass.setCollection2(ROOT.cMuons)
    dimuMass.setIgnoreDecision(True)
    selector.addOperator(dimuMass)

    dimuSign = ROOT.OppositeSign()
    dimuSign.setPrefix('dimu')
    dimuSign.setCollection1(ROOT.cMuons)
    dimuSign.setCollection2(ROOT.cMuons)
    dimuSign.setIgnoreDecision(True)
    selector.addOperator(dimuSign)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.cMuons, 'MuonSF')
        idsf.addFactor(muonTightSF)
        idsf.addFactor(muonLooseSF)
        idsf.setNParticles(2)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.cMuons, 'MuonTrackSF')
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

    mtCut = ROOT.LeptonMt()
    mtCut.setFlavor(ROOT.lMuon)
    mtCut.setMax(160.)
    mtCut.setIgnoreDecision(True)
    selector.addOperator(mtCut)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.cMuons, 'MuonSF')
        idsf.addFactor(muonTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.cMuons, 'MuonTrackSF')
        track.addFactor(muonTrackSF)
        track.setVariable(ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    return selector

def monomuonHadProxy(sample, selector):
    selector = muonBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(0, 1)

    mtCut = ROOT.LeptonMt()
    mtCut.setFlavor(ROOT.lMuon)
    mtCut.setMax(160.)
    mtCut.setIgnoreDecision(True)
    selector.addOperator(mtCut)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.cMuons, 'MuonSF')
        idsf.addFactor(muonTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.cMuons, 'MuonTrackSF')
        track.addFactor(muonTrackSF)
        track.setVariable(ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    selector = hadProxy(sample, selector)

    return selector

def oppflavor(sample, selector):
    selector = muonBase(sample, selector)
    selector.findOperator('LeptonSelection').setN(1, 1)

    if not sample.data:
        idsf = ROOT.IDSFWeight(ROOT.cElectrons, 'ElectronSF')
        idsf.addFactor(electronTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.cElectrons, 'GsfTrackSF')
        track.addFactor(electronTrackSF)
        track.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

        ### might not be 100% correct because there is no check 
        ### that both electron and muon are tight >.>

        idsf = ROOT.IDSFWeight(ROOT.cMuons, 'MuonSF')
        idsf.addFactor(muonTightSF)
        idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
        selector.addOperator(idsf)

        track = ROOT.IDSFWeight(ROOT.cMuons, 'MuonTrackSF')
        track.addFactor(muonTrackSF)
        track.setVariable(ROOT.IDSFWeight.kNpv)
        selector.addOperator(track)

    return selector

def wenuall(sample, name):
    """
    Candidate-like selection but for W->enu, no pixel veto on the photon.
    """

    selector = monophotonBase(sample, ROOT.WenuSelector(name))

    # selector.addOperator(ROOT.IDSFWeight(ROOT.cPhotons, photonSF, 'photonSF'))
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
    if sample.data:
        selector.addOperator(ROOT.HLTFilter('HLT_Ele27_WPTight_Gsf'), 0)

    tnp = selector.findOperator('TagAndProbePairZ')
    tnp.setTagSpecies(ROOT.cElectrons)
    tnp.setProbeSpecies(ROOT.cElectrons)

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
    if sample.data:
        selector.addOperator(ROOT.HLTFilter('HLT_IsoMu20_OR_HLT_IsoTkMu20'), 0)

    tnp = selector.findOperator('TagAndProbePairZ')
    tnp.setTagSpecies(ROOT.cMuons)
    tnp.setProbeSpecies(ROOT.cMuons)
    
    return selector

def zmmJets(sample, selector):
    """
    Require Z->mumu plus at least one high pt jet.
    """
    selector = zmmBase(sample, selector)

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

        sname = sample.name.replace('gj04', 'gj').replace('zllg', 'znng').replace('wglo', 'wnlg').replace('-o', '')

        qcdSource = ROOT.TFile.Open(datadir + '/kfactor.root')
        corr = qcdSource.Get(sname)

        qcd = ROOT.PhotonPtWeight(corr, 'QCDCorrection')
        qcd.setPhotonType(ROOT.PhotonPtWeight.kPostShower) # if possible

        for variation in ['renUp', 'renDown', 'facUp', 'facDown', 'scaleUp', 'scaleDown']:
            vcorr = qcdSource.Get(sname + '_' + variation)
            if vcorr:
                logger.debug('applying qcd var %s %s', variation, sample.name)
                qcd.addVariation('qcd' + variation, vcorr)

        # temporarily don't apply QCD k-factor until we redrive for nlo samples
        if not sample.name in ['znng', 'znng-130', 'zllg', 'zllg-130', 'wnlg', 'wnlg-130', 'wnlg-500']:
            selector.addOperator(qcd)

        ewkSource = ROOT.TFile.Open(datadir + '/ewk_corr.root')
        corr = ewkSource.Get(sname)
        if corr:
            logger.debug('applying ewk %s', sample.name)
            ewk = ROOT.PhotonPtWeight(corr, 'EWKNLOCorrection')
            ewk.setPhotonType(ROOT.PhotonPtWeight.kParton)

            for variation in ['Up', 'Down']:
                vcorr = ewkSource.Get(sname + '_' + variation)
                if vcorr:
                    logger.debug('applying ewk var %s %s', variation, sample.name)
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

def dph(generator):
    """
    Wrapper for diphoton samples to turn them into photon+dark photon samples by 'removing' one of the photons and adding it to the MET.
    """

    def invisible(sample, name):
        selector = generator(sample, name)
        
        recoil = ROOT.PhotonRecoil()
        selector.addOperator(recoil)

        return selector

    return invisible

def tagprobeBase(sample, selector):
    """
    Base for selectors skimming tag & probe input trees.
    """

    if type(selector) is str: # this is a name for the selector
        selector = ROOT.TagAndProbeSelector(selector)

    if sample.data:
        selector.addOperator(ROOT.HLTFilter('HLT_Photon165_HE10'))
    else:
        addPUWeight(sample, selector)

    return selector

def tpeg(sample, selector):
    """
    Electron + photon tag & probe.
    """

    selector = tagprobeBase(sample, selector)
    selector.addOperator(ROOT.TPElectronPhoton())

    return selector

def tpmg(sample, selector):
    """
    Muon + photon tag & probe.
    """

    selector = tagprobeBase(sample, selector)
    selector.addOperator(ROOT.TPMuonPhoton())

    return selector

def tpmmg(sample, selector):
    """
    Dimuon + photon tag & probe.
    """

    selector = tagprobeBase(sample, selector)
    operator = ROOT.TPMuonPhoton()
    operator.setMode(ROOT.TPMuonPhoton.kDouble)
    selector.addOperator(operator)

    return selector
