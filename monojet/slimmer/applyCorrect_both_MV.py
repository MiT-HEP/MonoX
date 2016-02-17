#! /usr/bin/python

import Corrector
import os,sys

directory = sys.argv[1]

applicator = Corrector.MakeApplicator('mcFactors',True,'events','events',100000)

def addCorr(name,expr,cut,fileName,histName):
    applicator.AddCorrector(Corrector.MakeCorrector(name,expr,cut,fileName,histName))
##

addCorr('puWeight','npv','1','files/new_puWeights_13TeV_25ns.root','puWeights')

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

ewk_a = Corrector.MakeCorrector('ewk_a','genBos_pt','genBos_PdgId == 22','files/scalefactors_v4.root','a_ewkcorr/a_ewkcorr')
ewk_z = Corrector.MakeCorrector('ewk_z','genBos_pt','abs(genBos_PdgId) == 23','files/scalefactors_v4.root','z_ewkcorr/z_ewkcorr')
ewk_w = Corrector.MakeCorrector('ewk_w','genBos_pt','abs(genBos_PdgId) == 24','files/scalefactors_v4.root','w_ewkcorr/w_ewkcorr')

kfactor  = Corrector.MakeCorrector('kfactor','genBos_pt','genBos_PdgId == 22','files/uncertainties_8bins.root',['GJets_1j_NLO/nominal_G','GJets_LO/inv_pt_G'])
zkfactor = Corrector.MakeCorrector('zkfactor','genBos_pt','abs(genBos_PdgId) == 23','files/scalefactors_v4.root',['znlo012/znlo012_nominal','zlo/zlo_nominal'])
wkfactor = Corrector.MakeCorrector('wkfactor','genBos_pt','abs(genBos_PdgId) == 24','files/uncertainties_8bins.root',['WJets_012j_NLO/nominal','WJets_LO/inv_pt'])

applicator.AddCorrector(ewk_a)
applicator.AddCorrector(ewk_z)
applicator.AddCorrector(ewk_w)
applicator.AddCorrector(kfactor)
applicator.AddCorrector(zkfactor)
applicator.AddCorrector(wkfactor)

a_ = { 'cut'   : 'genBos_PdgId == 22',
       'list'  : ['GJets'],
       'apply' : [ewk_a,kfactor] }
z_ = { 'cut'   : 'abs(genBos_PdgId) == 23',
       'list'  : ['DYJets','ZJets'],
       'apply' : [ewk_z,zkfactor] }
w_ = { 'cut'   : 'abs(genBos_PdgId) == 24',
       'list'  : ['WJets'],
       'apply' : [ewk_w,wkfactor] }

for fileName in os.listdir(directory):
    if not '.root' in fileName:
        continue
    ##

    for corrector in [ewk_a,ewk_z,ewk_w,kfactor,zkfactor,wkfactor]:
        corrector.SetInCut('runNum == 0')
    ##

    for checker in [a_,z_,w_]:
        for testName in checker['list']:
            if testName in fileName:
                for corrector in checker['apply']:
                    corrector.SetInCut(checker['cut'])
                ##
            ##
        ##
    ##
    
    applicator.ApplyCorrections(directory + "/" + fileName)
##
