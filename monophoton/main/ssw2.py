#!/usr/bin/env python

import sys
import os
import socket

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import main.selectors as selectors
import main.plotconfig as plotconfig
import config
from subprocess import Popen, PIPE
import shutil
from glob import glob

defaults = {
    'monoph': selectors.candidate,
    'signalRaw': selectors.signalRaw,
    'efake': selectors.eleProxy,
    'hfake': selectors.hadProxy,
    'hfakeUp': selectors.hadProxyUp,
    'hfakeDown': selectors.hadProxyDown,
    'purity': selectors.purity,
    'purityUp': selectors.purityUp,
    'purityDown': selectors.purityDown,
    'lowmt': selectors.lowmt,
    'lowmtEfake': selectors.lowmtEleProxy,
    'gjets': selectors.gjets,
    'dimu': selectors.dimuon,
    'monomu': selectors.monomuon,
    'monomuHfake': selectors.monomuonHadProxy,
    'diel': selectors.dielectron,
    'monoel': selectors.monoelectron,
    'monoelHfake': selectors.monoelectronHadProxy,
    'elmu': selectors.oppflavor,
    'eefake': selectors.zee,
    'wenu': selectors.wenuall,
    'zeeJets': selectors.zeeJets,
    'zmmJets': selectors.zmmJets
}

data_15 = []
data_sph = ['monoph', 'efake', 'hfake', 'hfakeUp', 'hfakeDown', 'purity', 'purityUp', 'purityDown', 'lowmt', 'lowmtEfake', 'gjets']
data_smu = ['dimu', 'monomu', 'monomuHfake', 'elmu', 'zmmJets']
data_sel = ['diel', 'monoel', 'monoelHfake', 'eefake', 'zeeJets']
mc_cand = ['monoph']
mc_qcd = ['hfake', 'hfakeUp', 'hfakeDown', 'purity', 'purityUp', 'purityDown', 'gjets'] 
mc_sig = ['monoph', 'signalRaw']
mc_lep = ['monomu', 'monoel']
mc_dilep = ['dimu', 'diel', 'elmu', 'zmmJets', 'zeeJets']
mc_vgcand = [(region, selectors.kfactor(defaults[region])) for region in mc_cand]
mc_vglep = [(region, selectors.kfactor(defaults[region])) for region in mc_lep]
mc_vgdilep = [(region, selectors.kfactor(defaults[region])) for region in mc_dilep]
#mc_gj = [('raw', selectors.kfactor(defaults['monoph'])), ('monoph', selectors.kfactor(selectors.gjSmeared)), ('purity', selectors.kfactor(selectors.purity))]
#mc_gj = [('raw', selectors.kfactor(defaults['monoph'])), ('monoph', selectors.kfactor(defaults['monoph'])), ('purity', selectors.kfactor(selectors.purity))]
mc_gj = [(region, selectors.kfactor(defaults[region])) for region in mc_qcd]
mc_wlnu = [(region, selectors.wlnu(defaults[region])) for region in mc_cand] + ['wenu', 'zmmJets', 'zeeJets']
mc_lowmt = ['lowmt']
mc_vglowmt = [(region, selectors.kfactor(defaults[region])) for region in mc_lowmt]

sphLumi = sum(allsamples[s].lumi for s in ['sph-16b2', 'sph-16c2', 'sph-16d2'])
haloNorms = [ 8.7 * allsamples[sph].lumi / sphLumi for sph in ['sph-16b2', 'sph-16c2', 'sph-16d2'] ]

neroSphLumi = allsamples['sph-16b2-d'].lumi + allsamples['sph-16c2-d'].lumi + allsamples['sph-16d2-d'].lumi
neroHaloNorms = [ 1.54 * allsamples[sph].lumi / neroSphLumi for sph in ['sph-16b2-d', 'sph-16c2-d', 'sph-16d2-d'] ]
neroSpikeNorms = [ 1. * allsamples[sph].lumi / neroSphLumi for sph in ['sph-16b2-d', 'sph-16c2-d', 'sph-16d2-d'] ]

