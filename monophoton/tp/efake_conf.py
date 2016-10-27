skimDir = '/scratch5/yiiyama/studies/monophoton16/efake_skim_nero'
outputDir = '/scratch5/yiiyama/studies/monophoton16/efake_nero'
roofitDictsDir = '/home/yiiyama/cms/studies/RooFit'

# Grouping of samples for convenience.
# Argument targets can be individual sample names or the config names (eldata/mudata/mc).
# Samples in the same data are skimmed for skimTypes (second parameters of the tuples) in the group.
skimConfig = {
    'eldata': (['sel-16b2', 'sel-16c2', 'sel-16d2'], ['kEG']),
    'mudata': (['smu-16b2', 'smu-16c2'], ['kMG', 'kMMG']),
    'mc': (['dy-50', 'wlnu', 'tt'], ['kEG', 'kMG', 'kMMG']),
    'mcgg': (['gg-80'], ['kEG'])
}

lumiSamples = ['sel-16b2-d', 'sel-16c2-d', 'sel-16d2-d']

def getBinning(binningName):
    if binningName == 'pt':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [40., 50., 60., 80., 100., 120., 140., 160., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.pt > {low:.0f} && probes.pt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

    elif binningName == 'highpt':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [160., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.pt > {low:.0f} && probes.pt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))
    
    elif binningName == 'eta':
        binningTitle = '|#eta^{probe}| (GeV)'
        binning = [0., 0.2, 0.4, 0.6, 1., 1.5]
    
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'eta_{low:.1f}_{high:.1f}'.format(**repl)
            cut = 'probes.pt > 40. && TMath::Abs(probes.eta) > {low:.1f} && TMath::Abs(probes.eta) < {high:.1f}'.format(**repl)
            fitBins.append((name, cut))
    
    elif binningName == 'njet':
        binningTitle = 'N^{jet}'
        binning = [0., 1., 2., 3., 4., 10.]
    
        fitBins = []
        for low, high in [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 10)]:
            repl = {'low': low, 'high': high}
            name = 'njet_{low}_{high}'.format(**repl)
            if low == high:
                cut = 'probes.pt > 40. && TMath::Max(0, jets.size - 2) == {low}'.format(**repl)
            else:
                cut = 'probes.pt > 40. && TMath::Max(0, jets.size - 2) >= {low} && TMath::Max(0, jets.size - 2) <= {high}'.format(**repl)
    
            fitBins.append((name, cut))
    
    elif binningName == 'npv':
        binningTitle = 'N^{PV}'
        binning = [1., 8., 10., 12., 16., 26.]
    
        fitBins = []
        for low, high in [(1, 7), (8, 9), (10, 11), (12, 15), (16, 25)]:
            repl = {'low': low, 'high': high}
            name = 'npv_{low}_{high}'.format(**repl)
            if low == high:
                cut = 'probes.pt > 40. && npv == {low}'.format(**repl)
            else:
                cut = 'probes.pt > 40. && npv >= {low} && npv <= {high}'.format(**repl)
    
            fitBins.append((name, cut))

    return binningTitle, binning, fitBins

if __name__ == '__main__':
    import sys

    fitBins = getBinning(sys.argv[1])[2]

    print ' '.join([name for name, cut in fitBins])
    
