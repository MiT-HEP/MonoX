#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array
import cuts
import os

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/CleanMETSkim/'
#directory = '/Users/dabercro/GradSchool/Winter15/CleanMETSkim_160201/'

stackPlotter.SetIsCMSPrelim(True)
stackPlotter.SetTreeName('events')
stackPlotter.SetAllHist('htotal')
stackPlotter.SetLuminosity(2240.0)
stackPlotter.AddDataFile(directory + 'monojet_Data.root')
stackPlotter.ReadMCConfig('MCTop.txt',directory)
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

outDir = '/afs/cern.ch/user/d/dabercro/www/monoV_160204_top/'

if not os.path.exists(outDir):
    os.makedirs(outDir)
##

stackPlotter.SetRatioMinMax(0.5,1.5)


xArray = [250,300,350,400,500,600,1000]


stackPlotter.SetForceTop('Resonant top')

stackPlotter.SetDefaultWeight(cuts.top)
stackPlotter.SetMCWeights('mcFactors')
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'top_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'top_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetForceTop('')

stackPlotter.SetMCWeights('mcFactors*METTrigger')
stackPlotter.SetDataWeights(cuts.METTrigger)


stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.topMu)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topMu_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topMu_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topMu_' + expr,8,0,8,"Number of Jets", "Events",False)


stackPlotter.SetMCWeights('mcFactors')
stackPlotter.SetDataWeights('')


stackPlotter.SetDefaultWeight(cuts.topEle + ' && ' + cuts.ETrigger)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topEle_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topEle_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topEle_' + expr,8,0,8,"Number of Jets", "Events",False)