selectors = {
    # Data 2016
    # dima
    'sph-16b2-d': data_sph + [('halo', selectors.haloMIP(neroHaloNorms[0]))
                              ,('haloUp', selectors.haloCSC(neroHaloNorms[0]))
                              ,('haloDown', selectors.haloSieie(neroHaloNorms[0]))
                              ,('spikeE2E9', selectors.spikeE2E9(neroSpikeNorms[0]))
                              ,('spikeSieie', selectors.spikeSieie(neroSpikeNorms[0]))
                              ,('spikeSipip', selectors.spikeSipip(neroSpikeNorms[0]))
                              ],
    'sph-16c2-d': data_sph + [('halo', selectors.haloMIP(neroHaloNorms[1]))
                              ,('haloUp', selectors.haloCSC(neroHaloNorms[1]))
                              ,('haloDown', selectors.haloSieie(neroHaloNorms[1]))
                              ,('spikeE2E9', selectors.spikeE2E9(neroSpikeNorms[1]))
                              ,('spikeSieie', selectors.spikeSieie(neroSpikeNorms[1]))
                              ,('spikeSipip', selectors.spikeSipip(neroSpikeNorms[1]))
                              ],
    'sph-16d2-d': data_sph + [('halo', selectors.haloMIP(neroHaloNorms[2]))
                              ,('haloUp', selectors.haloCSC(neroHaloNorms[2]))
                              ,('haloDown', selectors.haloSieie(neroHaloNorms[2]))
                              ,('spikeE2E9', selectors.spikeE2E9(neroSpikeNorms[2]))
                              ,('spikeSieie', selectors.spikeSieie(neroSpikeNorms[2]))
                              ,('spikeSipip', selectors.spikeSipip(neroSpikeNorms[2]))
                              ],
    'smu-16b2-d': data_smu,
    'smu-16c2-d': data_smu,
    'smu-16d2-d': data_smu,
    'sel-16b2-d': data_sel,
    'sel-16c2-d': data_sel,
    'sel-16d2-d': data_sel,
    # simple tree
    'sph-16b2': data_sph + [('halo', selectors.haloMIP(haloNorms[0]))
                            ,('haloUp', selectors.haloCSC(haloNorms[0]))
                            ,('haloDown', selectors.haloSieie(haloNorms[0]))
                             ],
    'sph-16c2': data_sph + [('halo', selectors.haloMIP(haloNorms[0]))
                            ,('haloUp', selectors.haloCSC(haloNorms[0]))
                            ,('haloDown', selectors.haloSieie(haloNorms[0]))
                             ],
    'sph-16d2': data_sph + [('halo', selectors.haloMIP(haloNorms[0]))
                            ,('haloUp', selectors.haloCSC(haloNorms[0]))
                            ,('haloDown', selectors.haloSieie(haloNorms[0]))
                             ],
    'smu-16b2': data_smu,
    'smu-16c2': data_smu,
    # 'smu-16d2': data_smu,
    'sel-16b2': data_sel,
    'sel-16c2': data_sel,
    'sel-16d2': data_sel,
    # Data 2015 rereco
    'sph-15d': data_15,
    'smu-15d': data_15,
    'sel-15d': data_15,
    # Data 2015 prompt reco
    'sph-d3': data_15,
    'sph-d4': data_15,
    'smu-d3': data_15,
    'smu-d4': data_15,
    'sel-d3': data_15,
    'sel-d4': data_15,
    # MC for signal region
    'znng-130': mc_vgcand + mc_vglowmt,
    'znng-d'  : mc_vgcand + mc_vglowmt,
    'wnlg-130': mc_vgcand + mc_vglep + mc_vglowmt,
    'wnlg-d'  : mc_vgcand + mc_vglep + mc_vglowmt,
    'zg': mc_cand + mc_lep + mc_dilep + mc_lowmt,
    'zllg-130': mc_vgcand + mc_vglep + mc_vgdilep + mc_vglowmt,
    # 'wg': mc_cand + mc_lep + mc_lowmt,
    'wglo': mc_cand + mc_lep + mc_lowmt,
    'gj-40': mc_gj + mc_lowmt,
    'gj-100': mc_gj + mc_lowmt,
    'gj-200': mc_gj + mc_lowmt,
    'gj-400': mc_gj + mc_lowmt,
    'gj-600': mc_gj + mc_lowmt,
    'gj-40-d': mc_gj + mc_lowmt,
    'gj-100-d': mc_gj + mc_lowmt,
    'gj-200-d': mc_gj + mc_lowmt,
    'gj-400-d': mc_gj + mc_lowmt,
    'gj-600-d': mc_gj + mc_lowmt,
    'gj04-40': mc_gj + mc_lowmt,
    'gj04-100': mc_gj + mc_lowmt,
    'gj04-200': mc_gj + mc_lowmt,
    'gj04-400': mc_gj + mc_lowmt,
    'gj04-600': mc_gj + mc_lowmt,
    'gg-80': mc_cand + mc_lowmt,
    'tg': mc_cand + mc_lep + mc_lowmt, 
    'ttg': mc_cand + mc_lep + mc_dilep + mc_lowmt,
    'wwg': mc_cand + mc_lep + mc_dilep + mc_lowmt,
    'ww': mc_cand + mc_lep + mc_dilep + mc_lowmt,
    'wz': mc_cand + mc_lep + mc_dilep + mc_lowmt,
    'zz': mc_cand + mc_lep + mc_dilep + mc_lowmt,
    'tt': mc_cand + mc_lep + mc_dilep,
    # 'zllg-130': mc_vgcand + mc_vglep + mc_vgdilep,
    'wlnu': mc_wlnu + mc_lep,
    'wlnu-100': mc_wlnu + mc_lep,
    'wlnu-200': mc_wlnu + mc_lep, 
    'wlnu-400': mc_wlnu + mc_lep, 
    'wlnu-600': mc_wlnu + mc_lep, 
    'wlnu-800': mc_wlnu + mc_lep,
    'wlnu-1200': mc_wlnu + mc_lep,
    'wlnu-2500': mc_wlnu + mc_lep,
    'dy-50': mc_cand + mc_lep + mc_dilep,
    'dy-50-100': mc_cand + mc_lep + mc_dilep,
    'dy-50-200': mc_cand + mc_lep + mc_dilep,
    'dy-50-400': mc_cand + mc_lep + mc_dilep,
    'dy-50-600': mc_cand + mc_lep + mc_dilep,
    'qcd-200': mc_cand + mc_qcd + mc_dilep + mc_lep,
    'qcd-300': mc_cand + mc_qcd + mc_dilep + mc_lep,
    'qcd-500': mc_cand + mc_qcd + mc_dilep + mc_lep,
    'qcd-700': mc_cand + mc_qcd + mc_dilep + mc_lep,
    'qcd-1000': mc_cand + mc_qcd + mc_dilep + mc_lep,
    'qcd-1500': mc_cand + mc_qcd + mc_dilep + mc_lep,
    'qcd-2000': mc_cand + mc_qcd + mc_dilep + mc_lep
}

