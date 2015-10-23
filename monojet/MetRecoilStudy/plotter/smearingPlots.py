#! /usr/bin/python

import ROOT
import tdrStyle
from array import array

ROOT.gROOT.LoadMacro('PlotBase.cc+')
ROOT.gROOT.LoadMacro('PlotHists.cc+')
ROOT.gROOT.LoadMacro('PlotResolution.cc+')

tdrStyle.setTDRStyle()

ROOT.gROOT.SetBatch(True)

dataDir   = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV4/"
sampledir = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV4/"

DataFile       = ROOT.TFile(dataDir + "monojet_Merged.root")
DYFile         = ROOT.TFile(sampledir + "monojet_DYJetsToLL_M-50.root")
ZToNuNuFile    = ROOT.TFile(sampledir + "monojet_DYJetsToNuNu.root")
GJetsFile      = ROOT.TFile(sampledir + "monojet_GJets.root")
TTFile         = ROOT.TFile(sampledir + "monojet_TTJets.root")
WJetsToLNuFile = ROOT.TFile(sampledir + "monojet_WJetsToLNu.root")
WWFile         = ROOT.TFile(sampledir + "monojet_WW.root")
WZFile         = ROOT.TFile(sampledir + "monojet_WZ.root")
ZZFile         = ROOT.TFile(sampledir + "monojet_ZZ.root")
QCDFile        = ROOT.TFile(sampledir + "monojet_QCD.root")

DataTree       = DataFile.Get("events")
DYTree         = DYFile.Get("events")
ZToNuNuTree    = ZToNuNuFile.Get("events")
GJetsTree      = GJetsFile.Get("events")
TTTree         = TTFile.Get("events")
WJetsToLNuTree = WJetsToLNuFile.Get("events")
WWTree         = WWFile.Get("events")
WZTree         = WZFile.Get("events")
ZZTree         = ZZFile.Get("events")
QCDTree        = QCDFile.Get("events")

plotter = ROOT.PlotResolution()

#####################################

plotter.SetDumpingFits(True)

fitBin = 150.0

xArray = [20,40,60,80,100,150,200,220,250,300,400,600,1000]

plotter.SetParameterLimits(0,-50,50)
plotter.SetParameterLimits(1,5,60)
plotter.SetParameterLimits(2,5,100)
plotter.SetParameterLimits(3,0.6,1)

#fitFunc = ROOT.TF1("fitter","[0]+[1]*x+[2]*x*x",0,1000)
fitFunc = ROOT.TF1("fitter","[0]+[1]*x+[2]*log(x)",0,1000)
linFunc = ROOT.TF1("fitter","[0]+[1]*x",0,1000)

#fitFunc.SetParLimits(2,-0.02,0.02)
fitFunc.SetParLimits(1,0,2)
fitFunc.SetParLimits(2,-5,5)
#fitFunc.SetParLimits(3,-0.005,0.01)

#allSelections = "(jet1isMonoJetId == 1 && jet1Pt > 100) && "
allSelections = "(jet1isMonoJetId == 1) && "

#####################################

plotter.AddTree(DataTree)
plotter.AddTree(DataTree)
plotter.AddTree(DYTree)
plotter.AddTree(ZToNuNuTree)
plotter.AddTree(GJetsTree)
plotter.AddTree(TTTree)
plotter.AddTree(WJetsToLNuTree)
plotter.AddTree(WWTree)
plotter.AddTree(WZTree)
plotter.AddTree(ZZTree)
plotter.AddTree(QCDTree)

fitFunc.SetLineStyle(2)
linFunc.SetLineStyle(2)

muFreq = 5

plotter.SetIncludeErrorBars(True)

ZSelection      = allSelections + "(n_looselep == 2 && n_tightlep > 0 && n_loosepho == 0 && n_tau == 0 && lep2Pt > 20) && abs(dilep_m - 91) < 30 && n_bjetsMedium == 0 && (lep1PdgId*lep2PdgId == -169 || (lep1PdgId*lep2PdgId == -121 && n_tightlep == 2)) "
WSelection      = allSelections + "(n_looselep == 1 && n_tightlep == 1 && n_loosepho == 0 && n_tau == 0) && (n_bjetsMedium == 0)"
phoSelection    = allSelections + "((photonIsTight == 1 || (photonPt < 175 && n_loosepho != 0)) && n_looselep == 0 && n_tau == 0)"
signalSelection = allSelections + "(n_looselep == 0 && n_loosepho == 0 && n_tau == 0)"

colors = [1,2,3,4,5,6,7,8,9,46,28,38,30]
entries = []
entries.append("Merged Data Boson")
entries.append("Merged Data Jet")
entries.append("DY to #ell#ell")
entries.append("Z to #nu#nu")
entries.append("#gamma + jets")
entries.append("tt")
entries.append("W to #ell#nu")
entries.append("WW")
entries.append("WZ")
entries.append("ZZ")
entries.append("QCD")

for index in range(len(entries)):
    plotter.AddLegendEntry(entries[index],colors[index])

