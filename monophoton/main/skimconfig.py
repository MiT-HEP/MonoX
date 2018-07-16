"""
Specify non-default skims in this configuration file.
"""

import os
import sys

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from datasets import allsamples
import selectors as s

import ROOT

def applyMod(sels, *mods):
    result = []
    for sel in sels:
        if type(sel) is str:
            result.append((sel, getattr(s, sel)) + mods)
        else:
            result.append(sel + mods)

    return result

tpegLowPt = ('tpeg', s.tpegLowPt)
tpmgLowPt = ('tpmg', s.tpmgLowPt)

data_sph = [
    'monoph', 
    'efake', 'hfake', 'trivialShower', 'halo',
    'dimu', 'diel', 'monomu', 'monoel',
    'dimuHfake', 'dielHfake', 'monomuHfake', 'monomuEfake', 'monoelHfake', 'monoelEfake', 'monoelQCD',
    'tpeg', 'tpmg',
    'emjet',
    'dimuAllPhoton', 'dielAllPhoton', 'monomuAllPhoton', 
    'dijet',
    'vbfg', 'vbfem', 'vbfgEfake', 'vbfgHfake', 'vbfgCtrl', 'vbfgHfakeCtrl', 'ph75', 'vbfgLJCtrl',
    'vbfzee', 'vbfzeeEfake',
    'gghg', 'gghEfake', 'gghHfake', 
    'gghe', 'ggheEfake', 'ggheHfake', 'gghm', 'gghmEfake', 'gghmHfake', 
    'gghee', 'gghmm',
    'fakeMetRandom', 'fakeMet25', 'fakeMet50', 'fakeMet75',
    'monophNoGSFix', 'gghgNoGSFix'
]

data_smu = [
    'dimu', 'monomu', 'monomuHfake', 'zmmJets', 'zmumu', 'tpmmg',
    tpmgLowPt, 'tp2m',
    'vbfm', 'vbfmm',
    'elmu'
]

data_sel = [
    'diel', 'monoel', 'monoelHfake', 'zeeJets',
    tpegLowPt, 'tp2e',
    'vbfe', 'vbfee'
]

mc_cand = ['monoph', 'emjet', 'vbfg', 'vbfgCtrl', 'vbfgLJCtrl', 'gghg']
mc_qcd = ['hfake', 'fakeMetRandom', 'fakeMet25', 'fakeMet50', 'fakeMet75']
mc_sig = ['monoph', 'emjet', 'vbfg', 'signalRaw', 'gghg']
mc_lep = ['monomu', 'monoel', 'vbfe', 'vbfm', 'gghe', 'gghm']
mc_dilep = ['dimu', 'dimuAllPhoton', 'diel', 'zmmJets', 'zeeJets', 'dielVertex', 'dimuVertex', 'tpmmg', 'vbfee', 'vbfmm', 'zmumu', 'gghee', 'gghmm']

mc_ewk = [ 'monoph250', 'monoph300', 'monoph400', 'monoph500', 'monoph600']
mc_ewk_lep = ['monomu250', 'monomu300', 'monomu400', 'monomu500', 'monomu600', 'monoel250', 'monoel300', 'monoel400', 'monoel500', 'monoel600']
mc_ewk_dilep = ['dimu250', 'dimu300', 'dimu400', 'dimu500', 'dimu600', 'diel250', 'diel300', 'diel400', 'diel500', 'diel600']

mc_wlnu = ['wenu', 'zmmJets', 'zeeJets', 'monoelVertex', 'monomuVertex', 'vbfe', 'vbfm'] + applyMod([('monoph', s.monophNoE), 'monomu', 'monoel', 'emjet', ('gghg', s.gghgNoE), 'gghe', 'gghm'], s.addGenPhotonVeto)

allSelectors_byPattern = [
    # Data
    ('sph-' + config.year + '*', data_sph),
    ('smu-' + config.year + '*', data_smu),
    ('sel-' + config.year + '*', data_sel),
]

    # MC
