#!/usr/bin/env python

import sys
import os
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples

sNames = sys.argv[1:]

sourceDir = '/scratch5/yiiyama/hist/simpletree10/t2mit/filefi/042'
neroInput = False
outputDir = '/scratch5/ballen/hist/monophoton/skim'

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.Load('libNeroProducerCore.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/tools')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/NeroProducer/Core/interface')

ROOT.gROOT.LoadMacro(thisdir + '/skimslimweight.cc+')

def makeEventProcessor(sample):
    global badEventsList

    proc = ROOT.EventProcessor()
    proc.setEventList(badEventsList)
    return proc

def makeListedEventProcessor(sample):
    global badEventsList

    proc = ROOT.ListedEventProcessor()
    proc.setEventList(badEventsList)
    return proc

def makeGenProcessor(sample, cls = ROOT.GenProcessor):
    global npvweight, gidscale

    proc = cls(sample.crosssection / sample.sumw)
    proc.setReweight(npvweight)
    proc.setIdScaleFactor(gidscale)
    return proc

def makeDimuonProcessor(sample):
    proc = ROOT.LeptonProcessor(0, 2)
    proc.setMinPhotonPt(60.)
    return proc

def makeMonomuonProcessor(sample):
    proc = ROOT.LeptonProcessor(0, 1)
    proc.setMinPhotonPt(60.)
    return proc

def makeGenDimuonProcessor(sample):
    global npvweight, gidscale

    proc = ROOT.GenLeptonProcessor(0, 2, sample.crosssection / sample.sumw)
    proc.setReweight(npvweight)
    proc.setIdScaleFactor(gidscale)
    proc.setMinPhotonPt(60.)
    return proc

def makeGenMonomuonProcessor(sample):
    global npvweight, gidscale

    proc = ROOT.GenLeptonProcessor(0, 1, sample.crosssection / sample.sumw)
    proc.setReweight(npvweight)
    proc.setIdScaleFactor(gidscale)
    proc.setMinPhotonPt(60.)
    return proc

def makeDielectronProcessor(sample):
    proc = ROOT.LeptonProcessor(2, 0)
    proc.setMinPhotonPt(60.)
    return proc

def makeMonoelectronProcessor(sample):
    proc = ROOT.LeptonProcessor(1, 0)
    proc.setMinPhotonPt(60.)
    return proc

def makeGenDielectronProcessor(sample):
    global npvweight, gidscale

    proc = ROOT.GenLeptonProcessor(2, 0, sample.crosssection / sample.sumw)
    proc.setReweight(npvweight)
    proc.setIdScaleFactor(gidscale)
    proc.setMinPhotonPt(60.)
    return proc

def makeGenMonoelectronProcessor(sample):
    global npvweight, gidscale

    proc = ROOT.GenLeptonProcessor(1, 0, sample.crosssection / sample.sumw)
    proc.setReweight(npvweight)
    proc.setIdScaleFactor(gidscale)
    proc.setMinPhotonPt(60.)
    return proc

def makeOppFlavorProcessor(sample):
    proc = ROOT.LeptonProcessor(1, 1)
    proc.setMinPhotonPt(60.)
    return proc

def makeGenOppFlavorProcessor(sample):
    global npvweight, gidscale

    proc = ROOT.GenLeptonProcessor(1, 1, sample.crosssection / sample.sumw)
    proc.setReweight(npvweight)
    proc.setIdScaleFactor(gidscale)
    proc.setMinPhotonPt(60.)
    return proc

def makeWenuProxyProcessor(sample):
    global eleproxyweight

    proc = ROOT.WenuProxyProcessor(eleproxyweight.GetY()[4])
    proc.setWeightErr(eleproxyweight.GetErrorY(4))
    return proc

def makeZeeProxyProcessor(sample):
    global eleproxyweight

    proc = ROOT.ZeeProxyProcessor(eleproxyweight.GetY()[4])
    proc.setWeightErr(eleproxyweight.GetErrorY(4))
    proc.setMinPhotonPt(60.)
    return proc

def makeHadronProxyProcessor(sample):
    global hadproxyweight

    proc = ROOT.HadronProxyProcessor(1.)
    proc.setReweight(hadproxyweight)
    return proc

def makeEMPlusJetProcessor(sample):
    return ROOT.EMPlusJetProcessor()

def makeGenWlnuProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenWlnuProcessor)

def makeGenWenuProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenWenuProcessor)

def makeGenWenuProxyProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenWenuProxyProcessor)

def makeGenGJetProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenGJetProcessor)

def makeGenZnnProxyProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenZnnProxyProcessor)

def makeGenHadronProcessor(sample):
    return makeGenProcessor(sample, cls = ROOT.GenHadronProcessor)

