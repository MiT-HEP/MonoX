import os
import workspace_config as wc

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
fitdir = workdir + '/fit'
distribution = 'mtPhoMet'

wc.config = wc.WorkspaceConfig(
    sourcename = workdir + '/plots/gghgNoFake_background_combined.root',
    outname = fitdir + '/ws_gghg_' + distribution + '.root',
    plotsOutname = fitdir + '/ws_gghg_' + distribution + '_plots.root',    
    cardname = fitdir + '/datacards/gghg_{signal}.dat',
    histname = distribution + '/{process}',
    signalHistname = distribution + '/samples/{process}_{region}',
    regions = ['gghg'],
#    bkgProcesses = ['efake', 'wg', 'zg', 'gjets', 'hfake', 'top', 'gg', 'fakemet'],
    bkgProcesses = ['efake', 'wg', 'zg', 'gjets', 'hfake', 'top', 'gg'],
    signals = ['dph-nlo-125'],
    xname = 'mtggh',
    xtitle = 'm_{T}({#gamma, E_{T}^{miss})',
    xunit = 'GeV'
    floatProcesses = ['fakemet'],
    scaleNuisances = ['lumi', 'photonSF', 'pixelVetoIDSF', 'leptonVetoSF', 'egfakerate', 'minorQCDScale'],
    flatParams = ['fakeMetShape']
)
