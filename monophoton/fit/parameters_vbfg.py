import os
import workspace_config as wc

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
distribution = 'mtFullSel'

wc.config = wc.WorkspaceConfig(
    sourcename = workdir + '/plots/vbfglo_background_combined.root',
    outname = workdir + '/fit/ws_vbfg_' + distribution + '.root',
    plotsOutname = workdir + '/fit/ws_vbfg_' + distribution + '_plots.root',
    cardname = workdir + '/fit/datacards/vbfg_{signal}.dat',
    histname = distribution + '/{process}',
    signalHistname = distribution + '/samples/{process}_{region}',
    regions = ['vbfg'],
    bkgProcesses = ['gjets', 'efake', 'zg', 'wg', 'hfake', 'top'],
    signals = ['dph-nlo-125'],
    xname = 'mtvbfh',
    xtitle = 'm_{T}^{#gamma}',
    xunit = 'GeV',
    scaleNuisances = ['lumi', 'photonSF', 'customIDSF', 'leptonVetoSF']
)
