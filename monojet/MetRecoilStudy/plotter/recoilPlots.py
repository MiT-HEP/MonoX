#! /usr/bin/python

import ROOT
import tdrStyle
from array import array
from selectionCuts import *

ROOT.gROOT.LoadMacro('PlotBase.cc+')
ROOT.gROOT.LoadMacro('PlotHists.cc+')
ROOT.gROOT.LoadMacro('PlotResolution.cc+')

tdrStyle.setTDRStyle()

ROOT.gROOT.SetBatch(True)

sampledir = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV7/"
goodRuns  = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV7/"

MuonFile       = ROOT.TFile(goodRuns + "monojet_SingleMuon.root")
SingleElecFile = ROOT.TFile(goodRuns + "monojet_SingleElectron.root")
SinglePhoFile  = ROOT.TFile(goodRuns + "monojet_SinglePhoton.root")
DYFile         = ROOT.TFile(sampledir + "monojet_DYJetsToLL_M-50.root")
GJetsFile      = ROOT.TFile(sampledir + "monojet_GJets.root")

MuonTree       = MuonFile.Get("events")
SingleElecTree = SingleElecFile.Get("events")
SinglePhoTree  = SinglePhoFile.Get("events")
DYTree         = DYFile.Get("events")
GJetsTree      = GJetsFile.Get("events")

plotter = ROOT.PlotResolution()

#####################################

plotter.SetDumpingFits(True)

fitBin = 150.0

xArray = [20,40,60,80,100,150,300,1000]

plotter.SetParameterLimits(0,-50,50)
plotter.SetParameterLimits(1,0,40)
plotter.SetParameterLimits(2,20,100)
plotter.SetParameterLimits(3,0.6,1)

#fitFunc = ROOT.TF1("fitter","[0]+[1]*x+[2]*x*x",0,1000)
fitFunc = ROOT.TF1("fitter","[0]+[1]*x+[2]*log(x)",100,1000)
linFunc = ROOT.TF1("fitter","[0]+[1]*x",100,1000)

#fitFunc.SetParLimits(2,-0.02,0.02)
fitFunc.SetParLimits(1,0,2)
fitFunc.SetParLimits(2,-5,5)
#fitFunc.SetParLimits(3,-0.005,0.01)

#allSelections = "(jet1isMonoJetId == 1 && jet1Pt > 100) && "
allSelections = "(jet1isMonoJetId == 1) && "

#####################################
fitFunc.SetLineStyle(2)
linFunc.SetLineStyle(2)

muFreq = 5

plotter.SetIncludeErrorBars(True)

plotter.AddTree(MuonTree)
plotter.AddTree(DYTree)
plotter.AddTree(SingleElecTree)
plotter.AddTree(DYTree)
plotter.AddTree(SinglePhoTree)
plotter.AddTree(GJetsTree)
#plotter.AddTree(WJetsTree)

plotter.AddLegendEntry("Z#mu#mu Data",1)
plotter.AddLegendEntry("Z#mu#mu",2)
plotter.AddLegendEntry("Zee Data",418)
plotter.AddLegendEntry("Zee",4)
plotter.AddLegendEntry("#gamma+jets Data",433)
plotter.AddLegendEntry("#gamma+jets",6)
#plotter.AddLegendEntry("W+jets",7)

plotter.AddWeight(ZmmSelection)
plotter.AddWeight("(" + ZmmSelection + " && genBos_PdgId == 23) * leptonSF * mcWeight * npvWeight")
plotter.AddWeight(ZeeSelection)
plotter.AddWeight("(" + ZeeSelection + " && genBos_PdgId == 23) * leptonSF * mcWeight * npvWeight")
plotter.AddWeight(phoLooseSelection)
plotter.AddWeight("(" + phoLooseSelection + " && genBos_PdgId == 22) * kfactor * XSecWeight * npvWeight")

