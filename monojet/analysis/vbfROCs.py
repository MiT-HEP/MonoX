#! /usr/bin/python

from vbfDists import *

from CrombieTools.PlotTools.PlotROC import plotter

vbfFile = TFile(inDir + 'monojet_VBFSignal.root')
bkgdFile = TFile(inDir + 'monojet_Bkgd.root')

plotter.AddVar('mjj')
plotter.AddVar('jjDEta')

plotter.AddLegendEntry('Di-jet Mass',1)
plotter.AddLegendEntry('Di-jet #Delta#eta',2)

plotter.SetLumiLabel('2.30')
plotter.SetIsCMSPrelim(True)
plotter.SetLegendLocation(plotter.kUpper,plotter.kLeft)

theCut = cuts.cut('monoJet_inc','signal') + '* (jjDEta > 0 && mjj > 0)'

plotter.SetSignalCut(theCut)
plotter.SetBackgroundCut(theCut)

plotter.SetSignalTree(vbfFile.events)
plotter.SetBackgroundTree(bkgdFile.events)

plotter.MakeCanvas(outDir + 'ROC_VBF')

plotter.SetPlotType(plotter.kSignificance)
plotter.SetLegendLocation(plotter.kUpper,plotter.kRight)

plotter.ResetVars()
plotter.AddVar('mjj')
plotter.MakeCanvas(outDir + 'Sig_VBF_mjj',500,'dijet mass cut [GeV]','Significance')

plotter.ResetVars()
plotter.AddVar('jjDEta')
plotter.MakeCanvas(outDir + 'Sig_VBF_jjDEta',500,'#Delta#eta cut','Significance')
