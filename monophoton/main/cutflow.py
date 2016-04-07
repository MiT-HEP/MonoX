import os
import sys
sys.dont_write_bytecode = True
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

snames = sys.argv[1:]

tree = ROOT.TChain('cutflow')
ntotal = 0
for sname in snames:
    tree.Add(config.skimDir + '/' + sname + '.root')
    sample = allsamples[sname[:sname.rfind('_')]]
    ntotal += sample.nevents

cutflow = [
    ('HLTPhoton165HE10', 'MetFilters'),
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
