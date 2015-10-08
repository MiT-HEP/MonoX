#! /usr/bin/python

import ROOT
import tdrStyle
from array import array

ROOT.gROOT.LoadMacro('PlotBase.cc+')
ROOT.gROOT.LoadMacro('PlotHists.cc+')
ROOT.gROOT.LoadMacro('PlotResolution.cc+')

tdrStyle.setTDRStyle()

ROOT.gROOT.SetBatch(True)

#datadir  = "/Users/dabercro/GradSchool/Winter15/flatTreesSkimmed/"
#goodRuns = "/Users/dabercro/GradSchool/Winter15/flatTreesSkimmed/"
datadir  = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTrees/"
goodRuns = "/afs/cern.ch/work/d/dabercro/public/Winter15/GoodRuns/"

MuonFile       = ROOT.TFile(goodRuns + "monojet_SingleMuon+Run2015D.root")
SingleElecFile = ROOT.TFile(goodRuns + "monojet_SingleElectron+Run2015D.root")
SinglePhoFile  = ROOT.TFile(goodRuns + "monojet_SinglePhoton+Run2015D.root")
DYFile         = ROOT.TFile(datadir + "monojet_DYJetsToLL_M-50.root")
GJetsFile      = ROOT.TFile(datadir + "monojet_GJets.root")
WJetsFile      = ROOT.TFile(datadir + "monojet_WJetsToLNu.root")

MuonTree       = MuonFile.Get("events")
SingleElecTree = SingleElecFile.Get("events")
SinglePhoTree  = SinglePhoFile.Get("events")
DYTree         = DYFile.Get("events")
GJetsTree      = GJetsFile.Get("events")
GJetsTree.AddFriend(GJetsFile.Get("nloTree"))
WJetsTree      = WJetsFile.Get("events")

plotter = ROOT.PlotResolution()
plotter.SetIncludeErrorBars(True)

plotter.SetParameterLimits(1,5,30)
plotter.SetParameterLimits(2,5,30)

plotter.AddTree(MuonTree)
plotter.AddTree(DYTree)
#plotter.AddTree(SingleElecTree)
#plotter.AddTree(DYTree)
#plotter.AddTree(SinglePhoTree)
#plotter.AddTree(GJetsTree)
#plotter.AddTree(WJetsTree)

plotter.AddLegendEntry("Z#mu#mu Data",1)
plotter.AddLegendEntry("Z#mu#mu",2)
#plotter.AddLegendEntry("Zee Data",3)
#plotter.AddLegendEntry("Zee",4)
#plotter.AddLegendEntry("#gamma+jets Data",5)
#plotter.AddLegendEntry("#gamma+jets",6)
#plotter.AddLegendEntry("W+jets",7)

muonSelection = "((lep1PdgId*lep2PdgId == -169) && abs(dilep_m - 91) < 30 && n_looselep == 2 && n_tightlep > 0 && n_loosepho == 0 && n_tau == 0)"
elecSelection = "((lep1PdgId*lep2PdgId == -121) && abs(dilep_m - 91) < 30 && n_looselep == 2 && n_tightlep == 2 && n_loosepho == 0 && n_tau == 0)"
phoSelection  = "(n_loosepho != 0 && n_looselep == 0 && n_tau == 0)"
#skimSelection = "(n_looselep < 3 && n_loosepho < 2 && n_jets > 0 && jet1Pt > 40 && (met > 50 || u_magZ > 50 || u_magW > 50 || u_magPho > 50))"
skimSelection = "(1 == 1)"

plotter.AddWeight(muonSelection + "&&" + skimSelection)
plotter.AddWeight(muonSelection + "&&" + skimSelection + " * mcWeight")
#plotter.AddWeight(elecSelection)
#plotter.AddWeight(elecSelection + " * mcWeight")
#plotter.AddWeight(phoSelection)
#plotter.AddWeight(phoSelection + " * nloFactor * XSecWeight")
#plotter.AddWeight("(abs(lep1PdgId) == 13 && n_tightlep == 1 && n_looselep == 1 && n_tau == 0 && mt > 50)")

plotter.AddExprX("dilep_pt")
plotter.AddExprX("dilep_pt")
#plotter.AddExprX("dilep_pt")
#plotter.AddExprX("dilep_pt")
#plotter.AddExprX("photonPt")
#plotter.AddExprX("photonPt")
#plotter.AddExprX("genW_pt")

