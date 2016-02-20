#!/usr/bin/env python

import sys
import os
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

sNames = sys.argv[1:]

dataSourceDir = config.ntuplesDir

neroInput = False

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.Load('libNeroProducerCore.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/tools')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/NeroProducer/Core/interface')

ROOT.gROOT.LoadMacro(thisdir + '/skimslimweight.cc+')

def makeEventProcessor(sample, cls = ROOT.EventProcessor, minPt = 175., args = tuple()):
    proc = cls(*args)
    proc.setMinPhotonPt(minPt)
    return proc

def makeCandidateProcessor(sample):
    return makeEventProcessor(sample, cls = ROOT.CandidateProcessor)

def makeLeptonProcessor(sample, nEl, nMu, cls = ROOT.LeptonProcessor, minPt = 30., args = tuple()):
    return makeEventProcessor(sample, cls = cls, minPt = minPt, args = (nEl, nMu) + args)

def makeDimuonProcessor(sample):
    return makeLeptonProcessor(sample, 0, 2)

def makeMonomuonProcessor(sample):
    return makeLeptonProcessor(sample, 0, 1)

def makeDielectronProcessor(sample):
    return makeLeptonProcessor(sample, 2, 0)

def makeMonoelectronProcessor(sample):
    return makeLeptonProcessor(sample, 1, 0)

def makeOppFlavorProcessor(sample):
    return makeLeptonProcessor(sample, 1, 1)

def makeWenuProxyProcessor(sample, cls = ROOT.WenuProxyProcessor, minPt = 175., args = tuple()):
    global eleproxyweight

    proc = makeEventProcessor(sample, cls = cls, minPt = minPt, args = (eleproxyweight.GetY()[4],) + args)

    proc.setWeightErr(eleproxyweight.GetErrorY(4))
    return proc

def makeZeeProxyProcessor(sample):
    return makeWenuProxyProcessor(sample, cls = ROOT.ZeeProxyProcessor, minPt = 60.)

def makeHadronProxyProcessor(sample, cls = ROOT.HadronProxyProcessor, minPt = 175., args = tuple()):
    global hadproxyweight

    proc = makeEventProcessor(sample, cls = cls, minPt = minPt, args = args)
    proc.setReweight(hadproxyweight)

    for sel in ['HOverE', 'NHIso', 'PhIso', 'EVeto', 'Sieie15', 'CHIso11']:
        proc.addSelection(True, getattr(ROOT.EMObjectProcessor, sel))
        proc.addVeto(True, getattr(ROOT.EMObjectProcessor, sel))

    proc.addSelection(False, ROOT.EMObjectProcessor.Sieie12, ROOT.EMObjectProcessor.CHIso)
    proc.addVeto(True, ROOT.EMObjectProcessor.Sieie12)
    proc.addVeto(True, ROOT.EMObjectProcessor.CHIso)

    return proc

def makeHadronProxyAltProcessor(sample, cls = ROOT.HadronProxyProcessor, minPt = 175., args = tuple()):
    global hadproxyaltweight

    proc = makeEventProcessor(sample, cls = cls, minPt = minPt, args = args)
    proc.setReweight(hadproxyaltweight)

    for sel in ['HOverE', 'EVeto', 'Sieie15', 'CHIso11', 'NHIso11', 'PhIso3']:
        proc.addSelection(True, getattr(ROOT.EMObjectProcessor, sel))
        proc.addVeto(True, getattr(ROOT.EMObjectProcessor, sel))

    proc.addSelection(False, ROOT.EMObjectProcessor.NHIso, ROOT.EMObjectProcessor.PhIso)
    proc.addVeto(True, ROOT.EMObjectProcessor.NHIso)
    proc.addVeto(True, ROOT.EMObjectProcessor.PhIso)

    return proc

def makeLowMtCandidateProcessor(sample):
    return makeEventProcessor(sample, cls = ROOT.LowMtCandidateProcessor)

def makeWenuProxyLowMtProcessor(sample):
    return makeWenuProxyProcessor(sample, cls = ROOT.WenuProxyLowMtProcessor)

def makePurityProcessor(sample):
    # One loose photon + high-pT jet.

    proc = makeEventProcessor(sample, cls = ROOT.EMPlusJetProcessor)

    for sel in ['HOverE', 'EVeto', 'Sieie15', 'CHIso11', 'NHIso', 'PhIso']:
        proc.addSelection(True, getattr(ROOT.EMObjectProcessor, sel))

    return proc

