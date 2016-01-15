#! /usr/bin/python

import sys,os
import ROOT
import os.path

ROOT.gROOT.LoadMacro('NeroTreeBambu.C+')
ROOT.gROOT.LoadMacro('MonoJetTree.cc+')
ROOT.gROOT.LoadMacro('NeroSlimmer.cc+')

if sys.argv[1] == "test":
        ROOT.NeroSlimmer(
        "root://eoscms//store/user/dmytro/Nero/v1.1.1/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISpring15MiniAODv2_TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_p2/151104_133348/0000/NeroNtuples_skimmed_3.root",
        "testMiniTT.root")
elif sys.argv[1] == "compile":
    exit()
else:
    if not os.path.isfile(sys.argv[2]):
        ROOT.NeroSlimmer(sys.argv[1],
                         sys.argv[2])
    else:
        print sys.argv[2] + " already exists!! Skipping..."
    
