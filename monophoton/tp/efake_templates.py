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
from tp.efake_conf import skimConfig, lumiSamples, outputDir, roofitDictsDir, getBinning
import tp.efake_plot as efake_plot

dataType = sys.argv[1] # "data" or "mc"
binningName = sys.argv[2] # see efake_conf

dataSource = 'sph' # sph or sel or smu
# panda::XPhoton::IDTune
itune = 1

if dataSource == 'sph':
    tpconfs = ['ee', 'eg', 'pass', 'fail']
elif dataSource == 'sel':
    tpconfs = ['ee', 'eg']
elif dataSource == 'smu':
    tpconfs = ['passiso', 'failiso']

monophSel = 'probes.mediumX[][%d] && probes.mipEnergy < 4.9 && TMath::Abs(probes.time) < 3. && probes.sieie > 0.001 && probes.sipip > 0.001' % itune

fitBins = getBinning(binningName)[2]

lumi = sum(allsamples[s].lumi for s in lumiSamples)

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load('libRooFit.so')
ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')
ROOT.gSystem.Load(roofitDictsDir + '/libCommonRooFit.so') # defines KeysShape

### Files ###

outputName = outputDir + '/fityields_' + dataType + '_' + binningName + '.root'

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

fitBinningT = (120, 60., 120.)
fitBinning = ROOT.RooUniformBinning(fitBinningT[1], fitBinningT[2], fitBinningT[0])
compBinning = ROOT.RooUniformBinning(81., 101., 20)

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
mass.setBinning(compBinning, 'compWindow')

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
    
        if dataSource == 'sel':
            egPlotter.setBaseSelection('tags.pt_ > 40.')
            mgPlotter.setBaseSelection('tags.pt_ > 40.')

    mcSource = ROOT.TFile.Open(outputDir + '/fityields_mc_' + binningName + '.root')
    mcWork = mcSource.Get('work')

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
        egPlotter.setBaseSelection('tags.pt_ > 50.')
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
            # target is a tree with pixelVeto
            # also perform binned max L fit
            cut = 'probes.mediumX[][{itune}] && probes.pixelVeto && ({fitCut})'.format(itune = itune, fitCut = fitCut)
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
        hbkg = template.Clone('bkg_' + suffix)
        objects.append(hbkg)
        tbkg = ROOT.TTree('bkgtree_' + suffix, 'background')
        objects.append(tbkg)

        mgPlotter.addPlot(hbkg, 'tp.mass', bkgcut)
        mgPlotter.addTree(tbkg, bkgcut)
        mgPlotter.addTreeBranch(tbkg, 'mass', 'tp.mass')

        if dataType == 'mc' and dataSource != 'smu':
            hmcbkg = template.Clone('mcbkg_' + suffix)
            objects.append(hmcbkg)
            tmcbkg = ROOT.TTree('mcbkgtree_' + suffix, 'truth background')
            objects.append(tmcbkg)

            egPlotter.addPlot(hmcbkg, 'tp.mass', cut + ' && !(TMath::Abs(probes.matchedGenId) == 11 && sample == 1)')
            egPlotter.addTree(tmcbkg, cut + ' && !(TMath::Abs(probes.matchedGenId) == 11 && sample == 1)')
            egPlotter.addTreeBranch(tmcbkg, 'mass', 'tp.mass')

egPlotter.fillPlots()
mgPlotter.fillPlots()

outputFile.cd()
outputFile.Write()
work.Write()

work = None
outputFile.Close()

shutil.copy(tmpOutName, outputName)

print 'Finished template preparation.'
