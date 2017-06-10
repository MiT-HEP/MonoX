import os

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton_noichmax'
distribution = 'phoPtHighMet'

sourcedir = workdir + '/plots'
outname = workdir + '/fit/ws_' + distribution + '.root'
plotsOutname = workdir + '/fit/ws_' + distribution + '_plots.root'
carddir = workdir + '/fit/datacards'

filename = '{region}.root'
histname = distribution + '/{process}'
signalHistname = distribution + '/samples/{process}_monoph'

# sr = 'bmonoph' # blinded version
sr = 'monoph'

regions = [sr, 'monoel', 'monomu', 'diel', 'dimu'] # , 'lowdphi'] # , 'lowmt']
processes = ['data_obs', 'efake', 'gjets', 'halo', 'hfake', 'minor', 'spike', 'vvg', 'wg', 'zg', 'gg', 'wjets', 'top', 'zjets']
#signals = ['dmv-500-1', 'dmv-1000-1', 'dmv-2000-1', 'dma-500-1', 'dma-1000-1', 'dma-2000-1', 'dmvlo-500-1', 'dmvlo-1000-1', 'dmvlo-2000-1', 'dmalo-1000-1', 'dmalo-2000-1', 'dph-1000', 'dph-125']
signals = ['dmvlo-1000-1']
xtitle = 'p_{T}^{#gamma} (GeV)'
binWidthNormalized = False

# Links between samples. List of tuples.
# The first sample (=target) of the tuple is represented by (transfer factor) * (second sample (=source)).
# In the fit, the normalization of the source and the transfer factors are allowed to float, with constraints
# on the transfer factors.
links = [
    (('zg', 'diel'), ('zg', sr)),
    (('zg', 'dimu'), ('zg', sr)),
    (('wg', 'monoel'), ('wg', sr)),
    (('wg', 'monomu'), ('wg', sr)),
    (('zg', 'monoel'), ('zg', sr)),
    (('zg', 'monomu'), ('zg', sr)),
    (('wg', sr), ('zg', sr)),
#     (('gjets', 'lowdphi'), ('gjets', sr)),
#     (('zg', 'lowdphi'), ('zg', sr)),
#     (('wg', 'lowdphi'), ('wg', sr))
]

# Sample with free normalization that are not involved in links.
floats = []

ignoredNuisances = {
    ('zg', 'diel'): ['leptonVetoSF', 'vgPDF', 'vgQCDscale', 'EWK', 'gec'], # leptonVetoSF ignored because it's supposed to be present in both SR and CR but is missing from CR
    ('zg', 'dimu'): ['leptonVetoSF', 'vgPDF', 'vgQCDscale', 'EWK', 'gec'], # minorPDF and minorQCDscale are on zg & wg because of a bug in plotconfig
    ('wg', 'monoel'): ['leptonVetoSF', 'vgPDF', 'vgQCDscale', 'EWK', 'gec'],
    ('wg', 'monomu'): ['leptonVetoSF', 'vgPDF', 'vgQCDscale', 'EWK', 'gec'],
    ('zg', 'monoel'): ['leptonVetoSF', 'vgPDF', 'vgQCDscale', 'EWK', 'gec'],
    ('zg', 'monomu'): ['leptonVetoSF', 'vgPDF', 'vgQCDscale', 'EWK', 'gec'],
#     ('zg', 'lowdphi'): ['leptonVetoSF', 'vgPDF', 'vgQCDscale', 'EWK', 'gec'],
#     ('wg', 'lowdphi'): ['leptonVetoSF', 'vgPDF', 'vgQCDscale', 'EWK', 'gec'],
#     ('halo', 'lowdphi'): ['haloShape'],
    ('wg', sr): ['leptonVetoSF', 'gec']
}

# Artificial bin-to-bin decorrelation (de-shaping)
deshapedNuisances = [
    'EWK',
]

# Correlation in ratios.
# {(target, source, nuisance): correlation}
ratioCorrelations = {
    (('wg', sr), ('zg', sr), 'vgQCDscale'): 0.8,
    (('wg', sr), ('zg', sr), 'vgPDF'): 1.,
    (('wg', sr), ('zg', sr), 'EWK'): 1.
}

# Nuisances affecting normalization only
scaleNuisances = ['lumi', 'photonSF', 'customIDSF', 'leptonVetoSF', 'egFakerate', 'haloNorm', 'spikeNorm', 'minorQCDScale', 'muonSF', 'electronSF'] # lepton SF also flat for now

# def customize(workspace):
