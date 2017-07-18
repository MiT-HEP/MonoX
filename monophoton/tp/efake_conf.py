import os

outputDir = '/data/t3home000/' + os.environ['USER'] + '/monophoton/efake_pog'
roofitDictsDir = '/home/yiiyama/cms/studies/RooFit'

# panda::XPhoton::IDTune { 0 : S15, 1 : S16, 2 : GJCWiso, 3 : ZGCWIso }
itune = 1

fitBinningT = (120, 60., 120.)

dataSource = 'sel' # sph or sel or smu
if dataSource == 'sph':
    tpconfs = ['ee', 'eg', 'pass', 'fail']
elif dataSource == 'sel':
    tpconfs = ['ee', 'eg', 'pass', 'fail']
elif dataSource == 'smu':
    tpconfs = ['passiso', 'failiso']

# Grouping of samples for convenience.
# Argument targets can be individual sample names or the config names (eldata/mudata/mc).
# Samples in the same data are skimmed for skimTypes (second parameters of the tuples) in the group.
dy50 = ['dy-50', 'dy-50-100', 'dy-50-200', 'dy-50-400', 'dy-50-600', 'dy-50-800', 'dy-50-1200', 'dy-50-2500']
skimConfig = {
    'phdata': (['sph-16b-m', 'sph-16c-m', 'sph-16d-m', 'sph-16e-m', 'sph-16f-m', 'sph-16g-m', 'sph-16h-m'], ['kEG', 'kMG']),
    'eldata': (['sel-16b-m', 'sel-16c-m', 'sel-16d-m', 'sel-16e-m', 'sel-16f-m', 'sel-16g-m', 'sel-16h-m'], ['kEG']),
#    'mudata': (['smu-16b-m', 'smu-16c-m', 'smu-16d-m', 'smu-16e-m', 'smu-16f-m', 'smu-16g-m', 'smu-16h-m'], ['kMG']),
    'mudata': (['smu-16c-m'], ['kME']),
    'mc': (dy50 + ['wglo', 'tt'], ['kEG', 'kMG', 'kMMG']),
    'mcmu': (dy50, ['kEG', 'kMG', 'kMMG']),
    'mcgg': (['gg-80'], ['kEG'])
}

lumiSamples = skimConfig['phdata'][0]

def getBinning(binningName):
    if binningName == 'inclusive':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [175., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

        binning.pop()
        binning.append(500.)

    elif binningName == 'pt':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [175., 200., 250., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

        binning.pop()
        binning.append(500.)

    elif binningName == 'ptalt':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [175., 200., 250., 300., 350., 400., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

        binning.pop()
        binning.append(500.)

    elif binningName == 'highpt':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [175., 200., 225., 250., 275., 300., 350., 400., 6500.] 
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

        binning.pop()
        binning.append(500.)

    elif binningName == 'highptH':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [175., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

    elif binningName == 'lowpt':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [24., 28., 32., 35., 38., 40., 42., 44., 46., 48., 50., 54., 58., 62., 66., 70., 75., 80., 85., 90., 100., 120., 140., 160.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

    elif binningName == 'pogpt':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [20., 35., 50., 90., 150., 6500.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

        binning.pop()
        binning.append(500.)

    elif binningName == 'test':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [24., 28.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.scRawPt > {low:.0f} && probes.scRawPt < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))

    elif binningName == 'mutest':
        binningTitle = 'p_{T}^{probe} (GeV)'
        binning = [24., 28.]
        
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
            cut = 'probes.pt_ > {low:.0f} && probes.pt_ < {high:.0f}'.format(**repl)
            fitBins.append((name, cut))
    
    elif binningName == 'eta':
        binningTitle = '|#eta^{probe}| (GeV)'
        binning = [0., 0.2, 0.4, 0.6, 1., 1.5]
    
        fitBins = []
        for iBin in range(len(binning) - 1):
            repl = {'low': binning[iBin], 'high': binning[iBin + 1]}
            name = 'eta_{low:.1f}_{high:.1f}'.format(**repl)
            cut = 'probes.scRawPt > 40. && TMath::Abs(probes.eta_) > {low:.1f} && TMath::Abs(probes.eta_) < {high:.1f}'.format(**repl)
            fitBins.append((name, cut))
    
    elif binningName == 'njet':
        binningTitle = 'N^{jet}'
        binning = [0., 1., 2., 3., 4., 10.]
    
        fitBins = []
        for low, high in [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 10)]:
            repl = {'low': low, 'high': high}
            name = 'njet_{low}_{high}'.format(**repl)
            if low == high:
                cut = 'probes.scRawPt > 40. && TMath::Max(0, jets.size - 2) == {low}'.format(**repl)
            else:
                cut = 'probes.scRawPt > 40. && TMath::Max(0, jets.size - 2) >= {low} && TMath::Max(0, jets.size - 2) <= {high}'.format(**repl)
    
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
                cut = 'probes.scRawPt > 175. && npv == {low} && runNumber >= 280919 && runNumber <= 284044'.format(**repl)
            else:
                cut = 'probes.scRawPt > 175. && npv >= {low} && npv <= {high} && runNumber >= 280919 && runNumber <= 284044'.format(**repl)
    
            fitBins.append((name, cut))

    elif binningName == 'npvbg':
        binningTitle = 'N^{PV}'
        binning = [0., 10., 20., 30.]
    
        fitBins = []
        for low, high in [(0, 9), (10, 19), (20, 29)]:
            repl = {'low': low, 'high': high}
            name = 'npvh_{low}_{high}'.format(**repl)
            if low == high:
                cut = 'probes.scRawPt > 175. && npv == {low} && runNumber >= 272007 && runNumber <= 280385'.format(**repl)
            else:
                cut = 'probes.scRawPt > 175. && npv >= {low} && npv <= {high} && runNumber >= 272007 && runNumber <= 280385'.format(**repl)
    
            fitBins.append((name, cut))

    elif binningName == 'run':
        binningTitle = 'run'
        binning = []

        fitBins = []
#        fitBins.append(('Run2016B', 'runNumber >= 272007 && runNumber <= 275376 && probes.scRawPt > 175.'))
#        fitBins.append(('Run2016C', 'runNumber >= 275657 && runNumber <= 276283 && probes.scRawPt > 175.'))
        fitBins.append(('Run2016BCD', 'runNumber >= 272007 && runNumber <= 276811 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
#        fitBins.append(('Run2016D', 'runNumber >= 276315 && runNumber <= 276811 && probes.pt > 175.'))
#        fitBins.append(('Run2016E', 'runNumber >= 276831 && runNumber <= 277420 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
#        fitBins.append(('Run2016F', 'runNumber >= 277772 && runNumber <= 278808 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
        fitBins.append(('Run2016EF', 'runNumber >= 276831 && runNumber <= 278808 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
        fitBins.append(('Run2016G', 'runNumber >= 278820 && runNumber <= 280385 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
        fitBins.append(('Run2016H1', 'runNumber >= 280919 && runNumber <= 282500 && probes.matchHLT[][2] && probes.scRawPt > 175.'))
        fitBins.append(('Run2016H2', 'runNumber >= 282500 && runNumber <= 284044 && probes.matchHLT[][2] && probes.scRawPt > 175.'))

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
    
