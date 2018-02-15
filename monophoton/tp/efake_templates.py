#!/usr/bin/env python

import sys
import os
import array
import math
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
import utils
from datasets import allsamples
from tp.efake_conf import skimConfig, lumiSamples, outputDir, roofitDictsDir, getBinning, itune, vetoCut, fitBinningT, dataSource, tpconfs, monophSel, analysis

dataType = sys.argv[1] # "data" or "mc"
binningName = sys.argv[2] # see efake_conf

fitBins = getBinning(binningName)[2]

lumi = sum(allsamples[s].lumi for s in lumiSamples)

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load('libRooFit.so')
ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')
ROOT.gSystem.Load(roofitDictsDir + '/libCommonRooFit.so') # defines KeysShape

### Files ###

outputName = outputDir + '/fittemplates_' + dataType + '_' + binningName + '.root'
try:
    os.makedirs(os.path.dirname(outputName))
except OSError:
    pass

tmpOutName = '/tmp/' + os.environ['USER'] + '/efake/' + os.path.basename(outputName)
try:
    os.makedirs(os.path.dirname(tmpOutName))
except OSError:
    pass

if os.path.exists(outputName):
    # make a backup
    shutil.copy(outputName, outputName.replace('.root', '_old.root'))

outputFile = ROOT.TFile.Open(tmpOutName, 'recreate')

### Setup ###

print 'Starting common setup.'

fitBinning = ROOT.RooUniformBinning(fitBinningT[1], fitBinningT[2], fitBinningT[0])

initVals = {
    'nbkg': 100.,
    'nsignal': 100.
}
if dataType == 'data':
    initVals.update({
        'mZ': 91.2,
        'gammaZ': 2.5,
        'm0': 0.,
        'sigma': 1.,
        'alpha': 2.,
        'n': 1.5
    })

# template of templates. used in both runModes
template = ROOT.TH1D('template', '', *fitBinningT)

# workspace
work = ROOT.RooWorkspace('work', 'work')

mass = work.factory('mass[60., 120.]')
mass.setUnit('GeV')
mass.setBinning(fitBinning, 'fitWindow')

weight = work.factory('weight[-1000000000., 1000000000.]')
ntarg = work.factory('ntarg[0., 100000000.]') # effective number of entries (differs from htarg integral in MC)
nbkg = work.factory('nbkg[0., 100000000.]')
nsignal = work.factory('nsignal[0., 100000000.]')
nZ = work.factory('nZ[0., 100000000.]')
mZ = work.factory('mZ[91.2, 86., 96.]')
gammaZ = work.factory('gammaZ[2.5, 1., 5.]')
m0 = work.factory('m0[-10., 10.]')
sigma = work.factory('sigma[0.001, 5.]')
alpha = work.factory('alpha[0.01, 5.]')
n = work.factory('n[1.01, 5.]')

tpconf = work.factory('tpconf[ee=0, eg=1, pass=2, fail=3, passiso=4, failiso=5]')
binName = work.factory('binName[]')
for ibin, (bin, _) in enumerate(fitBins):
    binName.defineType(bin, ibin)

print 'Finished common setup.'

### Fill template histograms ###

print 'Starting template preparation.'

# templates setup
egPlotter = ROOT.MultiDraw()
mgPlotter = ROOT.MultiDraw()

# egPlotter.setPrintLevel(2)
# mgPlotter.setPrintLevel(2)

