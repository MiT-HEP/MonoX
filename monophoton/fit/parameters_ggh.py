import os

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
fitdir = workdir + '/fit'
distribution = 'mtPhoMet'

config = WorkspaceConfig(
    sourcename = workdir + '/plots/{region}_combined.root',
    outname = fitdir + '/ws_gghg_' + distribution + '.root',
    plotsOutname = fitdir + '/ws_gghg_' + distribution + '_plots.root',    
    cardname = fitdir + '/datacards/gghg_{signal}.dat',
    histname = distribution + '/{process}',
    signalHistname = distribution + '/samples/{process}_{region}',
    regions = ['gghg'],
    bkgProcesses = ['efake', 'wg', 'zg', 'gjets', 'hfake', 'top', 'gg', 'fakemet'],
    signals = ['signal'],
    xtitle = 'm_{T}({#gamma, E_{T}^{miss}) (GeV)',
    floatProcesses = ['fakemet'],
    scaleNuisances = ['lumi', 'photonSF', 'pixelVetoIDSF', 'leptonVetoSF', 'egfakerate', 'minorQCDScale'],
    flatParams = ['fakeMetShape']
)
