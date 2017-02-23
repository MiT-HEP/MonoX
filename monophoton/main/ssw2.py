#!/usr/bin/env python

import sys
import os
import socket
import time

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

defaultSelectors = {
    'monoph': selectors.candidate,
    'signalRaw': selectors.signalRaw,
    'efake': selectors.eleProxy,
    'hfake': selectors.hadProxy,
    'hfakeTight': selectors.hadProxyTight,
    'hfakeLoose': selectors.hadProxyLoose,
    'hfakeVLoose': selectors.hadProxyVLoose,
    'purity': selectors.purity,
    'purityNom': selectors.purityNom,
    'purityTight': selectors.purityTight,
    'purityLoose': selectors.purityLoose,
    'purityVLoose': selectors.purityVLoose,
    'gjets': selectors.gjets,
    'halo': selectors.halo,
    'haloMIP': selectors.haloMIP,
    'haloMET': selectors.haloMET,
    'haloLoose': selectors.haloLoose,
    'haloMIPLoose': selectors.haloMIPLoose,
    'haloMETLoose': selectors.haloMETLoose,
    'haloMedium': selectors.haloMedium,
    'haloMIPMedium': selectors.haloMIPMedium,
    'haloMETMedium': selectors.haloMETMedium,
    'trivialShower': selectors.trivialShower,
    'dimu': selectors.dimuon,
    'dimuHfake': selectors.dimuonHadProxy,
    'monomu': selectors.monomuon,
    'monomuHfake': selectors.monomuonHadProxy,
    'diel': selectors.dielectron,
    'dielHfake': selectors.dielectronHadProxy,
    'monoel': selectors.monoelectron,
    'monoelHfake': selectors.monoelectronHadProxy,
    'elmu': selectors.oppflavor,
    'eefake': selectors.zee,
    'wenu': selectors.wenuall,
    'zeeJets': selectors.zeeJets,
    'zmmJets': selectors.zmmJets
}

def defaults(regions):
    return [(region, defaultSelectors[region]) for region in regions]

def applyMod(modifier, regions):
    result = []
    for entry in regions:
        if type(entry) is tuple:
            region, selector = entry
        else:
            region = entry
            selector = defaultSelectors[region]

        result.append((region, modifier(selector)))

    return result

sphLumi = sum(allsamples[s].lumi for s in ['sph-16b-r', 'sph-16c-r', 'sph-16d-r', 'sph-16e-r', 'sph-16f-r', 'sph-16g-r', 'sph-16h'])

data_sph =  ['monoph', 'efake', 'hfake',  'trivialShower'] 
data_sph += ['haloLoose', 'haloMIPLoose', 'haloMETLoose'] # , 'halo', 'haloMIP', 'haloMET', 'haloMedium', 'haloMIPMedium', 'haloMETMedium']
data_sph += ['hfakeTight', 'hfakeLoose'] # , 'hfakeVLoose']
data_sph += ['purity', 'purityNom', 'purityTight', 'purityLoose'] # , 'purityVLoose'] # , 'gjets'] 
data_sph += ['dimu', 'diel', 'monomu', 'monoel'] 
data_sph += ['dimuHfake', 'dielHfake', 'monomuHfake', 'monoelHfake'] 
data_smu = ['dimu', 'monomu', 'monomuHfake', 'elmu', 'zmmJets'] # are SinglePhoton triggers in this PD? (do the samples know about them, obviously they are not used to define it)
data_sel = ['diel', 'monoel', 'monoelHfake', 'eefake', 'zeeJets'] # are SinglePhoton triggers in this PD? (do the samples know about them, obviously they are not used to define it)
mc_cand = ['monoph'] # , 'purity']
mc_qcd = ['hfake', 'hfakeTight', 'hfakeLoose', 'hfakeVLoose', 'purity', 'purityTight', 'purityLoose', 'purityVLoose', 'gjets'] 
mc_sig = ['monoph', 'purity'] # , 'signalRaw']
mc_lep = ['monomu', 'monoel']
mc_dilep = ['dimu', 'diel', 'elmu', 'zmmJets', 'zeeJets']

wlnu = applyMod(selectors.wlnu, applyMod(selectors.genveto, mc_cand)) + applyMod(selectors.genveto, mc_lep) + defaults(['wenu', 'zmmJets', 'zeeJets'])