def makePurityAltProcessor(sample):
    # One loose photon + high-pT jet.

    proc = makeEventProcessor(sample, cls = ROOT.EMPlusJetProcessor)

    for sel in ['HOverE', 'EVeto', 'Sieie12', 'CHIso11', 'NHIso11', 'PhIso3']:
        proc.addSelection(True, getattr(ROOT.EMObjectProcessor, sel))

    proc.addSelection(False, ROOT.EMObjectProcessor.NHIso, ROOT.EMObjectProcessor.PhIso)

    return proc

def makeHadronProxyLowMtProcessor(sample):
    return makeHadronProxyProcessor(sample, cls = ROOT.HadronProxyLowMtProcessor)

def makeGenProcessor(sample, cls = ROOT.GenProcessor, minPt = 175., args = tuple()):
    global npvweight, gidscale

    proc = makeEventProcessor(sample, cls = cls, minPt = minPt, args = args + (sample.crosssection / sample.sumw,))

    proc.setReweight(npvweight)
    proc.setIdScaleFactor(gidscale)
    proc.useAlternativeWeights(True)
    return proc

def makeGenCandidateProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenCandidateProcessor)

def makeGenGUpProcessor(sample, cls = ROOT.GenCandidateProcessor, args = tuple()):
    proc = makeGenProcessor(sample, cls = cls, args = args)

    proc.setPhotonEnergyShift(0.015)
    return proc

def makeGenGDownProcessor(sample, cls = ROOT.GenCandidateProcessor, args = tuple()):
    proc = makeGenProcessor(sample, cls = cls, args = args)

    proc.setPhotonEnergyShift(-0.015)
    return proc

def makeGenJECUpProcessor(sample, cls = ROOT.GenCandidateProcessor, args = tuple()):
    proc = makeGenProcessor(sample, cls = cls, args = args)

    proc.setJetEnergyShift(1)
    return proc

def makeGenJECDownProcessor(sample, cls = ROOT.GenCandidateProcessor, args = tuple()):
    proc = makeGenProcessor(sample, cls = cls, args = args)

    proc.setJetEnergyShift(-1)
    return proc

def makeGenLeptonProcessor(sample, nEl, nMu, cls = ROOT.GenLeptonProcessor, minPt = 30., args = tuple()):
    return makeGenProcessor(sample, cls = cls, minPt = minPt, args = args + (nEl, nMu))

def makeGenDimuonProcessor(sample):
    return makeGenLeptonProcessor(sample, 0, 2)

def makeGenMonomuonProcessor(sample):
    return makeGenLeptonProcessor(sample, 0, 1)

def makeGenDielectronProcessor(sample):
    return makeGenLeptonProcessor(sample, 2, 0)

def makeGenMonoelectronProcessor(sample):
    return makeGenLeptonProcessor(sample, 1, 0)

def makeGenOppFlavorProcessor(sample):
    return makeGenLeptonProcessor(sample, 1, 1)

def makeGenWlnuProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenWlnuProcessor)

def makeGenWlnuGUpProcessor(sample):
    return makeGenGUpProcessor(sample, cls = ROOT.GenWlnuProcessor)

def makeGenWlnuGDownProcessor(sample):
    return makeGenGDownProcessor(sample, cls = ROOT.GenWlnuProcessor)

def makeGenWlnuJECUpProcessor(sample):
    return makeGenJECUpProcessor(sample, cls = ROOT.GenWlnuProcessor)

def makeGenWlnuJECDownProcessor(sample):
    return makeGenJECDownProcessor(sample, cls = ROOT.GenWlnuProcessor)

def makeGenWenuProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenWenuProcessor)

def makeGenWenuProxyProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenWenuProxyProcessor)

def makeGenLowMtProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenLowMtProcessor)

def makeGenGJetProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenGJetProcessor)

def makeGenGJetGUpProcessor(sample):
    return makeGenGUpProcessor(sample, cls = ROOT.GenGJetProcessor)

def makeGenGJetGDownProcessor(sample):
    return makeGenGDownProcessor(sample, cls = ROOT.GenGJetProcessor)

def makeGenGJetJECUpProcessor(sample):
    return makeGenJECUpProcessor(sample, cls = ROOT.GenGJetProcessor)

