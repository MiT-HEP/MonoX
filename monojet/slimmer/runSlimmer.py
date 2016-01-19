#! /usr/bin/python

import sys,os
import ROOT
import os.path

ROOT.gROOT.LoadMacro('NeroTreeBambu.C+')
ROOT.gROOT.LoadMacro('MonoJetTree.cc+')
ROOT.gROOT.LoadMacro('NeroSlimmer.cc+')

if sys.argv[1] == "test":
        ROOT.NeroSlimmer(
        "root://eoscms//store/caf/user/yiiyama/nerov5/WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0038.root",
        "test.root")
elif sys.argv[1] == "compile":
    exit()
else:
    if not os.path.isfile(sys.argv[2]):
        ROOT.NeroSlimmer(sys.argv[1],
                         sys.argv[2])
    else:
        print sys.argv[2] + " already exists!! Skipping..."
    
