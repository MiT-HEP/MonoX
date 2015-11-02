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

#dataDir   = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV4/"
dataDir   = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV4/"
sampledir = "/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV4/"

plotter = ROOT.PlotResolution()

#####################################

plotter.SetDumpingFits(True)

fitBin = 300.0

xArray = [20,40,60,80,100,150,200,220,250,300,400,600,1000]

plotter.SetParameterLimits(1,5,60)
plotter.SetParameterLimits(2,5,100)
plotter.SetParameterLimits(3,0.6,1)

#fitFunc = ROOT.TF1("fitter","[0]+[1]*x+[2]*x*x",0,1000)
fitFunc = ROOT.TF1("fitter","[0]+[1]*x",0,xArray[-1])
linFunc = ROOT.TF1("fitter","[0]+[1]*x",0,xArray[-1])

#fitFunc.SetParLimits(2,-0.02,0.02)
fitFunc.SetParLimits(1,0,2)
fitFunc.SetParLimits(2,-5,5)
#fitFunc.SetParLimits(3,-0.005,0.01)

#allSelections = "(jet1isMonoJetId == 1 && jet1Pt > 100) && "
allSelections = "(jet1isMonoJetId == 1) && "

skipThese = [1,6,9,10,11,12]

#####################################

entries = []
entries.append("Merged Data Boson")  #  0
entries.append("Merged Data Jet")    #  1
entries.append("DY to #mu#mu")       #  2
entries.append("DY to ee")           #  3
entries.append("Z to #nu#nu")        #  4
entries.append("#gamma + jets")      #  5
entries.append("tt")                 #  6
entries.append("W to #mu#nu")        #  7
entries.append("W to e#nu")          #  8
entries.append("WW")                 #  9
entries.append("WZ")                 # 10
entries.append("ZZ")                 # 11
entries.append("QCD")                # 12

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

trees = []
trees.append(DataTree)
trees.append(DataTree)
trees.append(DYTree)
trees.append(DYTree)
trees.append(ZToNuNuTree)
trees.append(GJetsTree)
trees.append(TTTree)
trees.append(WJetsToLNuTree)
trees.append(WJetsToLNuTree)
trees.append(WWTree)
trees.append(WZTree)
trees.append(ZZTree)
trees.append(QCDTree)

fitFunc.SetLineStyle(2)
linFunc.SetLineStyle(2)

muFreq = 5

plotter.SetIncludeErrorBars(True)

colors = [1,2,3,4,5,6,7,8,9,46,28,38,30]

MCfactors = " * leptonSF * mcWeight * npvWeight * kfactor * XSecWeight"

weights = []
weights.append("((" + ZmmSelection + " && boson_pt < 210)||(" + phoSelection + "&& boson_pt > 210))")
weights.append("((" + ZmmSelection + " && boson_pt < 210)||(" + phoSelection + "&& boson_pt > 210))")
weights.append("(" + ZmmSelection + " && genBos_PdgId == 23)" + MCfactors)
weights.append("(" + ZeeSelection + " && genBos_PdgId == 23)" + MCfactors)
weights.append("(" + signalSelection + " && genBos_PdgId == 23)" + MCfactors)
weights.append("(" + phoSelection + " && genBos_PdgId == 22)" + MCfactors)
weights.append("(" + singLeptonSelection + " && abs(genBos_PdgId) == 24)" + MCfactors)
weights.append("(" + WmnSelection + " && abs(genBos_PdgId) == 24)" + MCfactors)
weights.append("(" + WenSelection + " && abs(genBos_PdgId) == 24)" + MCfactors)
weights.append("(" + singLeptonSelection + " && abs(genBos_PdgId) == 24)" + MCfactors)
weights.append("(" + singLeptonSelection + " && abs(genBos_PdgId) == 24)" + MCfactors)
weights.append("(" + diLeptonSelection + " && genBos_PdgId == 23)" + MCfactors)
weights.append(signalSelection + MCfactors)

xExprs = []
xExprs.append("boson_pt")
xExprs.append("jet1Pt")
xExprs.append("genBos_pt")
xExprs.append("genBos_pt")
xExprs.append("genBos_pt")
xExprs.append("genBos_pt")
xExprs.append("genBos_pt")
xExprs.append("genBos_pt")
xExprs.append("genBos_pt")
xExprs.append("genBos_pt")
xExprs.append("genBos_pt")
xExprs.append("genBos_pt")
xExprs.append("jet1Pt")

Exprs = []
Exprs.append("boson_pt + u_para")
Exprs.append("jet1Pt + u_para")
Exprs.append("genBos_pt + u_para")
Exprs.append("genBos_pt + u_para")
Exprs.append("genBos_pt + u_paraGen")
Exprs.append("genBos_pt + u_para")
Exprs.append("genBos_pt + u_paraGen")
Exprs.append("genBos_pt + u_paraGen")
Exprs.append("genBos_pt + u_paraGen")
Exprs.append("genBos_pt + u_para")
Exprs.append("genBos_pt + u_para")
Exprs.append("genBos_pt + u_para")
Exprs.append("jet1Pt + u_paraGen")

