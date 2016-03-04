#!/usr/bin/env python

import sys
import os
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import main.selectors as selectors
import config

defaults = {
    'monoph': selectors.candidate,
    'efake': selectors.eleProxy,
    'hfake': selectors.hadProxy,
    'hfakeUp': selectors.hadProxyUp,
    'hfakeDown': selectors.hadProxyDown,
    'purity': selectors.purity,
    'gjets': selectors.gammaJets,
    'efakeGJets': selectors.eleProxyGammaJets,
    'hfakeGJets': selectors.hadProxyGammaJets,
    'dimu': selectors.dimuon,
    'monomu': selectors.monomuon,
    'diel': selectors.dielectron,
    'monoel': selectors.monoelectron,
    'elmu': selectors.oppflavor,
    'eefake': selectors.zee
}

data_sph = ['monoph', 'efake', 'hfake', 'hfakeUp', 'hfakeDown', 'purity', 'gjets']
data_smu = ['dimu', 'monomu', 'elmu']
data_sel = ['diel', 'monoel', 'eefake']
mc_cand = ['monoph'] 
mc_purity = ['purity']
mc_lep = ['monomu', 'monoel']
mc_dilep = ['dimu', 'diel', 'elmu']
mc_vgcand = [(region, selectors.kfactor(defaults[region])) for region in mc_cand]
mc_vglep = [(region, selectors.kfactor(defaults[region])) for region in mc_lep]
mc_vgdilep = [(region, selectors.kfactor(defaults[region])) for region in mc_dilep]
mc_wlnu = [(region, selectors.wlnu(defaults[region])) for region in mc_cand]

selectors = {
    # Data
    'sph-d3': data_sph,
    'sph-d4': data_sph,
    'smu-d3': data_smu,
    'smu-d4': data_smu,
    'sel-d3': data_sel,
    'sel-d4': data_sel,
    # MC for signal region
    'znng-130': mc_vgcand,
    'wnlg-130': mc_vgcand + mc_vglep,
    'wg': mc_cand,
    'gj-40': mc_cand + mc_purity,
    'gj-100': mc_cand + mc_purity,
    'gj-200': mc_cand + mc_purity,
    'gj-400': mc_cand + mc_purity,
    'gj-600': mc_cand + mc_purity,
    'ttg': mc_cand + mc_lep + mc_dilep,
    'zllg-130': mc_vgcand + mc_vglep + mc_vgdilep,
    'wlnu-100': mc_wlnu,
    'wlnu-200': mc_wlnu,
    'wlnu-400': mc_wlnu,
    'wlnu-600': mc_wlnu
}

for sname in ['add%d-%d' % (nd, md) for md in [1, 2, 3] for nd in [3, 4, 5, 6, 8]]:
    selectors[sname] = mc_cand

for mt in ['a', 'v']:
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

            selectors[sname] = mc_cand

if __name__ == '__main__':
    ROOT.gSystem.Load('libMitFlatDataFormats.so')
    ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
    
    ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')

    sNames = sys.argv[1:]

    if len(sNames) != 0:
        if sNames[0] == 'all':
            sNames = selectors.keys()
        elif sNames[0] == 'list':
            print ' '.join(sorted(selectors.keys()))
            sys.exit(0)
        elif sNames[0] == 'dm':
            sNames = [key for key in selectors.keys() if 'dm' in key]
            print ' '.join(sorted(sNames))
            """
            for sName in sorted(sNames):
                print sName
            """
            sys.exit(0)
    
    skimmer = ROOT.Skimmer()
    
    sampleNames = []
    for name in sNames:
        if allsamples[name].sumw > 0.:
            sampleNames.append(name)
    
    print ' '.join(sampleNames)
    if sNames[0] == 'all':
        sys.exit(0)
    
    if not os.path.exists(config.skimDir):
        os.makedirs(config.skimDir)

    dataSourceDir = config.ntuplesDir
    
    for sname in sampleNames:
        sample = allsamples[sname]
        print 'Starting sample', sname, str(sampleNames.index(sname)+1)+'/'+str(len(sampleNames))
    
        skimmer.reset()
    
        tree = ROOT.TChain('events')
    
        if sample.data:
            print 'Reading', sname, 'from', dataSourceDir
            tree.Add(dataSourceDir + '/' + sample.directory + '/simpletree_*.root')
    
        elif sname.startswith('dm'):
            if os.path.exists(config.phskimDir + '/' + sname + '.root'):
                print 'Reading', sname, 'from', config.phskimDir
                tree.Add(config.phskimDir + '/' + sname + '.root')
            else:
                sourceDir = config.ntuplesDir.replace("042", "043")
                print 'Reading', sname, 'from', sourceDir
                tree.Add(sourceDir + '/' + sample.directory + '/simpletree_*.root')
    
        else:
            if os.path.exists(config.phskimDir + '/' + sname + '.root'):
                print 'Reading', sname, 'from', config.phskimDir
                tree.Add(config.phskimDir + '/' + sname + '.root')
            else:
                print 'Reading', sname, 'from', config.ntuplesDir
                tree.Add(config.ntuplesDir + '/' + sample.directory + '/simpletree_*.root')
    
        for selconf in selectors[sname]:
            if type(selconf) == str:
                rname = selconf
                gen = defaults[rname]
            else:
                rname, gen = selconf

            selector = gen(sample, rname)
            skimmer.addSelector(selector)
    
        skimmer.run(tree, config.skimDir, sname, -1)
