import os
import sys

## directories to include
thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
if basedir not in sys.path:
    sys.path.append(basedir)

commondir = os.path.dirname(basedir) + '/common'
if commondir not in sys.path:
    sys.path.append(commondir)

import workspace_config as wc
import datasets
import config

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton' + config.year
fitdir = workdir + '/fit'
distribution = 'phoPtHighMet'
sr = 'vertical'

snames = [
    'dmvh-1000-1',
#     'add-3-8',
#    'dmvlo-*'
]

signals = []
for sname in snames:
    signals += [s.name for s in datasets.allsamples.getmany(sname)]

regions = [
    sr,
    'horizontal',
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
    (('zg', 'horizontal'), ('zg', sr)),
    (('wg', 'horizontal'), ('wg', sr)),
    (('halo', 'horizontal'), ('halo', sr)),
#     (('gg', 'diph'), ('zg', sr)),
#    (('gjets', 'lowdphi'), ('gjets', sr)),
#    (('zg', 'lowdphi'), ('zg', sr)),
#    (('wg', 'lowdphi'), ('wg', sr))
]

wzIgnoreListExp = ['lumi', 'photonSF', 'pixelVetoSF', 'leptonVetoSF', 'gec']
wzIgnoreListThe = ['vgPDF', 'vgQCDscale', 'zgEWKgamma', 'wgEWKgamma', 'zgEWKoverall', 'wgEWKoverall', 'zgEWKshape', 'wgEWKshape']
gjIgnoreList = ['lumi', 'photonSF', 'pixelVetoSF', 'leptonVetoSF', 'minorQCDScale']

ignoredNuisances = {
    ('zg', 'diel'): wzIgnoreListExp + wzIgnoreListThe, # leptonVetoSF ignored because it's supposed to be present in both SR and CR but is missing from CR
    ('zg', 'dimu'): wzIgnoreListExp + wzIgnoreListThe, # minorPDF and minorQCDscale are on zg & wg because of a bug in plotconfig
    ('wg', 'monoel'): wzIgnoreListExp + wzIgnoreListThe,
    ('wg', 'monomu'): wzIgnoreListExp + wzIgnoreListThe,
    ('zg', 'monoel'): wzIgnoreListExp + wzIgnoreListThe,
    ('zg', 'monomu'): wzIgnoreListExp + wzIgnoreListThe,
    ('zg', 'horizontal'): wzIgnoreListExp + wzIgnoreListThe,
    ('wg', 'horizontal'): wzIgnoreListExp + wzIgnoreListThe,
    ('halo', 'horizontal'): ['haloNorm'],
    ('zg', sr): wzIgnoreListExp,
    ('wg', sr): wzIgnoreListExp,
    ('halo', sr): ['haloNorm'],
#     ('gg', 'diph'): wzIgnoreListExp,
#    ('zg', 'lowdphi'): wzIgnoreListExp + wzIgnoreListThe,
#    ('wg', 'lowdphi'): wzIgnoreListExp + wzIgnoreListThe,
#    ('gjets', 'lowdphi'): gjIgnoreList,
#    ('gjets', 'horizontal'): gjIgnoreList,
#    ('gjets', sr): gjIgnoreList,
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
    signalHistname = distribution + '/samples/{process}_monoph',
    regions = regions,
    bkgProcesses = ['efake', 'gjets', 'hfake', 'minor', 'vvg', 'wg', 'zg', 'gg', 'wjets', 'top', 'zjets', 'spike', 'halo'],
    signals = signals,
    xname = 'pt',
    xtitle = 'p_{T}^{#gamma}',
    xunit = 'GeV',
    links = links,
    staticBase = [('halo', sr)],
    ignoredNuisances = ignoredNuisances,
    ratioCorrelations = ratioCorrelations,
    scaleNuisances = scaleNuisances
)
