#! /usr/bin/python

import sys
import ROOT

ROOT.gROOT.LoadMacro('NeroTree.C+')
ROOT.gROOT.LoadMacro('MonoJetTree.cc+')
ROOT.gROOT.LoadMacro('NeroSlimmer.cc+')

#if sys.argv[1] == "sync":
#    ROOT.NeroSlimmer(
#        "eos/cms/store/user/yiiyama/nerov3reredo/TTbarDMJets_pseudoscalar_Mchi-1_Mphi-100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0000.root",
#        "sync_ttbar_reredo.root")

if sys.argv[1] == "sync":
    ROOT.NeroSlimmer(
        "/tmp/zdemirag/SinglEl_flat_all.root",
        "single_el.root")

else:
    ROOT.NeroSlimmer(sys.argv[1],
                     sys.argv[2])
