import os
import workspace_config as wc

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
fitdir = workdir + '/fit'
distribution = 'mtPhoMet'

wc.config = wc.WorkspaceConfig(
    sourcename = 'injection.root',
    outname = 'workspace.root',
    cardname = 'datacard.dat',
    histname = distribution + '/{process}',
    signalHistname = distribution + '/samples/{process}_{region}',
    regions = ['gghg'],
    bkgProcesses = ['efake', 'wg', 'zg', 'gjets', 'hfake', 'top', 'gg', 'fakemet'],
    signals = ['dph-nlo-125'],
    xname = 'mtggh',
    xtitle = 'm_{T}({#gamma, E_{T}^{miss})',
    xunit = 'GeV',
    floatProcesses = ['fakemet'],
    scaleNuisances = ['lumi', 'photonSF', 'pixelVetoIDSF', 'leptonVetoSF', 'egfakerate', 'minorQCDScale'],
    flatParams = ['fakeMetShape']
)
