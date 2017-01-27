import os

histDir = '/data/t3home000/' + os.environ['USER'] + '/studies/monophoton'

distribution = 'phoPtHighMet'

version = 'ICHEP'

outdir = histDir + '/fit/' + version
outname = outdir + '/ws_' + distribution + '.root'
plotsOutname = outdir + '/ws_' + distribution + '_plots.root'
sourcedir = histDir + '/distributions/' + version
carddir = histDir + '/datacards/' + version

filename = '{region}_{distribution}.root'
histname = '{distribution}-{process}'

# sr = 'bmonoph' # blinded version
sr = 'monoph'

regions = [sr, 'monoel', 'monomu', 'diel', 'dimu'] # , 'lowmt']
processes = ['data', 'efake', 'gjets', 'halo', 'hfake', 'minor', 'spike', 'vvg', 'wg', 'zg', 'gg', 'wjets', 'top', 'zjets']
signals = ['dmv-500-1', 'dmv-1000-1', 'dmv-2000-1']
xtitle = 'p_{T}^{#gamma} (GeV)'
binWidthNormalized = False

# Links between samples. List of tuples.
# The first sample (=target) of the tuple is represented by (transfer factor) * (second sample (=source)).
# In the fit, the normalization of the source and the transfer factors are allowed to float, with constraints
# on the transfer factors.
links = [
    # (('zg', 'diel'), ('zg', sr)),
    # (('zg', 'dimu'), ('zg', sr)),
    # (('wg', 'monoel'), ('wg', sr)),
    # (('wg', 'monomu'), ('wg', sr)),
    # (('zg', 'monoel'), ('zg', sr)),
    # (('zg', 'monomu'), ('zg', sr)),
    (('wg', 'monoel'), ('zg', 'diel')),
    (('wg', 'monomu'), ('zg', 'dimu')),
    (('wg', sr), ('zg', sr))
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
    ('wg', sr): ['leptonVetoSF', 'gec']
}

# Artificial bin-to-bin decorrelation (de-shaping)
deshapedNuisances = [
    'EWK',
]

# Correlation in ratios.
# {(target, source, nuisance): correlation}
ratioCorrelations = {
    (('wg', 'monoel'), ('zg', 'diel'), 'vgQCDscale'): 0.8,
    (('wg', 'monoel'), ('zg', 'diel'), 'vgPDF'): 1.,
    (('wg', 'monoel'), ('zg', 'diel'), 'EWK'): 1.,
    (('wg', 'monomu'), ('zg', 'dimu'), 'vgQCDscale'): 0.8,
    (('wg', 'monomu'), ('zg', 'dimu'), 'vgPDF'): 1.,
    (('wg', 'monomu'), ('zg', 'dimu'), 'EWK'): 1.,
    (('wg', sr), ('zg', sr), 'vgQCDscale'): 0.8,
    (('wg', sr), ('zg', sr), 'vgPDF'): 1.,
    (('wg', sr), ('zg', sr), 'EWK'): 1.
}

# Nuisances affecting normalization only
scaleNuisances = ['lumi', 'photonSF', 'customIDSF', 'leptonVetoSF', 'egFakerate', 'haloNorm', 'spikeNorm', 'minorQCDScale', 'muonSF', 'electronSF'] # lepton SF also flat for now

# def customize(workspace):
