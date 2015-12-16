#! /usr/bin/python

import sys,os
import ROOT
import os.path

ROOT.gROOT.LoadMacro('NeroTree.C+')
ROOT.gROOT.LoadMacro('MonoJetTree.cc+')
ROOT.gROOT.LoadMacro('NeroSlimmer.cc+')

if sys.argv[1] == "test":
    ROOT.NeroSlimmer(
        "root://eoscms//store/user/yiiyama/transfer/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v3+AODSIM/nero_0001.root",
        "testDY.root")
    ROOT.NeroSlimmer(
        "root://eoscms//store/user/yiiyama/transfer/DYJetsToNuNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0002.root",
        "testZnn.root")
    ROOT.NeroSlimmer(
        "root://eoscms//store/user/yiiyama/transfer/GJets_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0001.root",
        "testGJets.root")
    ROOT.NeroSlimmer(
        "root://eoscms//store/user/yiiyama/transfer/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0001.root",
        "testWJets.root")
    ROOT.NeroSlimmer(
        "root://eoscms//store/user/yiiyama/transfer/MET+Run2015D-PromptReco-v3+AOD/nero_0001.root",
        "testData.root")
elif sys.argv[1] == "TT":
    ROOT.NeroSlimmer(
        "root://eoscms//store/user/yiiyama/transfer/TTbarDMJets_pseudoscalar_Mchi-1_Mphi-100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0000.root",
        "testTT.root")
elif sys.argv[1] == "miniAOD":
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
    
