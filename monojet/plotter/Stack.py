#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array
import cuts
import os

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/CleanMETSkim/'
#directory = '/Users/dabercro/GradSchool/Winter15/FatMETSkim_160129/'

stackPlotter.SetIsCMSPrelim(True)
stackPlotter.SetTreeName('events')
stackPlotter.SetAllHist('htotal')
stackPlotter.SetLuminosity(2240.0)
stackPlotter.AddDataFile(directory + 'monojet_Data.root')
#stackPlotter.ReadMCConfig('MCFiles.txt',directory)
#stackPlotter.ReadMCConfig('MCSig.txt',directory)
stackPlotter.ReadMCConfig('MCColors.txt',directory)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultExpr('met')
stackPlotter.SetEventsPer(1.0)
stackPlotter.SetMinLegendFrac(0.03)
stackPlotter.SetRatioMinMax(0.5,1.5)

xArray = [250,300,350,400,500,600,1000]
outDir = '/afs/cern.ch/user/d/dabercro/www/monoV_160201/'

if not os.path.exists(outDir):
    os.makedirs(outDir)
if not os.path.exists(outDir + 'rootFiles'):
    os.makedirs(outDir + 'rootFiles')
##

stackPlotter.SetDefaultWeight(cuts.signalMJ)
stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.SetMCWeights('mcFactors*METTrigger')
stackPlotter.SetDataWeights(cuts.METTrigger)
stackPlotter.SetDumpFileName(outDir + 'rootFiles/signal_region.root')
stackPlotter.MakeCanvas(outDir + 'signalMJ_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.ZmmMJ)
stackPlotter.SetRatioMinMax(0.0,2.0)
stackPlotter.SetDumpFileName(outDir + 'rootFiles/Zmm_region.root')
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.WmnMJ)
stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.SetDumpFileName(outDir + 'rootFiles/Wmn_region.root')
stackPlotter.MakeCanvas(outDir + 'WmnMJ_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDataWeights('')
stackPlotter.SetMCWeights('mcFactors')

stackPlotter.SetDefaultWeight(cuts.gjetMJ + ' && ' + cuts.GTrigger)
stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.SetDumpFileName(outDir + 'rootFiles/gamma_region.root')
stackPlotter.MakeCanvas(outDir + 'gjetMJ_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.ZeeMJ + ' && ' + cuts.ETrigger)
stackPlotter.SetRatioMinMax(0.0,2.0)
stackPlotter.SetDumpFileName(outDir + 'rootFiles/Zee_region.root')
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.WenMJ + ' && ' + cuts.ETrigger)
stackPlotter.SetRatioMinMax(0.0,2.0)
stackPlotter.SetDumpFileName(outDir + 'rootFiles/Wen_region.root')
stackPlotter.MakeCanvas(outDir + 'WenMJ_met',len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
