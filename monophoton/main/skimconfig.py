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

def applyMod(sels, *mods):
    result = []
    for sel in sels:
        if type(sel) is str:
            result.append((sel, getattr(s, sel)) + mods)
        else:
            result.append(sel + mods)

    return result

data_sph = [
    'monoph', 'efake', 'hfake',  'trivialShower', 'halo', 'emjet',
    'dimu', 'dimuAllPhoton', 'diel', 'dielAllPhoton', 'monomu', 'monomuAllPhoton', 'monoel',
    'dimuHfake', 'dielHfake', 'monomuHfake', 'monoelHfake',
    'tpeg', 'tpmg',
    'dijet'
]

data_smu = [
    'dimu', 'monomu', 'monomuHfake', 'elmu', 'zmmJets', 'zmumu', 'tpmmg',
    ('tpmg', s.tpmgLowPt)
]

data_sel = [
    'diel', 'monoel', 'monoelHfake', 'eefake', 'zeeJets',
    ('tpeg', s.tpegLowPt)
]

mc_cand = ['monoph', 'emjet']
mc_qcd = ['hfake']
mc_sig = ['monoph', 'emjet', 'signalRaw']
mc_lep = ['monomu', 'monoel']
mc_dilep = ['dimu', 'dimuAllPhoton', 'diel', 'elmu', 'zmmJets', 'zeeJets', 'dielVertex', 'dimuVertex', 'tpmmg']

mc_wlnu = ['wenu', 'zmmJets', 'zeeJets', 'monoelVertex', 'monomuVertex'] + applyMod([('monoph', s.monophNoE), 'monomu', 'monoel'], s.addGenPhotonVeto)

allSelectors_byPattern = [
    # Data 2016
    ('sph-16*', data_sph),
    ('smu-16*', data_smu),
    ('sel-16*', data_sel),
    # MC
    ('znng', mc_sig),
    ('znng-130', applyMod(mc_sig, s.addKfactor)),
    ('zllg', mc_sig + mc_lep + mc_dilep),
    ('zllg-130', mc_sig + mc_lep + mc_dilep),
    ('wnlg', mc_sig + mc_lep),
    ('wnlg-{130,500}', applyMod(mc_sig + mc_lep, s.addKfactor)),
    ('wglo', mc_cand + mc_lep),
    ('wglo-{130,500}', applyMod(mc_cand + mc_lep, s.addKfactor)),
    ('znng-40-o', mc_sig),
    ('znng-130-o', applyMod(mc_sig, s.addKfactor)),
    ('zllg-*-o', applyMod(mc_sig + mc_lep + mc_dilep, s.addKfactor)),
    ('wnlg-40-o', mc_sig + mc_lep),
    ('wnlg-130-o', applyMod(mc_sig + mc_lep, s.addKfactor)),
    ('gj{,04}-*', applyMod(mc_qcd + mc_cand, s.addKfactor)),
    ('gg-*', mc_cand + mc_lep + mc_dilep),
    ('ttg', mc_cand + mc_lep + mc_dilep),
    ('tg', mc_cand + mc_lep),
    ('ww', mc_cand + mc_lep + mc_dilep),
    ('wz', mc_cand + mc_lep + mc_dilep),
    ('zz', mc_cand + mc_lep + mc_dilep),
    ('tt', mc_cand + mc_lep + mc_dilep),
    ('wlnu{,n}-*', mc_wlnu),
    ('znn{,n}-*', mc_cand),
    ('dy-50*', applyMod(mc_cand + mc_lep + mc_dilep + ['tpeg', 'tpegLowPt'], s.addGenPhotonVeto)),
    ('dyn-50-*', applyMod(mc_cand + mc_lep + mc_dilep, s.addGenPhotonVeto)),
    ('qcd-*', mc_cand + mc_qcd + mc_dilep + mc_lep),
    ('add-*', mc_sig),
    ('dm*', mc_sig),
    ('dph*', mc_sig)
]

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