generators = {
    'sph-d3': {'monoph': makeEventProcessor, 'efake': makeWenuProxyProcessor, 'hfake': makeHadronProxyProcessor, 'emplusjet': makeEMPlusJetProcessor},
    'sph-d4': {'monoph': makeEventProcessor, 'efake': makeWenuProxyProcessor, 'hfake': makeHadronProxyProcessor, 'emplusjet': makeEMPlusJetProcessor},
    'smu-d3': {'dimu': makeDimuonProcessor, 'monomu': makeMonomuonProcessor, 'elmu': makeOppFlavorProcessor},
    'smu-d4': {'dimu': makeDimuonProcessor, 'monomu': makeMonomuonProcessor, 'elmu': makeOppFlavorProcessor},
    'sel-d3': {'diel': makeDielectronProcessor, 'monoel': makeMonoelectronProcessor, 'eefake': makeZeeProxyProcessor},
    'sel-d4': {'diel': makeDielectronProcessor, 'monoel': makeMonoelectronProcessor, 'eefake': makeZeeProxyProcessor},
    'wlnu': {'monoph': makeGenWlnuProcessor},
    'zg': {'monoph': makeGenZnnProxyProcessor, 'dimu': makeGenDimuonProcessor, 'diel': makeGenDielectronProcessor, 'monomu': makeGenMonomuonProcessor, 'monoel': makeGenMonoelectronProcessor, 'elmu': makeGenOppFlavorProcessor},
    'ttg': {'monoph': makeGenProcessor, 'dimu': makeGenDimuonProcessor, 'diel': makeGenDielectronProcessor, 'monomu': makeGenMonomuonProcessor, 'monoel': makeGenMonoelectronProcessor, 'elmu': makeGenOppFlavorProcessor},
    'wg': {'monoph':makeGenProcessor, 'monomu': makeGenMonomuonProcessor, 'monoel': makeGenMonoelectronProcessor},
    'znng-130': {'monoph':makeGenProcessor},
    'dy-50': {'monoph': makeGenProcessor},
    'znn-100': {'monoph': makeGenHadronProcessor},
    'znn-200': {'monoph': makeGenHadronProcessor},
    'znn-400': {'monoph': makeGenHadronProcessor},
    'znn-600': {'monoph': makeGenHadronProcessor},
    'g-40': {'monoph':makeGenGJetProcessor},
    'g-100': {'monoph':makeGenGJetProcessor},
    'g-200': {'monoph':makeGenGJetProcessor},
    'g-400': {'monoph':makeGenGJetProcessor},
    'g-600': {'monoph':makeGenGJetProcessor},
    'qcd-200': {'monoph':makeGenProcessor},
    'qcd-300': {'monoph':makeGenProcessor},
    'qcd-500': {'monoph':makeGenProcessor},
    'qcd-700': {'monoph':makeGenProcessor},
    'qcd-1000': {'monoph':makeGenProcessor}
}
for sname in ['add%d-%d' % (nd, md) for md in [1, 2, 3] for nd in [3, 4, 5, 6, 8]]:
    generators[sname] = {'monoph': makeGenProcessor}

npvSource = ROOT.TFile.Open(basedir + '/data/npv.root')
if not npvSource:
    print 'Generating NPV reweight histograms'
    ROOT.gROOT.LoadMacro('selectDimu.cc+')

    npvSource = ROOT.TFile.Open(npvSourceName, 'recreate')

    dataDir = npvSource.mkdir('data')
    dataTree = ROOT.TChain('events')
    dataTree.Add(sourceDir + '/' + allsamples['smu-d3'].directory + '/simpletree_*.root')
    dataTree.Add(sourceDir + '/' + allsamples['smu-d4'].directory + '/simpletree_*.root')
    ROOT.selectDimu(dataTree, dataDir)

    mcDir = npvSource.mkdir('mc')
    mcTree = ROOT.TChain('events')
    mcTree.Add(sourceDir + '/' + allsamples['dy-50'].directory + '/simpletree_*.root')
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

badEventsList = ROOT.EventList()
badEventsList.addSource('/scratch5/yiiyama/studies/monophoton/SinglePhoton_csc2015.txt')
badEventsList.addSource('/scratch5/yiiyama/studies/monophoton/SinglePhoton_ecalscn1043093.txt')

if len(sNames) != 0:
    if sNames[0] == 'all':
        sNames = generators.keys()
    elif sNames[0] == 'list':
        print ' '.join(sorted(generators.keys()))
        sys.exit(0)

skimmer = ROOT.SkimSlimWeight()

sampleNames = []
for name in sNames:
    if allsamples[name].sumw > 0.:
        sampleNames.append(name)

print ' '.join(sampleNames)
if sNames[0] == 'all':
    sys.exit(0)

for name in sampleNames:
    sample = allsamples[name]

    skimmer.reset()

    tree = ROOT.TChain('events')

# TEMPORARY
    if 'sph' in name:
        print 'Using simpletree10a for sph'
        tree.Add(sourceDir.replace('10', '10a') + '/' + sample.directory + '/simpletree_*.root')
    else:
        tree.Add(sourceDir + '/' + sample.directory + '/simpletree_*.root')
# TEMPORARY
 
    for pname, gen in generators[name].items():
        processor = gen(sample)
        skimmer.addProcessor(pname, processor)

    skimmer.run(tree, outputDir, name, -1, neroInput)
