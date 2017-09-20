import os

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
distribution = 'phoPtHighMet'

sourcedir = workdir + '/plots'
fitdir = workdir + '/fit'
outname = fitdir + '/ws_' + distribution + '.root'
plotsOutname = fitdir + '/ws_' + distribution + '_plots.root'
carddir = fitdir + '/datacards'

filename = '{region}.root'
histname = distribution + '/{process}'
signalHistname = distribution + '/samples/{process}_monoph'

# sr = 'bmonoph' # blinded version
sr = 'monophHighPhi'

regions = [sr, 'monophLowPhi', 'monoel', 'monomu', 'diel', 'dimu'] # + ['lowdphi'] # , 'lowmt']
data = 'data_obs' # name of data process
processes = ['efake', 'gjets', 'hfake', 'minor', 'vvg', 'wg', 'zg', 'gg', 'wjets', 'top', 'zjets', 'spike'] + ['halo']
#signals = ['dmv-500-1', 'dmv-1000-1', 'dmv-2000-1', 'dma-500-1', 'dma-1000-1', 'dma-2000-1', 'dmvlo-500-1', 'dmvlo-1000-1', 'dmvlo-2000-1', 'dmalo-1000-1', 'dmalo-2000-1', 'dph-1000', 'dph-125']
signals = ['dmvlo-1000-1'] # 
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
    (('zg', 'monophLowPhi'), ('zg', sr)),
    (('wg', 'monophLowPhi'), ('wg', sr)),
    (('halo', 'monophLowPhi'), ('halo', sr)),
#    (('gjets', 'lowdphi'), ('gjets', sr)),
#    (('zg', 'lowdphi'), ('zg', sr)),
#    (('wg', 'lowdphi'), ('wg', sr))
]

# Sample with free normalization that are not involved in links.
floats = []

wzIgnoreListExp = ['lumi', 'photonSF', 'pixelVetoSF', 'leptonVetoSF', 'gec']
wzIgnoreListThe = ['vgPDF', 'vgQCDscale', 'EWK']
gjIgnoreList = ['lumi', 'photonSF', 'pixelVetoSF', 'leptonVetoSF', 'minorQCDScale'],

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
#    ('zg', 'lowdphi'): wzIgnoreListExp + wzIgnoreListThe,
#    ('wg', 'lowdphi'): wzIgnoreListExp + wzIgnoreListThe,
#    ('gjets', 'lowdphi'): gjIgnoreList,
#    ('gjets', 'monophLowPhi'): gjIgnoreList,
#    ('gjets', 'monophHighPhi'): gjIgnoreList,


}

# Artificial bin-to-bin decorrelation (de-shaping)
deshapedNuisances = [
    'EWK',
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