"""
    ('znng', mc_sig + mc_ewk),
    ('znng-130', applyMod(mc_sig + mc_ewk, s.addKfactor)),
    ('zllg', mc_sig + mc_lep + mc_dilep + ['vbfzee']),
    ('zllg-130', mc_sig + mc_lep + mc_dilep),
    ('wnlg', mc_sig + mc_lep),
    ('wnlg-{130,500}', applyMod(mc_sig + mc_lep, s.addKfactor)),
    ('wglo', applyMod(mc_cand + mc_lep + [tpegLowPt, tpmgLowPt, 'vbfgWHadCtrl', 'vbfzee'], s.addKfactor)),
    ('wglo-{130,500}', applyMod(mc_cand + mc_lep, s.addKfactor)),
    ('znng-40-o', applyMod(mc_sig, s.ptTruncator(maximum = 130.))),
    ('znng-130-o', applyMod(mc_sig + mc_ewk + ['monophNoLVeto', 'trivialShower'], s.addKfactor)),
    ('zllg-130-o', applyMod(mc_sig + mc_lep + mc_dilep + mc_ewk + mc_ewk_lep + mc_ewk_dilep, s.addKfactor, s.ptTruncator(maximum = 300.))),
    ('zllg-300-o', applyMod(mc_sig + mc_lep + mc_dilep + mc_ewk + mc_ewk_lep + mc_ewk_dilep, s.addKfactor)),
    ('wnlg-40-o', mc_sig + mc_lep),
    ('wnlg-130-o', applyMod(mc_sig + mc_lep + mc_ewk + mc_ewk_lep, s.addKfactor)),
    ('wnlg-130-p', applyMod(mc_sig + mc_lep + mc_ewk + mc_ewk_lep, s.addKfactor)),
    ('gj{,04}-*', applyMod(mc_qcd + mc_cand + ['halo', 'monoel', 'vbfem', 'ph75', 'gjets325'], s.addKfactor)),
    ('gje-*', applyMod(['monoph'], s.addKfactor)),
    ('gjn*', mc_qcd + mc_cand + ['monoel', 'vbfem']),
    ('gg-*', mc_cand + mc_lep + mc_dilep),
    ('ttg', mc_cand + mc_lep + mc_dilep + ['vbfzee']),
    ('tg', mc_cand + mc_lep + ['vbfzee']),
    ('ww', mc_cand + mc_lep + mc_dilep),
    ('wz', mc_cand + mc_lep + mc_dilep),
    ('zz', mc_cand + mc_lep + mc_dilep),
    ('tt', mc_cand + mc_lep + mc_dilep + [tpegLowPt, tpmgLowPt, 'tp2e', 'tp2m']),
    ('st*', mc_lep),
    ('wlnu', applyMod(mc_wlnu, s.htTruncator(maximum = 70.))),
    ('wlnu{,n}-*', mc_wlnu),
    ('w{m,p}lnuewk', mc_wlnu),
    ('znn{,n}-*', mc_cand),
    ('dy-50', applyMod(mc_cand + mc_lep + mc_dilep + [tpegLowPt, tpmgLowPt, 'tp2e', 'tp2m'], s.addGenPhotonVeto)),
    ('dy-50@', applyMod(mc_cand + mc_lep + mc_dilep + [tpegLowPt, tpmgLowPt, 'tp2e', 'tp2m'], s.addGenPhotonVeto, s.htTruncator(maximum = 100.))),
    ('dyn-50', applyMod(mc_cand + mc_lep + mc_dilep + [tpegLowPt, tpmgLowPt, 'tp2e', 'tp2m'], s.addGenPhotonVeto)),
    ('dyn-50@', applyMod(mc_cand + mc_lep + mc_dilep + [tpegLowPt, tpmgLowPt, 'tp2e', 'tp2m'], s.addGenPhotonVeto, s.genBosonPtTruncator(maximum = 50.))),
    ('dy{,n}-50-*', applyMod(mc_cand + mc_lep + mc_dilep + [tpegLowPt, tpmgLowPt, 'tp2e', 'tp2m'], s.addGenPhotonVeto)),
    ('zewk', applyMod(mc_cand + mc_lep + mc_dilep + [tpegLowPt, tpmgLowPt, 'tp2e', 'tp2m'], s.addGenPhotonVeto)),
    ('qcd-*', mc_cand + mc_qcd + mc_dilep + mc_lep),
    ('add-*', mc_sig),
    ('dm*', mc_sig),
    ('dph*', mc_sig),
    ('hbb-nlo-125', mc_sig)
"""

allSelectors = {}
for pat, sels in allSelectors_byPattern:
    samples = allsamples.getmany(pat)
    for sample in samples:
        if sample in allSelectors:
            raise RuntimeError('Duplicate skim config for ' + sample.name)

        sampleSelectors = {}
        for sel in sels:
            # sel has to be either a selector function name or a tuple of form (region, selector[, modifiers])
            if type(sel) is str:
                sampleSelectors[sel] = getattr(s, sel)
            elif len(sel) == 2:
                sampleSelectors[sel[0]] = sel[1]
            else:
                sampleSelectors[sel[0]] = sel[1:]
            
        allSelectors[sample] = sampleSelectors
