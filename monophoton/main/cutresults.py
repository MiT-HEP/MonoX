import sys
import array
import ROOT

fname, event = sys.argv[1:3]

run, lumi, event = event.split(':')

source = ROOT.TFile.Open(fname)
tree = source.Get('cutflow')

bits = array.array('I', [0])
tree.SetBranchAddress('cutBits', bits)
branch = tree.GetBranch('cutBits')

tree.Draw('>>elist', 'run == %s && lumi == %s && event == %s' % (run, lumi, event), 'entrylist')
elist = ROOT.gDirectory.Get('elist')

tree.SetEntryList(elist)
iEntry = tree.GetEntryNumber(0)

branch.GetEntry(iEntry)

bitmasks = [
    'passTrigger',
    'beginEvent',
    'selectPhotons',
    'vetoMuons',
    'vetoElectrons',
    'vetoTaus',
    'cleanJets',
    'selectMet',
    'highMet',
    'metIso',
]

cutres = bits[0]
for iB in range(len(bitmasks)):
    if cutres & (1 << iB) != 0:
        print bitmasks[iB]
    else:
        print '!' + bitmasks[iB]