plotter.AddExprX("dilep_pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("dilep_pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("photonPt")
plotter.AddExprX("genBos_pt")

plotter.AddExpr("(u_para + dilep_pt)")
plotter.AddExpr("(u_para + dilep_pt)")
plotter.AddExpr("(u_para + dilep_pt)")
plotter.AddExpr("(u_para + dilep_pt)")
plotter.AddExpr("(u_para + photonPt)")
plotter.AddExpr("(u_para + photonPt)")

plotter.MakeFitGraphs(len(xArray)-1,array('d',xArray),100,-1*fitBin,fitBin)

mu_u1   = plotter.FitGraph(0)
sig1_u1 = plotter.FitGraph(1)
sig2_u1 = plotter.FitGraph(2)
sig3_u1 = plotter.FitGraph(3)

sig_u1 = plotter.FitGraph(5)

plotter.ResetExpr()
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perp")

plotter.MakeFitGraphs(len(xArray)-1,array('d',xArray),100,-150.0,150.0)

mu_u2   = plotter.FitGraph(0)
sig1_u2 = plotter.FitGraph(1)
sig2_u2 = plotter.FitGraph(2)
sig3_u2 = plotter.FitGraph(3)

sig_u2 = plotter.FitGraph(5)

processes = []
processes.append('Data_Zmm')
processes.append('MC_Zmm')
processes.append('Data_Zee')
processes.append('MC_Zee')
processes.append('Data_gjets')
processes.append('MC_gjets')

colors = [1,2,418,4,433,6]

fitVectors = [mu_u1,sig1_u1,sig2_u1,sig3_u1,sig_u1,mu_u2,sig1_u2,sig2_u2,sig3_u2,sig_u2]
fitNames   = ['mu_u1','sig1_u1','sig2_u1','sig3_u1','sig_u1','mu_u2','sig1_u2','sig2_u2','sig3_u2','sig_u2']

ROOT.gStyle.SetOptFit(False)

fitFile = ROOT.TFile("fitResults.root","RECREATE")
for i1 in range(len(processes)):
    linFunc.SetLineColor(colors[i1])
    fitFunc.SetLineColor(colors[i1])
    for i0 in range(len(fitVectors)):
        if i0 % muFreq == 0:
            fitResult = fitVectors[i0][i1].Fit(linFunc,"SO","",100,500)
            fitFile.WriteTObject(linFunc.Clone("fcn_"+fitNames[i0]+"_"+processes[i1]),"fcn_"+fitNames[i0]+"_"+processes[i1])
        else:
            fitResult = fitVectors[i0][i1].Fit(fitFunc,"SO","",100,500)
            fitFile.WriteTObject(fitFunc.Clone("fcn_"+fitNames[i0]+"_"+processes[i1]),"fcn_"+fitNames[i0]+"_"+processes[i1])
        ##
        fitFile.WriteTObject(fitResult.GetCovarianceMatrix().Clone("cov_"+fitNames[i0]+"_"+processes[i1]),"cov_"+fitNames[i0]+"_"+processes[i1])
##
fitFile.Close()

plotter.SetLegendLimits(0.6,0.15,0.9,0.35)
plotter.MakeCanvas("upara_mu",mu_u1,"","Boson p_{T} [GeV]","#mu_{u_{#parallel}+p_{T}^{#gamma/Z}}",-30,10)
plotter.MakeCanvas("upara_sig1",sig1_u1,"","Boson p_{T} [GeV]","#sigma_{1,u_{#parallel}+p_{T}^{#gamma/Z}}",0,40)
plotter.MakeCanvas("upara_sig2",sig2_u1,"","Boson p_{T} [GeV]","#sigma_{2,u_{#parallel}+p_{T}^{#gamma/Z}}",0,120)
plotter.MakeCanvas("upara_sig3",sig3_u1,"","Boson p_{T} [GeV]","#sigma_{3,u_{#parallel}+p_{T}^{#gamma/Z}}",0,50)
plotter.MakeCanvas("upara_singleSig",sig_u1,"","Boson p_{T} [GeV]","#sigma_{u_{#parallel}+p_{T}^{#gamma/Z}}",0,50)

plotter.SetLegendLimits(0.15,0.7,0.45,0.9)
plotter.MakeCanvas("uperp_mu",mu_u2,"","Boson p_{T} [GeV]","#mu_{u_{#perp}}",-10,10)
plotter.MakeCanvas("uperp_sig1",sig1_u2,"","Boson p_{T} [GeV]","#sigma_{1,u_{#perp}}",0,40)
plotter.MakeCanvas("uperp_sig2",sig2_u2,"","Boson p_{T} [GeV]","#sigma_{2,u_{#perp}}",0,120)
plotter.SetLegendLimits(0.6,0.7,0.9,0.9)
plotter.MakeCanvas("uperp_sig3",sig3_u2,"","Boson p_{T} [GeV]","#sigma_{3,u_{#perp}}",0,50)
plotter.MakeCanvas("uperp_singleSig",sig_u2,"","Boson p_{T} [GeV]","#sigma_{u_{#perp}}",0,50)

del plotter

MuonFile.Close()
SingleElecFile.Close()
SinglePhoFile.Close()
DYFile.Close()
GJetsFile.Close()
