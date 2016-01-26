#! /usr/bin/python

from ROOT import TFile
from CutflowMaker import cutflowMaker
import os, sys

inputName = sys.argv[1]
outputFolder = 'test'

def add(name,cut):
    cutflowMaker.AddCut(name,cut)
##

add("MET Cut","met>200")
add("Number of Leptons","n_looselep == 1")
add("Lepton Flavor","abs(lep1PdgId) == 13")
add("Lepton ID","n_tightlep == 1")
add("Number of taus","n_tau == 0")
add("Number of photons","n_loosepho == 0")
add("b Tag Veto","n_bjetsMedium == 0")
add("Jet pT","jet1Pt > 100")
add("Jet ID","jet1isMonoJetId == 1")

if not os.path.exists(outputFolder):
    os.mkdir(outputFolder)
##

inputFile = ROOT.TFile(inputName)
cutflowMaker.SetTree(inputFile.events)

cutflowMaker.PrintCutflow()
#cutflowMaker.MakePlot(outputFolder +"/test")

inputFile.Close()