def makeGenGJetJECDownProcessor(sample):
    return makeGenJECDownProcessor(sample, cls = ROOT.GenGJetProcessor)

def makeGenZnnProxyProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenZnnProxyProcessor)

def makeGenHadronProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenHadronProcessor)

def makeGenGJetLowMtProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenGJetLowMtProcessor)

def makeGenWtaunuProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenWtaunuProcessor)

def makeGenPurityProcessor(sample):
    # One loose photon + high-pT jet.

    proc = makeGenProcessor(sample, cls = ROOT.GenEMPlusJetProcessor)
    for sel in ['HOverE', 'EVeto', 'Sieie15', 'CHIso11', 'NHIso', 'PhIso']:
        proc.addSelection(True, getattr(ROOT.EMObjectProcessor, sel))

    return proc

def makeGenKFactorProcessor(sample, gen = makeGenCandidateProcessor):
    proc = gen(sample)

    with open(basedir + '/data/' + sample.name + '_kfactor.dat') as source:
        for line in source:
            pt, kfactor = map(float, line.split()[:2])
            proc.setKFactorPtBin(pt, kfactor)

    return proc

def makeGenKFactorGUpProcessor(sample):
    return makeGenKFactorProcessor(sample, gen = makeGenGUpProcessor)

def makeGenKFactorGDownProcessor(sample):
    return makeGenKFactorProcessor(sample, gen = makeGenGDownProcessor)

def makeGenKFactorJECUpProcessor(sample):
    return makeGenKFactorProcessor(sample, gen = makeGenJECUpProcessor)

def makeGenKFactorJECDownProcessor(sample):
    return makeGenKFactorProcessor(sample, gen = makeGenJECDownProcessor)

def makeGenKFactorLowMtProcessor(sample):
    return makeGenKFactorProcessor(sample, gen = makeGenLowMtProcessor)

def makeGenKFactorMonomuonProcessor(sample):
    return makeGenKFactorProcessor(sample, gen = makeGenMonomuonProcessor)

def makeGenKFactorDimuonProcessor(sample):
    return makeGenKFactorProcessor(sample, gen = makeGenDimuonProcessor)

def makeGenKFactorMonoelectronProcessor(sample):
    return makeGenKFactorProcessor(sample, gen = makeGenMonoelectronProcessor)

