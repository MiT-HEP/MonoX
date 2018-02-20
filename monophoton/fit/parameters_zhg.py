import os
import workspace_config as wc

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
distribution = 'imt'

wc.config = wc.WorkspaceConfig(
    sourcename = basedir + '/data/zh_results.root',
    outname = workdir + '/fit/ws_zhg_' + distribution + '.root',
    plotsOutname = workdir + '/fit/ws_zhg_' + distribution + '_plots.root',
    cardname = workdir + '/fit/datacards/zhg_{signal}.dat',
    histname = distribution + '/{process}',
    regions = ['zhg'],
    bkgProcesses = ['EM', 'VVV', 'ZZ', 'Zjets', 'WZ'],
    signals = ['dph-nlo-125'],
    xtitle = 'm_{T}^{#gamma} (GeV)',
    scaleNuisances = ['lumi', 'photonSF', 'zh_triggerSF']
)
