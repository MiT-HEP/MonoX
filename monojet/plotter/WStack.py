#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array
import cuts
import os

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/Correct_w_MJ/'
#directory = '/Users/dabercro/GradSchool/Winter15/CleanMETSkim_160201/'

stackPlotter.SetIsCMSPrelim(True)
stackPlotter.SetTreeName('events')
stackPlotter.SetAllHist('htotal')
stackPlotter.SetLuminosity(2240.0)
stackPlotter.AddDataFile(directory + 'monojet_Data.root')
#stackPlotter.ReadMCConfig('MCFiles.txt',directory)
#stackPlotter.ReadMCConfig('MCSig.txt',directory)
stackPlotter.ReadMCConfig('MCColors.txt',directory)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetEventsPer(1.0)
stackPlotter.SetMinLegendFrac(0.03)
stackPlotter.SetIgnoreInLinear(0.005)
stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.SetOthersColor(922)
stackPlotter.SetRatioTitle("Data/Pred.")
stackPlotter.SetRatioDivisions(504,False)
stackPlotter.SetRatioGrid(1)
stackPlotter.SetCanvasSize(600,700)
stackPlotter.SetFontSize(0.03)
stackPlotter.SetAxisTitleOffset(1.2)
stackPlotter.SetDumpFileName('dump.root')

outDir = '/afs/cern.ch/user/d/dabercro/www/monoV_160209_w/'

if not os.path.exists(outDir):
    os.makedirs(outDir)
if not os.path.exists(outDir + 'rootFiles'):
    os.makedirs(outDir + 'rootFiles')
##

stackPlotter.SetRatioMinMax(0.5,1.5)

xArray = [200,250,300,350,400,500,600,1000]

########## MET Trigger stuff

stackPlotter.SetMCWeights('mcFactors*METTrigger')
stackPlotter.SetDataWeights(cuts.METTrigger)


stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDumpFileName('dump/WmnMJ.root')
stackPlotter.SetDefaultWeight(cuts.WmnMJ)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)


########## Ending MET Trigger region

stackPlotter.SetDataWeights('')
stackPlotter.SetMCWeights('mcFactors')

stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.WenMJ + ' && ' + cuts.ETrigger)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.SetDumpFileName('dump/WenMJ.root')
stackPlotter.MakeCanvas(outDir + 'WenMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

########## MET Trigger stuff

xArray = [250,300,350,400,500,600,1000]


stackPlotter.SetDefaultWeight(cuts.signalMV)
stackPlotter.SetMCWeights('mcFactors')
stackPlotter.SetMCWeights('mcFactors*METTrigger')
stackPlotter.SetDataWeights(cuts.METTrigger)

stackPlotter.SetDefaultWeight(cuts.WmnMV)
expr = 'met'
stackPlotter.SetDumpFileName('dump/WmnMV.root')
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)

########## Ending MET Trigger region

stackPlotter.SetDataWeights('')
stackPlotter.SetMCWeights('mcFactors')

stackPlotter.SetDefaultWeight(cuts.WenMV + ' && ' + cuts.ETrigger)
expr = 'met'
stackPlotter.SetDumpFileName('dump/WenMV.root')
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
