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

import ROOT

ROOT.gSystem.Load(config.libobjs)
ROOT.gSystem.Load('libfastjet.so')

# if the objects library is compiled with CLING dictionaries, ROOT must load the
# full library first before compiling the macros.
try:
    e = ROOT.panda.Event
except AttributeError:
    pass

ROOT.gROOT.LoadMacro(thisdir + '/operators.cc+')
try:
    o = ROOT.Operator
except:
    logger.error("Couldn't compile operators.cc. Quitting.")
    sys.exit(1)

ROOT.gROOT.LoadMacro(thisdir + '/selectors.cc+')
try:
    o = ROOT.EventSelectorBase
except:
    logger.error("Couldn't compile selectors.cc. Quitting.")
    sys.exit(1)

# MEDIUM ID
photonWP = 1

photonFullSelection = [
    'HOverE',
    'Sieie',
    'NHIso',
    'PhIso',
    'CHIso',
    'EVeto',
    'MIP49',
    'Time',
    'SieieNonzero',
    'SipipNonzero',
    'NoisyRegion'
]

def setupPhotonSelection(operator, veto = False, changes = []):
    ##### !!!!! IMPORTANT - NOTE THE RESETS #####
    if veto:
        operator.resetVeto()
    else:
        operator.resetSelection()


    sels = list(photonFullSelection)

    for change in changes:
        if change.startswith('-'):
            sels.remove(change[1:])
        elif change.startswith('+'):
            sels.append(change[1:])
        elif change.startswith('!'):
            try:
                sels.remove(change[1:])
            except:
                pass

            sels.append(change)

    if veto:
        for sel in sels:
            if sel.startswith('!'):
                operator.addVeto(False, getattr(ROOT.PhotonSelection, sel[1:]))
            else:
                operator.addVeto(True, getattr(ROOT.PhotonSelection, sel))
    else:
        for sel in sels:
            if sel.startswith('!'):
                operator.addSelection(False, getattr(ROOT.PhotonSelection, sel[1:]))
            else:
                operator.addSelection(True, getattr(ROOT.PhotonSelection, sel))
    

# avoid auto-deletion by python
_garbage = []

# Other weights
def getFromFile(path, name, newname = ''):
    if newname == '':
        newname = name

    obj = ROOT.gROOT.Get(newname)
    if obj:
        return obj

    f = ROOT.TFile.Open(path)
    orig = f.Get(name)
    if not orig:
        return None

    ROOT.gROOT.cd()
    obj = orig.Clone(newname)

    f.Close()

    logger.debug('Picked up %s from %s', name, path)
    
    _garbage.append(obj)

    return obj

##################
# BASE SELECTORS #
##################

