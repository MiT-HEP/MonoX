#!/usr/bin/env python

import sys
import os

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import main.selectors as selectors
import main.plotconfig as plotconfig
import config

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
    'gjets': selectors.gjets,
    'dimu': selectors.dimuon,
    'monomu': selectors.monomuon,
    'diel': selectors.dielectron,
    'monoel': selectors.monoelectron,
    'elmu': selectors.oppflavor,
    'eefake': selectors.zee,
    'wenu': selectors.wenuall
}

data_sph = ['monoph', 'efake', 'hfake', 'hfakeUp', 'hfakeDown', 'purity', 'purityUp', 'purityDown', 'gjets']
data_smu = ['dimu', 'monomu', 'elmu']
data_sel = ['diel', 'monoel', 'eefake']
mc_cand = ['monoph']
mc_qcd = ['hfake', 'hfakeUp', 'hfakeDown', 'purity', 'purityUp', 'purityDown', 'gjets'] 
mc_sig = ['monoph', 'signalRaw']
mc_lep = ['monomu', 'monoel']
mc_dilep = ['dimu', 'diel', 'elmu']
mc_vgcand = [(region, selectors.kfactor(defaults[region])) for region in mc_cand]
mc_vglep = [(region, selectors.kfactor(defaults[region])) for region in mc_lep]
mc_vgdilep = [(region, selectors.kfactor(defaults[region])) for region in mc_dilep]
mc_gj = [('monoph', selectors.kfactor(selectors.gjSmeared)), ('purity', selectors.kfactor(selectors.purity))]
mc_wlnu = [(region, selectors.wlnu(defaults[region])) for region in mc_cand] + ['wenu']

sphLumi = allsamples['sph-d3'].lumi + allsamples['sph-d4'].lumi
haloNorms = [ 5.9 * allsamples[sph].lumi / sphLumi for sph in ['sph-d3', 'sph-d4'] ]

selectors = {
    # Data 2016
    'sph-b2': [ 'monoph' ],
    # Data 2015
    'sph-d3': data_sph + [('halo', selectors.haloCSC(haloNorms[0]))
                          ,('haloUp', selectors.haloMIP(haloNorms[0]))
                          ,('haloDown', selectors.haloSieie(haloNorms[0]))
                          ],
    'sph-d4': data_sph + [('halo', selectors.haloCSC(haloNorms[1]))
                          ,('haloUp', selectors.haloMIP(haloNorms[1]))
                          ,('haloDown', selectors.haloSieie(haloNorms[1]))
                          ],
    'smu-d3': data_smu,
    'smu-d4': data_smu,
    'sel-d3': data_sel,
    'sel-d4': data_sel,
    # MC for signal region
    'znng-130': mc_vgcand,
    'wnlg-130': mc_vgcand + mc_vglep,
    'zg': mc_cand + mc_lep + mc_dilep,
    'wg': mc_cand,
    'gj-40': mc_gj + mc_qcd,
    'gj-100': mc_gj + mc_qcd,
    'gj-200': mc_gj + mc_qcd,
    'gj-400': mc_gj + mc_qcd,
    'gj-600': mc_gj + mc_qcd,
    'ttg': mc_cand + mc_lep + mc_dilep,
    'tt': mc_cand + mc_lep + mc_dilep,
    'zllg-130': mc_vgcand + mc_vglep + mc_vgdilep,
    'wlnu': mc_wlnu,
    'wlnu-100': mc_wlnu,
    'wlnu-200': mc_wlnu, 
    'wlnu-400': mc_wlnu, 
    'wlnu-600': mc_wlnu, 
    'dy-50-100': mc_cand + mc_lep + mc_dilep,
    'dy-50-200': mc_cand + mc_lep + mc_dilep,
    'dy-50-400': mc_cand + mc_lep + mc_dilep,
    'dy-50-600': mc_cand + mc_lep + mc_dilep,
    'qcd-200': mc_cand + mc_qcd,
    'qcd-300': mc_cand + mc_qcd,
    'qcd-500': mc_cand + mc_qcd,
    'qcd-700': mc_cand + mc_qcd,
    'qcd-1000': mc_cand + mc_qcd
}

