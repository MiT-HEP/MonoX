import os

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
distribution = 'mtFullSel'
#distribution = 'mtFullSelDPhiCut'

sourcedir = workdir + '/plots'
outname = workdir + '/fit/ws_' + distribution + '.root'
plotsOutname = workdir + '/fit/ws_' + distribution + '_plots.root'
carddir = workdir + '/fit/datacards'

filename = 'vbfglo.root'
histname = distribution + '/{process}'
signalHistname = distribution + '/samples/{process}_vbfg'

regions = ['vbfg']
data = 'data_obs' # name of data process
processes = ['gjets', 'efake', 'zg', 'wg', 'hfake', 'top']
signals = ['dphv-nlo-125']
xtitle = 'm_{T}^{#gamma} (GeV)'
binWidthNormalized = False

# Links between samples. List of tuples.
# The first sample (=target) of the tuple is represented by (transfer factor) * (second sample (=source)).
# In the fit, the normalization of the source and the transfer factors are allowed to float, with constraints
# on the transfer factors.
links = []

# Sample with free normalization that are not involved in links.
#floats = [('gjets', 'vbfg')]
floats = []

ignoredNuisances = {}

# Artificial bin-to-bin decorrelation (de-shaping)
deshapedNuisances = []

# Correlation in ratios.
# {(target, source, nuisance): correlation}
ratioCorrelations = {}

# Nuisances affecting normalization only
scaleNuisances = ['lumi', 'photonSF', 'customIDSF', 'leptonVetoSF']

# def customize(workspace):
