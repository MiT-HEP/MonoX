import os
import sys

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from datasets import allsamples
import selectors

def defaults(regions):
    return [(region, getattr(selectors, region)) for region in regions]

def applyMod(modifier, regions):
    result = []
    for entry in regions:
        if type(entry) is tuple:
            region, selector = entry
        else:
            region = entry
            selector = getattr(selectors, region)

        result.append((region, modifier(selector)))

    return result


mc_cand = ['monoph'] # , 'purity']
mc_qcd = ['hfake', 'hfakeTight', 'hfakeLoose', 'purity', 'purityNom', 'purityTight', 'purityLoose'] # , 'gjets'] 
mc_sig = ['monoph', 'purity', 'signalRaw']
mc_lep = ['monomu', 'monoel']
mc_dilep = ['dimu', 'dimuAllPhoton', 'diel', 'elmu', 'zmmJets', 'zeeJets', 'dielVertex', 'dimuVertex']

wlnu = applyMod(selectors.wlnu, applyMod(selectors.genveto, mc_cand)) + applyMod(selectors.genveto, mc_lep) + defaults(['wenu', 'zmmJets', 'zeeJets', 'monoelVertex', 'monomuVertex'])

allSelectors_byPattern = {
    # Data 2016
    'sph-16*': defaults(['monoph', 'efake', 'hfake',  'trivialShower']
                        + ['haloLoose', 'haloMIPLoose', 'haloMETLoose', 'haloNoShowerCut'] # , 'halo', 'haloMIP', 'haloMET', 'haloMedium', 'haloMIPMedium', 'haloMETMedium']
                        + ['hfakeTight', 'hfakeLoose'] # , 'hfakeVLoose']
                        + ['purity', 'purityNom', 'purityTight', 'purityLoose'] # , 'purityVLoose'] # , 'gjets']
                        + ['dimu', 'dimuAllPhoton', 'diel', 'dielAllPhoton', 'monomu', 'monomuAllPhoton', 'monoel']
                        + ['dimuHfake', 'dielHfake', 'monomuHfake', 'monoelHfake']
                        + ['tpeg', 'tpmg']
                        + ['dijet']),
    'smu-16*': defaults(['dimu', 'monomu', 'monomuHfake', 'elmu', 'zmmJets', 'zmumu', 'tpmmg']) + [('tpmg', selectors.tpmgLowPt)],
    'sel-16*': defaults(['diel', 'monoel', 'monoelHfake', 'eefake', 'zeeJets']) + [('tpeg', selectors.tpegLowPt)],
    # Hgg -> Dark Photon MC no gen changes
    'hgg-*': applyMod(selectors.dph, mc_sig),
    # MC
    'znng': defaults(mc_sig),
    'znng-130': applyMod(selectors.kfactor, mc_sig),
    'zllg': defaults(mc_sig + mc_lep + mc_dilep),
    'zllg-130': applyMod(selectors.kfactor, mc_sig + mc_lep + mc_dilep),
    'wnlg': defaults(mc_sig + mc_lep),
    'wnlg-{130,500}': applyMod(selectors.kfactor, mc_sig + mc_lep),
    'wglo': defaults(mc_cand + mc_lep),
    'wglo-{130,500}': applyMod(selectors.kfactor, mc_cand + mc_lep),
    'znng-40-o': defaults(mc_sig),
    'znng-130-o': applyMod(selectors.kfactor, mc_sig),
    'zllg-130-o': applyMod(selectors.kfactor, mc_sig + mc_lep + mc_dilep),
    'wnlg-40-o': defaults(mc_sig + mc_lep),
    'wnlg-130-o': applyMod(selectors.kfactor, mc_sig + mc_lep),
    'gj{,04}-*': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gg-*': defaults(mc_cand + mc_lep + mc_dilep),
    'ttg': defaults(mc_cand + mc_lep + mc_dilep),
    'tg': defaults(mc_cand + mc_lep),
    'ww': defaults(mc_cand + mc_lep + mc_dilep),
    'wz': defaults(mc_cand + mc_lep + mc_dilep),
    'zz': defaults(mc_cand + mc_lep + mc_dilep),
    'tt': defaults(mc_cand + mc_lep + mc_dilep),
    'wlnu*': wlnu,
    'wlnun-*': wlnu,
    'znn-*': defaults(mc_cand),
    'znnn-*': defaults(mc_cand),
    'dy-50*': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dyn-50-*': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'qcd-*': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
}

allSelectors = {}
for key, sels in allSelectors_byPattern.items():
    samples = allsamples.getmany(key)
    for sample in samples:
        allSelectors[sample.name] = sels

# all the rest are mc_sig
for sname in allsamples.names():
    if sname not in allSelectors:
        # print 'Sample ' + sname + ' not found in selectors dict. Appyling mc_sig.'
        allSelectors[sname] = defaults(mc_sig)