if dataType == 'data':
    egPlotter.setWeightBranch('')
    mgPlotter.setWeightBranch('')

    # target samples
    if dataSource == 'smu':
        for sname in skimConfig['mudata'][0]:
            egPlotter.addInputPath(utils.getSkimPath(sname, 'tp2m'))
            mgPlotter.addInputPath(utils.getSkimPath(sname, 'tp2m'))

        egPlotter.setBaseSelection('tags.pt_ > 50. && probes.loose')
        mgPlotter.setBaseSelection('tags.pt_ > 50.')

    else:
        if dataSource == 'sph':
            egSamp = 'phdata'
            mgSamp = 'phdata'
        elif dataSource == 'sel':
            egSamp = 'eldata'
            mgSamp = 'mudata'
    
        for sname in skimConfig[egSamp][0]:
            egPlotter.addInputPath(utils.getSkimPath(sname, 'tpeg'))
    
        for sname in skimConfig[mgSamp][0]:
            mgPlotter.addInputPath(utils.getSkimPath(sname, 'tpmg'))

        if dataSource == 'sph' and analysis == 'monophoton':
            egPlotter.setBaseSelection('probes.triggerMatch[][8]') # 8 = fPh165HE10
            mgPlotter.setBaseSelection('probes.triggerMatch[][8]')
        elif dataSource == 'sel':
            egPlotter.setBaseSelection('tags.pt_ > 40.')
            mgPlotter.setBaseSelection('tags.pt_ > 40.')

else:
    trigsource = ROOT.TFile.Open(basedir + '/data/trigger_efficiency.root')
    eleTrigEff = trigsource.Get('electron_sel/leppt/el27_eff')
    muTrigEff = trigsource.Get('muon_smu/leppt/mu24ortrk24_eff')
    if not eleTrigEff or not muTrigEff:
        raise RuntimeError('Trigger efficiency source not found')

    egPlotter.setConstantWeight(lumi)
    mgPlotter.setConstantWeight(lumi)

    if dataSource == 'smu':
        for sname in skimConfig['mcmu'][0]:
            egPlotter.addInputPath(utils.getSkimPath(sname, 'tp2m'))
            mgPlotter.addInputPath(utils.getSkimPath(sname, 'tp2m'))

        egPlotter.setReweight('tags.pt_', muTrigEff)
        mgPlotter.setReweight('tags.pt_', muTrigEff)

    else:
        for sname in skimConfig['mc'][0]:
            egPlotter.addInputPath(utils.getSkimPath(sname, 'tpeg'))
            mgPlotter.addInputPath(utils.getSkimPath(sname, 'tpmg'))

        egPlotter.setReweight('tags.pt_', eleTrigEff)
        mgPlotter.setReweight('tags.pt_', muTrigEff)

    if dataSource == 'sel':
        egPlotter.setBaseSelection('tags.pt_ > 40.')
        mgPlotter.setBaseSelection('tags.pt_ > 40.')
    elif dataSource == 'smu':
        egPlotter.setBaseSelection('tags.pt_ > 50. && probes.loose')
        mgPlotter.setBaseSelection('tags.pt_ > 50.')

#    for sname in skimConfig['mcgg'][0]:
#        egPlotter.addInputPath(utils.getSkimPath(sname, 'tpeg'))

objects = []

# fill templates
outputFile.cd()
for bin, fitCut in fitBins:
    if dataType == 'mc':
        hsig = template.Clone('sig_' + bin)
        objects.append(hsig)
        if dataSource == 'sel':
            egPlotter.addPlot(hsig, 'tp.mass', fitCut + ' && TMath::Abs(probes.matchedGenId) == 11 && sample == 1')
        else:
            egPlotter.addPlot(hsig, 'tp.mass', fitCut + ' && sample == 1')

    for conf in tpconfs:
        suffix = conf + '_' + bin

        htarg = template.Clone('target_' + suffix)
        objects.append(htarg)
        # unbinned fit
        # ttarg = ROOT.TTree('target_' + suffix, 'target')
        # objects.append(ttarg)

        if conf == 'ee':
            # target is a histogram with !csafeVeto
            # perform binned max L fit
            cut = 'probes.mediumX[][{itune}] && !probes.csafeVeto && ({fitCut})'.format(itune = itune, fitCut = fitCut)
            bkgcut = cut + ' && !probes.hasCollinearL'
        elif conf == 'eg':
            # target is a tree with vetoCut
            # also perform binned max L fit
            cut = ('probes.mediumX[][{itune}] && {vetoCut} && ({fitCut})').format(itune = itune, vetoCut = vetoCut, fitCut = fitCut)
            bkgcut = cut + ' && !probes.hasCollinearL'
        elif conf == 'pass':
            cut = '({monophSel}) && ({fitCut})'.format(monophSel = monophSel, fitCut = fitCut)
            bkgcut = 'probes.sieie > 0.012 && probes.chIsoX[][{itune}] > 3. && {fitCut}'.format(itune = itune, fitCut = fitCut)
        elif conf == 'fail':
            cut = '!({monophSel}) && ({fitCut})'.format(monophSel = monophSel, fitCut = fitCut)
            bkgcut = 'probes.sieie > 0.012 && probes.chIsoX[][{itune}] > 3. && {fitCut}'.format(itune = itune, fitCut = fitCut)
        elif conf == 'passiso':
            cut = '({iso}) && ({fitCut})'.format(iso = '(probes.chIso + TMath::Max(probes.nhIso + probes.phIso - 0.5 * probes.puIso, 0.)) / probes.pt_ < 0.25', fitCut = fitCut)
