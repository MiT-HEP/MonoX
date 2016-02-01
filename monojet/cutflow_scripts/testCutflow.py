#! /usr/bin/python

import ROOT
from CutflowMaker import cutflowMaker
import os, sys
import cuts

outputFolder = '/afs/cern.ch/user/d/dabercro/www/monoV_160130/'

def add(name,cut):
    cutflowMaker.AddCut(name,cut)
##

#add("tau cut","n_tau == 0 && 1")
#add("Min MET dPhi","abs(minJetMetDPhi_clean) > 0.5")
#add("B Veto","n_bjetsMedium == 0")
#add("Lep Veto","n_looselep == 0")
#add("Num Photons","n_loosepho == 1")
#add("Photon ID","n_mediumpho == 1")
#add("Photon pT","photonPt > 175")
#add("Photon eta","abs(photonEta) < 1.4442")
add("Mono jet","n_tau == 0 && abs(minJetMetDPhi_clean) > 0.5 && leadingJet_outaccp == 0 && met > 250 && n_bjetsMedium == 0 && n_looselep == 0 && photonPt > 175 && abs(photonEta) < 1.4442 && n_mediumpho == 1 && n_loosepho == 1")
add("Fat Jet pT","fatjet1Pt > 250")
add("N-Subjettiness","fatjet1tau21 < 0.6")
add("High Mass Cut","fatjet1PrunedM < 105")
add("Low Mass Cut","fatjet1PrunedM > 65")

if not os.path.exists(outputFolder):
    os.mkdir(outputFolder)
##

inputFile = ROOT.TFile('/afs/cern.ch/work/d/dabercro/public/Winter15/CleanMETSkim/monojet_Data.root')
cutflowMaker.SetTree(inputFile.events)

cutflowMaker.PrintCutflow()
#cutflowMaker.MakePlot(outputFolder +"/test")

inputFile.Close()