def monophotonBase(sample, rname, selcls = None):
    """
    Monophoton candidate-like selection (high-pT photon, lepton veto, dphi(photon, MET) and dphi(jet, MET)).
    Base for other selectors.
    """

    if selcls is None:
        selector = ROOT.EventSelector(rname)
    else:
        selector = selcls(rname)

    if sample.data:
        selector.addOperator(ROOT.HLTFilter('HLT_Photon165_HE10'))

    operators = [
        'MetFilters',
        'PhotonSelection',
        'MuonVeto',
        'ElectronVeto',
        'TauVeto',
        'JetCleaning',
        'BjetVeto',
        'CopyMet',
        'CopySuperClusters'
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
    photonSel.setMinPt(175.)
    photonSel.setWP(photonWP)

    if not sample.data:
        metVar = selector.findOperator('MetVariations')
        metVar.setPhotonSelection(photonSel)

        photonDPhi = selector.findOperator('PhotonMetDPhi')
        photonDPhi.setMetVariations(metVar)
        
        jetDPhi = selector.findOperator('JetMetDPhi')
        jetDPhi.setMetVariations(metVar)

        selector.findOperator('PhotonJetDPhi').setMetVariations(metVar)

        selector.addOperator(ROOT.ConstantWeight(sample.crosssection / sample.sumw, 'crosssection'))

        addPUWeight(sample, selector)
        addPDFVariation(sample, selector)

    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('BjetVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.cTaus, False)
    selector.findOperator('PhotonMetDPhi').setIgnoreDecision(True)
    selector.findOperator('JetMetDPhi').setIgnoreDecision(True)
    selector.findOperator('HighMet').setIgnoreDecision(True)

    return selector

def emjetBase(sample, rname):
    """
    Base selector for EM+Jet control region. For MC, a gen-level photon is required.
    """

    selector = monophotonBase(sample, rname)

    selector.removeOperator('HighMet')
    selector.removeOperator('PhotonMt')

    jets = ROOT.HighPtJetSelection()
    jets.setJetPtCut(100.)
    selector.addOperator(jets)

    if not sample.data:
        genPhotonSel = ROOT.GenParticleSelection("GenPhotonSelection")
        genPhotonSel.setPdgId(22)
        genPhotonSel.setMinPt(140.)
        genPhotonSel.setMaxEta(1.7)

        selector.addOperator(genPhotonSel, 1)

    return selector

def leptonBase(sample, rname, flavor):
    """
    Base for n-lepton + photon selection
    """

    if sample.data:
        selector = ROOT.EventSelector(rname)
        selector.addOperator(ROOT.HLTFilter('HLT_Photon165_HE10'))
    else:
        selector = ROOT.PartonSelector(rname)
        if flavor == ROOT.lElectron:
            selector.setAcceptedPdgId(11)
        elif flavor == ROOT.lMuon:
            selector.setAcceptedPdgId(13)

    operators = [
        'MetFilters',
        'PhotonSelection',
        'LeptonSelection',
        'TauVeto',
        'JetCleaning',
        'BjetVeto',
        'CopyMet',
        'CopySuperClusters',
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

    setupPhotonSelection(photonSel)

    selector.findOperator('LeptonRecoil').setFlavor(flavor)

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
        addIDSFWeight(sample, selector)
        addPDFVariation(sample, selector)

        if flavor == ROOT.lElectron:
            addElectronIDSFWeight(sample, selector)
        else:
            addMuonIDSFWeight(sample, selector)

    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('BjetVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.cTaus, False)
    selector.findOperator('PhotonMetDPhi').setIgnoreDecision(True)
    selector.findOperator('JetMetDPhi').setIgnoreDecision(True)
    selector.findOperator('HighMet').setIgnoreDecision(True)

    return selector

def eefake(sample, rname):
    selector = ROOT.ZeeEventSelector(rname)

    eeSel = selector.findOperator('EEPairSelection')
    eeSel.setMinPt(140.)

    setupPhotonSelection(eeSel, changes = ['!EVeto'])

    selector.findOperator('TauVeto').setIgnoreDecision(True)
    selector.findOperator('JetCleaning').setCleanAgainst(ROOT.cTaus, False)

    return selector

def zmumu(sample, rname):
    """
    Just dimuon. 
    """

    selector = ROOT.EventSelector(rname)
    selector.setCanPhotonSkim(False)

    selector.addOperator(ROOT.MetFilters())

    leptons = ROOT.LeptonSelection()
    leptons.setN(0, 2)
    leptons.setStrictMu(False)
    leptons.setRequireTight(False)
    selector.addOperator(leptons)

    vtx = ROOT.LeptonVertex()
    vtx.setSpecies(ROOT.lMuon)
    selector.addOperator(vtx)

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

def TagAndProbeBase(sample, rname):
    """
    Base for Z->ll tag and probe stuff.
    """

    selector = ROOT.EventSelector(rname)

    operators = [
        'MetFilters',
        'MuonVeto',
        'ElectronVeto',
        'TauVeto',
        'TagAndProbePairZ',
        'JetCleaning',
        'BjetVeto',
        'CopyMet',
        'CopySuperClusters',
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

def tagprobeBase(sample, rname):
    """
    Base for selectors skimming tag & probe input trees.
    """

    selector = ROOT.TagAndProbeSelector(rname)

    if sample.name.startswith('sph'):
        selector.addOperator(ROOT.HLTFilter('HLT_Photon165_HE10'))
    elif sample.name.startswith('sel'):
        selector.addOperator(ROOT.HLTFilter('HLT_Ele27_WPTight_Gsf'))
    elif sample.name.startswith('smu'):
        selector.addOperator(ROOT.HLTFilter('HLT_IsoMu24_OR_HLT_IsoTkMu24'))

    if not sample.data:
        addPUWeight(sample, selector)

    return selector

#####################
# DERIVED SELECTORS #
#####################

def monoph(sample, rname):
    """
    Full monophoton selection.
    """

    selector = monophotonBase(sample, rname)

    setupPhotonSelection(selector.findOperator('PhotonSelection'))

    if not sample.data:
        addIDSFWeight(sample, selector)

    return selector

def monophNoE(sample, rname):
    """
    Full monophoton selection filtering out electron events.
    """

    selector = monophotonBase(sample, rname, selcls = ROOT.PartonSelector)
    selector.setRejectedPdgId(11)

    setupPhotonSelection(selector.findOperator('PhotonSelection'))

    addIDSFWeight(sample, selector)

    return selector

def monophNoLVeto(sample, rname):
    """
    Full monophoton selection without lepton veto (for lepton veto eff. scale factor measurement)
    """

    selector = monoph(sample, rname)

    selector.findOperator('ElectronVeto').setIgnoreDecision(True)
    selector.findOperator('MuonVeto').setIgnoreDecision(True)

    return selector

def signalRaw(sample, rname):
    """
    Ignore decisions of all cuts to compare shapes for different simulations.
    """

    selector = monoph(sample, rname)

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

def efake(sample, rname):
    """
    Candidate-like but with inverted electron veto
    """

    selector = monophotonBase(sample, rname)

    weight = ROOT.PhotonPtWeight(getFromFile(datadir + '/efake_data_ptalt.root', 'frate'), 'egfakerate')
    weight.useErrors(True) # use errors of eleproxyWeight as syst. variation
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')

    setupPhotonSelection(photonSel, changes = ['-EVeto', '!CSafeVeto'])
    setupPhotonSelection(photonSel, veto = True)

    return selector

def emjet(sample, rname):
    """
    EM Object is candidate-like. used for photon purity measurement and hadronTFactor derivation.
    """

    selector = emjetBase(sample, rname)

    if not sample.data:
        # measure the parton-level dR between gamma and q/g.
        selector.addOperator(ROOT.GJetsDR())

    photonSel = selector.findOperator('PhotonSelection')
    
    setupPhotonSelection(photonSel, changes = ['-Sieie', '+Sieie15', '-CHIso', '-NHIso', '+NHIsoLoose', '-PhIso', '+PhIsoLoose', '-EVeto'])
        
    return selector

def hfake(sample, rname):
    """
    Candidate-like but with inverted CHIso.
    """

    selector = monophotonBase(sample, rname)

    hadproxyTightWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactTight')
    hadproxyLooseWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactLoose')
    hadproxyPurityUpWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactNomPurityUp')
    hadproxyPurityDownWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactNomPurityDown')

#    modHfake(selector)

#    weight = selector.findOperator('hadProxyWeight')
#
#    weight.addVariation('proxyDefUp', hadproxyTightWeight)
#    weight.addVariation('proxyDefDown', hadproxyLooseWeight)
#    weight.addVariation('purityUp', hadproxyPurityUpWeight)
#    weight.addVariation('purityDown', hadproxyPurityDownWeight)

    isoTFactor = getFromFile(datadir + '/hadronTFactor.root', 'tfactNom')
    noIsoTFactor = getFromFile(datadir + '/hadronTFactorNoICH.root', 'tfactNom')
    isoVertexScore = getFromFile(datadir + '/vertex_scores.root', 'iso')
    noIsoVertexScore = getFromFile(datadir + '/vertex_scores.root', 'noIso')
    rcProb = getFromFile(datadir + '/randomcone.root', 'chIso')

    vtxWeight = ROOT.VtxAdjustedJetProxyWeight(isoTFactor, isoVertexScore, noIsoTFactor, noIsoVertexScore)

    vtxWeight.setRCProb(rcProb, 1.163)
    vtxWeight.addVariation('proxyDefUp', hadproxyTightWeight)
    vtxWeight.addVariation('proxyDefDown', hadproxyLooseWeight)
    vtxWeight.addVariation('purityUp', hadproxyPurityUpWeight)
    vtxWeight.addVariation('purityDown', hadproxyPurityDownWeight)

    selector.addOperator(vtxWeight)

    # CHIso is already inverted in modHfake
    photonSel = selector.findOperator('PhotonSelection')

#   modHfake
#    setupPhotonSelection(photonSel, changes = ['!CHIso', '+CHIso11'])
#    setupPhotonSelection(photonSel, veto = True)

    # Need to keep the cuts looser than nominal to accommodate proxyDefUp & Down
    # Proper cut applied at plotconfig as variations
    setupPhotonSelection(photonSel, changes = ['!CHIso', '+CHIso11', '-NHIso', '+NHIsoLoose', '-PhIso', '+PhIsoLoose'])
    setupPhotonSelection(photonSel, veto = True)

    return selector

def gjets(sample, rname):
    """
    For GJets MC study. 
    """
    
    selector = emjetBase(sample, rname)

    # measure the parton-level dR between gamma and q/g.
    selector.addOperator(ROOT.GJetsDR())

    photonSel = selector.findOperator('PhotonSelection')

    setupPhotonSelection(photonSel, changes = ['-Sieie', '-CHIso', '+Sieie15', '+CHIso11'])
    photonSel.addSelection(False, ROOT.PhotonSelection.Sieie12, ROOT.PhotonSelection.CHIso)
    setupPhotonSelection(photonSel, veto = True)
    
    return selector

def gjSmeared(sample, rname):
    """
    Candidate-like, with a smeared MET distribution.
    """

    selector = monophotonBase(sample, rname, selcls = ROOT.SmearingSelector)

    params = {}
    paramsFile = file(datadir + '/gjSmearParams_linear.txt', 'r')
    for line in paramsFile:
        param = line.split()
        params[param[0]] = (param[1], param[2])
    paramsFile.close()

    smearing = ROOT.TF1('smearing', 'TMath::Landau(x, [0], [1]*(1. + [2]*x))', 0., 100.)
    mean = params['mean'][0]
    sigmar = params['sigmar'][0]
    alpha = params['alpha'][0]
    smearing.SetParameters(mean, sigmar, alpha) # measured in gjets/smearfit.py
    selector.setNSamples(1)
    selector.setFunction(smearing)

    setupPhotonSelection(selector.findOperator('PhotonSelection'))

    addIDSFWeight(sample, selector)

    return selector

def dijet(sample, rname):
    """
    Dijet events with no overlap removal for jet vertex score study.
    """
    
    selector = ROOT.EventSelector(rname)

    if sample.data:
        selector.addOperator(ROOT.HLTFilter('HLT_Photon165_HE10'))

    photonSel = ROOT.PhotonSelection()
    
    setupPhotonSelection(photonSel, changes = ['!Sieie'])
    setupPhotonSelection(photonSel, veto = True)

    selector.addOperator(photonSel)

    jets = ROOT.JetClustering()
    jets.setMinPt(30.)
    jets.setOverwrite(True)
    selector.addOperator(jets)

    photonSel.setIgnoreDecision(True)

#    jetSel = ROOT.HighPtJetSelection()
#    jetSel.setJetPtCut(150.)
#    jetSel.setNMin(2)
#    jetSel.setNMax(2)
#    selector.addOperator(jetSel)

    selector.addOperator(ROOT.JetScore())

    selector.addOperator(ROOT.CopyMet())

    if not sample.data:
        addPDFVariation(sample, selector)

    return selector

def halo(sample, rname):
    """
    Candidate sample but with inverted MIP cut and halo tag.
    """

    selector = monophotonBase(sample, rname)

    photonSel = selector.findOperator('PhotonSelection')

    # setting up loose to allow variations at plot level
    
    setupPhotonSelection(photonSel, changes = ['+MIP49', '-Sieie', '+Sieie15'])
    photonSel = selector.findOperator('PhotonSelection')

    selector.findOperator('MetFilters').setFilter(0, 0)

    return selector

def trivialShower(sample, rname):
    """
    Candidate sample but with inverted sieie cut.
    """

    selector = monophotonBase(sample, rname)

    photonSel = selector.findOperator('PhotonSelection')

    setupPhotonSelection(photonSel, changes = ['!SieieNonzero'])

    return selector

def diel(sample, rname):
    selector = leptonBase(sample, rname, ROOT.lElectron)
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
        electronLooseSF = getFromFile(datadir + '/egamma_electron_loose_SF_ichep.root', 'EGamma_SF2D', 'electronLooseSF') # x: sc eta, y: pt
        electronTrackSF = getFromFile(datadir + '/egamma_gsf_tracking_SF_ichep.root', 'EGamma_SF2D', 'electronTrackSF') # x: sc eta, y: npv

        idsf = selector.findOperator('ElectronSF')
        idsf.addFactor(electronLooseSF)
        idsf.setNParticles(2)

        track = selector.findOperator('GsfTrackSF')
        track.addFactor(electronTrackSF)
        track.setNParticles(2)

    return selector

def dielAllPhoton(sample, rname):
    selector = diel(sample, rname)

    vtx = ROOT.LeptonVertex()
    vtx.setSpecies(ROOT.lElectron)
    selector.addOperator(vtx)

    electrons = selector.findOperator('LeptonSelection')
    electrons.setStrictEl(True)
    electrons.setRequireTight(True)

    photons = selector.findOperator('PhotonSelection')
    photons.resetSelection()
    photons.addSelection(True, ROOT.PhotonSelection.HOverE)

    return selector

def dielHfake(sample, rname):
    selector = diel(sample, rname)
        
    modHfake(selector)

    return selector

def monoel(sample, rname):
    selector = leptonBase(sample, rname, ROOT.lElectron)
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

    return selector

def monoelHfake(sample, rname):
    selector = monoel(sample, rname)
    
    modHfake(selector)

    return selector

def dimu(sample, rname):
    selector = leptonBase(sample, rname, ROOT.lMuon)
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
        muonLooseSF = getFromFile(datadir + '/scaleFactor_muon_looseid_12p9.root', 'scaleFactor_muon_looseid_RooCMSShape') # x: abs eta, y: pt
        muonTrackSF = getFromFile(datadir + '/muonpog_muon_tracking_SF_ichep.root', 'htrack2') # x: npv

        idsf = selector.findOperator('MuonSF')
        idsf.addFactor(muonLooseSF)
        idsf.setNParticles(2)

        track = selector.findOperator('MuonTrackSF')
        track.addFactor(muonTrackSF)
        track.setNParticles(2)

    return selector

def dimuAllPhoton(sample, rname):
    selector = dimu(sample, rname)

    vtx = ROOT.LeptonVertex()
    vtx.setSpecies(ROOT.lMuon)
    selector.addOperator(vtx)

    muons = selector.findOperator('LeptonSelection')
    muons.setStrictMu(True)
    muons.setRequireTight(False)
    muons.setRequireMedium(True)

    photons = selector.findOperator('PhotonSelection')
    photons.resetSelection()
    photons.addSelection(True, ROOT.PhotonSelection.HOverE)

    return selector

def dimuHfake(sample, rname):
    selector = dimu(sample, rname)

    modHfake(selector)

    return selector

def monomu(sample, rname):
    selector = leptonBase(sample, rname, ROOT.lMuon)
    selector.findOperator('LeptonSelection').setN(0, 1)

    mtCut = ROOT.LeptonMt()
    mtCut.setFlavor(ROOT.lMuon)
    mtCut.setMax(160.)
    mtCut.setIgnoreDecision(True)
    selector.addOperator(mtCut)

    return selector

def monomuAllPhoton(sample, rname):
    selector = monomu(sample, rname)

    vtx = ROOT.LeptonVertex()
    vtx.setSpecies(ROOT.lMuon)
    selector.addOperator(vtx)

    muons = selector.findOperator('LeptonSelection')
    muons.setStrictMu(True)
    muons.setRequireMedium(True)

    photons = selector.findOperator('PhotonSelection')
    photons.resetSelection()
    photons.addSelection(True, ROOT.PhotonSelection.HOverE)

    return selector

def monomuHfake(sample, rname):
    selector = monomu(sample, rname)

    modHfake(selector)

    return selector

def elmu(sample, rname):
    selector = leptonBase(sample, rname, ROOT.lMuon)
    selector.findOperator('LeptonSelection').setN(1, 1)

    if not sample.data:
        addElectronIDSFWeight(sample, selector)

    return selector

def wenu(sample, rname):
    """
    Candidate-like selection but for W->enu, no pixel veto on the photon.
    """

    selector = monophotonBase(sample, rname, selcls = ROOT.PartonSelector)
    selector.setAcceptedPdgId(11)

    photonSel = selector.findOperator('PhotonSelection')
    photonSel.setMinPt(15.)
    
    setupPhotonSelection(photonSel, changes = ['-EVeto'])

    return selector

def monoelVertex(sample, rname):
    """
    Monoel-like selection with e or mu, with LeptonVertex
    """

    selector = monoel(sample, rname)

    vtx = ROOT.LeptonVertex()
    vtx.setSpecies(ROOT.lElectron)
    selector.addOperator(vtx)

    return selector

def monomuVertex(sample, rname):
    """
    Monomu-like selection with e or mu, with LeptonVertex
    """

    selector = monomu(sample, rname)

    leptons = selector.findOperator('LeptonSelection')
    leptons.setRequireTight(False)
    leptons.setRequireMedium(True)

    vtx = ROOT.LeptonVertex()
    vtx.setSpecies(ROOT.lMuon)
    selector.addOperator(vtx)

    return selector

def dielVertex(sample, rname):
    """
    Diel-like selection with e or mu, with LeptonVertex
    """

    selector = diel(sample, rname)

    vtx = ROOT.LeptonVertex()
    vtx.setSpecies(ROOT.lElectron)
    selector.addOperator(vtx)

    return selector

def dimuVertex(sample, rname):
    """
    Dimu-like selection with e or mu, with LeptonVertex
    """

    selector = dimu(sample, rname)

    leptons = selector.findOperator('LeptonSelection')
    leptons.setRequireTight(True)
#    leptons.setRequireMedium(True)

    vtx = ROOT.LeptonVertex()
    vtx.setSpecies(ROOT.lMuon)
    selector.addOperator(vtx)

    return selector

def zeeJets(sample, rname):
    """
    Require Z->ee plus at least one high pt jet.
    """

    selector = TagAndProbeBase(sample, rname)
    if sample.data:
        selector.addOperator(ROOT.HLTFilter('HLT_Ele27_WPTight_Gsf'), 0)

    tnp = selector.findOperator('TagAndProbePairZ')
    tnp.setTagSpecies(ROOT.cElectrons)
    tnp.setProbeSpecies(ROOT.cElectrons)

    b2b = ROOT.ZJetBackToBack()
    b2b.setTagAndProbePairZ(selector.findOperator('TagAndProbePairZ'))
    b2b.setMinJetPt(100.)
    b2b.setMinDeltaPhi(3.)
    selector.addOperator(b2b)

    return selector

def zmmJets(sample, rname):
    """
    Require Z->mumu plus at least one high pt jet.
    """

    selector = TagAndProbeBase(sample, rname)
    if sample.data:
        selector.addOperator(ROOT.HLTFilter('HLT_IsoMu20_OR_HLT_IsoTkMu20'), 0)

    tnp = selector.findOperator('TagAndProbePairZ')
    tnp.setTagSpecies(ROOT.cMuons)
    tnp.setProbeSpecies(ROOT.cMuons)

    b2b = ROOT.ZJetBackToBack()
    b2b.setTagAndProbePairZ(selector.findOperator('TagAndProbePairZ'))
    b2b.setMinJetPt(100.)
    b2b.setMinDeltaPhi(3.)
    selector.addOperator(b2b)

    return selector

def tpeg(sample, rname):
    """
    Electron + photon tag & probe.
    """

    selector = tagprobeBase(sample, rname)
    tp = ROOT.TPLeptonPhoton()
    tp.setFlavor(ROOT.lElectron)
    selector.addOperator(tp)

    selector.addOperator(ROOT.TPJetCleaning())

    return selector

def tpmg(sample, rname):
    """
    Muon + photon tag & probe.
    """

    selector = tagprobeBase(sample, rname)
    tp = ROOT.TPLeptonPhoton()
    tp.setFlavor(ROOT.lMuon)
    selector.addOperator(tp)

    selector.addOperator(ROOT.TPJetCleaning())

    return selector

def tpegLowPt(sample, rname):
    """
    Electron + photon tag & probe.
    """

    selector = tagprobeBase(sample, rname)
    tp = ROOT.TPLeptonPhoton()
    tp.setFlavor(ROOT.lElectron)
    tp.setMinProbePt(25.)
    tp.setMinTagPt(30.)
    tp.setTagTriggerMatch(True)

    selector.addOperator(tp)

    selector.addOperator(ROOT.TPJetCleaning())

    selector.setCanPhotonSkim(False)

    return selector

def tpmgLowPt(sample, rname):
    """
    Muon + photon tag & probe.
    """

    selector = tagprobeBase(sample, rname)
    tp = ROOT.TPLeptonPhoton()
    tp.setFlavor(ROOT.lMuon)
    tp.setMinProbePt(25.)
    tp.setMinTagPt(30.)
    tp.setTagTriggerMatch(True)

    selector.addOperator(tp)

    selector.addOperator(ROOT.TPJetCleaning())

    selector.setCanPhotonSkim(False)

    return selector

def tpmmg(sample, rname):
    """
    Dimuon + photon tag & probe.
    """

    selector = tagprobeBase(sample, rname)
    tp = ROOT.TPLeptonPhoton()
    tp.setFlavor(ROOT.lMuon)
    tp.setMinProbePt(25.)
    tp.setMinTagPt(30.)
    tp.setTagTriggerMatch(True)
    tp.setMode(ROOT.TPLeptonPhoton.kDouble)
    selector.addOperator(tp)

    # for lepton veto efficiency measurement; just write electron and muon sizes
    veto = ROOT.TPLeptonVeto()
    veto.setIgnoreDecision(True)
    selector.addOperator(veto)

    selector.addOperator(ROOT.TPJetCleaning())

    selector.setCanPhotonSkim(False)

    return selector

######################
# SELECTOR MODIFIERS #
######################

def addPUWeight(sample, selector):
    pudir = ROOT.gROOT.GetDirectory('puweights')

    if not pudir:
        pudir = ROOT.gROOT.mkdir('puweights')
        f = ROOT.TFile.Open(datadir + '/pileup.root')
        for k in f.GetListOfKeys():
            if k.GetName().startswith('puweight_'):
                logger.debug('Loading PU weights %s', k.GetName())
                pudir.cd()
                obj = k.ReadObj().Clone(k.GetName().replace('puweight_', ''))
                _garbage.append(obj)
        
        f.Close()

    for hist in pudir.GetList():
        if hist.GetName() in sample.fullname:
            logger.debug('Using PU weights %s for %s', hist.GetName(), sample.name)
            selector.addOperator(ROOT.PUWeight(hist))
            break
    else:
        raise RuntimeError('Pileup profile for ' + sample.name + ' not defined')

def addIDSFWeight(sample, selector):
    idsf = ROOT.IDSFWeight(ROOT.cPhotons, 'photonSF')
    idsf.addFactor(getFromFile(datadir + '/photon_id_sf16.root', 'EGamma_SF2D', newname = 'photonSF'))
    idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
    selector.addOperator(idsf)
    selector.addOperator(ROOT.ConstantWeight(0.991, 'extraSF'))

def addElectronIDSFWeight(sample, selector):
    electronTightSF = getFromFile(datadir + '/egamma_electron_tight_SF_ichep.root', 'EGamma_SF2D', 'electronTightSF') # x: sc eta, y: pt
    electronTrackSF = getFromFile(datadir + '/egamma_gsf_tracking_SF_ichep.root', 'EGamma_SF2D', 'electronTrackSF') # x: sc eta, y: npv

    idsf = ROOT.IDSFWeight(ROOT.cElectrons, 'ElectronSF')
    idsf.addFactor(electronTightSF)
    idsf.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kPt)
    selector.addOperator(idsf)

    track = ROOT.IDSFWeight(ROOT.cElectrons, 'GsfTrackSF')
    track.addFactor(electronTrackSF)
    track.setVariable(ROOT.IDSFWeight.kEta, ROOT.IDSFWeight.kNpv)
    selector.addOperator(track)

def addMuonIDSFWeight(sample, selector):
    muonTightSF = getFromFile(datadir + '/scaleFactor_muon_tightid_12p9.root', 'scaleFactor_muon_tightid_RooCMSShape') # x: abs eta, y: pt
    muonTrackSF = getFromFile(datadir + '/muonpog_muon_tracking_SF_ichep.root', 'htrack2') # x: npv

    idsf = ROOT.IDSFWeight(ROOT.cMuons, 'MuonSF')
    idsf.addFactor(muonTightSF)
    idsf.setVariable(ROOT.IDSFWeight.kAbsEta, ROOT.IDSFWeight.kPt)
    selector.addOperator(idsf)

    track = ROOT.IDSFWeight(ROOT.cMuons, 'MuonTrackSF')
    track.addFactor(muonTrackSF)
    track.setVariable(ROOT.IDSFWeight.kNpv)
    selector.addOperator(track)

def addPDFVariation(sample, selector):
    if 'amcatnlo' in sample.fullname or 'madgraph' in sample.fullname: # ouh la la..
        selector.addOperator(ROOT.NNPDFVariation())

def addKfactor(sample, selector):
    """
    Apply the k-factor corrections.
    """

    sname = sample.name.replace('gj04', 'gj').replace('zllg', 'znng').replace('wglo', 'wnlg').replace('-o', '')

    # temporarily don't apply QCD k-factor until we redrive for nlo samples
    if sample.name not in ['znng', 'znng-130', 'zllg', 'zllg-130', 'wnlg', 'wnlg-130', 'wnlg-500']:
        corr = getFromFile(datadir + '/kfactor.root', sname, newname = sname + '_kfactor')
        if not corr:
            raise RuntimeError('kfactor not found for ' + sample.name)
    
        qcd = ROOT.PhotonPtWeight(corr, 'QCDCorrection')
        qcd.setPhotonType(ROOT.PhotonPtWeight.kPostShower) # if possible
    
        for variation in ['renUp', 'renDown', 'facUp', 'facDown', 'scaleUp', 'scaleDown']:
            vcorr = getFromFile(datadir + '/kfactor.root', sname + '_' + variation)
            if vcorr:
                logger.debug('applying qcd var %s %s', variation, sample.name)
                qcd.addVariation('qcd' + variation, vcorr)

        selector.addOperator(qcd)

    corr = getFromFile(datadir + '/ewk_corr.root', sname, newname = sname + '_ewkcorr')
    if corr:
        logger.debug('applying ewk %s', sample.name)
        ewk = ROOT.PhotonPtWeight(corr, 'EWKNLOCorrection')
        ewk.setPhotonType(ROOT.PhotonPtWeight.kParton)

        for variation in ['Up', 'Down']:
            vcorr = getFromFile(datadir + '/ewk_corr.root', sname + '_' + variation)
            if vcorr:
                logger.debug('applying ewk var %s %s', variation, sample.name)
                ewk.addVariation('ewk' + variation, vcorr)

        selector.addOperator(ewk)

def addGenPhotonVeto(sample, selector):
    veto = ROOT.GenPhotonVeto()
    veto.setMinPt(130.)
    veto.setMinPartonDR(0.5)

    selector.addOperator(veto, 0)

def addGenPhotonPtCut(sample, selector):
    truncator = ROOT.PhotonPtTruncator()
    truncator.setPtMax(500.)

    selector.addOperator(truncator, 0)

def addPhotonRecoil(sample, selector):
    """
    Wrapper for diphoton samples to turn them into photon+dark photon samples by 'removing' one of the photons and adding it to the MET.
    """
    selector.addOperator(ROOT.PhotonRecoil())

def modHfake(selector):
    """Append PhotonPtWeight with hadProxyWeights and set up the photon selections."""

    hadproxyWeight = getFromFile(datadir + '/hadronTFactor.root', 'tfactNom')

    weight = ROOT.PhotonPtWeight(hadproxyWeight, 'hadProxyWeight')
    weight.setPhotonType(ROOT.PhotonPtWeight.kReco)
    selector.addOperator(weight)

    photonSel = selector.findOperator('PhotonSelection')

    setupPhotonSelection(photonSel, changes = ['!CHIso', '+CHIso11'])
    setupPhotonSelection(photonSel, veto = True)


if needHelp:
    sys.argv.append('--help')