# all the rest are mc_sig
for sname in allsamples.names():
    if sname not in selectors:
        selectors[sname] = mc_sig


if __name__ == '__main__':

    from argparse import ArgumentParser
    
    argParser = ArgumentParser(description = 'Plot and count')
    argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '*', help = 'Sample names to skim.')
    argParser.add_argument('--list', '-L', action = 'store_true', dest = 'list', help = 'List of samples.')
    argParser.add_argument('--plot-config', '-p', metavar = 'PLOTCONFIG', dest = 'plotConfig', default = '', help = 'Run on samples used in PLOTCONFIG.')
    argParser.add_argument('--nero-input', '-n', action = 'store_true', dest = 'neroInput', help = 'Specify that input is Nero instead of simpletree.')
    
    args = argParser.parse_args()
    sys.argv = []

    import ROOT

    ROOT.gSystem.Load(config.libsimpletree)
    ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')
    ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/tools')

    ROOT.gSystem.Load(config.libnerocore)
    ROOT.gSystem.AddIncludePath('-I' + config.nerocorepath + '/interface')

    ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')

    snames = []

    if args.plotConfig:
        # if a plot config is specified, use the samples for that
        snames = plotconfig.getConfig(args.plotConfig).samples()

    else:
        snames = args.snames

    # handle special group names
    if 'all' in snames:
        snames.remove('all')
        snames = selectors.keys()
    elif 'dmfs' in snames:
        snames.remove('dmfs')
        snames += [key for key in selectors.keys() if key.startswith('dm') and key[3:5] == 'fs']
    elif 'dm' in snames:
        snames.remove('dm')
        snames += [key for key in selectors.keys() if key.startswith('dm')]
    elif 'add' in snames:
        snames.remove('add')
        snames += [key for key in selectors.keys() if key.startswith('add')]
    if 'fs' in snames:
        snames.remove('fs')
        snames += [key for key in selectors.keys() if 'fs' in key]

    # filter out empty samples
    tmp = [name for name in snames if allsamples[name].sumw > 0.]
    snames = tmp

    if args.list:
        print ' '.join(sorted(snames))
        # for sname in sorted(snames):
            # print sname
        sys.exit(0)
    
    skimmer = ROOT.Skimmer()
    
    if not os.path.exists(config.skimDir):
        os.makedirs(config.skimDir)

    for sname in snames:
        sample = allsamples[sname]
        print 'Starting sample %s (%d/%d)' % (sname, snames.index(sname) + 1, len(snames))
    
        skimmer.reset()
    
        if args.neroInput:
            tree = ROOT.TChain('nero/events')
        else:
            tree = ROOT.TChain('events')

        if os.path.exists(config.phskimDir + '/' + sname + '.root'):
            print 'Reading', sname, 'from', config.phskimDir
            tree.Add(config.phskimDir + '/' + sname + '.root')

        else:
            if sample.data:
                sourceDir = config.dataNtuplesDir + sample.book + '/' + sample.directory
            else:
                sourceDir = config.ntuplesDir + sample.book + '/' + sample.directory

            print 'Reading', sname, 'from', sourceDir
            if args.neroInput:
                if sample.data:
                    tree.Add(sourceDir + '/NeroNtuples_Photon_9*.root')
                else:
                    tree.Add(sourceDir + '/NeroNtuples_*.root')
            else:
                tree.Add(sourceDir + '/simpletree*.root')

        print tree.GetEntries()
    
        for selconf in selectors[sname]:
            if type(selconf) == str:
                rname = selconf
                gen = defaults[rname]
            else:
                rname, gen = selconf

            selector = gen(sample, rname)
            skimmer.addSelector(selector)
    
        skimmer.run(tree, config.skimDir, sname, -1, args.neroInput)
