#! /usr/bin/python

from ROOT import TFile
from CrombieTools.PlotTools.PlotROC import plotter
import cuts

inDir = '/afs/cern.ch/work/d/dabercro/public/Winter15/SkimOut_VBFStudy/files/'
outDir = '/afs/cern.ch/user/d/dabercro/www/VBFStudy/'

vbfFile = TFile(inDir + 'monojet_VBFSignal.root')
bkgdFile = TFile(inDir + 'monojet_Bkgd.root')

#plotter.AddVar('mjj')
plotter.AddVar('jjDEta')

#plotter.AddLegendEntry('Di-jet Mass',1)
#plotter.AddLegendEntry('Di-jet #Delta#eta',2)

#plotter.SetLumiLabel('2.30')
#plotter.SetIsCMSPrelim(True)
#plotter.SetLegendLocation(plotter.kLower,plotter.kLeft)

theCut = cuts.cut('monoJet_inc','signal')

plotter.SetSignalCut(theCut)
plotter.SetBackgroundCut(theCut)

plotter.SetSignalTree(vbfFile.events)
plotter.SetBackgroundTree(bkgdFile.events)

plotter.MakeCanvas(outDir + 'ROC_VBF')