# all the rest are mc_sig
for sname in allsamples.names():
    if sname not in selectors:
        selectors[sname] = mc_sig

def processSampleNames(_inputNames, _selectorKeys, _plotConfig = ''):
    snames = []

    if _plotConfig:
        # if a plot config is specified, use the samples for that
        snames = plotconfig.getConfig(_plotConfig).samples()

    else:
        snames = _inputNames

    # handle special group names
    if 'all' in snames:
        snames.remove('all')
        snames = _selectorKeys
    if 'data16' in snames:
        snames.remove('data16')
        snames += [key for key in _selectorKeys if '16' in key and allsamples[key].data]
    if 'bkgd' in snames:
        snames.remove('bkgd')
        snames += [key for key in _selectorKeys if not allsamples[key].data and not key.startswith('dm') and not key.startswith('add') and not key.endswith('-d')]
    if 'dmfs' in snames:
        snames.remove('dmfs')
        snames += [key for key in _selectorKeys if key.startswith('dm') and key[3:5] == 'fs']
    if 'dm' in snames:
        snames.remove('dm')
        snames += [key for key in _selectorKeys if key.startswith('dm') and not key[3:5] == 'fs']
    if 'add' in snames:
        snames.remove('add')
        snames += [key for key in _selectorKeys if key.startswith('add')]
    if 'fs' in snames:
        snames.remove('fs')
        snames += [key for key in _selectorKeys if 'fs' in key]

    # filter out empty samples
    tmp = [name for name in snames if allsamples[name].sumw != 0.]
    snames = tmp

    return snames

