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
    return proc

def makeEMPlusJetProcessor(sample):
    return makeEventProcessor(sample, cls = ROOT.EMPlusJetProcessor)

def makeLowMtProcessor(sample):
    return makeEventProcessor(sample, cls = ROOT.LowMtProcessor)

def makeWenuProxyLowMtProcessor(sample):
    return makeWenuProxyProcessor(sample, cls = ROOT.WenuProxyLowMtProcessor)

def makeHadronProxyLowMtProcessor(sample):
    return makeHadronProxyProcessor(sample, cls = ROOT.HadronProxyLowMtProcessor)

def makeGenProcessor(sample, cls = ROOT.GenProcessor, minPt = 175., args = tuple()):
    global npvweight, gidscale

    proc = makeEventProcessor(sample, cls = cls, minPt = minPt, args = args + (sample.crosssection / sample.sumw,))

    proc.setReweight(npvweight)
    proc.setIdScaleFactor(gidscale)
    proc.useAlternativeWeights(True)
    return proc

def makeGenGUpProcessor(sample, cls = ROOT.GenProcessor, args = tuple()):
    proc = makeGenProcessor(sample, cls = cls, args = args)

    proc.setPhotonEnergyShift(0.015)
    return proc

def makeGenGDownProcessor(sample, cls = ROOT.GenProcessor, args = tuple()):
    proc = makeGenProcessor(sample, cls = cls, args = args)

    proc.setPhotonEnergyShift(-0.015)
    return proc

def makeGenJECUpProcessor(sample, cls = ROOT.GenProcessor, args = tuple()):
    proc = makeGenProcessor(sample, cls = cls, args = args)

    proc.setJetEnergyShift(1)
    return proc

def makeGenJECDownProcessor(sample, cls = ROOT.GenProcessor, args = tuple()):
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

def makeGenWenuProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenWenuProcessor)

def makeGenWenuProxyProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenWenuProxyProcessor)

def makeGenLowMtProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenLowMtProcessor)

def makeGenGJetProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenGJetProcessor)

def makeGenZnnProxyProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenZnnProxyProcessor)

def makeGenHadronProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenHadronProcessor)

def makeGenGJetLowMtProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenGJetLowMtProcessor)

def makeGenWtaunuProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenWtaunuProcessor)

