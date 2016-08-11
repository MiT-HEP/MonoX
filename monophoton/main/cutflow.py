import os
import sys
sys.dont_write_bytecode = True
from argparse import ArgumentParser

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

argParser = ArgumentParser(description = 'Print cut flow')
argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '+', help = 'Sample names.')
argParser.add_argument('region', metavar = 'REGION', help = 'Control/signal egion name.')
argParser.add_argument('--skim-dir', '-s', metavar = 'PATH', dest = 'skimDir', default = config.skimDir, help = 'Directory of skim files to read from.')
argParser.add_argument('--ntuples-dir', '-n', metavar = 'PATH', dest = 'ntuplesDir', default = config.ntuplesDir, help = 'Directory of source ntuples.')

args = argParser.parse_args()
sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

data = False

ntotal = 0

tree = ROOT.TChain('cutflow')
for sname in args.snames:
    tree.Add(args.skimDir + '/' + sname + '_' + args.region + '.root')
    sample = allsamples[sname]
    if sample.data:
        data = True

    if args.skimDir == config.skimDir:
        # default skim directory -> assume nevents in DB is accurate
        ntotal += sample.nevents

    else:
        # otherwise open the original files
        sdir = args.ntuplesDir + '/' + sample.book + '/' + sample.fullname
        for fname in os.listdir(sdir):
            source = ROOT.TFile.Open(sdir + '/' + fname)
            counter = source.Get('counter')
            if not counter:
                source.Close()
                continue
    
            ntotal += counter.GetBinContent(1)
            source.Close()

cutflow = []
if data:
    cutflow.append(('HLT_Photon165_HE10',))
#    cutflow.append(('HLTPhoton165HE10',))
    cutflow.append(('MetFilters',))

cutflow += [
    ('PhotonSelection',),
    ('HighMet',),
    ('PhotonMetDPhi',),
    ('MuonVeto', 'ElectronVeto'),
    ('JetMetDPhi',),
    ('TauVeto',)
]

# print ntotal, 1

print "%40s %15d %15.4e %15.1e" % ("total", ntotal, (float(ntotal) / ntotal), (ROOT.TEfficiency.ClopperPearson(ntotal, ntotal, 0.6826895, True) - float(ntotal) / ntotal))

expr = ''
for cuts in cutflow:
    if expr == '':
        name = ' && '.join(cuts)
        expr = name
    else:
        name = ' && ' + ' && '.join(cuts)
        expr += name

    nevt = tree.GetEntries(expr)
    # print nevt, '%.4e' % (float(nevt) / ntotal), '%.1e' % (ROOT.TEfficiency.ClopperPearson(ntotal, nevt, 0.6826895, True) - float(nevt) / ntotal), name
    print "%40s %15d %15.4e %15.1e" % (name, nevt, (float(nevt) / ntotal), (ROOT.TEfficiency.ClopperPearson(ntotal, nevt, 0.6826895, True) - float(nevt) / ntotal))
