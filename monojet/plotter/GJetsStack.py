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
stackPlotter.ReadMCConfig('MCGJets.txt',directory)
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

xArray = [200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]

stackPlotter.SetDataWeights('')
stackPlotter.SetMCWeights('mcFactors')

stackPlotter.SetDefaultWeight(cuts.gjetMJ_inc + ' && ' + cuts.GTrigger)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMJ_inc_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
stackPlotter.MakeCanvas(outDir + 'gjetMJ_inc_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)

stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.gjetMJ + ' && ' + cuts.GTrigger)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMJ_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMJ_' + expr,8,0,8,"Number of Jets", "Events",False)
stackPlotter.SetDataWeights('')
stackPlotter.SetMCWeights('mcFactors')

xArray = [250,300,350,400,500,600,1000]

stackPlotter.SetDefaultWeight(cuts.gjetMV + ' && ' + cuts.GTrigger)
expr = 'met'
stackPlotter.SetDumpFileName(outDir + 'rootFiles/gjetsMV_met_dump.root')
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDumpFileName('')
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMV_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMV_' + expr,8,0,8,"Number of Jets", "Events",False)
