#! /usr/bin/python

import ROOT
import tdrStyle
from array import array

ROOT.gROOT.LoadMacro('PlotBase.cc+')
ROOT.gROOT.LoadMacro('PlotHists.cc+')
ROOT.gROOT.LoadMacro('PlotResolution.cc+')

tdrStyle.setTDRStyle()

ROOT.gROOT.SetBatch(True)

sampledir = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTrees/"
goodRuns  = "/afs/cern.ch/work/d/dabercro/public/Winter15/GoodRuns/"

MuonFile       = ROOT.TFile(goodRuns + "monojet_SingleMuon+Run2015D.root")
SingleElecFile = ROOT.TFile(goodRuns + "monojet_SingleElectron+Run2015D.root")
SinglePhoFile  = ROOT.TFile(goodRuns + "monojet_SinglePhoton+Run2015D.root")
DYFile         = ROOT.TFile(sampledir + "monojet_DYJetsToLL_M-50.root")
GJetsFile      = ROOT.TFile(sampledir + "monojet_GJets.root")
WJetsFile      = ROOT.TFile(sampledir + "monojet_WJetsToLNu.root")

MuonTree       = MuonFile.Get("events")
SingleElecTree = SingleElecFile.Get("events")
SinglePhoTree  = SinglePhoFile.Get("events")
DYTree         = DYFile.Get("events")
GJetsTree      = GJetsFile.Get("events")
GJetsTree.AddFriend(GJetsFile.Get("nloTree"))
WJetsTree      = WJetsFile.Get("events")

plotter = ROOT.PlotResolution()

#####################################

fitBin = 150.0

xArray = [10,20,40,60,80,100,150,300,1000]
plotter.SetFractionLimit(0.05)

plotter.SetParameterLimits(0,-50,50)
plotter.SetParameterLimits(1,5,60)
plotter.SetParameterLimits(2,5,60)

#fitFunc = ROOT.TF1("fitter","[0]+[1]*x+[2]*x*x",0,1000)
fitFunc = ROOT.TF1("fitter","[0]+[1]*x+[2]*log(x)",0,1000)
linFunc = ROOT.TF1("fitter","[0]+[1]*x",0,1000)

#fitFunc.SetParLimits(2,-0.02,0.02)
fitFunc.SetParLimits(1,0,2)
fitFunc.SetParLimits(2,-5,5)
#fitFunc.SetParLimits(3,-0.005,0.01)

allSelections = "(jet1isMonoJetId == 1) && "
#allSelections = "(jet1Pt > 30) && "

#####################################
fitFunc.SetLineStyle(2)
linFunc.SetLineStyle(2)

muFreq = 5

plotter.SetIncludeErrorBars(True)

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
#plotter.AddLegendEntry("#gamma+jets Data",3)
#plotter.AddLegendEntry("#gamma+jets",4)
#plotter.AddLegendEntry("W+jets",7)

muonSelection = allSelections + "((lep1PdgId*lep2PdgId == -169) && abs(dilep_m - 91) < 15 && n_looselep == 2 && n_tightlep == 2 && n_loosepho == 0 && n_tau == 0 && lep2Pt > 30)"
elecSelection = allSelections + "((lep1PdgId*lep2PdgId == -121) && abs(dilep_m - 91) < 30 && n_looselep == 2 && n_tightlep == 2 && n_loosepho == 0 && n_tau == 0)"
phoSelection  = allSelections + "(n_loosepho != 0 && n_looselep == 0 && n_tau == 0)"

plotter.AddWeight(muonSelection)
plotter.AddWeight(muonSelection + " * mcWeight")
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

plotter.SetDumpingFits(True)

plotter.MakeFitGraphs(len(xArray)-1,array('d',xArray),100,-1*fitBin,fitBin)

mu_u1   = plotter.FitGraph(0)
sig1_u1 = plotter.FitGraph(1)
sig2_u1 = plotter.FitGraph(2)
sig3_u1 = plotter.FitGraph(3)

sig_u1 = plotter.FitGraph(5)

plotter.ResetExpr()
plotter.AddExpr("u_perpZ")
plotter.AddExpr("u_perpZ")
#plotter.AddExpr("u_perpZ")
#plotter.AddExpr("u_perpZ")
#plotter.AddExpr("u_perpPho")
#plotter.AddExpr("u_perpPho")
#plotter.AddExpr("u_perpW")