generators = {
    # Data
    'sph-d3': {'monoph': makeCandidateProcessor, 'monophpv': makeEventProcessor, 'efake': makeWenuProxyProcessor, 'hfake': makeHadronProxyProcessor, 'hfakealt': makeHadronProxyAltProcessor, 'lowmt': makeLowMtCandidateProcessor, 'efakelowmt': makeWenuProxyLowMtProcessor, 'hfakelowmt': makeHadronProxyLowMtProcessor, 'purity': makePurityProcessor, 'purityalt': makePurityAltProcessor},
    'sph-d4': {'monoph': makeCandidateProcessor, 'monophpv': makeEventProcessor, 'efake': makeWenuProxyProcessor, 'hfake': makeHadronProxyProcessor, 'hfakealt': makeHadronProxyAltProcessor, 'lowmt': makeLowMtCandidateProcessor, 'efakelowmt': makeWenuProxyLowMtProcessor, 'hfakelowmt': makeHadronProxyLowMtProcessor, 'purity': makePurityProcessor, 'purityalt': makePurityAltProcessor},
    'smu-d3': {'dimu': makeDimuonProcessor, 'monomu': makeMonomuonProcessor, 'elmu': makeOppFlavorProcessor},
    'smu-d4': {'dimu': makeDimuonProcessor, 'monomu': makeMonomuonProcessor, 'elmu': makeOppFlavorProcessor},
    'sel-d3': {'diel': makeDielectronProcessor, 'monoel': makeMonoelectronProcessor, 'eefake': makeZeeProxyProcessor},
    'sel-d4': {'diel': makeDielectronProcessor, 'monoel': makeMonoelectronProcessor, 'eefake': makeZeeProxyProcessor},
    # MC for signal region
    'znng-130': {'monoph':makeGenKFactorProcessor, 'monoph-gup':makeGenKFactorGUpProcessor, 'monoph-gdown':makeGenKFactorGDownProcessor, 'monoph-jecup':makeGenKFactorJECUpProcessor, 'monoph-jecdown':makeGenKFactorJECDownProcessor, 'lowmt': makeGenKFactorLowMtProcessor},
    'wg': {'monoph':makeGenCandidateProcessor, 'monoph-gup':makeGenGUpProcessor, 'monoph-gdown':makeGenGDownProcessor, 'monoph-jecup':makeGenJECUpProcessor, 'monoph-jecdown':makeGenJECDownProcessor, 'monomu': makeGenMonomuonProcessor, 'monoel': makeGenMonoelectronProcessor, 'lowmt': makeGenLowMtProcessor}, # NLO low stats
    'wnlg-130': {'monoph':makeGenKFactorProcessor, 'monoph-gup':makeGenKFactorGUpProcessor, 'monoph-gdown':makeGenKFactorGDownProcessor, 'monoph-jecup':makeGenKFactorJECUpProcessor, 'monoph-jecdown':makeGenKFactorJECDownProcessor, 'monomu': makeGenKFactorMonomuonProcessor, 'monoel': makeGenKFactorMonoelectronProcessor, 'lowmt': makeGenKFactorLowMtProcessor},
    'g-40': {'monoph':makeGenGJetProcessor, 'monoph-gup':makeGenGJetGUpProcessor, 'monoph-gdown':makeGenGJetGDownProcessor, 'monoph-jecup':makeGenGJetJECUpProcessor, 'monoph-jecdown':makeGenGJetJECDownProcessor, 'lowmt': makeGenGJetLowMtProcessor, 'purity': makeGenPurityProcessor},
    'g-100': {'monoph':makeGenGJetProcessor, 'monoph-gup':makeGenGJetGUpProcessor, 'monoph-gdown':makeGenGJetGDownProcessor, 'monoph-jecup':makeGenGJetJECUpProcessor, 'monoph-jecdown':makeGenGJetJECDownProcessor, 'lowmt': makeGenGJetLowMtProcessor, 'purity': makeGenPurityProcessor},
    'g-200': {'monoph':makeGenGJetProcessor, 'monoph-gup':makeGenGJetGUpProcessor, 'monoph-gdown':makeGenGJetGDownProcessor, 'monoph-jecup':makeGenGJetJECUpProcessor, 'monoph-jecdown':makeGenGJetJECDownProcessor, 'lowmt': makeGenGJetLowMtProcessor, 'purity': makeGenPurityProcessor},
    'g-400': {'monoph':makeGenGJetProcessor, 'monoph-gup':makeGenGJetGUpProcessor, 'monoph-gdown':makeGenGJetGDownProcessor, 'monoph-jecup':makeGenGJetJECUpProcessor, 'monoph-jecdown':makeGenGJetJECDownProcessor, 'lowmt': makeGenGJetLowMtProcessor, 'purity': makeGenPurityProcessor},
    'g-600': {'monoph':makeGenGJetProcessor, 'monoph-gup':makeGenGJetGUpProcessor, 'monoph-gdown':makeGenGJetGDownProcessor, 'monoph-jecup':makeGenGJetJECUpProcessor, 'monoph-jecdown':makeGenGJetJECDownProcessor, 'lowmt': makeGenGJetLowMtProcessor, 'purity': makeGenPurityProcessor},
    'ttg': {'monoph': makeGenCandidateProcessor, 'monoph-gup':makeGenGUpProcessor, 'monoph-gdown':makeGenGDownProcessor, 'monoph-jecup':makeGenJECUpProcessor, 'monoph-jecdown':makeGenJECDownProcessor, 'dimu': makeGenDimuonProcessor, 'diel': makeGenDielectronProcessor, 'monomu': makeGenMonomuonProcessor, 'monoel': makeGenMonoelectronProcessor, 'elmu': makeGenOppFlavorProcessor, 'lowmt': makeGenLowMtProcessor}, # NLO low stats
    'zg': {'monoph': makeGenCandidateProcessor, 'monoph-gup':makeGenGUpProcessor, 'monoph-gdown':makeGenGDownProcessor, 'monoph-jecup':makeGenJECUpProcessor, 'monoph-jecdown':makeGenJECDownProcessor, 'dimu': makeGenDimuonProcessor, 'diel': makeGenDielectronProcessor, 'monomu': makeGenMonomuonProcessor, 'monoel': makeGenMonoelectronProcessor, 'elmu': makeGenOppFlavorProcessor, 'lowmt': makeGenLowMtProcessor}, # NLO low stats
    'zllg-130': {'monoph':makeGenKFactorProcessor, 'monoph-gup':makeGenKFactorGUpProcessor, 'monoph-gdown':makeGenKFactorGDownProcessor, 'monoph-jecup':makeGenKFactorJECUpProcessor, 'monoph-jecdown':makeGenKFactorJECDownProcessor, 'dimu': makeGenKFactorDimuonProcessor},
    'wlnu': {'monoph': makeGenWlnuProcessor, 'monoph-gup':makeGenWlnuGUpProcessor, 'monoph-gdown':makeGenWlnuGDownProcessor, 'monoph-jecup':makeGenWlnuJECUpProcessor, 'monoph-jecdown':makeGenWlnuJECDownProcessor, 'monomu': makeGenMonomuonProcessor, 'tau' : makeGenWtaunuProcessor}, # NLO low stats
    'wlnu-100': {'monoph': makeGenWlnuProcessor, 'monoph-gup':makeGenWlnuGUpProcessor, 'monoph-gdown':makeGenWlnuGDownProcessor, 'monoph-jecup':makeGenWlnuJECUpProcessor, 'monoph-jecdown':makeGenWlnuJECDownProcessor, 'monomu': makeGenMonomuonProcessor, 'tau' : makeGenWtaunuProcessor},
    'wlnu-200': {'monoph': makeGenWlnuProcessor, 'monoph-gup':makeGenWlnuGUpProcessor, 'monoph-gdown':makeGenWlnuGDownProcessor, 'monoph-jecup':makeGenWlnuJECUpProcessor, 'monoph-jecdown':makeGenWlnuJECDownProcessor, 'monomu': makeGenMonomuonProcessor, 'tau' : makeGenWtaunuProcessor},
    'wlnu-400': {'monoph': makeGenWlnuProcessor, 'monoph-gup':makeGenWlnuGUpProcessor, 'monoph-gdown':makeGenWlnuGDownProcessor, 'monoph-jecup':makeGenWlnuJECUpProcessor, 'monoph-jecdown':makeGenWlnuJECDownProcessor, 'monomu': makeGenMonomuonProcessor, 'tau' : makeGenWtaunuProcessor},
    'wlnu-600': {'monoph': makeGenWlnuProcessor, 'monoph-gup':makeGenWlnuGUpProcessor, 'monoph-gdown':makeGenWlnuGDownProcessor, 'monoph-jecup':makeGenWlnuJECUpProcessor, 'monoph-jecdown':makeGenWlnuJECDownProcessor, 'monomu': makeGenMonomuonProcessor, 'tau' : makeGenWtaunuProcessor},
    # other MC
    'dy-50': {'monoph': makeGenCandidateProcessor, 'monomu': makeGenMonomuonProcessor},
    'znn-100': {'monoph': makeGenHadronProcessor},
    'znn-200': {'monoph': makeGenHadronProcessor},
    'znn-400': {'monoph': makeGenHadronProcessor},
    'znn-600': {'monoph': makeGenHadronProcessor},
    'qcd-200': {'monoph':makeGenCandidateProcessor},
    'qcd-300': {'monoph':makeGenCandidateProcessor},
    'qcd-500': {'monoph':makeGenCandidateProcessor},
    'qcd-700': {'monoph':makeGenCandidateProcessor},
    'qcd-1000': {'monoph':makeGenCandidateProcessor}
}
for sname in ['add%d-%d' % (nd, md) for md in [1, 2, 3] for nd in [3, 4, 5, 6, 8]]:
    generators[sname] = {'monoph': makeGenCandidateProcessor, 'monoph-gup':makeGenGUpProcessor, 'monoph-gdown':makeGenGDownProcessor, 'monoph-jecup':makeGenJECUpProcessor, 'monoph-jecdown':makeGenJECDownProcessor}

