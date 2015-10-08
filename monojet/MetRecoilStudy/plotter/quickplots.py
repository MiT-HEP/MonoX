#! /usr/bin/python

import ROOT
import tdrStyle

ROOT.gROOT.LoadMacro('PlotBase.cc+')
ROOT.gROOT.LoadMacro('PlotHists.cc+')

tdrStyle.setTDRStyle()

ROOT.gROOT.SetBatch(True)

MCFile   = ROOT.TFile("monojet_DY.root")
dataFile = ROOT.TFile("/afs/cern.ch/work/d/dabercro/public/Winter15/GoodRuns/monojet_SingleMuon+Run2015D.root")

plotter = ROOT.PlotHists()

mcTree = MCFile.Get("events")
mcTree.AddFriend(MCFile.Get("recoilVariables"))

plotter.AddTree(mcTree)
plotter.AddTree(mcTree)
plotter.AddTree(dataFile.Get("events"))

plotter.AddLegendEntry("MC MET",1,1,1)
plotter.AddLegendEntry("Smeared MET",2,1,2)
plotter.AddLegendEntry("Data MET",3)

muonSelection = "((lep1PdgId*lep2PdgId == -169) && abs(dilep_m - 91) < 30 && n_looselep == 2 && n_tightlep > 0 && n_loosepho == 0 && n_tau == 0)"

plotter.AddWeight(muonSelection + " && u_magZ > 20")
plotter.AddWeight(muonSelection + " && sqrt(u1*u1 + u2*u2) > 20")
plotter.AddWeight(muonSelection + " && u_magZ > 20")

plotter.AddExpr("u_paraZ + dilep_pt")
plotter.AddExpr("u1 + dilep_pt")
plotter.AddExpr("u_paraZ + dilep_pt")

plotter.SetNormalizedHists(True)

plotter.MakeCanvas(50,-100,100,"~/www/MetCheck_1","","U_{#parallel} + p_{T}^{Z}","AU")

plotter.ResetExpr()
plotter.AddExpr("u_magZ")
plotter.AddExpr("sqrt(u1*u1 + u2*u2)")
plotter.AddExpr("u_magZ")

plotter.MakeCanvas(40,100,300,"~/www/MetCheck_2","","|U|","AU",True)

del plotter
