#! /usr/bin/python

import sys,os
import ROOT
import os.path

OutTreeName = 'MonoJetTree'

os.system(os.environ['CROMBIEPATH'] + '/scripts/MakeTree.sh ' + OutTreeName)
ROOT.gROOT.LoadMacro(OutTreeName + '.cc+')

ROOT.gROOT.LoadMacro('NeroTree76.C+')
ROOT.gROOT.LoadMacro('NeroSlimmer.cc+')

if sys.argv[1] == "test":
    ROOT.NeroSlimmer(
#        "root://eoscms//eos/cms/store/user/dabercro/Nero/v1.2/MET/MET-Run2015D-v4/160216_152458/0000/NeroNtuples_2.root",
#        "root://eoscms//eos/cms/store/user/dabercro/Nero/v1.2/DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/DYJetsToLL_M-50_HT-100to200/160216_150808/0000/NeroNtuples_31.root",
        "root://eoscms//eos/cms/store/user/dabercro/Nero/v1.2/VBF_HToInvisible_M125_13TeV_powheg_pythia8/VBF_HToInvisible_M125_13TeV/160216_151800/0000/NeroNtuples_1.root",
#        "/scratch3/ceballos/hist/monov_all/t2mit/filefi/043/VectorMonoW_Mphi-50_Mchi-10_gSM-1p0_gDM-1p0_13TeV-madgraph+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0000.root",
        "test.root")
elif sys.argv[1] == "compile":
    exit()
else:
    if not os.path.isfile(sys.argv[2]):
        try:
            testFile = ROOT.TFile.Open(sys.argv[1])
            if not 'nero' in testFile.GetListOfKeys():
                testFile.Close()
                exit(0)

            testFile.Close()
            isSig = False
            if (((('DMS' in sys.argv[1]) or ('DMV' in sys.argv[1])) and 
                 ('NNPDF' in sys.argv[1]) and ('powheg' in sys.argv[1])) or 
                (('MonoW' in sys.argv[1]) or ('MonoZ' in sys.argv[1])) or
                ('JHUGen_Higgs' in sys.argv[1])):
                isSig = True
                print 'Running on signal!'

            ROOT.NeroSlimmer(sys.argv[1],
                         sys.argv[2],
                         isSig)
        except:
            print " Something didn't open right ... "
    else:
        print sys.argv[2] + " already exists!! Skipping..."
    
exit(0)
