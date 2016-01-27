#! /usr/bin/python

from LimitTreeMaker import newLimitTreeMaker

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/CorrectorTest/'

ltm = newLimitTreeMaker('output.root')

ltm.SetTreeName('events')
ltm.AddKeepBranch('met')
ltm.AddKeepBranch('genBos_pt')
ltm.AddKeepBranch('jet1Pt')
ltm.AddWeightBranch('mcFactors')
ltm.SetAllHistName('htotal')
ltm.SetOutputWeightBranch('scaleMC_w')
ltm.SetLuminosity(2109.0)

ltm.AddRegion('Zmm','(triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)&&jet1isMonoJetIdNew==1&&n_looselep == 2 && abs(dilep_m - 91) < 30 && (lep1PdgId*lep2PdgId == -169)&&abs(jet1Eta)<2.5&&n_tau==0&&n_bjetsMedium==0&&n_loosepho==0&&jet1Pt>100.&&n_tightlep > 0&&abs(minJetMetDPhi_withendcap)>0.5&&met>200.0')

ltm.AddRegion('wmn','(triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)&&jet1isMonoJetIdNew==1&&abs(jet1Eta)<2.5&&n_tau==0&&n_bjetsMedium==0&&n_loosepho==0&&jet1Pt>100.&&\
n_tightlep > 0&&abs(minJetMetDPhi_withendcap)>0.5&&n_looselep == 1 && abs(lep1PdgId)==13 &&met>200.0')

ltm.AddFile(directory + 'monojet_DYJetsToLL_M-50_HT-100to200.root','DYJetsToLL_M-50_HT-100to200',148.0)
ltm.AddFile(directory + 'monojet_DYJetsToLL_M-50_HT-200to400.root','DYJetsToLL_M-50_HT-200to400',40.94)
ltm.AddFile(directory + 'monojet_DYJetsToLL_M-50_HT-400to600.root','DYJetsToLL_M-50_HT-400to600',5.497)
ltm.AddFile(directory + 'monojet_DYJetsToLL_M-50_HT-600toInf.root','DYJetsToLL_M-50_HT-600toInf',2.193)
ltm.AddFile(directory + 'monojet_ZJetsToNuNu_HT-100To200_13TeV.root','ZJetsToNuNu_HT-100To200_13TeV',280.5)
ltm.AddFile(directory + 'monojet_ZJetsToNuNu_HT-200To400_13TeV.root','ZJetsToNuNu_HT-200To400_13TeV',78.36)
ltm.AddFile(directory + 'monojet_ZJetsToNuNu_HT-400To600_13TeV.root','ZJetsToNuNu_HT-400To600_13TeV',10.94)
ltm.AddFile(directory + 'monojet_ZJetsToNuNu_HT-600ToInf_13TeV.root','ZJetsToNuNu_HT-600ToInf_13TeV',4.20)
ltm.AddFile(directory + 'monojet_WJetsToLNu_HT-100To200.root','WJetsToLNu_HT-100To200',1343.0)
ltm.AddFile(directory + 'monojet_WJetsToLNu_HT-200To400.root','WJetsToLNu_HT-200To400',359.6)
ltm.AddFile(directory + 'monojet_WJetsToLNu_HT-400To600.root','WJetsToLNu_HT-400To600',48.85)
ltm.AddFile(directory + 'monojet_WJetsToLNu_HT-600ToInf.root','WJetsToLNu_HT-600ToInf',18.91)
ltm.AddFile(directory + 'monojet_QCD_HT200to300.root','QCD_HT200to300',1735000.0)
ltm.AddFile(directory + 'monojet_QCD_HT300to500.root','QCD_HT300to500',366800.0)
ltm.AddFile(directory + 'monojet_QCD_HT500to700.root','QCD_HT500to700',29370.0)
ltm.AddFile(directory + 'monojet_QCD_HT700to1000.root','QCD_HT700to1000',6524.0)
ltm.AddFile(directory + 'monojet_QCD_HT1000to1500.root','QCD_HT1000to1500',1064.0)
ltm.AddFile(directory + 'monojet_GJets_HT-40To100.root','GJets_HT-40To100',23080.0)
ltm.AddFile(directory + 'monojet_GJets_HT-100To200.root','GJets_HT-100To200',9235.0)
ltm.AddFile(directory + 'monojet_GJets_HT-200To400.root','GJets_HT-200To400',2298.0)
ltm.AddFile(directory + 'monojet_GJets_HT-400To600.root','GJets_HT-400To600',277.6)
ltm.AddFile(directory + 'monojet_GJets_HT-600ToInf.root','GJets_HT-600ToInf',93.47)
ltm.AddFile(directory + 'monojet_TTJets.root','TTJets',831.76)
ltm.AddFile(directory + 'monojet_ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8.root','ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8',26.22)
ltm.AddFile(directory + 'monojet_ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8.root','ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8',44.07)
ltm.AddFile(directory + 'monojet_ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8.root','ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8',35.6)
ltm.AddFile(directory + 'monojet_ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8.root','ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8',35.6)
ltm.AddFile(directory + 'monojet_WW.root','WW',118.7)
ltm.AddFile(directory + 'monojet_ZZ.root','ZZ',16.6)
ltm.AddFile(directory + 'monojet_WZ.root','WZ',47.2)

ltm.MakeTree()
