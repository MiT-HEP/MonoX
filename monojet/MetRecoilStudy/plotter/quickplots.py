#! /usr/bin/python

import ROOT
import tdrStyle
import time
import os

ROOT.gROOT.LoadMacro('PlotBase.cc+')
ROOT.gROOT.LoadMacro('PlotHists.cc+')

tdrStyle.setTDRStyle()

ROOT.gROOT.SetBatch(True)

allSelections = "(jet1isMonoJetId == 1) && "
metBin = ["100","1000"]

MCFile   = ROOT.TFile("/afs/cern.ch/work/d/dabercro/public/Winter15/forSid/monojet_DY.root")
dataFile = ROOT.TFile("/afs/cern.ch/work/d/dabercro/public/Winter15/GoodRuns/monojet_SingleMuon+Run2015D.root")
#MCFile   = ROOT.TFile("/afs/cern.ch/work/d/dabercro/public/Winter15/flatTrees/monojet_GJets.root")
#dataFile = ROOT.TFile("/afs/cern.ch/work/d/dabercro/public/Winter15/GoodRuns/monojet_SinglePhoton+Run2015D.root")

plotter = ROOT.PlotHists()

mcTree = MCFile.Get("events")
mcTree.AddFriend(MCFile.Get("recoilVariables"))

plotter.AddTree(mcTree)
plotter.AddTree(mcTree)
plotter.AddTree(dataFile.Get("events"))

plotter.SetLegendLimits(0.92,0.9,0.68,0.7)

plotter.AddLegendEntry("MC MET",4)
plotter.AddLegendEntry("Smeared MET",2)
plotter.AddLegendEntry("Data MET",1)

lepSelection  = "(n_looselep == 2 && n_tightlep > 0 && n_loosepho == 0 && n_tau == 0 && lep2Pt > 20) && abs(dilep_m - 91) < 15 && "
muonSelection = allSelections + lepSelection + "(lep1PdgId*lep2PdgId == -169)"
phoSelection  = allSelections + "(n_loosepho != 0 && n_looselep == 0 && n_tau == 0)"

#plotter.SetDefaultWeight(muonSelection + " && dilep_pt > " + metBin[0] + " && dilep_pt < " + metBin[1])
plotter.AddWeight(muonSelection + " && u_magZ > " + metBin[0] + " && u_magZ < " + metBin[1] + " * mcWeight")
plotter.AddWeight(muonSelection + " && sqrt(u1*u1 + u2*u2) > " + metBin[0] + " && sqrt(u1*u1 + u2*u2) < " + metBin[1] + " * mcWeight")
plotter.AddWeight(muonSelection + " && u_magZ > " + metBin[0] + " && u_magZ < " + metBin[1])

plotter.AddExpr("u_paraZ + dilep_pt")
plotter.AddExpr("u1 + dilep_pt")
plotter.AddExpr("u_paraZ + dilep_pt")

plotter.MakeCanvas(25,-150,150,"~/www/somePlots_"+time.strftime("%y%m%d")+"/1_"+metBin[0]+"to"+metBin[1],"","U_{#parallel} + p_{T}^{Z}","Events/12 GeV",2,False)

plotter.ResetExpr()
plotter.AddExpr("u_magZ")
plotter.AddExpr("sqrt(u1*u1 + u2*u2)")
plotter.AddExpr("u_magZ")

plotter.MakeCanvas(20,100,500,"~/www/somePlots_"+time.strftime("%y%m%d")+"/2_"+metBin[0]+"to"+metBin[1],"","|U|","Events/20 GeV",2,True)
plotter.SetLegendLimits(0.15,0.6,0.6,0.85)
plotter.MakeRatio(20,100,500,"~/www/somePlots_"+time.strftime("%y%m%d")+"/3_"+metBin[0]+"to"+metBin[1],"","|U|","Ratio",2)

plotter.ResetExpr()
plotter.AddExpr("trueMet")
plotter.AddExpr("met_smeared")
plotter.AddExpr("trueMet")

#plotter.MakeCanvas(50,0,200,"~/www/somePlots2_"+time.strftime("%y%m%d")+"/3_"+metBin[0]+"to"+metBin[1],"","True MET","AU",True)

del plotter
