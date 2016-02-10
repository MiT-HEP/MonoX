#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array
import cuts
import os

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/Correct_both_MJ/'
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
stackPlotter.SetOthersColor(922)
stackPlotter.SetRatioTitle("Data/Pred.")
stackPlotter.SetRatioDivisions(504,False)
stackPlotter.SetRatioGrid(1)
stackPlotter.SetCanvasSize(600,700)
stackPlotter.SetFontSize(0.03)
stackPlotter.SetAxisTitleOffset(1.2)

outDir = '/afs/cern.ch/user/d/dabercro/www/monoV_160209_both/'

if not os.path.exists(outDir):
    os.makedirs(outDir)
##


xArray = [250,300,350,400,500,600,1000]


stackPlotter.SetRatioMinMax(0.5,1.5)
stackPlotter.SetForceTop('Resonant top')


stackPlotter.SetMCWeights('mcFactors')
expr = 'fatjet1DRGenW'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.SetDefaultWeight(cuts.top)
stackPlotter.SetEventsPer(0.1)
stackPlotter.MakeCanvas(outDir + 'top_' + expr,20,0,4,"#Delta R(W,j)", "Events Per 0.1",False)
stackPlotter.SetEventsPer(1.0)

exit()

expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.SetDefaultWeight(cuts.top + ' && fatjet1tau21 < 0.6')
stackPlotter.MakeCanvas(outDir + 'N1top_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
stackPlotter.SetDefaultExpr(expr)
stackPlotter.SetDefaultWeight(cuts.top + ' && fatjet1PrunedM < 105 && fatjet1PrunedM > 62')
stackPlotter.MakeCanvas(outDir + 'N1top_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)

expr = 'fatjet1PrunedM'
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultExpr(expr)
stackPlotter.SetDefaultWeight(cuts.top)
stackPlotter.MakeCanvas(outDir + 'top_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'top_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)

stackPlotter.SetRatioMinMax(0.0,2.0)
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
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topMu_' + expr,8,0,8,"Number of Jets", "Events",False)


stackPlotter.SetMCWeights('mcFactors')
stackPlotter.SetDataWeights('')


stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.topEle + ' && ' + cuts.ETrigger)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topEle_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topEle_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topEle_' + expr,8,0,8,"Number of Jets", "Events",False)


stackPlotter.SetRatioMinMax(0.0,2.0)
stackPlotter.SetForceTop('')


stackPlotter.SetMCWeights('mcFactors*METTrigger')
stackPlotter.SetDataWeights(cuts.METTrigger)


stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.topMJMu)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topMJMu_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topMJMu_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topMJMu_' + expr,8,0,8,"Number of Jets", "Events",False)


stackPlotter.SetMCWeights('mcFactors')
stackPlotter.SetDataWeights('')


stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.topMJEle + ' && ' + cuts.ETrigger)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topMJEle_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topMJEle_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'topMJEle_' + expr,8,0,8,"Number of Jets", "Events",False)