numSkipped = 0

for index in range(len(entries)):
    if index in skipThese:
        numSkipped = numSkipped + 1
        continue
    plotter.AddLegendEntry(entries[index],colors[index - numSkipped])
    plotter.AddTree(trees[index])
    plotter.AddWeight(weights[index])
    plotter.AddExprX(xExprs[index])
    plotter.AddExpr(Exprs[index])

plotter.MakeFitGraphs(len(xArray)-1,array('d',xArray),100,-1*fitBin,fitBin)

mu_u1   = plotter.FitGraph(0)
sig1_u1 = plotter.FitGraph(1)
sig2_u1 = plotter.FitGraph(2)
sig3_u1 = plotter.FitGraph(3)

sig_u1 = plotter.FitGraph(5)

Exprs = []
Exprs.append("u_perp")
Exprs.append("u_perp")
Exprs.append("u_perp")
Exprs.append("u_perp")
Exprs.append("u_perpGen")
Exprs.append("u_perp")
Exprs.append("u_perpGen")
Exprs.append("u_perpGen")
Exprs.append("u_perpGen")
Exprs.append("u_perp")
Exprs.append("u_perp")
Exprs.append("u_perp")
Exprs.append("u_perpGen")

plotter.ResetExpr()

for index in range(len(entries)):
    if index in skipThese:
        continue
    plotter.AddExpr(Exprs[index])

plotter.MakeFitGraphs(len(xArray)-1,array('d',xArray),100,-150.0,150.0)

mu_u2   = plotter.FitGraph(0)
sig1_u2 = plotter.FitGraph(1)
sig2_u2 = plotter.FitGraph(2)
sig3_u2 = plotter.FitGraph(3)

sig_u2 = plotter.FitGraph(5)

processes1 = []
processes1.append('Data_Zmm')
processes1.append('Data_Jet')
processes1.append('MC_Zmm')
processes1.append('MC_Zee')
processes1.append('MC_Znn')
processes1.append('MC_gjets')
processes1.append('MC_tt')
processes1.append('MC_Wmn')
processes1.append('MC_Wen')
processes1.append('MC_WW')
processes1.append('MC_WZ')
processes1.append('MC_ZZ')
processes1.append('MC_QCD')

processes = []
for i1 in range(len(processes1)):
    if i1 in skipThese:
        continue
    processes.append(processes1[i1])

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
plotter.MakeCanvas("upara_mu",mu_u1,"","Boson p_{T} [GeV]","#mu_{u_{#parallel}+p_{T}^{#gamma/Z}}",-20,100)
plotter.MakeCanvas("upara_sig1",sig1_u1,"","Boson p_{T} [GeV]","#sigma_{1,u_{#parallel}+p_{T}^{#gamma/Z}}",0,100)
plotter.SetLegendLimits(0.6,0.15,0.9,0.35)
plotter.MakeCanvas("upara_sig2",sig2_u1,"","Boson p_{T} [GeV]","#sigma_{2,u_{#parallel}+p_{T}^{#gamma/Z}}",0,120)
plotter.SetLegendLimits(0.15,0.7,0.45,0.9)
plotter.MakeCanvas("upara_sig3",sig3_u1,"","Boson p_{T} [GeV]","#sigma_{3,u_{#parallel}+p_{T}^{#gamma/Z}}",0,100)
plotter.MakeCanvas("upara_singleSig",sig_u1,"","Boson p_{T} [GeV]","#sigma_{u_{#parallel}+p_{T}^{#gamma/Z}}",0,100)

plotter.MakeCanvas("uperp_mu",mu_u2,"","Boson p_{T} [GeV]","#mu_{u_{#perp}}",-15,15)
plotter.MakeCanvas("uperp_sig1",sig1_u2,"","Boson p_{T} [GeV]","#sigma_{1,u_{#perp}}",0,40)
plotter.SetLegendLimits(0.6,0.15,0.9,0.35)
plotter.MakeCanvas("uperp_sig2",sig2_u2,"","Boson p_{T} [GeV]","#sigma_{2,u_{#perp}}",0,100)
plotter.SetLegendLimits(0.15,0.7,0.45,0.9)
plotter.MakeCanvas("uperp_sig3",sig3_u2,"","Boson p_{T} [GeV]","#sigma_{3,u_{#perp}}",0,40)
plotter.MakeCanvas("uperp_singleSig",sig_u2,"","Boson p_{T} [GeV]","#sigma_{u_{#perp}}",0,50)

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
