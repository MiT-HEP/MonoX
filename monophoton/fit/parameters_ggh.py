import os

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
distribution = 'mtPhoMet'

sourcedir = workdir + '/plots'
fitdir = workdir + '/fit'
outname = fitdir + '/ws_' + distribution + '.root'
plotsOutname = fitdir + '/ws_' + distribution + '_plots.root'
carddir = fitdir + '/datacards'

filename = '{region}.root'
histname = distribution + '/{process}'
signalHistname = distribution + '/samples/{process}_gghg'

# sr = 'bmonoph' # blinded version
sr = 'gghg'

regions = [sr, 
           # 'gghe', 
           # 'gghm', 
           ]

data = 'data_obs' # name of data process
processes = ['efake', 'wg', 'zg', 'gjets', 'hfake', 'top', 'wjets', 'gg']
signals = ['dph-125'] 
xtitle = 'm_{T}({#gamma, E_{T}^{miss}) (GeV)'
binWidthNormalized = False

# Links between samples. List of tuples.
# The first sample (=target) of the tuple is represented by (transfer factor) * (second sample (=source)).
# In the fit, the normalization of the source and the transfer factors are allowed to float, with constraints
# on the transfer factors.
links = [
    (('wg', 'gghe'), ('wg', sr)),
    (('wg', 'gghm'), ('wg', sr)),
    # (('zg', 'gghe'), ('zg', sr)),
    # (('zg', 'gghm'), ('zg', sr)),
    # (('wg', sr), ('zg', sr)),
]

# Sample with free normalization that are not involved in links.
floats = []

wzIgnoreListExp = ['lumi', 'photonSF', 'pixelVetoSF', 'leptonVetoSF', 'gec']
wzIgnoreListThe = ['vgPDF', 'vgQCDscale', 'EWK']
gjIgnoreList = ['lumi', 'photonSF', 'pixelVetoSF', 'leptonVetoSF', 'minorQCDScale'],

ignoredNuisances = {
    ('wg', 'gghe'): wzIgnoreListExp + wzIgnoreListThe,
    ('wg', 'gghm'): wzIgnoreListExp + wzIgnoreListThe,
    # ('zg', 'gghe'): wzIgnoreListExp + wzIgnoreListThe,
    # ('zg', 'gghm'): wzIgnoreListExp + wzIgnoreListThe,
    # ('zg', sr): wzIgnoreListExp,
    # ('wg', sr): wzIgnoreListExp + wzIgnoreListThe,
}

# Artificial bin-to-bin decorrelation (de-shaping)
deshapedNuisances = [
#     'EWK',
]

# Correlation in ratios.
# {(target, source, nuisance): correlation}
ratioCorrelations = {
    (('wg', sr), ('zg', sr), 'vgQCDscale'): 1.,
    (('wg', sr), ('zg', sr), 'vgPDF'): 1.,
    (('wg', sr), ('zg', sr), 'EWK'): 1.
}

# Nuisances affecting normalization only
#scaleNuisances = ['lumi', 'photonSF', 'customIDSF', 'leptonVetoSF', 'egFakerate', 'haloNorm', 'spikeNorm', 'minorQCDScale', 'muonSF', 'electronSF'] # lepton SF also flat for now
scaleNuisances = ['lumi', 'photonSF', 'pixelVetoIDSF', 'leptonVetoSF', 'egFakerate', 'spikeNorm', 'minorQCDScale', 'muonSF', 'electronSF'] # lepton SF also flat for now

# def customize(workspace):
