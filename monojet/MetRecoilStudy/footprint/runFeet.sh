#! /bin/bash

root -q -b -l feetses.cc+\(\"monojet_SingleElectron+Run2015D.root\",\"dilep_pt\",\"u_paraZ\",\"mu_Zee_Data\"\)
root -q -b -l feetses.cc+\(\"monojet_SinglePhoton+Run2015D.root\",\"photonPt\",\"u_paraPho\",\"mu_gjets_Data\"\)
root -q -b -l feetses.cc+\(\"monojet_SingleMuon+Run2015D.root\",\"dilep_pt\",\"u_paraZ\",\"mu_Zmm_Data\"\)
