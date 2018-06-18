import sys
import ROOT

signal = ['dph-nlo-125', 'dphv-nlo-125']
targetname = 'dph-nlo-125'

source = ROOT.TFile.Open(sys.argv[1])
region = sys.argv[2]
out = ROOT.TFile.Open(sys.argv[3], 'recreate')

for dkey in source.GetListOfKeys():
    dist = dkey.GetName()

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
    
    shists = {}
    for s in signal:
        shists[s] = {}
    
    for key in ROOT.gDirectory.GetListOfKeys():
        name = key.GetName()
        if name.endswith('_original'):
            continue
    
        for s in signal:
            sr = s + '_' + region
            if name.startswith(sr):
                suffix = name.replace(sr, '')
                shists[s][suffix] = key.ReadObj()
                break
        else:
            out.cd(dist + '/samples')
            hist = key.ReadObj()
            hist.Write()
    
    out.cd(dist + '/samples')
    s0 = signal[0]
    for suffix in shists[s0].keys():
        base = shists[s0][suffix]
        hist = base.Clone(targetname + '_' + region + suffix)
    
        for s in signal[1:]:
            hist.Add(shists[s][suffix])
    
        hist.Write()
