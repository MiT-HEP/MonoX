import os

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
fitdir = workdir + '/fit'
distribution = 'mtPhoMet'

config = WorkspaceConfig(
    sourcename = workdir + '/plots/{region}_combined.root',
    outname = fitdir + '/ws_' + distribution + '.root',
    plotsOutname = fitdir + '/ws_' + distribution + '_plots.root',    
    carddir = fitdir + '/datacards',
    cardname = 'gghg_{signal}.dat',
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
