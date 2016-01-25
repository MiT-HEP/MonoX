#! /usr/bin/python

import ROOT
import tdrStyle
import time
import os
import sys

ROOT.gROOT.LoadMacro('PlotBase.cc+')
ROOT.gROOT.LoadMacro('PlotHists.cc+')

tdrStyle.setTDRStyle()

ROOT.gROOT.SetBatch(True)

#direc = "/afs/cern.ch/work/d/dabercro/public/Winter15/MonoX/monojet/MetRecoilStudy/footprint/"
direc = "/Users/dabercro/GradSchool/Winter15/MonoX/monojet/MetRecoilStudy/footprint/"

metCut = "300"

fileMuon   = ROOT.TFile(direc + "monojet_SingleMuon+Run2015D.root")
fileElec   = ROOT.TFile(direc + "monojet_SingleElectron+Run2015D.root")
filePhoton = ROOT.TFile(direc + "monojet_SinglePhoton+Run2015D.root")

treeMuon   = fileMuon.Get("events")
treeMuon.AddFriend(fileMuon.Get("footprints"))
treeMuon.AddFriend(fileMuon.Get("ptweights"))
treeElec   = fileElec.Get("events")
treeElec.AddFriend(fileElec.Get("footprints"))
treeElec.AddFriend(fileElec.Get("ptweights"))
treePhoton = filePhoton.Get("events")
treePhoton.AddFriend(filePhoton.Get("footprints"))
treePhoton.AddFriend(filePhoton.Get("ptweights"))

plotter = ROOT.PlotHists()

plotter.SetLegendLimits(0.13,0.9,0.38,0.7)
#plotter.SetLegendLimits(0.92,0.9,0.68,0.7)

plotter.AddTree(treeMuon)
plotter.AddTree(treeElec)
plotter.AddTree(treePhoton)

plotter.AddLegendEntry("Z #rightarrow #mu#mu",1,4,1)
plotter.AddLegendEntry("Z #rightarrow ee",4)
plotter.AddLegendEntry("#gamma + jets",2,3,7)

allSelections = "(jet1isMonoJetId == 1) && "
lepSelection  = "(n_looselep == 2 && n_tightlep > 0 && n_loosepho == 0 && n_tau == 0 && lep2Pt > 20) && abs(dilep_m - 91) < 15 && dilep_pt > " + metCut + " && "

muonSelection = allSelections + lepSelection + "(lep1PdgId*lep2PdgId == -169)"
elecSelection = allSelections + lepSelection + "(lep1PdgId*lep2PdgId == -121)"
phoSelection  = allSelections + "(n_tightpho != 0 && n_looselep == 0 && n_tau == 0) && photonIsTight == 1 && photonPt > " + metCut

plotter.AddExpr("dilep_pt")
plotter.AddExpr("dilep_pt")
plotter.AddExpr("photonPt")

plotter.AddWeight(muonSelection)
plotter.AddWeight(elecSelection)
plotter.AddWeight(phoSelection) 

print ""
print "###############" + "FootPlots/metCut" + metCut +"_raw_pt" + "###############"
print ""

plotter.MakeCanvas(16,100.0,500.0,"FootPlots/metCut" + metCut +"_raw_pt","","p_{T}^{Z/#gamma} [GeV]","Events")
plotter.MakeCanvas(16,100.0,500.0,"FootPlots/metCut" + metCut +"_raw_pt_Norm","","p_{T}^{Z/#gamma} [GeV]","Events",0,False)

plotter.ResetWeight()
plotter.AddWeight("(" + muonSelection + ") * ptWeight")
plotter.AddWeight("(" + elecSelection + ") * ptWeight")
plotter.AddWeight("(" + phoSelection +  ") * ptWeight")

print ""
print "###############" + "FootPlots/metCut" + metCut +"_reweigh_pt" + "###############"
print ""

plotter.MakeCanvas(13,175.0,500.0,"FootPlots/metCut" + metCut +"_reweigh_pt","","p_{T}^{Z/#gamma} [GeV]","Events")

plotter.ResetExpr()
plotter.AddExpr("u_paraFoot")
plotter.AddExpr("u_paraFoot")
plotter.AddExpr("u_paraFoot")

print ""
print "###############" + "FootPlots/metCut" + metCut +"_reweigh_foot" + "###############"
print ""

plotter.MakeCanvas(20,-400.0,0.0,"FootPlots/metCut" + metCut +"_reweigh_foot","","Corrected u_{#parallel} [GeV]","Events",0,False)

plotter.ResetExpr()
plotter.AddExpr("u_paraZ")
plotter.AddExpr("u_paraZ")
plotter.AddExpr("u_paraPho")

print ""
print "###############" + "FootPlots/metCut" + metCut +"_reweigh_para" + "###############"
print ""

plotter.MakeCanvas(20,-400.0,0.0,"FootPlots/metCut" + metCut +"_reweigh_para","","Raw u_{#parallel} [GeV]","Events",0,False)

plotter.ResetExpr()
plotter.AddExpr("u_paraFoot + dilep_pt")
plotter.AddExpr("u_paraFoot + dilep_pt")
plotter.AddExpr("u_paraFoot + photonPt")

print ""
print "###############" + "FootPlots/metCut" + metCut +"_reweigh_footResp" + "###############"
print ""

plotter.MakeCanvas(20,-150.0,150.0,"FootPlots/metCut" + metCut +"_reweigh_footResp","","Corrected u_{#parallel} + p_{T}^{Z/#gamma} [GeV]","Events",0,False)

plotter.ResetExpr()
plotter.AddExpr("u_paraZ + dilep_pt")
plotter.AddExpr("u_paraZ + dilep_pt")
plotter.AddExpr("u_paraPho + photonPt")

print ""
print "###############" + "FootPlots/metCut" + metCut +"_reweigh_paraResp" + "###############"
print ""

plotter.MakeCanvas(20,-150.0,150.0,"FootPlots/metCut" + metCut +"_reweigh_paraResp","","Raw u_{#parallel} + p_{T}^{Z/#gamma} [GeV]","Events",0,False)

plotter.ResetExpr()
plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpPho")

print ""
print "###############" + "FootPlots/metCut" + metCut +"_reweigh_perp" + "###############"
print ""

plotter.MakeCanvas(30,-150.0,150.0,"FootPlots/metCut" + metCut +"_reweigh_perp","","u_{#perp} [GeV]","Events",0,False)

plotter.ResetWeight()
plotter.AddWeight(muonSelection)
plotter.AddWeight(elecSelection)
plotter.AddWeight(phoSelection) 

print ""
print "###############" + "FootPlots/metCut" + metCut +"_raw_perp" + "###############"
print ""

plotter.MakeCanvas(30,-150.0,150.0,"FootPlots/metCut" + metCut +"_raw_perp","","u_{#perp} [GeV]","Events",0,False)

del plotter
