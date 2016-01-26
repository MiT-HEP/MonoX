#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/SkimTest/'

stackPlotter.SetTreeName('events')
stackPlotter.AddFriend('corrections')
stackPlotter.SetAllHist('htotal')
stackPlotter.SetLuminosity(2109.0)
stackPlotter.AddDataFile(directory + 'monojet_MET+Run2015D-PromptReco-v3+AOD.root')
stackPlotter.AddDataFile(directory + 'monojet_MET+Run2015D-PromptReco-v4+AOD.root')
stackPlotter.ReadMCConfig('MCFiles.txt',directory)
stackPlotter.SetDefaultWeight("(jet1isMonoJetId == 1) && (n_looselep == 0 && n_loosepho == 0 && n_tau == 0 && minJetMetDPhi_withendcap > 0.4)")
stackPlotter.SetMCWeights("mcFactors")
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)

stackPlotter.SetDefaultExpr("met")
stackPlotter.SetEventsPer(10.0)
xArray = [200,250,300,350,400,500,600,1000]
stackPlotter.MakeCanvas("plots/met",len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per 10 GeV",True)

stackPlotter.SetDefaultExpr("npv")
stackPlotter.SetEventsPer(1)
stackPlotter.MakeCanvas("plots/npv",23,2,25,"NPV", "Events",False)
