#! /usr/bin/python

import ROOT

ROOT.gROOT.LoadMacro('ptReweight.cc+')

allSelections = "(jet1isMonoJetId == 1) && "

lepSelection  = "(n_looselep == 2 && n_tightlep > 0 && n_loosepho == 0 && n_tau == 0 && lep2Pt > 20) && abs(dilep_m - 91) < 15 && "

muonSelection = allSelections + lepSelection + "(lep1PdgId*lep2PdgId == -169)"
elecSelection = allSelections + lepSelection + "(lep1PdgId*lep2PdgId == -121)"
phoSelection  = allSelections + "(n_loosepho != 0 && n_looselep == 0 && n_tau == 0)"


ROOT.ptReweight("monojet_SingleElectron+Run2015D.root","dilep_pt",elecSelection)
ROOT.ptReweight("monojet_SingleMuon+Run2015D.root","dilep_pt",muonSelection)
ROOT.ptReweight("monojet_SinglePhoton+Run2015D.root","photonPt",phoSelection)

