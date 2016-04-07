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
    'dimu': selectors.dimuon,
    'monomu': selectors.monomuon,
    'diel': selectors.dielectron,
    'monoel': selectors.monoelectron,
    'elmu': selectors.oppflavor,
    'eefake': selectors.zee
}

data_sph = ['monoph', 'efake', 'hfake', 'hfakeUp', 'hfakeDown', 'purity', 'purityUp', 'purityDown']
data_smu = ['dimu', 'monomu', 'elmu']
data_sel = ['diel', 'monoel', 'eefake']
mc_cand = ['monoph'] 
mc_sig = ['monoph', 'signalRaw']
mc_lep = ['monomu', 'monoel']
mc_dilep = ['dimu', 'diel', 'elmu']
mc_vgcand = [(region, selectors.kfactor(defaults[region])) for region in mc_cand]
mc_vglep = [(region, selectors.kfactor(defaults[region])) for region in mc_lep]
mc_vgdilep = [(region, selectors.kfactor(defaults[region])) for region in mc_dilep]
mc_gj = [('monoph', selectors.kfactor(selectors.gjSmeared)), ('purity', selectors.kfactor(selectors.purity))]
mc_wlnu = [(region, selectors.wlnu(defaults[region])) for region in mc_cand]

sphLumi = allsamples['sph-d3'].lumi + allsamples['sph-d4'].lumi
haloNorms = [ 5.9 * allsamples[sph].lumi / sphLumi for sph in ['sph-d3', 'sph-d4'] ]

selectors = {
    # Data
    'sph-d3': data_sph + [('halo', selectors.halo(haloNorms[0]))
                          ,('haloUp', selectors.haloCSC(haloNorms[0]))
                          ,('haloDown', selectors.haloSieie(haloNorms[0]))
                          ],
    'sph-d4': data_sph + [('halo', selectors.halo(haloNorms[1]))
                          ,('haloUp', selectors.haloCSC(haloNorms[1]))
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
    'gj-40': mc_gj,
    'gj-100': mc_gj,
    'gj-200': mc_gj,
    'gj-400': mc_gj,
    'gj-600': mc_gj,
    'ttg': mc_cand + mc_lep + mc_dilep,
    'zllg-130': mc_vgcand + mc_vglep + mc_vgdilep,
    'wlnu-100': mc_wlnu,
    'wlnu-200': mc_wlnu,
    'wlnu-400': mc_wlnu,
    'wlnu-600': mc_wlnu
}

for sname in ['add-%d-%d' % (nd, md) for md in [1, 2, 3] for nd in [3, 4, 5, 6, 8]]:
    selectors[sname] = mc_cand

for mt in ['a', 'v']:
    for dm in [1, 10, 50, 150, 500, 1000]:
        for mm in [10, 20, 50, 100, 200, 300, 500, 1000, 2000, 10000]:
            if mm == 2 * dm:
                mm = mm - 5
            for prod in ['', 'fs']:
                sname = 'dm%s%s-%d-%d' % (mt, prod, mm, dm)
                try:
                    # print sname
                    allsamples[sname]
                except KeyError:
                    # print "This combination is not part of the DMWG recommendations, moving onto next one."
                    continue;

                selectors[sname] = mc_sig

for sname in ['dmewk-%d-%d' % (_lambda, mx) for _lambda in [3000] for mx in [1, 10, 50, 100, 200, 400, 800, 1300]]:
    selectors[sname] = mc_cand

for sname in ['zgr-750-%s' % width for width in ['0014', '5600']]:
    selectors[sname] = mc_cand

if __name__ == '__main__':

    from argparse import ArgumentParser
    
    argParser = ArgumentParser(description = 'Plot and count')
    argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '*', help = 'Sample names to skim.')
    argParser.add_argument('--list', '-L', action = 'store_true', dest = 'list', help = 'List of samples.')
    argParser.add_argument('--plot-config', '-p', metavar = 'PLOTCONFIG', dest = 'plotConfig', default = '', help = 'Run on samples used in PLOTCONFIG.')
    
    args = argParser.parse_args()
    sys.argv = []

    import ROOT

    ROOT.gSystem.Load('libMitFlatDataFormats.so')
    ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
    
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
    if 'dm' in snames:
        snames.remove('dm')
        snames += [key for key in selectors.keys() if key.startswith('dm')]
    if 'add' in snames:
        snames.remove('add')
        snames += [key for key in selectors.keys() if key.startswith('add')]

    # filter out empty samples
    tmp = [name for name in snames if allsamples[name].sumw > 0.]
    snames = tmp

    if args.list:
        print ' '.join(sorted(snames))
        sys.exit(0)
    
    skimmer = ROOT.Skimmer()
    
    if not os.path.exists(config.skimDir):
        os.makedirs(config.skimDir)

    for sname in snames:
        sample = allsamples[sname]
        print 'Starting sample %s (%d/%d)' % (sname, snames.index(sname) + 1, len(snames))
    
        skimmer.reset()
    
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
            tree.Add(sourceDir + '/simpletree*.root')
    
        for selconf in selectors[sname]:
            if type(selconf) == str:
                rname = selconf
                gen = defaults[rname]
            else:
                rname, gen = selconf

            selector = gen(sample, rname)
            skimmer.addSelector(selector)
    
        skimmer.run(tree, config.skimDir, sname, -1)