plotter.AddWeight("((" + ZSelection + " && boson_pt < 200)||(" + phoSelection + "&& boson_pt > 200)) && correctEvent")
plotter.AddWeight("((" + ZSelection + " && boson_pt < 200)||(" + phoSelection + "&& boson_pt > 200)) && correctEvent")
plotter.AddWeight(ZSelection + " && (genBos_PdgId == 23) * leptonSF * mcWeight * npvWeight * kfactor * XSecWeight")
plotter.AddWeight(signalSelection + " && (genBos_PdgId == 23) * leptonSF * mcWeight * npvWeight * kfactor * XSecWeight")
plotter.AddWeight(phoSelection + " && (genBos_PdgId == 22) * leptonSF * mcWeight * npvWeight * kfactor * XSecWeight")
plotter.AddWeight(WSelection + " && (abs(genBos_PdgId) == 24) * leptonSF * mcWeight * npvWeight * kfactor * XSecWeight")
plotter.AddWeight(WSelection + " && (abs(genBos_PdgId) == 24) * leptonSF * mcWeight * npvWeight * kfactor * XSecWeight")
plotter.AddWeight(WSelection + " && (abs(genBos_PdgId) == 24) * leptonSF * mcWeight * npvWeight * kfactor * XSecWeight")
plotter.AddWeight(ZSelection + " && (genBos_PdgId == 23) * leptonSF * mcWeight * npvWeight * kfactor * XSecWeight")
plotter.AddWeight(ZSelection + " && (genBos_PdgId == 23) * leptonSF * mcWeight * npvWeight * kfactor * XSecWeight")
plotter.AddWeight(signalSelection + " * leptonSF * mcWeight * npvWeight * kfactor * XSecWeight")

plotter.AddExprX("boson_pt")
plotter.AddExprX("jet1Pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("genBos_pt")
plotter.AddExprX("jet1Pt")

plotter.AddExpr("boson_pt + u_para")
plotter.AddExpr("jet1Pt + u_para")
plotter.AddExpr("boson_pt + u_para")
plotter.AddExpr("genBos_pt + u_paraGen")
plotter.AddExpr("boson_pt + u_para")
plotter.AddExpr("genBos_pt + u_paraGen")
plotter.AddExpr("genBos_pt + u_paraGen")
plotter.AddExpr("genBos_pt + u_paraGen")
plotter.AddExpr("boson_pt + u_para")
plotter.AddExpr("jet1Pt + u_paraGen")

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
plotter.AddExpr("u_perpGen")
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perpGen")
plotter.AddExpr("u_perpGen")
plotter.AddExpr("u_perpGen")
plotter.AddExpr("u_perp")
plotter.AddExpr("u_perpGen")

plotter.MakeFitGraphs(len(xArray)-1,array('d',xArray),100,-150.0,150.0)

mu_u2   = plotter.FitGraph(0)
sig1_u2 = plotter.FitGraph(1)
sig2_u2 = plotter.FitGraph(2)
sig3_u2 = plotter.FitGraph(3)

sig_u2 = plotter.FitGraph(5)

processes = []

processes.append('Data_Bos')
processes.append('Data_Jet')
processes.append('MC_Zll')
processes.append('MC_Znn')
processes.append('MC_gjets')
processes.append('MC_tt')
processes.append('MC_Wln')
processes.append('MC_WW')
processes.append('MC_WZ')
processes.append('MC_ZZ')
processes.append('MC_QCD')

fitVectors = [mu_u1,sig1_u1,sig2_u1,sig3_u1,sig_u1,mu_u2,sig1_u2,sig2_u2,sig3_u2,sig_u2]
fitNames   = ['mu_u1','sig1_u1','sig2_u1','sig3_u1','sig_u1','mu_u2','sig1_u2','sig2_u2','sig3_u2','sig_u2']

ROOT.gStyle.SetOptFit(False)

fitFile = ROOT.TFile("fitShit.root","RECREATE")
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

plotter.SetLegendLimits(0.15,0.7,0.45,0.9)
plotter.MakeCanvas("upara_mu",mu_u1,"","Boson p_{T} [GeV]","#mu_{u_{#parallel}+p_{T}^{#gamma/Z}}",-30,50)
plotter.MakeCanvas("upara_sig1",sig1_u1,"","Boson p_{T} [GeV]","#sigma_{1,u_{#parallel}+p_{T}^{#gamma/Z}}",0,50)
plotter.SetLegendLimits(0.6,0.15,0.9,0.35)
plotter.MakeCanvas("upara_sig2",sig2_u1,"","Boson p_{T} [GeV]","#sigma_{2,u_{#parallel}+p_{T}^{#gamma/Z}}",0,120)
plotter.SetLegendLimits(0.15,0.7,0.45,0.9)
plotter.MakeCanvas("upara_sig3",sig3_u1,"","Boson p_{T} [GeV]","#sigma_{3,u_{#parallel}+p_{T}^{#gamma/Z}}",0,60)
plotter.MakeCanvas("upara_singleSig",sig_u1,"","Boson p_{T} [GeV]","#sigma_{u_{#parallel}+p_{T}^{#gamma/Z}}",0,100)

plotter.MakeCanvas("uperp_mu",mu_u2,"","Boson p_{T} [GeV]","#mu_{u_{#perp}}",-10,10)
plotter.MakeCanvas("uperp_sig1",sig1_u2,"","Boson p_{T} [GeV]","#sigma_{1,u_{#perp}}",0,40)
plotter.SetLegendLimits(0.6,0.15,0.9,0.35)
plotter.MakeCanvas("uperp_sig2",sig2_u2,"","Boson p_{T} [GeV]","#sigma_{2,u_{#perp}}",0,60)
plotter.SetLegendLimits(0.15,0.7,0.45,0.9)
plotter.MakeCanvas("uperp_sig3",sig3_u2,"","Boson p_{T} [GeV]","#sigma_{3,u_{#perp}}",0,40)
plotter.MakeCanvas("uperp_singleSig",sig_u2,"","Boson p_{T} [GeV]","#sigma_{u_{#perp}}",0,100)

del plotter

DataFile.Close()
DYFile.Close()
ZToNuNuFile.Close()
GJetsFile.Close()
TTFile.Close()
WJetsToLNuFile.Close()
WWFile.Close()
WZFile.Close()
ZZFile.Close()
QCDFile.Close()
