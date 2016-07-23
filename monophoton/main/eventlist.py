import sys
sys.dont_write_bytecode = True
import os
import array
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

snames = sys.argv[1:]
data = True

tree = ROOT.TChain('cutflow')
for sr in snames:
    tree.Add(config.skimDir + '/' + sr + '.root')
    sname = sr[:sr.rfind('_')]
    sample = allsamples[sname]

    data = sample.data

run = array.array('I', [0])
lumi = array.array('I', [0])
event = array.array('I', [0])

tree.SetBranchAddress('run', run)
tree.SetBranchAddress('lumi', lumi)
tree.SetBranchAddress('event', event)

cuts = []

if data:
    cuts += ['HLT_Photon165_HE10', 'MetFilters']
    # cuts += [ 'MetFilters']

cuts += [
    'PhotonSelection',
    'HighMet',
    'PhotonMetDPhi',
    'MuonVeto',
    'ElectronVeto',
    'JetMetDPhi'
]

tree.Draw('>>elist', ' && '.join(cuts), 'entrylist')
elist = ROOT.gDirectory.Get('elist')
tree.SetEntryList(elist)

evlist = []

iListEntry = 0
while True:
    iEntry = tree.GetEntryNumber(iListEntry)
    if iEntry < 0:
        break

    iListEntry += 1

    tree.GetEntry(iEntry)

    evlist.append((run[0], lumi[0], event[0]))

evlist.sort()

with open('events_' + '+'.join(snames) + '.list', 'w') as output:
    for tup in evlist:
        output.write('%d:%d:%d\n' % tup)
