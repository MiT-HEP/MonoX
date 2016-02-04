#! /usr/bin/python

from ROOT import TFile
from HistPlotter import histPlotter as plotter
from array import array
import cuts

plotter.SetCanvasSize(600,700)

xArray = [200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/CleanMETSkim/'

#outDir = '~/www/monoV_160203/'
outDir = '~/public/dump/'

gammaMCFile = TFile(directory + 'merged/monojet_GJets.root')
print gammaMCFile.GetName()
zeeMCFile   = TFile(directory + 'merged/monojet_DY.root')
print zeeMCFile.GetName()
dataFile    = TFile(directory + 'monojet_Data.root')
print dataFile.GetName()

plotter.SetLumiLabel('2.24')
plotter.SetIsCMSPrelim(True)
plotter.SetLegendLocation(plotter.kUpper,plotter.kRight)
plotter.SetDefaultExpr('met')
plotter.SetEventsPer(1.0)

plotter.AddTreeWeight(zeeMCFile.events,'(' + cuts.ZllMJ + ')*mcFactors*XSecWeight')
plotter.AddTreeWeight(dataFile.events,cuts.ZllMJ)
zPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

plotter.ResetTree()
plotter.ResetWeight()

plotter.AddTreeWeight(gammaMCFile.events,'(' + cuts.gjetMJ + ')*mcFactors*XSecWeight')
plotter.AddTreeWeight(dataFile.events,cuts.gjetMJ)

gammaPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

plotter.AddLegendEntry('MC',2)
plotter.AddLegendEntry('Data',1)

plotter.SetDataIndex(1)
plotter.SetRatioIndex(0)

ratio = plotter.MakeRatio(zPlots,gammaPlots)

plotter.MakeCanvas(outDir + 'Zgamma_ratio_ZllMJ_met',ratio,'|U| [GeV]','Yield Ratio (Zll/#gamma)')

plotter.SetDefaultExpr('photonPt')
gammaPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

plotter.ResetTree()
plotter.ResetWeight()

plotter.SetDefaultExpr('dilep_pt')
plotter.AddTreeWeight(zeeMCFile.events,'(' + cuts.ZllMJ + ')*mcFactors*XSecWeight')
plotter.AddTreeWeight(dataFile.events,cuts.ZllMJ)
zPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

ratio = plotter.MakeRatio(zPlots,gammaPlots)

plotter.MakeCanvas(outDir + 'Zgamma_ratio_ZllMJ_pt',ratio,'Boson p_{T} [GeV]','Yield Ratio (Zll/#gamma)')

plotter.ResetTree()
plotter.ResetWeight()

## Mono V

xArray = [250,300,350,400,500,600,1000]


plotter.AddTreeWeight(zeeMCFile.events,'(' + cuts.ZllMV + ')*mcFactors*XSecWeight')
plotter.AddTreeWeight(dataFile.events,cuts.ZllMV)
zPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

plotter.SetDefaultExpr('met')

plotter.ResetTree()
plotter.ResetWeight()


plotter.AddTreeWeight(gammaMCFile.events,'(' + cuts.gjetMV + ')*mcFactors*XSecWeight')
plotter.AddTreeWeight(dataFile.events,cuts.gjetMV)


gammaPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

ratio = plotter.MakeRatio(zPlots,gammaPlots)

plotter.MakeCanvas(outDir + 'Zgamma_ratio_ZllMV_met',ratio,'|U| [GeV]','Yield Ratio (Zll/#gamma)')



plotter.SetDefaultExpr('photonPt')
gammaPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

plotter.ResetTree()
plotter.ResetWeight()

plotter.SetDefaultExpr('dilep_pt')
plotter.AddTreeWeight(zeeMCFile.events,'(' + cuts.ZllMV + ')*mcFactors*XSecWeight')
plotter.AddTreeWeight(dataFile.events,cuts.ZllMV)
zPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

ratio = plotter.MakeRatio(zPlots,gammaPlots)

plotter.MakeCanvas(outDir + 'Zgamma_ratio_ZllMV_pt',ratio,'Boson p_{T} [GeV]','Yield Ratio (Zll/#gamma)')
