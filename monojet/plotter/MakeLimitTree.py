#! /usr/bin/python

from LimitTreeMaker import newLimitTreeMaker
import cuts

#directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/CleanMETSkim/'
#directory = '/Users/dabercro/GradSchool/Winter15/FatMETSkim_160129/'
directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/Correct_w_MJ/'

theFiles = [
    ['monojet_DYJetsToLL_M-50_HT-100to200.root','Zll_ht100',148.0],
    ['monojet_DYJetsToLL_M-50_HT-200to400.root','Zll_ht200',40.94],
    ['monojet_DYJetsToLL_M-50_HT-400to600.root','Zll_ht400',5.497],
    ['monojet_DYJetsToLL_M-50_HT-600toInf.root','Zll_ht600',2.193],
    ['monojet_ZJetsToNuNu_HT-100To200_13TeV.root','Zvv_ht100',280.5],
    ['monojet_ZJetsToNuNu_HT-200To400_13TeV.root','Zvv_ht200',78.36],
    ['monojet_ZJetsToNuNu_HT-400To600_13TeV.root','Zvv_ht400',10.94],
    ['monojet_ZJetsToNuNu_HT-600ToInf_13TeV.root','Zvv_ht600',4.20],
    ['monojet_WJetsToLNu_HT-100To200.root','Wlv_ht100',1343.0],
    ['monojet_WJetsToLNu_HT-200To400.root','Wlv_ht200',359.6],
    ['monojet_WJetsToLNu_HT-400To600.root','Wlv_ht400',48.85],
    ['monojet_WJetsToLNu_HT-600To800.root','Wlv_ht600',12.05],
    ['monojet_WJetsToLNu_HT-800To1200.root','Wlv_ht800',5.501],
    ['monojet_WJetsToLNu_HT-1200To2500.root','Wlv_ht1200',1.329],
    ['monojet_WJetsToLNu_HT-2500ToInf.root','Wlv_ht2500',0.03216],
    ['monojet_QCD_HT200to300.root','QCD_200To300',1735000.0],
    ['monojet_QCD_HT300to500.root','QCD_300To500',366800.0],
    ['monojet_QCD_HT500to700.root','QCD_500To700',29370.0],
    ['monojet_QCD_HT700to1000.root','QCD_700To1000',6524.0],
    ['monojet_QCD_HT1000to1500.root','QCD_1000To1500',1064.0],
    ['monojet_GJets_HT-40To100.root','GJets_40To100',23080.0],
    ['monojet_GJets_HT-100To200.root','GJets_100To200',9235.0],
    ['monojet_GJets_HT-200To400.root','GJets_200To400',2298.0],
    ['monojet_GJets_HT-400To600.root','GJets_400To600',277.6],
    ['monojet_GJets_HT-600ToInf.root','GJets_600ToInf',93.47],
    ['monojet_TTJets.root','others',831.76],
    ['monojet_ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8.root','antitop',26.22],
    ['monojet_ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8.root','top',44.07],
    ['monojet_ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8.root','antitop_5f',35.6],
    ['monojet_ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8.root','top_5f',35.6],
    ['monojet_WW.root','WW',118.7],
    ['monojet_ZZ.root','ZZ',16.6],
    ['monojet_WZ.root','WZ',47.2],
    ['monojet_GluGlu_HToInvisible_M125_13TeV_powheg_pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root','signal_h_ggf',43.92],
    ['monojet_Data.root','data',-1]
]

ltm = newLimitTreeMaker('limits/MonoJetLimitsTrees.root')

ltm.SetTreeName('events')
ltm.AddKeepBranch('met')
ltm.AddKeepBranch('genBos_pt')
ltm.AddKeepBranch('jet1Pt')
ltm.AddWeightBranch('mcFactors')
ltm.SetAllHistName('htotal')
ltm.SetOutputWeightBranch('scaleMC_w')
ltm.SetLuminosity(2240.0)
    