selectors = {
    # Data 2016
    'sph-16b-m': defaults(data_sph),
    'sph-16c-m': defaults(data_sph),
    'sph-16d-m': defaults(data_sph),
    'sph-16e-m': defaults(data_sph),
    'sph-16f-m': defaults(data_sph),
    'sph-16g-m': defaults(data_sph),
    'sph-16h-m': defaults(data_sph),
    'sph-16b-r': defaults(data_sph),
    'sph-16c-r': defaults(data_sph),
    'sph-16d-r': defaults(data_sph),
    'sph-16e-r': defaults(data_sph),
    'sph-16f-r': defaults(data_sph),
    'sph-16g-r': defaults(data_sph),
    'sph-16h': defaults(data_sph),
    'smu-16b-r': defaults(data_smu),
    'smu-16c-r': defaults(data_smu),
    'smu-16d-r': defaults(data_smu),
    'smu-16e-r': defaults(data_smu),
    'smu-16f-r': defaults(data_smu),
    'smu-16g-r': defaults(data_smu),
    'smu-16h': defaults(data_smu),
    'sel-16b-r': defaults(data_sel),
    'sel-16c-r': defaults(data_sel),
    'sel-16d-r': defaults(data_sel),
    'sel-16e-r': defaults(data_sel),
    'sel-16f-r': defaults(data_sel),
    'sel-16g-r': defaults(data_sel),
    'sel-16h': defaults(data_sel),
    # MC for signal region
    'znng-130': applyMod(selectors.kfactor, mc_sig),
    'wnlg-130': applyMod(selectors.kfactor, mc_sig + mc_lep),
    'zllg-130': applyMod(selectors.kfactor, mc_sig + mc_lep + mc_dilep),
    'wglo': applyMod(selectors.wglo, mc_cand + mc_lep),
    'wglo-500': defaults(mc_cand + mc_lep),
    'gj-100': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gj-200': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gj-400': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gj-600': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gj04-100': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gj04-200': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gj04-400': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gj04-600': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gg-40': defaults(mc_cand + mc_lep + mc_dilep),
    'gg-80': defaults(mc_cand + mc_lep + mc_dilep),
    'tt': defaults(mc_cand + mc_lep + mc_dilep),
    'tg': defaults(mc_cand + mc_lep),
    'ttg': defaults(mc_cand + mc_lep + mc_dilep),
    'wwg': defaults(mc_cand + mc_lep + mc_dilep),
    'ww': defaults(mc_cand + mc_lep + mc_dilep),
    'wz': defaults(mc_cand + mc_lep + mc_dilep),
    'zz': defaults(mc_cand + mc_lep + mc_dilep),
    'wlnu-100': wlnu,
    'wlnu-200': wlnu,
    'wlnu-400': wlnu,
    'wlnu-600': wlnu,
    'wlnu-800': wlnu,
    'wlnu-1200': wlnu,
    'wlnu-2500': wlnu,
    'dy-50': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-100': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-200': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-400': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-600': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-800': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-1200': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-2500': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'qcd-200': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-300': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-500': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-700': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-1000': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-1500': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-2000': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep)
}

# all the rest are mc_sig
for sname in allsamples.names():
    if sname not in selectors:
        selectors[sname] = defaults(mc_sig)

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
    for name in list(snames):
        if '*' in name: # wild card
            snames.remove(name)
            snames.extend([s.name for s in allsamples.getmany(name)])
        try:
            samp = allsamples[name]
        except KeyError:
            print name, "is not in datasets.csv. Removing it from the list of samples to run over."
            snames.remove(name)
            

    snames = [name for name in snames if allsamples[name].sumw != 0.]

    return snames

