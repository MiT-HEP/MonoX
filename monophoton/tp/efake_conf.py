import os

skimDir = '/data/t3home000/' + os.environ['USER'] + '/studies/monophoton_panda/efake_skim'
outputDir = '/data/t3home000/' + os.environ['USER'] + '/studies/monophoton_panda/efake'
roofitDictsDir = '/home/yiiyama/cms/studies/RooFit'

# Grouping of samples for convenience.
# Argument targets can be individual sample names or the config names (eldata/mudata/mc).
# Samples in the same data are skimmed for skimTypes (second parameters of the tuples) in the group.
skimConfig = {
#    'phdata': (['sph-16b-m', 'sph-16c-m', 'sph-16d-m', 'sph-16e-m', 'sph-16f-m', 'sph-16g-m', 'sph-16h-m'], ['kEG', 'kMG']),
    'phdata': (['sph-16c-m'], ['kEG', 'kMG']),
#    'mudata': (['smu-16b2', 'smu-16c2'], ['kMG', 'kMMG']),
    'mc': (['dy-50', 'wlnu', 'tt'], ['kEG', 'kMG', 'kMMG']),
    'mcgg': (['gg-80'], ['kEG'])
}

lumiSamples = skimConfig['phdata'][0]

def getBinning(binningName):
    if binningName == 'pt':
        binningTitle = 'p_{T}^{probe} (GeV)'
#        binning = [40., 50., 60., 80., 100., 120., 140., 160., 6500.]
        binning = [175., 200., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

    elif binningName == 'ptalt':
        binningTitle = 'p_{T}^{probe} (GeV)'
#        binning = [40., 50., 60., 80., 100., 120., 140., 160., 6500.]
        binning = [175., 200., 250., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

        binning = [175., 200., 250., 300.]

    elif binningName == 'highpt':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [175., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
#            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            cut = 'probes.pt > {low:.0f} && probes.pt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

    elif binningName == 'highptH':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [175., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
#            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            cut = 'probes.pt > {low:.0f} && probes.pt < {high:.0f} && run >= 280919 && run <= 284044'.format(**repl)
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
        binning = [0., 10., 20., 30.]
    
        fitBins = []
        for low, high in [(0, 9), (10, 19), (20, 29)]:
            repl = {'low': low, 'high': high}
            name = 'npv_{low}_{high}'.format(**repl)
            if low == high:
                cut = 'probes.scRawPt > 175. && npv == {low}'.format(**repl)
            else:
                cut = 'probes.scRawPt > 175. && npv >= {low} && npv <= {high}'.format(**repl)
    
            fitBins.append((name, cut))

    elif binningName == 'npvh':
        binningTitle = 'N^{PV}'
        binning = [0., 10., 20., 30.]
    
        fitBins = []
        for low, high in [(0, 9), (10, 19), (20, 29)]:
            repl = {'low': low, 'high': high}
            name = 'npvh_{low}_{high}'.format(**repl)
            if low == high:
                cut = 'probes.scRawPt > 175. && npv == {low} && run >= 280919 && run <= 284044'.format(**repl)
            else:
                cut = 'probes.scRawPt > 175. && npv >= {low} && npv <= {high} && run >= 280919 && run <= 284044'.format(**repl)
    
            fitBins.append((name, cut))

    elif binningName == 'npvbg':
        binningTitle = 'N^{PV}'
        binning = [0., 10., 20., 30.]
    
        fitBins = []
        for low, high in [(0, 9), (10, 19), (20, 29)]:
            repl = {'low': low, 'high': high}
            name = 'npvh_{low}_{high}'.format(**repl)
            if low == high:
                cut = 'probes.scRawPt > 175. && npv == {low} && run >= 272007 && run <= 280385'.format(**repl)
            else:
                cut = 'probes.scRawPt > 175. && npv >= {low} && npv <= {high} && run >= 272007 && run <= 280385'.format(**repl)
    
            fitBins.append((name, cut))

    elif binningName == 'run':
        binningTitle = 'run'
        binning = []

        fitBins = []
#        fitBins.append(('Run2016B', 'run >= 272007 && run <= 275376 && probes.scRawPt > 175.'))
#        fitBins.append(('Run2016C', 'run >= 275657 && run <= 276283 && probes.scRawPt > 175.'))
        fitBins.append(('Run2016BCD', 'run >= 272007 && run <= 276811 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
#        fitBins.append(('Run2016D', 'run >= 276315 && run <= 276811 && probes.pt > 175.'))
#        fitBins.append(('Run2016E', 'run >= 276831 && run <= 277420 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
#        fitBins.append(('Run2016F', 'run >= 277772 && run <= 278808 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
        fitBins.append(('Run2016EF', 'run >= 276831 && run <= 278808 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
        fitBins.append(('Run2016G', 'run >= 278820 && run <= 280385 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
        fitBins.append(('Run2016H1', 'run >= 280919 && run <= 282500 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
        fitBins.append(('Run2016H2', 'run >= 282500 && run <= 284044 && probes.matchHLT[][2] && probes.scRawPt > 175.'))

    elif binningName == 'chiso':
        binningTitle = 'chiso'
        binning = [0., 0.01, 0.5, 1., 1.37]

        fitBins = []

        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'chiso_{low:.2f}_{high:.2f}'.format(**repl)
            cut = 'probes.scRawPt > 175. && probes.chIso >= {low:.2f} && probes.chIso < {high:.2f}'.format(**repl)
            fitBins.append((name, cut))

    return binningTitle, binning, fitBins

if __name__ == '__main__':
    import sys

    fitBins = getBinning(sys.argv[1])[2]

    print ' '.join([name for name, cut in fitBins])
    
