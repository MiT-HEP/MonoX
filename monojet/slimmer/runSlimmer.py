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
        "root://eoscms//eos/cms/store/user/dabercro/Nero/v1.2/JHUGen_Higgs_ZH_125_10/JHUGen_Higgs_ZH_125_10/160221_112337/0000/NeroNtuples_1.root",
#        "/scratch3/ceballos/hist/monov_all/t2mit/filefi/043/VectorMonoW_Mphi-50_Mchi-10_gSM-1p0_gDM-1p0_13TeV-madgraph+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0000.root",
        "test.root")
elif sys.argv[1] == "compile":
    exit()
else:
    if not os.path.isfile(sys.argv[2]):
        try:
            testFile = ROOT.TFile(sys.argv[1])
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
