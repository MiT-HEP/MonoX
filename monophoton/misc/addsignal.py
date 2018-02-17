import sys
import ROOT

signal = ['dph-nlo-125', 'dphv-nlo-125']

source = ROOT.TFile.Open(sys.argv[1])
out = ROOT.TFile.Open('addsignal.root', 'recreate')

dist = sys.argv[2]

out.mkdir(dist)

source.cd(dist)
for key in ROOT.gDirectory.GetListOfKeys():
    if key.GetName() == 'samples':
        continue

    out.cd(dist)
    hist = key.ReadObj()
    hist.Write()

out.mkdir(dist + '/samples')

source.cd(dist + '/samples')
for key in ROOT.gDirectory.GetListOfKeys():
    name = key.GetName()
    if name.startswith(signal[0]):
        if name.endswith('_original'):
            continue

        name1 = name.replace(signal[0], signal[1])

        out.cd(dist + '/samples')
        hist = key.ReadObj()
        hist.SetName(name.replace(signal[0], 'signal'))
        hist.Add(source.Get(dist + '/samples/' + name1))
        hist.Write()

    elif name.startswith(signal[1]):
        continue

    else:
        out.cd(dist + '/samples')
        hist = key.ReadObj()
        hist.Write()
