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
    tree.Add(config.skimDir + '/' + sname + '_monoph.root')
    sample = allsamples[sname]
    ntotal += sample.nevents

bitmasks = {
    'passTrigger': 1 << 0,
    'beginEvent': 1 << 1,
    'vetoMuons': 1 << 2,
    'vetoElectrons': 1 << 3,
    'vetoTaus': 1 << 4,
    'selectPhotons': 1 << 5,
    'cleanJets': 1 << 6,
    'selectMet': 1 << 7,
    'highMet': 1 << 8,
    'metIso': 1 << 9
}

cutflow = [
    ('passTrigger', 'beginEvent', 'cleanJets'),
    ('selectPhotons',),
    ('highMet',),
    ('selectMet',),
    ('vetoMuons', 'vetoElectrons'),
    ('metIso',),
    ('vetoTaus',)
]

# print ntotal, 1

print "%40s %15d %15.4e %15.1e" % ("total", ntotal, (float(ntotal) / ntotal), (ROOT.TEfficiency.ClopperPearson(ntotal, ntotal, 0.6826895, True) - float(ntotal) / ntotal))

mask = 0
for cuts in cutflow:
    if mask == 0:
        name = ' && '.join(cuts)
    else:
        name = ' && ' + ' && '.join(cuts)

    for bitname in cuts:
        mask |= bitmasks[bitname]

    nevt = tree.GetEntries('(cutBits & {mask}) == {mask}'.format(mask = mask))
    # print nevt, '%.4e' % (float(nevt) / ntotal), '%.1e' % (ROOT.TEfficiency.ClopperPearson(ntotal, nevt, 0.6826895, True) - float(nevt) / ntotal), name
    print "%40s %15d %15.4e %15.1e" % (name, nevt, (float(nevt) / ntotal), (ROOT.TEfficiency.ClopperPearson(ntotal, nevt, 0.6826895, True) - float(nevt) / ntotal))
