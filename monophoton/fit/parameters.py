outname = '/local/yiiyama/exec/ws.root'
sourcedir = '/data/t3home000/yiiyama/studies/monophoton/distributions'
filename = '{region}_{distribution}.root'
histname = '{distribution}-{process}'

regions = ['monoph', 'monoel', 'monomu', 'diel', 'dimu', 'lowmt']
processes = ['data', 'efake', 'gjets', 'halo', 'hfake', 'minor', 'spike', 'vvg', 'wg', 'zg', 'gg', 'wjets', 'top', 'zjets', '']
processes += ['dmv-500-1', 'dmv-1000-1', 'dmv-2000-1']
distribution = 'phoPtHighMet'
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
#    (('wg', 'monoph'), ('zg', 'monoph'))
]

# Sample with free normalization that are not involved in links.
floats = []

ignoredNuisances = {
    ('zg', 'diel'): ['leptonVetoSF', 'minorPDF', 'minorQCDscale', 'vgPDF', 'vgQCDscale', 'zgEWK', 'gec'], # leptonVetoSF ignored because it's supposed to be present in both SR and CR but is missing from CR
    ('zg', 'dimu'): ['leptonVetoSF', 'minorPDF', 'minorQCDscale', 'vgPDF', 'vgQCDscale', 'zgEWK', 'gec'], # minorPDF and minorQCDscale are on zg & wg because of a bug in plotconfig
    ('wg', 'monoel'): ['leptonVetoSF', 'minorPDF', 'minorQCDscale', 'vgPDF', 'vgQCDscale', 'wgEWK', 'gec'],
    ('wg', 'monomu'): ['leptonVetoSF', 'minorPDF', 'minorQCDscale', 'vgPDF', 'vgQCDscale', 'wgEWK', 'gec'],
    ('zg', 'monoel'): ['leptonVetoSF', 'minorPDF', 'minorQCDscale', 'vgPDF', 'vgQCDscale', 'zgEWK', 'gec'],
    ('zg', 'monomu'): ['leptonVetoSF', 'minorPDF', 'minorQCDscale', 'vgPDF', 'vgQCDscale', 'zgEWK', 'gec']
}

# Artificial bin-to-bin decorrelation
decorrelatedNuisances = [
    'zgEWK',
    'wgEWK'
]

# Partial correlation in ratios.
# {(target, source, nuisance): correlation}
partialCorrelation = {
    (('wg', 'monoph'), ('zg', 'monoph'), 'vgQCDscale'): 0.8
}

# Nuisances affecting normalization only
scaleNuisances = ['lumi', 'photonSF', 'customIDSF', 'leptonVetoSF', 'egFakerate', 'haloNorm', 'spikeNorm', 'minorQCDScale']

def customize(workspace):
    
