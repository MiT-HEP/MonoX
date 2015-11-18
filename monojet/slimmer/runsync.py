#! /usr/bin/python

import sys
import ROOT

ROOT.gROOT.LoadMacro('NeroTree.C+')
ROOT.gROOT.LoadMacro('MonoJetTree.cc+')
ROOT.gROOT.LoadMacro('NeroSlimmer.cc+')

if sys.argv[1] == "sync":
    ROOT.NeroSlimmer(
        "eos/cms/store/caf/user/yiiyama/nerov3redo/TTbarDMJets_pseudoscalar_Mchi-1_Mphi-100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0000.root",
        "sync_ttbar_redo.root")

#if sys.argv[1] == "sync":
#    ROOT.NeroSlimmer(
#        "root://eoscms//store/user/yiiyama/transfer/TTbarDMJets_pseudoscalar_Mchi-1_Mphi-100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0000.root",
#        "sync_ttbar.root")

else:
    ROOT.NeroSlimmer(sys.argv[1],
                     sys.argv[2])
