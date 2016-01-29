#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array
import cuts
import os

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/FatMETSkim/'

stackPlotter.SetIsCMSPrelim(True)
stackPlotter.SetTreeName('events')
stackPlotter.SetAllHist('htotal')
stackPlotter.SetLuminosity(2109.0)
stackPlotter.AddDataFile(directory + 'monojet_Data.root')
stackPlotter.ReadMCConfig('MCFiles.txt',directory)
#stackPlotter.ReadMCConfig('MCSig.txt',directory)
stackPlotter.SetMCWeights('mcFactors')
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultExpr('met')
stackPlotter.SetEventsPer(1.0)
stackPlotter.SetMinLegendFrac(0.03)
stackPlotter.SetRatioMinMax(0.5,1.5)

xArray = [200,250,300,350,400,500,600,1000]
outDir = '/afs/cern.ch/user/d/dabercro/www/monoV_160129_sync/'

if not os.path.exists(outDir):
    os.makedirs(outDir)
##

stackPlotter.SetDefaultWeight(cuts.gjetMV)
stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.MakeCanvas(outDir + 'met_gjetMV',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.ZmmMV)
stackPlotter.SetRatioMinMax(0.0,2.0)
stackPlotter.MakeCanvas(outDir + 'met_ZmmMV',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.ZeeMV)
stackPlotter.SetRatioMinMax(0.0,2.0)
stackPlotter.MakeCanvas(outDir + 'met_ZeeMV',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.WmnMV)
stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.MakeCanvas(outDir + 'met_WmnMV',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.WenMV)
stackPlotter.SetRatioMinMax(0.0,2.0)
stackPlotter.MakeCanvas(outDir + 'met_WenMV',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.signalMV)
stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.MakeCanvas(outDir + 'met_signalMV',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",False)
