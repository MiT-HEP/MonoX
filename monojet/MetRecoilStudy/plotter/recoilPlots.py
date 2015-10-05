#! /usr/bin/python

import ROOT
import tdrStyle
from MitAna.TreeMod.bambu import mithep, analysis

tdrStyle.setTDRStyle()

datadir = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTrees/"

MetFile        = ROOT.TFile(datadir + "monojet_MET+Run2015D.root")
SingleElecFile = ROOT.TFile(datadir + "monojet_SingleElectron+Run2015D.root")
SinglePhoFile  = ROOT.TFile(datadir + "monojet_SinglePhoton+Run2015D.root")
DYFile         = ROOT.TFile(datadir + "monojet_DYJetsToLL_M-50.root")
GJetsFile      = ROOT.TFile(datadir + "monojet_GJets.root")

MetTree        = MetFile.Get("events")
SingleElecTree = SingleElecFile.Get("events")
SinglePhoTree  = SinglePhoFile.Get("events")
DYTree         = DYFile.Get("events")
GJetsTree      = GJetsFile.Get("events")
print GJetsTree
GJetsTree.AddFriend(GJetsFile.Get("nloTree"))

#plotter = mithep.PlotRecoil()
plotter = mithep.PlotResolution()
plotter.SetIncludeErrorBars(True)

plotter.SetParameterLimits(0,0,1e8)
plotter.SetParameterLimits(1,-20,20)
plotter.SetParameterLimits(2,5,60)

plotter.AddTree(MetTree)
plotter.AddTree(DYTree)
plotter.AddTree(SingleElecTree)
plotter.AddTree(DYTree)
plotter.AddTree(SinglePhoTree)
plotter.AddTree(GJetsTree)

plotter.AddLegendEntry("Z#mu#mu Data",1)
plotter.AddLegendEntry("Z#mu#mu",2)
plotter.AddLegendEntry("Zee Data",3)
plotter.AddLegendEntry("Zee",4)
plotter.AddLegendEntry("#gamma+jets Data",5)
plotter.AddLegendEntry("#gamma+jets",6)

plotter.AddWeight("((lep1PdgId*lep2PdgId == -169) && abs(dilep_m - 91) < 30)")
plotter.AddWeight("((lep1PdgId*lep2PdgId == -169) && abs(dilep_m - 91) < 30)*mcWeight")
plotter.AddWeight("((lep1PdgId*lep2PdgId == -121) && abs(dilep_m - 91) < 30)")
plotter.AddWeight("((lep1PdgId*lep2PdgId == -121) && abs(dilep_m - 91) < 30)*mcWeight")
plotter.AddWeight("(n_loosepho != 0)")
plotter.AddWeight("(n_loosepho != 0) * nloFactor * XSecWeight")

plotter.AddExprX("dilep_pt")
plotter.AddExprX("dilep_pt")
plotter.AddExprX("dilep_pt")
plotter.AddExprX("dilep_pt")
plotter.AddExprX("photonPt")
plotter.AddExprX("photonPt")

plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpPho")
plotter.AddExpr("u_perpPho")

plotter.SetDumpingFits(True)
fits = plotter.MakeFitGraphs(10,0,500,50,-100.0,100.0,2)
#plotter.MakeCanvas(50,-100,100,"test","","","")

plotter.MakeCanvas("UPerp",fits,"","Boson p_{T} [GeV]","#sigma_{u_{#perp}}",0,60)

del plotter

MetFile.Close()
SingleElecFile.Close()
SinglePhoFile.Close()
DYFile.Close()
GJetsFile.Close()
