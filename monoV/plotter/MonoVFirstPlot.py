#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array

directory = '/Users/dabercro/mnt/work/public/Winter15/SkimOut/'

xArray = [200,250,300,350,400,600,1000]

stackPlotter.SetTreeName('events')
stackPlotter.SetAllHist('htotal')
stackPlotter.SetLuminosity(2140.0)
stackPlotter.AddDataFile(directory + 'monojet_MET.root')
stackPlotter.ReadMCConfig('MCFiles.txt',directory)
stackPlotter.SetDefaultWeight("((jet1isMonoJetId == 1 && minJetMetDPhi > 0.5) && (n_looselep == 0 && n_loosepho == 0 && n_tau == 0 && minJetMetDPhi > 0.4))*mcWeight*npvWeight*ewk_w*kfactor")
stackPlotter.SetDefaultExpr("met")
stackPlotter.SetEventsPer(10.0)

stackPlotter.OnlyPDF()
stackPlotter.MakeCanvas("testMonoV",len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per 10 GeV",True)