plotter.MakeFitGraphs(len(xArray)-1,array('d',xArray),100,-150.0,150.0)

mu_u2   = plotter.FitGraph(0)
sig1_u2 = plotter.FitGraph(1)
sig2_u2 = plotter.FitGraph(2)
sig3_u2 = plotter.FitGraph(3)

sig_u2 = plotter.FitGraph(5)

processes = []
processes.append('Data_Zmm')
processes.append('MC_Zmm')
#processes.append('Data_gjets')
#processes.append('MC_gjets')

colors = [1,2]

fitVectors = [mu_u1,sig1_u1,sig2_u1,sig3_u1,sig_u1,mu_u2,sig1_u2,sig2_u2,sig3_u2,sig_u2]
fitNames   = ['mu_u1','sig1_u1','sig2_u1','sig3_u1','sig_u1','mu_u2','sig1_u2','sig2_u2','sig3_u2','sig_u2']

ROOT.gStyle.SetOptFit(False)

fitFile = ROOT.TFile("fitResults.root","RECREATE")
for i1 in range(len(processes)):
    linFunc.SetLineColor(colors[i1])
    fitFunc.SetLineColor(colors[i1])
    for i0 in range(len(fitVectors)):
        if i0 % muFreq == 0:
            fitResult = fitVectors[i0][i1].Fit(linFunc,"SO")
            fitFile.WriteTObject(linFunc.Clone("fcn_"+fitNames[i0]+"_"+processes[i1]),"fcn_"+fitNames[i0]+"_"+processes[i1])
        else:
            fitResult = fitVectors[i0][i1].Fit(fitFunc,"SO")
            fitFile.WriteTObject(fitFunc.Clone("fcn_"+fitNames[i0]+"_"+processes[i1]),"fcn_"+fitNames[i0]+"_"+processes[i1])
        ##
        fitFile.WriteTObject(fitResult.GetCovarianceMatrix().Clone("cov_"+fitNames[i0]+"_"+processes[i1]),"cov_"+fitNames[i0]+"_"+processes[i1])
##
fitFile.Close()

plotter.MakeCanvas("upara_mu",mu_u1,"","Boson p_{T} [GeV]","#mu_{u_{#parallel}+p_{T}^{#gamma/Z}}",-30,100)
plotter.MakeCanvas("upara_sig1",sig1_u1,"","Boson p_{T} [GeV]","#sigma_{1,u_{#parallel}+p_{T}^{#gamma/Z}}",0,100)
plotter.MakeCanvas("upara_sig2",sig2_u1,"","Boson p_{T} [GeV]","#sigma_{2,u_{#parallel}+p_{T}^{#gamma/Z}}",0,100)
plotter.MakeCanvas("upara_sig3",sig3_u1,"","Boson p_{T} [GeV]","#sigma_{3,u_{#parallel}+p_{T}^{#gamma/Z}}",0,100)
plotter.MakeCanvas("upara_singleSig",sig_u1,"","Boson p_{T} [GeV]","#sigma_{u_{#parallel}+p_{T}^{#gamma/Z}}",0,100)

plotter.MakeCanvas("uperp_mu",mu_u2,"","Boson p_{T} [GeV]","#mu_{u_{#perp}}",-10,10)
plotter.MakeCanvas("uperp_sig1",sig1_u2,"","Boson p_{T} [GeV]","#sigma_{1,u_{#perp}}",0,100)
plotter.MakeCanvas("uperp_sig2",sig2_u2,"","Boson p_{T} [GeV]","#sigma_{2,u_{#perp}}",0,100)
plotter.MakeCanvas("uperp_sig3",sig3_u2,"","Boson p_{T} [GeV]","#sigma_{3,u_{#perp}}",0,100)
plotter.MakeCanvas("uperp_singleSig",sig_u2,"","Boson p_{T} [GeV]","#sigma_{u_{#perp}}",0,100)

del plotter

MuonFile.Close()
SingleElecFile.Close()
SinglePhoFile.Close()
DYFile.Close()
GJetsFile.Close()
WJetsFile.Close()
