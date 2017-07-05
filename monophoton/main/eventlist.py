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
import utils

region = sys.argv[1] 
snames = sys.argv[2:]
data = False

sampleNames = []

tree = ROOT.TChain('cutflow')
for sample in allsamples.getmany(snames):
    sampleNames.append(sample.name)
    tree.Add(utils.getSkimPath(sample.name, region))
    data = sample.data

run = array.array('I', [0])
lumi = array.array('I', [0])
event = array.array('I', [0])

tree.SetBranchAddress('runNumber', run)
tree.SetBranchAddress('lumiNumber', lumi)
tree.SetBranchAddress('eventNumber', event)

cuts = []

if data:
    cuts += ['HLT_Photon165_HE10', 'MetFilters']

cuts += [
    'PhotonSelection_nominal',
    'HighMet',
    'LeptonSelection',
    'PhotonMetDPhi',
    'JetMetDPhi',
]

if region == 'monomu':
    cuts += ['LeptonMt']

elif region == 'monoel':
    cuts += ['RealMetCut', 'LeptonMt']

elif region in ['dimu', 'diel']:
    cuts += ['Mass', 'OppositeSign']

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

print len(evlist)

with open('events_' + region + '_' + '+'.join(sampleNames) + '.list', 'w') as output:
    for tup in evlist:
        output.write('%d:%d:%d\n' % tup)
