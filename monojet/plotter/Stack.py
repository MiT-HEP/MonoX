#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array
import cuts
import os

#directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/FatMETSkim/'
directory = '/Users/dabercro/GradSchool/Winter15/FatMETSkim_160129/'

stackPlotter.SetIsCMSPrelim(True)
stackPlotter.SetTreeName('events')
stackPlotter.SetAllHist('htotal')
stackPlotter.SetLuminosity(2240.0)
stackPlotter.AddDataFile(directory + 'monojet_Data.root')
#stackPlotter.ReadMCConfig('MCFiles.txt',directory)
stackPlotter.ReadMCConfig('MCSig.txt',directory)
stackPlotter.SetMCWeights('mcFactors')
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultExpr('met')
stackPlotter.SetEventsPer(1.0)
stackPlotter.SetMinLegendFrac(0.03)
stackPlotter.SetRatioMinMax(0.5,1.5)

xArray = [250,300,350,400,500,600,1000]
outDir = 'syncPlots/'

if not os.path.exists(outDir):
    os.makedirs(outDir)
##

stackPlotter.SetDefaultWeight(cuts.gjetMV)
stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.SetDumpFileName('syncPlots/gamma_region.root')
stackPlotter.MakeCanvas(outDir + 'gjetMV_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.ZmmMV)
stackPlotter.SetRatioMinMax(0.0,2.0)
stackPlotter.SetDumpFileName('syncPlots/Zmm_region.root')
stackPlotter.MakeCanvas(outDir + 'ZmmMV_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.ZeeMV)
stackPlotter.SetRatioMinMax(0.0,2.0)
stackPlotter.SetDumpFileName('syncPlots/Zee_region.root')
stackPlotter.MakeCanvas(outDir + 'ZeeMV_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.WmnMV)
stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.SetDumpFileName('syncPlots/Wmn_region.root')
stackPlotter.MakeCanvas(outDir + 'WmnMV_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.WenMV)
stackPlotter.SetRatioMinMax(0.0,2.0)
stackPlotter.SetDumpFileName('syncPlots/Wen_region.root')
stackPlotter.MakeCanvas(outDir + 'WenMV_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.signalMV)
stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.SetDumpFileName('syncPlots/signal_region.root')
stackPlotter.MakeCanvas(outDir + 'signal_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
