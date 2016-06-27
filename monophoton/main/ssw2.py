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
    'lowmt': selectors.lowmt,
    'lowmtEfake': selectors.lowmtEleProxy,
    'gjets': selectors.gjets,
    'dimu': selectors.dimuon,
    'monomu': selectors.monomuon,
    'diel': selectors.dielectron,
    'monoel': selectors.monoelectron,
    'elmu': selectors.oppflavor,
    'eefake': selectors.zee,
    'wenu': selectors.wenuall
}

data_sph = ['monoph', 'efake', 'hfake', 'hfakeUp', 'hfakeDown', 'purity', 'purityUp', 'purityDown', 'lowmt', 'lowmtEfake', 'gjets']
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
mc_lowmt = ['lowmt']
mc_vglowmt = [(region, selectors.kfactor(defaults[region])) for region in mc_lowmt]

sphLumi = allsamples['sph-16b2'].lumi
haloNorms = [ 5.9 * allsamples[sph].lumi / sphLumi for sph in ['sph-16b2'] ]

selectors = {
    # Data 2016
    'sph-16b2': data_sph,
    'smu-16b2': data_smu,
    'sel-16b2': data_sel,
    # MC for signal region
    'znng-130': mc_vgcand + mc_vglowmt,
    'wnlg-130': mc_vgcand + mc_vglep + mc_vglowmt,
    'zg': mc_cand + mc_lep + mc_dilep + mc_lowmt,
    'wg': mc_cand + mc_lowmt,
    'gj-40': mc_gj + mc_qcd + mc_lowmt,
    'gj-100': mc_gj + mc_qcd + mc_lowmt,
    'gj-200': mc_gj + mc_qcd + mc_lowmt,
    'gj-400': mc_gj + mc_qcd + mc_lowmt,
    'gj-600': mc_gj + mc_qcd + mc_lowmt,
    'ttg': mc_cand + mc_lep + mc_dilep + mc_lowmt,
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
    argParser.add_argument('--nentries', '-n', metavar = 'N', dest = 'nentries', type = int, default = -1, help = 'Maximum number of entries.')
    
    args = argParser.parse_args()
    sys.argv = []

    import ROOT

    ROOT.gSystem.Load(config.libsimpletree)
    ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')
    
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
    tmp = [name for name in snames if allsamples[name].sumw != 0.]
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
    
        tree = ROOT.TChain('events')

        if os.path.exists(config.photonSkimDir + '/' + sname + '.root'):
            print 'Reading', sname, 'from', config.photonSkimDir
            tree.Add(config.photonSkimDir + '/' + sname + '.root')

        else:
            if sample.data:
                sourceDir = config.dataNtuplesDir + sample.book + '/' + sample.fullname
            else:
                sourceDir = config.ntuplesDir + sample.book + '/' + sample.fullname

            print 'Reading', sname, 'from', sourceDir
            tree.Add(sourceDir + '/*.root')
    
        for selconf in selectors[sname]:
            if type(selconf) == str:
                rname = selconf
                gen = defaults[rname]
            else:
                rname, gen = selconf

            selector = gen(sample, rname)
            skimmer.addSelector(selector)

        skimmer.run(tree, config.skimDir, sname, args.nentries)