def makeGenKFactorProcessor(sample, gen = makeGenProcessor):
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
    'sph-d3': {'monoph': makeEventProcessor, 'efake': makeWenuProxyProcessor, 'hfake': makeHadronProxyProcessor, 'emplusjet': makeEMPlusJetProcessor, 'lowmt': makeLowMtProcessor, 'efakelowmt': makeWenuProxyLowMtProcessor, 'hfakelowmt': makeHadronProxyLowMtProcessor},
    'sph-d4': {'monoph': makeEventProcessor, 'efake': makeWenuProxyProcessor, 'hfake': makeHadronProxyProcessor, 'emplusjet': makeEMPlusJetProcessor, 'lowmt': makeLowMtProcessor, 'efakelowmt': makeWenuProxyLowMtProcessor, 'hfakelowmt': makeHadronProxyLowMtProcessor},
    'smu-d3': {'dimu': makeDimuonProcessor, 'monomu': makeMonomuonProcessor, 'elmu': makeOppFlavorProcessor},
    'smu-d4': {'dimu': makeDimuonProcessor, 'monomu': makeMonomuonProcessor, 'elmu': makeOppFlavorProcessor},
    'sel-d3': {'diel': makeDielectronProcessor, 'monoel': makeMonoelectronProcessor, 'eefake': makeZeeProxyProcessor},
    'sel-d4': {'diel': makeDielectronProcessor, 'monoel': makeMonoelectronProcessor, 'eefake': makeZeeProxyProcessor},
    # MC for signal region
    'znng-130': {'monoph':makeGenKFactorProcessor, 'monoph-gup':makeGenKFactorGUpProcessor, 'monoph-gdown':makeGenKFactorGDownProcessor, 'monoph-jecup':makeGenKFactorJECUpProcessor, 'monoph-jecdown':makeGenKFactorJECDownProcessor, 'lowmt': makeGenKFactorLowMtProcessor},
    'wg': {'monoph':makeGenProcessor, 'monomu': makeGenMonomuonProcessor, 'monoel': makeGenMonoelectronProcessor, 'lowmt': makeGenLowMtProcessor}, # NLO low stats
    'wnlg-130': {'monoph':makeGenKFactorProcessor, 'monoph-gup':makeGenKFactorGUpProcessor, 'monoph-gdown':makeGenKFactorGDownProcessor, 'monoph-jecup':makeGenKFactorJECUpProcessor, 'monoph-jecdown':makeGenKFactorJECDownProcessor, 'monomu': makeGenKFactorMonomuonProcessor, 'monoel': makeGenKFactorMonoelectronProcessor, 'lowmt': makeGenKFactorLowMtProcessor},
    'g-40': {'monoph':makeGenGJetProcessor, 'lowmt': makeGenGJetLowMtProcessor},
    'g-100': {'monoph':makeGenGJetProcessor, 'lowmt': makeGenGJetLowMtProcessor},
    'g-200': {'monoph':makeGenGJetProcessor, 'lowmt': makeGenGJetLowMtProcessor},
    'g-400': {'monoph':makeGenGJetProcessor, 'lowmt': makeGenGJetLowMtProcessor},
    'g-600': {'monoph':makeGenGJetProcessor, 'lowmt': makeGenGJetLowMtProcessor},
    'ttg': {'monoph': makeGenProcessor, 'monoph-gup':makeGenGUpProcessor, 'monoph-gdown':makeGenGDownProcessor, 'monoph-jecup':makeGenJECUpProcessor, 'monoph-jecdown':makeGenJECDownProcessor, 'dimu': makeGenDimuonProcessor, 'diel': makeGenDielectronProcessor, 'monomu': makeGenMonomuonProcessor, 'monoel': makeGenMonoelectronProcessor, 'elmu': makeGenOppFlavorProcessor, 'lowmt': makeGenLowMtProcessor}, # NLO low stats
    'zg': {'monoph': makeGenProcessor, 'monoph-gup':makeGenGUpProcessor, 'monoph-gdown':makeGenGDownProcessor, 'monoph-jecup':makeGenJECUpProcessor, 'monoph-jecdown':makeGenJECDownProcessor, 'dimu': makeGenDimuonProcessor, 'diel': makeGenDielectronProcessor, 'monomu': makeGenMonomuonProcessor, 'monoel': makeGenMonoelectronProcessor, 'elmu': makeGenOppFlavorProcessor, 'lowmt': makeGenLowMtProcessor}, # NLO low stats
    'zllg-130': {'monoph':makeGenKFactorProcessor, 'dimu': makeGenKFactorDimuonProcessor},
    'wlnu': {'monoph': makeGenWlnuProcessor, 'monomu': makeGenMonomuonProcessor, 'tau' : makeGenWtaunuProcessor}, # NLO low stats
    'wlnu-100': {'monoph': makeGenWlnuProcessor, 'monomu': makeGenMonomuonProcessor, 'tau' : makeGenWtaunuProcessor},
    'wlnu-200': {'monoph': makeGenWlnuProcessor, 'monomu': makeGenMonomuonProcessor, 'tau' : makeGenWtaunuProcessor},
    'wlnu-400': {'monoph': makeGenWlnuProcessor, 'monomu': makeGenMonomuonProcessor, 'tau' : makeGenWtaunuProcessor},
    'wlnu-600': {'monoph': makeGenWlnuProcessor, 'monomu': makeGenMonomuonProcessor, 'tau' : makeGenWtaunuProcessor},
    # other MC
    'dy-50': {'monoph': makeGenProcessor, 'monomu': makeGenMonomuonProcessor},
    'znn-100': {'monoph': makeGenHadronProcessor},
    'znn-200': {'monoph': makeGenHadronProcessor},
    'znn-400': {'monoph': makeGenHadronProcessor},
    'znn-600': {'monoph': makeGenHadronProcessor},
    'qcd-200': {'monoph':makeGenProcessor},
    'qcd-300': {'monoph':makeGenProcessor},
    'qcd-500': {'monoph':makeGenProcessor},
    'qcd-700': {'monoph':makeGenProcessor},
    'qcd-1000': {'monoph':makeGenProcessor}
}
for sname in ['add%d-%d' % (nd, md) for md in [1, 2, 3] for nd in [3, 4, 5, 6, 8]]:
    generators[sname] = {'monoph': makeGenProcessor}
"""
for sname in ['dm%s-%d-%d' % (mt, mm, dm) for mt in [ 'a', 'v' ] for mm in [10, 20, 50, 100, 200, 300, 500, 1000, 2000, 10000] for dm in [1, 10, 50, 150, 500, 1000]]:
    generators[sname] = {'monoph': makeGenProcessor}
"""
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
            generators[sname] = {'monoph': makeGenProcessor}

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
        sourceDir = config.ntuplesDir.replace("042", "043")
        print 'Reading', name, 'from', sourceDir
        tree.Add(sourceDir + '/' + sample.directory + '/simpletree_*.root')
    else:
        print 'Reading', name, 'from', config.ntuplesDir
        tree.Add(config.ntuplesDir + '/' + sample.directory + '/simpletree_*.root')

    for pname, gen in generators[name].items():
        processor = gen(sample)
        skimmer.addProcessor(pname, processor)

    skimmer.run(tree, config.skimDir, name, -1, neroInput)