for mt in [ 'a', 'v' ]:
    for dm in [1, 10, 50, 150, 500, 1000]:
        for mm in [10, 20, 50, 100, 200, 300, 500, 1000, 2000, 10000]:
            if mm == 2 * dm:
                mm = mm - 5
            sname = 'dm%s-%d-%d' % (mt, mm, dm)
            try:
                # print sname
                allsamples[sname]
            except KeyError:
                # print "This combination is not part of the DMWG recommendations, moving onto next one."
                continue;
            generators[sname] = {'monoph': makeGenCandidateProcessor, 'monoph-gup':makeGenGUpProcessor, 'monoph-gdown':makeGenGDownProcessor, 'monoph-jecup':makeGenJECUpProcessor, 'monoph-jecdown':makeGenJECDownProcessor}

npvSource = ROOT.TFile.Open(basedir + '/data/npv.root')
if not npvSource:
    print 'Generating NPV reweight histograms'
    ROOT.gROOT.LoadMacro('selectDimu.cc+')

    npvSource = ROOT.TFile.Open(npvSourceName, 'recreate')

    dataDir = npvSource.mkdir('data')
    dataTree = ROOT.TChain('events')
    dataTree.Add(config.ntuplesDir + '/' + allsamples['smu-d3'].directory + '/simpletree_*.root')
    dataTree.Add(config.ntuplesDir + '/' + allsamples['smu-d4'].directory + '/simpletree_*.root')
    ROOT.selectDimu(dataTree, dataDir)

    mcDir = npvSource.mkdir('mc')
    mcTree = ROOT.TChain('events')
    mcTree.Add(config.ntuplesDir + '/' + allsamples['dy-50'].directory + '/simpletree_*.root')
    ROOT.selectDimu(mcTree, mcDir)

    npvSource.cd()
    data = npvSource.Get('data/Npv')
    data.Scale(1. / data.GetSumOfWeights())
    mc = npvSource.Get('mc/Npv')
    mc.Scale(1. / mc.GetSumOfWeights())

    npvweight = data.Clone('npvweight')
    npvweight.Divide(mc)
    npvweight.Write()

