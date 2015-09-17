#!/usr/bin/env python

OUTPUTDIR='/afs/cern.ch/work/d/dabercro/public/Winter15/monojet'

import os
import sys
import glob
import shutil
import ROOT
ROOT.gROOT.SetBatch(True)

sample = sys.argv[1]

ROOT.gROOT.LoadMacro('TreeManager.cc+')
ROOT.gROOT.LoadMacro('monojet.C+')

fChain = ROOT.TChain("nero/events")
globChain = ROOT.TChain("nero/all")

with open('sourceFiles/' + sample + '.txt') as sourceList:
    nSources = 0
    for line in sourceList:
        fChain.Add(line.strip())
        globChain.Add(line.strip())
        nSources += 1

print nSources, 'files added!'

timer = ROOT.TStopwatch()
timer.Start()

monojet = ROOT.monojet(fChain)
monojet.setSuffix(sample)

fChain.Process(monojet)

# reopen output file
Target = ROOT.TFile.Open("monojet_" + sample + ".root","UPDATE")

globChain.Merge(Target,0,"keep")

htotal = ROOT.TH1D('htotal', '', 1, 0., 1.)
globChain.Draw('0.5>>htotal', 'mcWeight', 'goff')

htotal.Write()

print "Total number of effective events:", htotal.GetBinContent(1)
    
Target.SaveSelf(True)
Target.Close()

print "\n\nDone!"
print "CPU Time :", timer.CpuTime()
print "RealTime :", timer.RealTime()
print ''

shutil.copy('monojet_' + sample + '.root', OUTPUTDIR + '/')
os.remove('monojet_' + sample + '.root')
