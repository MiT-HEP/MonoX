#! /usr/bin/python

from LimitTreeMaker import newLimitTreeMaker

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/CleanSkim/'

shit = [
    [directory + 'monojet_DYJetsToLL_M-50_HT-100to200.root','Zll_ht100',148.0],
    [directory + 'monojet_DYJetsToLL_M-50_HT-200to400.root','Zll_ht200',40.94],
    [directory + 'monojet_DYJetsToLL_M-50_HT-400to600.root','Zll_ht400',5.497],
    [directory + 'monojet_DYJetsToLL_M-50_HT-600toInf.root','Zll_ht600',2.193],
    [directory + 'monojet_ZJetsToNuNu_HT-100To200_13TeV.root','Zvv_ht100',280.5],
    [directory + 'monojet_ZJetsToNuNu_HT-200To400_13TeV.root','Zvv_ht200',78.36],
    [directory + 'monojet_ZJetsToNuNu_HT-400To600_13TeV.root','Zvv_ht400',10.94],
    [directory + 'monojet_ZJetsToNuNu_HT-600ToInf_13TeV.root','Zvv_ht600',4.20],
    [directory + 'monojet_WJetsToLNu_HT-100To200.root','Wlv_ht100',1343.0],
    [directory + 'monojet_WJetsToLNu_HT-200To400.root','Wlv_ht200',359.6],
    [directory + 'monojet_WJetsToLNu_HT-400To600.root','Wlv_ht400',48.85],
    [directory + 'monojet_WJetsToLNu_HT-600ToInf.root','Wlv_ht600',18.91],
    [directory + 'monojet_QCD_HT200to300.root','QCD_200To300',1735000.0],
    [directory + 'monojet_QCD_HT300to500.root','QCD_300To500',366800.0],
    [directory + 'monojet_QCD_HT500to700.root','QCD_500To700',29370.0],
    [directory + 'monojet_QCD_HT700to1000.root','QCD_700To1000',6524.0],
    [directory + 'monojet_QCD_HT1000to1500.root','QCD_1000To1500',1064.0],
    [directory + 'monojet_GJets_HT-40To100.root','GJets_40To100',23080.0],
    [directory + 'monojet_GJets_HT-100To200.root','GJets_100To200',9235.0],
    [directory + 'monojet_GJets_HT-200To400.root','GJets_200To400',2298.0],
    [directory + 'monojet_GJets_HT-400To600.root','GJets_400To600',277.6],
    [directory + 'monojet_GJets_HT-600ToInf.root','GJets_600ToInf',93.47],
    [directory + 'monojet_TTJets.root','others',831.76],
    [directory + 'monojet_ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8.root','antitop',26.22],
    [directory + 'monojet_ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8.root','top',44.07],
    [directory + 'monojet_ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8.root','antitop_5f',35.6],
    [directory + 'monojet_ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8.root','top_5f',35.6],
    [directory + 'monojet_WW.root','WW',118.7],
    [directory + 'monojet_ZZ.root','ZZ',16.6],
    [directory + 'monojet_WZ.root','WZ',47.2],
    [directory + 'monojet_GluGlu_HToInvisible_M125_13TeV_powheg_pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root','signal_h_ggf',43.92],
    [directory + 'monojet_Data.root','data',-1]
]

for thing in shit:

    ltm = newLimitTreeMaker('limits/' + thing[1] + '.root')

    ltm.SetTreeName('events')
    ltm.AddKeepBranch('met')
    ltm.AddKeepBranch('genBos_pt')
    ltm.AddKeepBranch('jet1Pt')
    ltm.AddWeightBranch('mcFactors')
    ltm.SetAllHistName('htotal')
    ltm.SetOutputWeightBranch('scaleMC_w')
    ltm.SetLuminosity(2109.0)
    
    monoVCut = '&& fatjet1tau21 < 0.45 && fatjet1PrunedM > 65 && fatjet1PrunedM < 105 &&fatjet1Pt > 250 && fatjet1Eta < 2.5 && fatjet1MonojetId == 1'

    ltm.AddRegion('Zmm','(triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)&&n_looselep == 2 && abs(dilep_m - 91) < 30 && (lep1PdgId*lep2PdgId == -169)&&n_tau==0&&n_bjetsMedium==0&&n_loosepho==0&&n_tightlep > 0&&abs(minJetMetDPhi_withendcap)>0.5&&met>200.0' + monoVCut)
    
    ltm.AddRegion('Wmn','(triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)&&n_tau==0&&n_bjetsMedium==0&&n_loosepho==0&& n_tightlep > 0&&abs(minJetMetDPhi_withendcap)>0.5&&n_looselep == 1 && abs(lep1PdgId)==13 &&met>200.0' + monoVCut)
    
    ltm.AddRegion('Wen','(triggerFired[4]==1) || (triggerFired[5]==1) || (triggerFired[11]==1 || triggerFired[12]==1 || triggerFired[13]==1)&&n_tau==0&&n_bjetsMedium==0&&n_loosepho==0&&n_tightlep > 0&&abs(minJetMetDPhi_withendcap)>0.5&&n_looselep == 1 && abs(lep1PdgId)==11 && trueMet > 50 &&met > 200.0' + monoVCut)
    
    ltm.AddRegion('Zee','(triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)&&n_looselep == 2 && abs(dilep_m - 91) < 30 && (lep1PdgId*lep2PdgId == -121)&&n_tau==0&&n_bjetsMedium==0&&n_loosepho==0&&n_tightlep > 0&&abs(minJetMetDPhi_withendcap)>0.5&&met>200.0' + monoVCut)
    
    ltm.AddRegion('signal','(triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)&&n_looselep==0&&n_tau==0&&n_bjetsMedium==0&&n_loosepho==0&&abs(minJetMetDPhi_clean)>0.5&&met>200.0' + monoVCut)
    
    ltm.AddRegion('gjets','(triggerFired[11]==1 || triggerFired[12]==1 || triggerFired[13]==1)&&photonPt > 175 && abs(photonEta) < 1.4442 && n_mediumpho == 1 && n_loosepho == 1&&n_looselep==0&&n_tau==0&&n_bjetsMedium==0&&n_loosepho==0&&met > 200' + monoVCut)

    ltm.AddFile(thing[0],thing[1],thing[2])

    ltm.MakeTree()
