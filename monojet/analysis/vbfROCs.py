#! /usr/bin/python

from vbfDists import *

from CrombieTools.PlotTools.PlotROC import plotter

vbfFile = TFile(inDir + 'monojet_VBFSignal.root')
bkgdFile = TFile(inDir + 'monojet_Bkgd.root')

plotter.AddLegendEntry('Di-jet Mass',1)
plotter.AddLegendEntry('Di-jet #Delta#eta',2)

plotter.SetLumiLabel('2.30')
plotter.SetIsCMSPrelim(True)
plotter.SetLegendLocation(plotter.kUpper,plotter.kLeft)

theCut = cuts.cut('monoJet_inc','signal') + '* (jjDEta > 0 && mjj > 0 && mjj < 2000)'

plotter.SetSignalCut(theCut)
plotter.SetBackgroundCut(theCut)

plotter.SetSignalTree(vbfFile.events)
plotter.SetBackgroundTree(bkgdFile.events)

plotter.AddVar('mjj')
plotter.AddVar('jjDEta')
plotter.MakeCanvas(outDir + 'ROC_VBF')

plotter.SetPlotType(plotter.kSignificance)
plotter.SetLegendLocation(plotter.kUpper,plotter.kRight)

plotter.ResetVars()
plotter.AddVar('mjj')
plotter.MakeCanvas(outDir + 'Sig_VBF_mjj',500,'dijet mass cut [GeV]','Significance')

plotter.ResetVars()
plotter.ResetLegend()
plotter.AddLegendEntry('Di-jet #Delta#eta',2)
plotter.AddVar('jjDEta')
plotter.MakeCanvas(outDir + 'Sig_VBF_jjDEta',500,'#Delta#eta cut','Significance')

theCut = cuts.cut('monoJet_inc','signal') + '* (gen_jjDEta > 0 && gen_mjj > 0 && gen_mjj < 2000)'

plotter.SetSignalCut(theCut)
plotter.SetBackgroundCut(theCut)

plotter.SetPlotType(plotter.kROC)
plotter.SetLegendLocation(plotter.kUpper,plotter.kLeft)

plotter.ResetLegend()
plotter.AddLegendEntry('Di-jet Mass',1)
plotter.AddLegendEntry('Di-jet #Delta#eta',2)

plotter.ResetVars()
plotter.AddVar('gen_mjj')
plotter.AddVar('gen_jjDEta')
plotter.MakeCanvas(outDir + 'ROC_VBF_gen')

plotter.SetPlotType(plotter.kSignificance)
plotter.SetLegendLocation(plotter.kUpper,plotter.kRight)

plotter.ResetVars()
plotter.ResetLegend()
plotter.AddLegendEntry('Di-jet Mass [GeV]',1)
plotter.AddVar('gen_mjj')
plotter.MakeCanvas(outDir + 'Sig_VBF_gen_mjj',500,'dijet mass cut [GeV]','Significance')

plotter.ResetVars()
plotter.ResetLegend()
plotter.AddLegendEntry('Di-jet #Delta#eta',2)
plotter.AddVar('gen_jjDEta')
plotter.MakeCanvas(outDir + 'Sig_VBF_gen_jjDEta',500,'#Delta#eta cut','Significance')
