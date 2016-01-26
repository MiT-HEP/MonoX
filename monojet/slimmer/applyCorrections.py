#! /usr/bin/python

import Corrector
import os,sys

directory = sys.argv[1]

applicator = Corrector.MakeApplicator('mcFactors',True,'events','corrections',100000)

def addCorr(name,expr,cut,fileName,histName):
    applicator.AddCorrector(Corrector.MakeCorrector(name,expr,cut,fileName,histName))
##

addCorr('puWeight','npv','1','files/new_puWeights_13TeV_25ns.root','puWeights')
addCorr('kfactor','genBos_pt','genBos_PdgId == 22','files/scalefactors_v4.root','anlo1_over_alo/anlo1_over_alo')
addCorr('ewk_a','genBos_pt','genBos_PdgId == 22','files/scalefactors_v4.root','a_ewkcorr/a_ewkcorr')
addCorr('ewk_z','genBos_pt','abs(genBos_PdgId) == 23 ','files/scalefactors_v4.root','z_ewkcorr/z_ewkcorr')
addCorr('ewk_w','genBos_pt','abs(genBos_PdgId) == 24','files/scalefactors_v4.root','w_ewkcorr/w_ewkcorr')
addCorr('akfactor','genBos_pt','genBos_PdgId == 22','files/scalefactors_v4.root',['anlo1/anlo1_nominal','alo/alo_nominal'])
addCorr('zkfactor','genBos_pt','abs(genBos_PdgId) == 23','files/scalefactors_v4.root',['znlo012/znlo012_nominal','zlo/zlo_nominal'])
addCorr('wkfactor','genBos_pt','abs(genBos_PdgId) == 24','files/scalefactors_v4.root',['wnlo012/wnlo012_nominal','wlo/wlo_nominal'])

## Loose electron
addCorr('lepton_SF',['abs(lep1Eta)','lep1Pt'],'!(lep1IsMedium || lep1IsTight) && lep1Pt > 0 && abs(lep1PdgId) == 11',
        'files/scalefactors_ele-2.root','unfactorized_scalefactors_Veto_ele')
addCorr('lepton_SF',['abs(lep2Eta)','lep2Pt'],'!(lep2IsMedium || lep2IsTight) && lep2Pt > 0 && abs(lep2PdgId) == 11',
        'files/scalefactors_ele-2.root','unfactorized_scalefactors_Veto_ele')
## Medium electron
addCorr('lepton_SF',['abs(lep1Eta)','lep1Pt'],'lep1IsMedium && !lep1IsTight && lep1Pt > 0 && abs(lep1PdgId) == 11',
        'files/scalefactors_ele-2.root','unfactorized_scalefactors_Medium_ele')
addCorr('lepton_SF',['abs(lep2Eta)','lep2Pt'],'lep2IsMedium && !lep2IsTight && lep2Pt > 0 && abs(lep2PdgId) == 11',
        'files/scalefactors_ele-2.root','unfactorized_scalefactors_Medium_ele')
## Tight electron
addCorr('lepton_SF',['abs(lep1Eta)','lep1Pt'],'lep1IsTight && lep1Pt > 0 && abs(lep1PdgId) == 11',
        'files/scalefactors_ele-2.root','unfactorized_scalefactors_Tight_ele')
addCorr('lepton_SF',['abs(lep2Eta)','lep2Pt'],'lep2IsTight && lep2Pt > 0 && abs(lep2PdgId) == 11',
        'files/scalefactors_ele-2.root','unfactorized_scalefactors_Tight_ele')
## Loose muon
addCorr('lepton_SF',['abs(lep1Eta)','lep1Pt'],'!(lep1IsMedium || lep1IsTight) && lep1Pt > 0 && abs(lep1PdgId) == 13',
        'files/scalefactors_mu-2.root','unfactorized_scalefactors_Loose_mu')
addCorr('lepton_SF',['abs(lep2Eta)','lep2Pt'],'!(lep2IsMedium || lep2IsTight) && lep2Pt > 0 && abs(lep2PdgId) == 13',
        'files/scalefactors_mu-2.root','unfactorized_scalefactors_Loose_mu')
## Medium muon
addCorr('lepton_SF',['abs(lep1Eta)','lep1Pt'],'lep1IsMedium && !lep1IsTight && lep1Pt > 0 && abs(lep1PdgId) == 13',
        'files/scalefactors_mu-2.root','unfactorized_scalefactors_Medium_mu')
addCorr('lepton_SF',['abs(lep2Eta)','lep2Pt'],'lep2IsMedium && !lep2IsTight && lep2Pt > 0 && abs(lep2PdgId) == 13',
        'files/scalefactors_mu-2.root','unfactorized_scalefactors_Medium_mu')
## Tight muon
addCorr('lepton_SF',['abs(lep1Eta)','lep1Pt'],'lep1IsTight && lep1Pt > 0 && abs(lep1PdgId) == 13',
        'files/scalefactors_mu-2.root','unfactorized_scalefactors_Tight_mu')
addCorr('lepton_SF',['abs(lep2Eta)','lep2Pt'],'lep2IsTight && lep2Pt > 0 && abs(lep2PdgId) == 13',
        'files/scalefactors_mu-2.root','unfactorized_scalefactors_Tight_mu')

applicator.AddFactorToMerge('mcWeight')

for fileName in os.listdir(directory):
    applicator.ApplyCorrections(directory + "/" + fileName)
##