if __name__ == '__main__':

    padd = os.environ['CMSSW_BASE'] + '/bin/' + os.environ['SCRAM_ARCH'] + '/padd'
    condor_run = '/home/yiiyama/bin/condor-run'

    from argparse import ArgumentParser
    import json
    
    argParser = ArgumentParser(description = 'Plot and count')
    argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '*', help = 'Sample names to skim.')
    argParser.add_argument('--list', '-L', action = 'store_true', dest = 'list', help = 'List of samples.')
    argParser.add_argument('--plot-config', '-p', metavar = 'PLOTCONFIG', dest = 'plotConfig', default = '', help = 'Run on samples used in PLOTCONFIG.')
    argParser.add_argument('--eos-input', '-e', action = 'store_true', dest = 'eosInput', help = 'Specify that input needs to be read from eos.')
    argParser.add_argument('--nentries', '-N', metavar = 'N', dest = 'nentries', type = int, default = -1, help = 'Maximum number of entries.')
    argParser.add_argument('--compile-only', '-C', action = 'store_true', dest = 'compileOnly', help = 'Compile and exit.')
    argParser.add_argument('--filesets', '-f', metavar = 'ID', dest = 'filesets', nargs = '+', default = [], help = 'Fileset id when running in split mode.')
    argParser.add_argument('--split', '-B', action = 'store_true', dest = 'split', help = 'Use condor-run to run one instance per fileset. Output is merged at the end.')
    
    args = argParser.parse_args()
    sys.argv = []

    import ROOT

    ROOT.gSystem.Load(config.libobjs)
    ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')
    ROOT.gSystem.AddIncludePath('-I' + os.path.dirname(basedir) + '/common')

    compiled = ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')
    # doesn't seem to be returning different values if compilation fails :(
    if (compiled < 0 ):
        print "Couldn't compile Skimmer.cc. Quitting."
        sys.exit()

    if args.compileOnly:
        sys.exit(0)

    snames = processSampleNames(args.snames, selectors.keys(), args.plotConfig)

    if args.list:
        print ' '.join(sorted(snames))
        # for sname in sorted(snames):
            # print sname
        sys.exit(0)

    for sname in snames:
        sample = allsamples[sname]
        print 'Starting sample %s (%d/%d)' % (sname, snames.index(sname) + 1, len(snames))

        selnames = []
        for rname, gen in selectors[sname]:
            selnames.append(rname)

        splitOutDir = config.skimDir + '/' + sname

        if len(args.filesets) != 0:
            outDir = splitOutDir
        else:
            outDir = config.skimDir

        if not os.path.exists(outDir):
            os.makedirs(outDir)

        if args.split:
            # Will spawn condor jobs and wait

            if args.eosInput:
                # Case for running on LXPLUS (used for ICHEP 2016 with simpletree from MINIAOD)
                # not maintained any more

                sourceDir = sample.book + '/' + sample.fullname

                # lsCmd = ['/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select', 'ls', sourceDir + '/*.root']
                lsCmd = ['lcg-ls', '-b', '-D', 'srmv2', 'srm://srm-eoscms.cern.ch:8443/srm/v2/server?SFN='+sourceDir]
                listFiles = Popen(lsCmd, stdout=PIPE, stderr=PIPE)
            
                """
                (lout, lerr) = listFiles.communicate()
                print lout, '\n'
                print lerr, '\n'
                sys.exit()
                """

                pathPrefix = 'root://eoscms'                
                filesList = [pathPrefix + line.strip() for line in listFiles.stdout if line.endswith('.root\n')] 

            else:
                filesList = sorted(glob(config.photonSkimDir + '/' + sname + '/*.root'))

            filesets = []

            for fname in filesList:
                fileset = fname[fname.rfind('_') + 1:fname.rfind('.root')]
                if len(args.filesets) != 0 and fileset not in args.filesets:
                    continue

                filesets.append(fileset)

            # remove the output first
            for fileset in filesets:
                for selname in selnames:
                    path = splitOutDir + '/' + sname + '_' + fileset + '_' + selname + '.root'
                    try:
                        os.remove(path)
                    except:
                        pass

            proc = Popen([condor_run, os.path.realpath(__file__), '-H', '-e', sname, '-j'] + ['-f %s' % fileset for fileset in filesets], stdout = PIPE, stderr = PIPE)
            out, err = proc.communicate()
            print out.strip()
            print err.strip()

            print 'Waiting for individual skim jobs to complete.'
        
            while True:
                for fileset in filesets:
                    for selname in selnames:
                        path = splitOutDir + '/' + sname + '_' + fileset + '_' + selname + '.root'
                        if not os.path.exists(path) or os.stat(path).st_size == 0:
                            break
                    else:
                        # all selnames present
                        continue
                    
                    # some selnames missing
                    break
        
                else:
                    # all filesets exist
                    break
        
                time.sleep(10)

            print 'Merging the split skims.'
            for selname in selnames:
                outName = sname + '_' + selname + '.root'

                proc = subprocess.Popen([padd, '/tmp/' + outName] + [splitOutDir + '/' + sname + '_' + fileset + '_' + selname + '.root' for fileset in filesets], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                out, err = proc.communicate()
                print out.strip()
                print err.strip()

                shutil.copy('/tmp/' + outName, config.skimDir)
                os.remove('/tmp/' + outName)

        else:
            # Will do the actual skimming

            skimmer = ROOT.Skimmer()
    
            for rname, gen in selectors[sname]:
                selector = gen(sample, rname)
                skimmer.addSelector(selector)

            tmpDir = '/tmp/' + os.environ['USER'] + '/' + sname
            if not os.path.exists(tmpDir):
                os.makedirs(tmpDir)

            if len(args.filesets) == 0:
                print 'Reading', sname, 'from', config.photonSkimDir
                allpaths = {'': config.photonSkimDir + '/' + sname + '.root'}

            else:
                allpaths = {}
                for fileset in args.filesets:
                    print 'Reading', sname, fileset, 'from', config.photonSkimDir + '/' + sname
                    allpaths['_' + fileset] = config.photonSkimDir + '/' + sname + '/' + sname + '_' + fileset + '.root'

            for suffix, sourcePath in allpaths.items():
                source = ROOT.TFile.Open(sourcePath)
                tree = source.Get('events')

                print tree.GetEntries(), 'entries'
                if tree.GetEntries() == 0:
                    print 'Tree has no entries. Skipping.'
                    continue
    
                skimmer.run(tree, tmpDir, sname + suffix, args.nentries)

                for selname in selnames:
                    outName = sname + suffix + '_' + selname + '.root'

                    shutil.copy(tmpDir + '/' + outName, outDir)
                    os.remove(tmpDir + '/' + outName)
