import os
import sys

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from datasets import allsamples
import main.selectors as selectors

defaultSelectors = {
    'monoph': selectors.candidate,
    'signalRaw': selectors.signalRaw,
    'efake': selectors.eleProxy,
    'hfake': selectors.hadProxy,
    'hfakeTight': selectors.hadProxyTight,
    'hfakeLoose': selectors.hadProxyLoose,
    'purity': selectors.purity,
    'purityNom': selectors.purityNom,
    'purityTight': selectors.purityTight,
    'purityLoose': selectors.purityLoose,
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

data_sph =  ['monoph', 'efake', 'hfake',  'trivialShower'] 
data_sph += ['haloLoose', 'haloMIPLoose', 'haloMETLoose'] # , 'halo', 'haloMIP', 'haloMET', 'haloMedium', 'haloMIPMedium', 'haloMETMedium']
data_sph += ['hfakeTight', 'hfakeLoose'] # , 'hfakeVLoose']
data_sph += ['purity', 'purityNom', 'purityTight', 'purityLoose'] # , 'purityVLoose'] # , 'gjets'] 
data_sph += ['dimu', 'diel', 'monomu', 'monoel'] 
data_sph += ['dimuHfake', 'dielHfake', 'monomuHfake', 'monoelHfake'] 
data_smu = ['dimu', 'monomu', 'monomuHfake', 'elmu', 'zmmJets'] # are SinglePhoton triggers in this PD? (do the samples know about them, obviously they are not used to define it)
data_sel = ['diel', 'monoel', 'monoelHfake', 'eefake', 'zeeJets'] # are SinglePhoton triggers in this PD? (do the samples know about them, obviously they are not used to define it)
mc_cand = ['monoph'] # , 'purity']
mc_qcd = ['hfake', 'hfakeTight', 'hfakeLoose', 'purity', 'purityNom', 'purityTight', 'purityLoose'] # , 'gjets'] 
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
    # MC
    'znng': defaults(mc_sig),
    'znng-130': defaults(mc_sig),
    'zllg': defaults(mc_sig + mc_lep + mc_dilep),
    'zllg-130': defaults(mc_sig + mc_lep + mc_dilep),
    'wnlg': defaults(mc_sig + mc_lep),
    'wnlg-130': defaults(mc_sig + mc_lep),
    'wnlg-500': defaults(mc_sig + mc_lep),
    'wglo': applyMod(selectors.kfactor, mc_cand + mc_lep),
    'wglo-130': applyMod(selectors.kfactor, mc_cand + mc_lep),
    'wglo-500': applyMod(selectors.kfactor, mc_cand + mc_lep),
    'znng-40-o': applyMod(selectors.kfactor, mc_sig),
    'znng-130-o': applyMod(selectors.kfactor, mc_sig),
    'zllg-130-o': applyMod(selectors.kfactor, mc_sig + mc_lep + mc_dilep),
    'wnlg-40-o': applyMod(selectors.kfactor, mc_sig + mc_lep),
    'wnlg-130-o': applyMod(selectors.kfactor, mc_sig + mc_lep),
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
    'ttg': defaults(mc_cand + mc_lep + mc_dilep),
    'tg': defaults(mc_cand + mc_lep),
    'ww': defaults(mc_cand + mc_lep + mc_dilep),
    'wz': defaults(mc_cand + mc_lep + mc_dilep),
    'zz': defaults(mc_cand + mc_lep + mc_dilep),
    'tt': defaults(mc_cand + mc_lep + mc_dilep),
    'wlnu': wlnu,
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
        # print 'Sample ' + sname + ' not found in selectors dict. Appyling mc_sig.'
        selectors[sname] = defaults(mc_sig)
