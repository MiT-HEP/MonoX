outname = '/data/t3home000/yiiyama/studies/monophoton/fit/ws_phoPtHighMet.root'
plotsOutname = '/data/t3home000/yiiyama/studies/monophoton/fit/ws_phoPtHighMet_plots.root'
sourcedir = '/data/t3home000/yiiyama/studies/monophoton/distributions_19fbinv'
filename = '{region}_{distribution}.root'
histname = '{distribution}-{process}'
carddir = '/data/t3home000/yiiyama/studies/monophoton/datacards_19fbinv'

regions = ['monoph', 'monoel', 'monomu', 'diel', 'dimu'] # , 'lowmt']
processes = ['data', 'efake', 'gjets', 'halo', 'hfake', 'minor', 'spike', 'vvg', 'wg', 'zg', 'gg', 'wjets', 'top', 'zjets']
signals = ['dmv-500-1', 'dmv-1000-1', 'dmv-2000-1']
distribution = 'phoPtHighMet'
xtitle = 'p_{T}^{#gamma} (GeV)'
binWidthNormalized = False

# Links between samples. List of tuples.
# The first sample (=target) of the tuple is represented by (transfer factor) * (second sample (=source)).
# In the fit, the normalization of the source and the transfer factors are allowed to float, with constraints
# on the transfer factors.
links = [
    (('zg', 'diel'), ('zg', 'monoph')),
    (('zg', 'dimu'), ('zg', 'monoph')),
    (('wg', 'monoel'), ('wg', 'monoph')),
    (('wg', 'monomu'), ('wg', 'monoph')),
    (('zg', 'monoel'), ('zg', 'monoph')),
    (('zg', 'monomu'), ('zg', 'monoph')),
    (('wg', 'monoph'), ('zg', 'monoph'))
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
    ('wg', 'monoph'): ['leptonVetoSF', 'gec']
}

# Artificial bin-to-bin decorrelation (de-shaping)
deshapedNuisances = [
    'EWK',
]

# Correlation in ratios.
# {(target, source, nuisance): correlation}
ratioCorrelations = {
    (('wg', 'monoph'), ('zg', 'monoph'), 'vgQCDscale'): 0.8,
    (('wg', 'monoph'), ('zg', 'monoph'), 'vgPDF'): 1.,
    (('wg', 'monoph'), ('zg', 'monoph'), 'EWK'): 1.
}

# Nuisances affecting normalization only
scaleNuisances = ['lumi', 'photonSF', 'customIDSF', 'leptonVetoSF', 'egFakerate', 'haloNorm', 'spikeNorm', 'minorQCDScale']

# def customize(workspace):
