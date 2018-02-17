import os

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
distribution = 'mtFullSel'

config = WorkspaceConfig(
    sourcename = workdir + '/plots/vbfg_combined.root',
    outname = workdir + '/fit/ws_' + distribution + '.root',
    plotsOutname = workdir + '/fit/ws_' + distribution + '_plots.root',
    carddir = workdir + '/fit/datacards',
    cardname = 'vbfg_{signal}.dat',
    histname = distribution + '/{process}',
    signalHistname = distribution + '/samples/{process}_{region}',
    regions = ['vbfg'],
    bkgProcesses = ['gjets', 'efake', 'zg', 'wg', 'hfake', 'top'],
    signals = ['signal'],
    xtitle = 'm_{T}^{#gamma} (GeV)',
    scaleNuisances = ['lumi', 'photonSF', 'customIDSF', 'leptonVetoSF']
)