ltm.AddRegion('Zmm',cuts.ZmmMJ)
ltm.AddRegion('Wmn',cuts.WmnMJ)
ltm.AddRegion('signal',cuts.signalMJ_unblinded)
ltm.AddRegion('Wen',cuts.WenMJ + ' && ' + cuts.ETrigger)
ltm.AddRegion('Zee',cuts.ZeeMJ + ' && ' + cuts.ETrigger)
ltm.AddRegion('gjets',cuts.gjetMJ + ' && ' +  cuts.GTrigger)

for aFile in theFiles:
    ltm.AddFile(directory + aFile[0],aFile[1],aFile[2])
##

ltm.AddExceptionDataCut('Zmm',cuts.METTrigger)
ltm.AddExceptionWeightBranch('Zmm','METTrigger')
ltm.AddExceptionDataCut('Wmn',cuts.METTrigger)
ltm.AddExceptionWeightBranch('Wmn','METTrigger')
ltm.AddExceptionDataCut('signal',cuts.METTrigger)
ltm.AddExceptionWeightBranch('signal','METTrigger')


ltm.ExceptionSkip('gjets','QCD_200To300')
ltm.ExceptionSkip('gjets','QCD_300To500')
ltm.ExceptionSkip('gjets','QCD_500To700')
ltm.ExceptionSkip('gjets','QCD_700To1000')
ltm.ExceptionSkip('gjets','QCD_1000To1500')
ltm.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-40To100.root','QCD_40To100',23080.0)
ltm.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-100To200.root','QCD_100To200',9235.0)
ltm.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-200To400.root','QCD_200To400',2298.0)
ltm.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-400To600.root','QCD_400To600',277.6)
ltm.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-600ToInf.root','QCD_600ToInf',93.47)

ltm.MakeTrees()

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/Correct_w_MV/'

ltmV = newLimitTreeMaker('limits/MonoVLimitsTrees.root')

ltmV.SetTreeName('events')
ltmV.AddKeepBranch('met')
ltmV.AddKeepBranch('genBos_pt')
ltmV.AddKeepBranch('jet1Pt')
ltmV.AddWeightBranch('mcFactors')
ltmV.SetAllHistName('htotal')
ltmV.SetOutputWeightBranch('scaleMC_w')
ltmV.SetLuminosity(2109.0)
    
ltmV.AddRegion('Zmm',cuts.ZmmMV)
ltmV.AddRegion('Wmn',cuts.WmnMV)
ltmV.AddRegion('signal',cuts.signalMV_unblinded)
ltmV.AddRegion('Wen',cuts.WenMV + ' && ' + cuts.ETrigger)
ltmV.AddRegion('Zee',cuts.ZeeMV + ' && ' + cuts.ETrigger)
ltmV.AddRegion('gjets',cuts.gjetMV + ' && ' +  cuts.GTrigger)

for aFile in theFiles:
    ltmV.AddFile(directory + aFile[0],aFile[1],aFile[2])
##

ltmV.AddExceptionDataCut('Zmm',cuts.METTrigger)
ltmV.AddExceptionWeightBranch('Zmm','METTrigger')
ltmV.AddExceptionDataCut('Wmn',cuts.METTrigger)
ltmV.AddExceptionWeightBranch('Wmn','METTrigger')
ltmV.AddExceptionDataCut('signal',cuts.METTrigger)
ltmV.AddExceptionWeightBranch('signal','METTrigger')


ltmV.ExceptionSkip('gjets','QCD_200To300')
ltmV.ExceptionSkip('gjets','QCD_300To500')
ltmV.ExceptionSkip('gjets','QCD_500To700')
ltmV.ExceptionSkip('gjets','QCD_700To1000')
ltmV.ExceptionSkip('gjets','QCD_1000To1500')
ltmV.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-40To100.root','QCD_40To100',23080.0)
ltmV.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-100To200.root','QCD_100To200',9235.0)
ltmV.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-200To400.root','QCD_200To400',2298.0)
ltmV.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-400To600.root','QCD_400To600',277.6)
ltmV.ExceptionAdd('gjets',directory + 'Purity/monojet_GJets_HT-600ToInf.root','QCD_600ToInf',93.47)

ltmV.MakeTrees()