#            bkgcut = '{fitCut} && !probes.loose && (probes.chIso + TMath::Max(probes.nhIso + probes.phIso - 0.5 * probes.puIso, 0.)) / probes.pt_ > 0.25'.format(fitCut = fitCut)
            bkgcut = '{fitCut} && !probes.loose'.format(fitCut = fitCut)
        elif conf == 'failiso':
            cut = '({iso}) && ({fitCut})'.format(iso = '(probes.chIso + TMath::Max(probes.nhIso + probes.phIso - 0.5 * probes.puIso, 0.)) / probes.pt_ > 0.25', fitCut = fitCut)
#            bkgcut = '{fitCut} && !probes.loose && (probes.chIso + TMath::Max(probes.nhIso + probes.phIso - 0.5 * probes.puIso, 0.)) / probes.pt_ > 0.25'.format(fitCut = fitCut)
            bkgcut = '{fitCut} && !probes.loose'.format(fitCut = fitCut)

        egPlotter.addPlot(htarg, 'tp.mass', cut)
        # if doing unbinned fits, make a tree
        # egPlotter.addTree(ttarg, cut)
        # egPlotter.addTreeBranch(ttarg, 'mass', 'tp.mass')

        # background is approximately lepton flavor symmetric - will use muon templates
        hMuBkg = template.Clone('mubkg_' + suffix)
        objects.append(hMuBkg)
        tMuBkg = ROOT.TTree('mubkgtree_' + suffix, 'background')
        objects.append(tMuBkg)

        mgPlotter.addPlot(hMuBkg, 'tp.mass', bkgcut)
        mgPlotter.addTree(tMuBkg, bkgcut)
        mgPlotter.addTreeBranch(tMuBkg, 'mass', 'tp.mass')

        if dataType == 'mc' and dataSource != 'smu':
            hTrueBkg = template.Clone('truebkg_' + suffix)
            objects.append(hTrueBkg)
            tTrueBkg = ROOT.TTree('truebkgtree_' + suffix, 'truth background')
            objects.append(tTrueBkg)

            hTrueSig = template.Clone('truesig_' + suffix)
            objects.append(hTrueSig)
            tTrueSig = ROOT.TTree('truesigtree_' + suffix, 'truth signal')
            objects.append(tTrueSig)

            egPlotter.addPlot(hTrueBkg, 'tp.mass', cut + ' && !(TMath::Abs(probes.matchedGenId) == 11 && sample == 1)')
            egPlotter.addTree(tTrueBkg, cut + ' && !(TMath::Abs(probes.matchedGenId) == 11 && sample == 1)')
            egPlotter.addTreeBranch(tTrueBkg, 'mass', 'tp.mass')

            egPlotter.addPlot(hTrueSig, 'tp.mass', cut + ' && (TMath::Abs(probes.matchedGenId) == 11 && sample == 1)')
            egPlotter.addTree(tTrueSig, cut + ' && (TMath::Abs(probes.matchedGenId) == 11 && sample == 1)')
            egPlotter.addTreeBranch(tTrueSig, 'mass', 'tp.mass')

egPlotter.fillPlots()
mgPlotter.fillPlots()

outputFile.cd()
outputFile.Write()
work.Write()

work = None
outputFile.Close()

shutil.copy(tmpOutName, outputName)

print 'Finished template preparation.'