plotter.AddExpr("u_paraZ + dilep_pt")
plotter.AddExpr("u_paraZ + dilep_pt")
#plotter.AddExpr("u_paraZ + dilep_pt")
#plotter.AddExpr("u_paraZ + dilep_pt")
#plotter.AddExpr("u_paraPho + photonPt")
#plotter.AddExpr("u_paraPho + photonPt")
#plotter.AddExpr("u_paraW + genW_pt")

#plotter.AddExpr("u_paraZ")
#plotter.AddExpr("u_paraZ")
#plotter.AddExpr("u_paraZ")
#plotter.AddExpr("u_paraZ")
#plotter.AddExpr("u_paraPho")
#plotter.AddExpr("u_paraPho")
#plotter.AddExpr("u_paraW")

xArray = [20,40,60,100,150,500]

plotter.SetDumpingFits(True)

plotter.MakeFitGraphs(len(xArray)-1,array('d',xArray),50,-100.0,100.0)

mu_u1   = plotter.FitGraph(0)
sig1_u1 = plotter.FitGraph(1)
sig2_u1 = plotter.FitGraph(2)
sig3_u1 = plotter.FitGraph(3)

plotter.ResetExpr()
plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpPho")
plotter.AddExpr("u_perpPho")
plotter.AddExpr("u_perpW")

plotter.MakeFitGraphs(len(xArray)-1,array('d',xArray),50,-100.0,100.0)

mu_u2   = plotter.FitGraph(0)
sig1_u2 = plotter.FitGraph(1)
sig2_u2 = plotter.FitGraph(2)
sig3_u2 = plotter.FitGraph(3)

# Zmm data
# Zmm
# Zee data
# Zee
# GJets data
# GJets

processes = []
processes.append('Data_Zmm')
processes.append('MC_Zmm')

fitVectors = [mu_u1,sig1_u1,sig2_u1,sig3_u1,mu_u2,sig1_u2,sig2_u2,sig3_u2]
fitNames   = ['mu_U1','sig1_U1','sig2_U1','sig3_U1','mu_U2','sig1_U2','sig2_U2','sig3_U2']

muFreq = 4

fitFunc = ROOT.TF1("fitter","[0]+[1]*x+[2]*x*x",0,500)
linFunc = ROOT.TF1("fitter","[0]+[1]*x",0,500)

#############################################################

fitFile = ROOT.TFile("fitResults.root","RECREATE")
for i1 in range(len(processes)):
    for i0 in range(len(fitVectors)):
        if i0 % muFreq == 0:
            fitResult = fitVectors[i0][i1].Fit(linFunc,"S")
            fitFile.WriteTObject(linFunc.Clone("fcn_"+fitNames[i0]+"_"+processes[i1]),"fcn_"+fitNames[i0]+"_"+processes[i1])
        else:
            fitResult = fitVectors[i0][i1].Fit(fitFunc,"S")
            fitFile.WriteTObject(fitFunc.Clone("fcn_"+fitNames[i0]+"_"+processes[i1]),"fcn_"+fitNames[i0]+"_"+processes[i1])
        ##
        fitFile.WriteTObject(fitResult.GetCovarianceMatrix().Clone("cov_"+fitNames[i0]+"_"+processes[i1]),"cov_"+fitNames[i0]+"_"+processes[i1])
##
fitFile.Close()

#############################################################

plotter.MakeCanvas("upara_mu",mu_u1,"","Boson p_{T} [GeV]","#mu_{u_{#parallel}}",-10,60)
plotter.MakeCanvas("upara_sig1",sig1_u1,"","Boson p_{T} [GeV]","#sigma_{1,u_{#parallel}}",0,60)
plotter.MakeCanvas("upara_sig2",sig2_u1,"","Boson p_{T} [GeV]","#sigma_{2,u_{#parallel}}",0,60)
plotter.MakeCanvas("upara_sig3",sig3_u1,"","Boson p_{T} [GeV]","#sigma_{3,u_{#parallel}}",0,60)

plotter.MakeCanvas("uperp_mu",mu_u2,"","Boson p_{T} [GeV]","#mu_{u_{#perp}}",-10,60)
plotter.MakeCanvas("uperp_sig1",sig1_u2,"","Boson p_{T} [GeV]","#sigma_{1,u_{#perp}}",0,60)
plotter.MakeCanvas("uperp_sig2",sig2_u2,"","Boson p_{T} [GeV]","#sigma_{2,u_{#perp}}",0,60)
plotter.MakeCanvas("uperp_sig3",sig3_u2,"","Boson p_{T} [GeV]","#sigma_{3,u_{#perp}}",0,60)

del plotter

MuonFile.Close()
SingleElecFile.Close()
SinglePhoFile.Close()
DYFile.Close()
GJetsFile.Close()
WJetsFile.Close()
