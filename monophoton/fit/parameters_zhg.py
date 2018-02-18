import os

workdir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'
distribution = 'imt'

config = WorkspaceConfig(
    sourcename = '/home/yiiyama/cms/studies/MonoX/monophoton/data/zh_results.root',
    outname = workdir + '/fit/ws_zhg_' + distribution + '.root',
    plotsOutname = workdir + '/fit/ws_zhg_' + distribution + '_plots.root',
    cardname = workdir + '/fit/datacards/zhg_{signal}.dat',
    histname = distribution + '/{process}',
    signalHistname = distribution + '/{process}',
    regions = ['zhg'],
    bkgProcesses = ['EM', 'VVV', 'ZZ', 'Zjets', 'WZ'],
    signals = ['signal'],
    xtitle = 'm_{T}^{#gamma} (GeV)',
    scaleNuisances = ['lumi', 'photonSF', 'zh_triggerSF']
)
