#! /usr/bin/python

from ROOT import TFile
from CrombieTools.PlotTools.PlotHists import plotter
from CrombieTools.LoadConfig import cuts

from array import array

signalFile = TFile('/afs/cern.ch/work/d/dabercro/public/Winter15/SkimOut_160212/monojet_VectorMonoZ_Mphi-200_Mchi-10_gSM-1p0_gDM-1p0_13TeV.root')

plotter.SetDefaultTree(signalFile.events)
plotter.SetDefaultExpr('met')

plotter.AddWeight(cuts.cut('monoJet','signal') + '* mcFactors')
plotter.AddWeight(cuts.cut('monoJet','signal') + '* (lepton_SF * mcWeight)')

plotter.AddLegendEntry('With Pileup Reweighting',1)
plotter.AddLegendEntry('Without Pileup Reweighting',1)

plotter.SetNormalizedHists(True)

MJArray = [200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]

plotter.MakeCanvas('test',len(MJArray) - 1,array('d',MJArray),'MET [GeV]','AU',False)
