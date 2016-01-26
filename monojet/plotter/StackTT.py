#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/SkimOut/'

stackPlotter.SetTreeName('events')
stackPlotter.SetAllHist('htotal')
stackPlotter.SetLuminosity(2109.0)
stackPlotter.AddDataFile(directory + 'monojet_MET+Run2015D-PromptReco-v3+AOD.root')
stackPlotter.AddDataFile(directory + 'monojet_MET+Run2015D-PromptReco-v4+AOD.root')
stackPlotter.ReadMCConfig('MCFiles.txt',directory)
stackPlotter.SetDefaultWeight("((jet1isMonoJetId == 1) && (n_looselep == 0 && n_loosepho == 0 && n_tau == 0 && minJetMetDPhi_withendcap > 0.4))*mcWeight*npvWeight*ewk_w*kfactor")
stackPlotter.SetDefaultExpr("met")
stackPlotter.SetEventsPer(10.0)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)

xArray = [200,250,300,350,400,500,600,1000]

stackPlotter.MakeCanvas("~/www/out/test",len(xArray)-1,array('d',xArray),"Jet Mass [GeV]", "Events Per 10 GeV",True)
