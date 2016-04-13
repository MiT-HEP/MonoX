skimDir = '/scratch5/yiiyama/studies/egfake_skim'
outputDir = '/scratch5/yiiyama/studies/egfake'
roofitDictsDir = '/home/yiiyama/cms/studies/RooFit'

binningName = 'eta'

if binningName == 'pt':
    binning = [40., 50., 60., 80., 100., 6500.]
    
    fitBins = []
    for iBin in range(len(binning) - 1):
        repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
        name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
        cut = 'probes.pt > {low:.0f} && probes.pt < {high:.0f}'.format(**repl)
        fitBins.append((name, cut))

elif binningName == 'eta':
    binning = [0., 0.2, 0.4, 0.6, 1., 1.5]

    fitBins = []
    for iBin in range(len(binning) - 1):
        repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
        name = 'eta_{low:.0f}_{high:.0f}'.format(**repl)
        cut = 'probes.pt > 40. && TMath::Abs(probes.eta) > {low:.0f} && TMath::Abs(probes.eta) < {high:.0f}'.format(**repl)
        fitBins.append((name, cut))

elif binningName == 'njet':
    fitBins = []
    for low, high in [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 10)]:
        repl = {'low': low, 'high': high}
        name = 'njet_{low}_{high}'.format(**repl)
        if low == high:
            cut = 'probes.pt > 40. && jets.size == {low}'.repl(**repl)
        else:
            cut = 'probes.pt > 40. && jets.size >= {low} && jets.size <= {high}'
        fitBins.append((name, cut))