if __name__ == '__main__':

    from argparse import ArgumentParser
    import json
    
    argParser = ArgumentParser(description = 'Plot and count')
    argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '*', help = 'Sample names to skim.')
    argParser.add_argument('--list', '-L', action = 'store_true', dest = 'list', help = 'List of samples.')
    argParser.add_argument('--plot-config', '-p', metavar = 'PLOTCONFIG', dest = 'plotConfig', default = '', help = 'Run on samples used in PLOTCONFIG.')
    argParser.add_argument('--nero-input', '-n', action = 'store_true', dest = 'neroInput', help = 'Specify that input is Nero instead of simpletree.')
    argParser.add_argument('--eos-input', '-e', action = 'store_true', dest = 'eosInput', help = 'Specify that input needs to be read from eos.')
    argParser.add_argument('--nentries', '-N', metavar = 'N', dest = 'nentries', type = int, default = -1, help = 'Maximum number of entries.')
    argParser.add_argument('--files', '-f', metavar = 'nStart nEnd', dest = 'files', nargs = 2, type = int, default = [], help = 'Range of files to run on.')
    
    args = argParser.parse_args()
    sys.argv = []

    import ROOT

    ROOT.gSystem.Load(config.libsimpletree)
    ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')
    ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/tools')
    ROOT.gSystem.AddIncludePath('-I' + os.path.dirname(basedir) + '/common')
    ROOT.gSystem.AddIncludePath('-I' + config.nerocorepath + '/interface')

    if args.neroInput:
        ROOT.gSystem.Load(config.libnerocore)
        ROOT.gROOT.LoadMacro(os.path.dirname(basedir) + '/common/GoodLumiFilter.cc+')
     
    compiled = ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')
    print compiled
    # doesn't seem to be returning different values if compilation fails :(
    if (compiled < 0 ):
        print "Couldn't compile Skimmer.cc. Quitting."
        sys.exit()

    snames = processSampleNames(args.snames, selectors.keys(), args.plotConfig)

    if args.list:
        print ' '.join(sorted(snames))
        # for sname in sorted(snames):
            # print sname
        sys.exit(0)
    
    skimmer = ROOT.Skimmer()

    if args.neroInput:
        goodLumi = ROOT.GoodLumiFilter()

        with open(os.environ['MIT_JSON_DIR'] + '/Cert_271036-276811_13TeV_PromptReco_Collisions16_JSON_NoL1T.txt') as source:
            lumiList = json.loads(source.read())

            for run, lumiranges in lumiList.items():
                for lumirange in lumiranges:
                    lumirange[1] += 1
                    for lumi in range(*tuple(lumirange)):
                        goodLumi.addLumi(int(run), lumi)

        skimmer.addGoodLumiFilter(goodLumi)
    
    if not os.path.exists(config.skimDir):
        os.makedirs(config.skimDir)

    if args.files:
        nStart = args.files[0]
        nEnd = args.files[1]
    else:
        nStart = -1
        nEnd = 100000

    for sname in snames:
        sample = allsamples[sname]
        print 'Starting sample %s (%d/%d)' % (sname, snames.index(sname) + 1, len(snames))
    
        skimmer.reset()
    
        if args.neroInput:
            tree = ROOT.TChain('nero/events')
            if sample.data:
                skimmer.setUseLumiFilter(True)
        else:
            tree = ROOT.TChain('events')

        if os.path.exists(config.photonSkimDir + '/' + sname + '.root'):
            print 'Reading', sname, 'from', config.photonSkimDir
            tree.Add(config.photonSkimDir + '/' + sname + '.root')

        else:
            if args.eosInput:
                sourceDir = sample.book + '/' + sample.fullname
            elif sample.data:
                sourceDir = config.dataNtuplesDir + sample.book + '/' + sample.fullname
            else:
                sourceDir = config.ntuplesDir + sample.book + '/' + sample.fullname

            print 'Reading', sname, 'from', sourceDir

            if args.eosInput:
                # lsCmd = ['/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select', 'ls', sourceDir + '/*.root']
                lsCmd = ['lcg-ls', '-b', '-D', 'srmv2', 'srm://srm-eoscms.cern.ch:8443/srm/v2/server?SFN='+sourceDir]
                listFiles = Popen(lsCmd, stdout=PIPE, stderr=PIPE)
            
                """
                (lout, lerr) = listFiles.communicate()
                print lout, '\n'
                print lerr, '\n'
                sys.exit()
                """
                
                filesList = [ line for line in listFiles.stdout if line.endswith('.root\n') ] 
                pathPrefix = 'root://eoscms'
            else:
                filesList = sorted(glob(sourceDir + '/*.root'))
                
            for iF, File in enumerate(filesList):
                if iF < nStart:
                    continue
                if iF > nEnd:
                    break
                File = File.strip(' \n')
                
                if args.eosInput:
                    print pathPrefix + File
                    tree.Add(pathPrefix + File)
                else:
                    tree.Add(File)

        print tree.GetEntries()
        if tree.GetEntries() == 0:
            print 'Tree has no entries. Skipping.'
            continue

        selnames = []
        for selconf in selectors[sname]:
            if type(selconf) == str:
                rname = selconf
                gen = defaults[rname]
            else:
                rname, gen = selconf

            selnames.append(rname)
            selector = gen(sample, rname)
            skimmer.addSelector(selector)

        if nStart >= 0:
            sname = sname + '_' + str(nStart) + '-' + str(nEnd)

        tmpDir = '/tmp/ballen'
        if not os.path.exists(tmpDir):
            os.makedirs(tmpDir)
        skimmer.run(tree, tmpDir, sname, args.nentries, args.neroInput)
        for selname in selnames:
            if os.path.exists(config.skimDir + '/' + sname + '_' + selname + '.root'):
                os.remove(config.skimDir + '/' + sname + '_' + selname + '.root')
            shutil.move(tmpDir + '/' + sname + '_' + selname + '.root', config.skimDir)