npvweight = npvSource.Get('npvweight')

hadproxySource = ROOT.TFile.Open(basedir + '/data/hadronTFactor.root')
hadproxyweight = hadproxySource.Get('tfact')

hadproxyaltSource = ROOT.TFile.Open(basedir + '/data/hadronTFactorAlt.root')
hadproxyaltweight = hadproxyaltSource.Get('tfact')

eleproxySource = ROOT.TFile.Open(basedir + '/data/egfake_data.root')
eleproxyweight = eleproxySource.Get('fraction')

gidSource = ROOT.TFile.Open(basedir + '/data/photonEff.root')
gidscale = gidSource.Get('scalefactor')

if len(sNames) != 0:
    if sNames[0] == 'all':
        sNames = generators.keys()
    elif sNames[0] == 'list':
        print ' '.join(sorted(generators.keys()))
        sys.exit(0)
    elif sNames[0] == 'dm':
        sNames = [key for key in generators.keys() if 'dm' in key]
        print ' '.join(sorted(sNames))
        """
        for sName in sorted(sNames):
            print sName
        """
        sys.exit(0)

skimmer = ROOT.SkimSlimWeight()

sampleNames = []
for name in sNames:
    if allsamples[name].sumw > 0.:
        sampleNames.append(name)

print ' '.join(sampleNames)
if sNames[0] == 'all':
    sys.exit(0)

if not os.path.exists(config.skimDir):
    os.makedirs(config.skimDir)

for name in sampleNames:
    sample = allsamples[name]
    print 'Starting sample', name, str(sampleNames.index(name)+1)+'/'+str(len(sampleNames))

    skimmer.reset()

    tree = ROOT.TChain('events')

    if sample.data:
        print 'Reading', name, 'from', dataSourceDir
        tree.Add(dataSourceDir + '/' + sample.directory + '/simpletree_*.root')

    elif name.startswith('dm'):
        if os.path.exists(config.phskimDir + '/' + name + '.root'):
            print 'Reading', name, 'from', config.phskimDir
            tree.Add(config.phskimDir + '/' + name + '.root')
        else:
            sourceDir = config.ntuplesDir.replace("042", "043")
            print 'Reading', name, 'from', sourceDir
            tree.Add(sourceDir + '/' + sample.directory + '/simpletree_*.root')

    else:
        if os.path.exists(config.phskimDir + '/' + name + '.root'):
            print 'Reading', name, 'from', config.phskimDir
            tree.Add(config.phskimDir + '/' + name + '.root')
        else:
            print 'Reading', name, 'from', config.ntuplesDir
            tree.Add(config.ntuplesDir + '/' + sample.directory + '/simpletree_*.root')

    for pname, gen in generators[name].items():
        processor = gen(sample)
        skimmer.addProcessor(pname, processor)

    skimmer.run(tree, config.skimDir, name, -1, neroInput)
