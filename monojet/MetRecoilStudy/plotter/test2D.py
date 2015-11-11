#! /usr/bin/python

import ROOT
import tdrStyle
from array import array
from selectionCuts import *

ROOT.gROOT.LoadMacro('PlotBase.cc+')
#ROOT.gROOT.LoadMacro('PlotHists.cc+')
ROOT.gROOT.LoadMacro('Plot2D.cc+')

tdrStyle.setTDRStyle()

ROOT.gROOT.SetBatch(True)

sampledir = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV5/"
goodRuns  = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV5/"
#sampledir = "/Users/dabercro/GradSchool/Winter15/flatTreesSkimmedV3/"
#goodRuns  = "/Users/dabercro/GradSchool/Winter15/GoodRunsV3/"

MuonFile       = ROOT.TFile(goodRuns + "monojet_SingleMuon+Run2015D.root")
SingleElecFile = ROOT.TFile(goodRuns + "monojet_SingleElectron+Run2015D.root")
SinglePhoFile  = ROOT.TFile(goodRuns + "monojet_SinglePhoton+Run2015D.root")
DYFile         = ROOT.TFile(sampledir + "monojet_DYJetsToLL_M-50.root")
GJetsFile      = ROOT.TFile(sampledir + "monojet_GJets.root")

MuonTree       = MuonFile.Get("events")
SingleElecTree = SingleElecFile.Get("events")
SinglePhoTree  = SinglePhoFile.Get("events")
DYTree         = DYFile.Get("events")
GJetsTree      = GJetsFile.Get("events")

plotter = ROOT.Plot2D()

#####################################

fitBin = 150.0
ptCut  = 60.0

allSelections = "(jet1isMonoJetId == 1 && jet1Pt > 100) && "

#####################################

plotter.SetIncludeErrorBars(True)

plotter.AddTree(MuonTree)
plotter.AddTree(DYTree)
plotter.AddTree(SingleElecTree)
plotter.AddTree(DYTree)
plotter.AddTree(SinglePhoTree)
plotter.AddTree(GJetsTree)

plotter.AddLegendEntry("Z#mu#mu Data",1)
plotter.AddLegendEntry("Z#mu#mu",2)
plotter.AddLegendEntry("Zee Data",3)
plotter.AddLegendEntry("Zee",4)
plotter.AddLegendEntry("#gamma+jets Data",3)
plotter.AddLegendEntry("#gamma+jets",4)

plotter.AddName("Zmm_Data")
plotter.AddName("Zmm_MC")
plotter.AddName("Zee_Data")
plotter.AddName("Zee_MC")
plotter.AddName("gjets_Data")
plotter.AddName("gjets_MC")

plotter.AddWeight("(" + ZmmSelection + " && dilep_pt > " + str(ptCut) + ")")
plotter.AddWeight("(" + ZmmSelection + " && genBos_PdgId == 23 && genBos_pt > " + str(ptCut) + ") * leptonSF * mcWeight * npvWeight")
plotter.AddWeight("(" + ZeeSelection + " && dilep_pt > " + str(ptCut) + ")")
plotter.AddWeight("(" + ZeeSelection + " && genBos_PdgId == 23 && genBos_pt > " + str(ptCut) + ") * leptonSF * mcWeight * npvWeight")
plotter.AddWeight("(" + phoSelection + " && photonPtRaw > " + str(ptCut) + ")")
plotter.AddWeight("(" + phoSelection + " && genBos_PdgId == 22 && genBos_pt > " + str(ptCut) + ") * kfactor * XSecWeight * npvWeight")

plotter.AddExprX("dilep_pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("dilep_pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("photonPtRaw")
plotter.AddExprX("genBos_pt")

plotter.AddExpr("u_para + dilep_pt")
plotter.AddExpr("u_para + dilep_pt")
plotter.AddExpr("u_para + dilep_pt")
plotter.AddExpr("u_para + dilep_pt")
plotter.AddExpr("u_para + photonPtRaw")
plotter.AddExpr("u_para + photonPtRaw")

plotter.MakeFitGraphs(100,0,1000,300,-1*fitBin,fitBin)

plotter.ResetExpr()
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perp")

plotter.MakeFitGraphs(100,0,1000,300,-1*fitBin,fitBin)

del plotter

MuonFile.Close()
SingleElecFile.Close()
SinglePhoFile.Close()
DYFile.Close()
GJetsFile.Close()
