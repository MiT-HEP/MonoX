#! /usr/bin/python

import Corrector
import os

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/SkimTest'

applicator = Corrector.MakeApplicator('test',True,'events','test',100000)
applicator.AddCorrector(Corrector.MakeCorrector('puWeight','npv','1','files/puWeights_13TeV_25ns.root','puWeights'))
applicator.AddCorrector(Corrector.MakeCorrector('kfactor','genBos_pt','genBos_PdgId == 22','files/scalefactors_v3.root','anlo1_over_alo/anlo1_over_alo'))
applicator.AddCorrector(Corrector.MakeCorrector('ewk_a','genBos_pt','genBos_PdgId == 22','files/scalefactors_v3.root','a_ewkcorr/a_ewkcorr'))
applicator.AddCorrector(Corrector.MakeCorrector('ewk_z','genBos_pt','abs(genBos_PdgId) == 23 ','files/scalefactors_v3.root','z_ewkcorr/z_ewkcorr'))
applicator.AddCorrector(Corrector.MakeCorrector('ewk_w','genBos_pt','abs(genBos_PdgId) == 24','files/scalefactors_v3.root','w_ewkcorr/w_ewkcorr'))
applicator.AddCorrector(Corrector.MakeCorrector('wkfactor','genBos_pt','abs(genBos_PdgId) == 24','files/scalefactors_v3.root','wnlo012_over_wlo/wnlo012_over_wlo'))

## Loose electron
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep1Eta)','lep1Pt'],'!(lep1IsMedium || lep1IsTight) && lep1Pt > 0 && abs(lep1PdgId) == 11',
                                                'files/scalefactors_ele-2.root','unfactorized_scalefactors_Veto_ele'))
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep2Eta)','lep2Pt'],'!(lep2IsMedium || lep2IsTight) && lep2Pt > 0 && abs(lep2PdgId) == 11',
                                                'files/scalefactors_ele-2.root','unfactorized_scalefactors_Veto_ele'))
## Medium electron
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep1Eta)','lep1Pt'],'lep1IsMedium && !lep1IsTight && lep1Pt > 0 && abs(lep1PdgId) == 11',
                                                'files/scalefactors_ele-2.root','unfactorized_scalefactors_Medium_ele'))
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep2Eta)','lep2Pt'],'lep2IsMedium && !lep2IsTight && lep2Pt > 0 && abs(lep2PdgId) == 11',
                                                'files/scalefactors_ele-2.root','unfactorized_scalefactors_Medium_ele'))
## Tight electron
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep1Eta)','lep1Pt'],'lep1IsTight && lep1Pt > 0 && abs(lep1PdgId) == 11',
                                                'files/scalefactors_ele-2.root','unfactorized_scalefactors_Tight_ele'))
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep2Eta)','lep2Pt'],'lep2IsTight && lep2Pt > 0 && abs(lep2PdgId) == 11',
                                                'files/scalefactors_ele-2.root','unfactorized_scalefactors_Tight_ele'))
## Loose muon
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep1Eta)','lep1Pt'],'!(lep1IsMedium || lep1IsTight) && lep1Pt > 0 && abs(lep1PdgId) == 13',
                                                'files/scalefactors_mu-2.root','unfactorized_scalefactors_Loose_mu'))
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep2Eta)','lep2Pt'],'!(lep2IsMedium || lep2IsTight) && lep2Pt > 0 && abs(lep2PdgId) == 13',
                                                'files/scalefactors_mu-2.root','unfactorized_scalefactors_Loose_mu'))
## Medium muon
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep1Eta)','lep1Pt'],'lep1IsMedium && !lep1IsTight && lep1Pt > 0 && abs(lep1PdgId) == 13',
                                                'files/scalefactors_mu-2.root','unfactorized_scalefactors_Medium_mu'))
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep2Eta)','lep2Pt'],'lep2IsMedium && !lep2IsTight && lep2Pt > 0 && abs(lep2PdgId) == 13',
                                                'files/scalefactors_mu-2.root','unfactorized_scalefactors_Medium_mu'))
## Tight muon
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep1Eta)','lep1Pt'],'lep1IsTight && lep1Pt > 0 && abs(lep1PdgId) == 13',
                                                'files/scalefactors_mu-2.root','unfactorized_scalefactors_Tight_mu'))
applicator.AddCorrector(Corrector.MakeCorrector('lepton_SF',['abs(lep2Eta)','lep2Pt'],'lep2IsTight && lep2Pt > 0 && abs(lep2PdgId) == 13',
                                                'files/scalefactors_mu-2.root','unfactorized_scalefactors_Tight_mu'))

applicator.AddFactorToMerge('mcWeight')

for fileName in os.listdir(directory):
    if fileName == 'monojet_ZZ.root':
        applicator.ApplyCorrections(directory + "/" + fileName)
    ##
##
