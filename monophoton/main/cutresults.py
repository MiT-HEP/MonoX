import sys
import array
import ROOT

fname, event = sys.argv[1:3]

run, lumi, event = event.split(':')

source = ROOT.TFile.Open(fname)
tree = source.Get('cutflow')

branches = tree.GetListOfBranches()
results = {}
for branch in branches:
    bname = branch.GetName()
    if bname == 'run' or bname == 'lumi' or bname == 'event':
        continue

    bit = array.array('B', [0])
    tree.SetBranchAddress(bname, bit)
    results[bname] = (branch, bit)

tree.Draw('>>elist', 'run == %s && lumi == %s && event == %s' % (run, lumi, event), 'entrylist')
elist = ROOT.gDirectory.Get('elist')

if elist.GetN() == 0:
    print 'No event %s:%s:%s found' % (run, lumi, event)
    sys.exit(1)

tree.SetEntryList(elist)
iEntry = tree.GetEntryNumber(0)

for bname in sorted(results.keys()):
    branch, bit = results[bname]

    branch.GetEntry(iEntry)
    if bit[0] != 0:
        print bname
    else:
        print '!' + bname
