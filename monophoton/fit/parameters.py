import os
import sys

import workspace_config as wc

## directories to include
thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
if basedir not in sys.path:
    sys.path.append(basedir)

import datasets

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
fitdir = workdir + '/fit'
distribution = 'phoPtHighMet'
sr = 'monophHighPhi'

snames = [
    'add-3-4',
#    'dmvlo-*'
]

signals = []
for sname in snames:
    signals += [s.name for s in datasets.allsamples.getmany(sname)]

regions = [
    sr,
    'monophLowPhi',
    'monoel',
    'monomu',
    'diel',
    'dimu'
]

links = [
    (('zg', 'diel'), ('zg', sr)),
    (('zg', 'dimu'), ('zg', sr)),
    (('wg', 'monoel'), ('wg', sr)),
    (('wg', 'monomu'), ('wg', sr)),
    (('zg', 'monoel'), ('zg', sr)),
    (('zg', 'monomu'), ('zg', sr)),
    (('wg', sr), ('zg', sr)),
    (('zg', 'monophLowPhi'), ('zg', sr)),
    (('wg', 'monophLowPhi'), ('wg', sr)),
    (('halo', 'monophLowPhi'), ('halo', sr)),
#     (('gg', 'diph'), ('zg', sr)),
#    (('gjets', 'lowdphi'), ('gjets', sr)),
#    (('zg', 'lowdphi'), ('zg', sr)),
#    (('wg', 'lowdphi'), ('wg', sr))
]

wzIgnoreListExp = ['lumi', 'photonSF', 'pixelVetoSF', 'leptonVetoSF', 'gec']
wzIgnoreListThe = ['vgPDF', 'vgQCDscale', 'EWK']
gjIgnoreList = ['lumi', 'photonSF', 'pixelVetoSF', 'leptonVetoSF', 'minorQCDScale']

ignoredNuisances = {
    ('zg', 'diel'): wzIgnoreListExp + wzIgnoreListThe, # leptonVetoSF ignored because it's supposed to be present in both SR and CR but is missing from CR
    ('zg', 'dimu'): wzIgnoreListExp + wzIgnoreListThe, # minorPDF and minorQCDscale are on zg & wg because of a bug in plotconfig
    ('wg', 'monoel'): wzIgnoreListExp + wzIgnoreListThe,
    ('wg', 'monomu'): wzIgnoreListExp + wzIgnoreListThe,
    ('zg', 'monoel'): wzIgnoreListExp + wzIgnoreListThe,
    ('zg', 'monomu'): wzIgnoreListExp + wzIgnoreListThe,
    ('zg', 'monophLowPhi'): wzIgnoreListExp + wzIgnoreListThe,
    ('wg', 'monophLowPhi'): wzIgnoreListExp + wzIgnoreListThe,
    ('halo', 'monophLowPhi'): ['haloNorm'],
    ('zg', 'monophHighPhi'): wzIgnoreListExp,
    ('wg', 'monophHighPhi'): wzIgnoreListExp,
    ('halo', 'monophHighPhi'): ['haloNorm'],
#     ('gg', 'diph'): wzIgnoreListExp,
#    ('zg', 'lowdphi'): wzIgnoreListExp + wzIgnoreListThe,
#    ('wg', 'lowdphi'): wzIgnoreListExp + wzIgnoreListThe,
#    ('gjets', 'lowdphi'): gjIgnoreList,
#    ('gjets', 'monophLowPhi'): gjIgnoreList,
#    ('gjets', 'monophHighPhi'): gjIgnoreList,
}

ratioCorrelations = {
    (('wg', sr), ('zg', sr), 'vgQCDscale'): 1.,
    (('wg', sr), ('zg', sr), 'vgPDF'): 1.,
}

# Nuisances affecting normalization only
scaleNuisances = [
    'lumi',
    'photonSF',
    'customIDSF',
    'leptonVetoSF',
    'egFakerate',
    'haloNorm',
    'spikeNorm',
    'minorQCDScale',
    'muonSF', # lepton SF also flat for now
    'electronSF' # lepton SF also flat for now
]

wc.config = wc.WorkspaceConfig(
    sourcename = workdir + '/plots/{region}.root',
    outname = fitdir + '/ws_' + distribution + '.root',
    plotsOutname = fitdir + '/ws_' + distribution + '_plots.root',
    cardname = fitdir + '/datacards/monoph_{signal}.dat',
    histname = distribution + '/{process}',
    signalHistname = distribution + '/samples/{process}_{region}',
    regions = regions,
    bkgProcesses = ['efake', 'gjets', 'hfake', 'minor', 'vvg', 'wg', 'zg', 'gg', 'wjets', 'top', 'zjets', 'spike', 'halo'],
    signals = signals,
    xtitle = 'p_{T}^{#gamma} (GeV)',
    links = links,
    staticBase = [('halo', 'monophLowPhi')],
    ignoredNuisances = ignoredNuisances,
    ratioCorrelations = ratioCorrelations,
    scaleNuisances = scaleNuisances
)
