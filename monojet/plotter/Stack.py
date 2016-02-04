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


outDir = '/afs/cern.ch/user/d/dabercro/www/monoV_160204/'

if not os.path.exists(outDir):
    os.makedirs(outDir)
if not os.path.exists(outDir + 'rootFiles'):
    os.makedirs(outDir + 'rootFiles')
##

stackPlotter.SetRatioMinMax(0.5,1.5)

xArray = [200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]

########## MET Trigger stuff

stackPlotter.SetDefaultWeight(cuts.signalMJ)
stackPlotter.SetMCWeights('mcFactors*METTrigger')
stackPlotter.SetDataWeights(cuts.METTrigger)


stackPlotter.SetDefaultWeight(cuts.ZmmMJ_inc)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_inc_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_inc_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.ZmmMJ)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_' + expr,8,0,8,"Number of Jets", "Events",False)


stackPlotter.SetDefaultWeight(cuts.WmnMJ_inc)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_inc_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_inc_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.WmnMJ)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_' + expr,8,0,8,"Number of Jets", "Events",False)


########## Ending MET Trigger region

stackPlotter.SetDataWeights('')
stackPlotter.SetMCWeights('mcFactors')


stackPlotter.SetDefaultWeight(cuts.ZeeMJ_inc + ' && ' + cuts.ETrigger)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_inc_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_inc_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.ZeeMJ + ' && ' + cuts.ETrigger)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_' + expr,8,0,8,"Number of Jets", "Events",False)


stackPlotter.SetDefaultWeight(cuts.WenMJ_inc + ' && ' + cuts.ETrigger)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMJ_inc_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMJ_inc_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.WenMJ + ' && ' + cuts.ETrigger)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMJ_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMJ_' + expr,8,0,8,"Number of Jets", "Events",False)

########## MET Trigger stuff

xArray = [250,300,350,400,500,600,1000]


stackPlotter.SetDefaultWeight(cuts.signalMV)
stackPlotter.SetMCWeights('mcFactors')
stackPlotter.SetMCWeights('mcFactors*METTrigger')
stackPlotter.SetDataWeights(cuts.METTrigger)


stackPlotter.SetDefaultWeight(cuts.ZmmMV)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMV_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMV_' + expr,8,0,8,"Number of Jets", "Events",False)



stackPlotter.SetDefaultWeight(cuts.WmnMV)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMV_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMV_' + expr,8,0,8,"Number of Jets", "Events",False)


########## Ending MET Trigger region

stackPlotter.SetDataWeights('')
stackPlotter.SetMCWeights('mcFactors')


stackPlotter.SetDefaultWeight(cuts.ZeeMV + ' && ' + cuts.ETrigger)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMV_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMV_' + expr,8,0,8,"Number of Jets", "Events",False)


stackPlotter.SetDefaultWeight(cuts.WenMV + ' && ' + cuts.ETrigger)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMV_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMV_' + expr,8,0,8,"Number of Jets", "Events",False)


## Signal regions

stackPlotter.AddSignalFile(directory + 'monojet_DMV_NNPDF30_Axial_Mphi-2000_Mchi-1_gSM-1p0_gDM-1p0_13TeV-powheg+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM.root',
                           1.0,'Signal V (1 TeV)',2)

stackPlotter.SetMCWeights('mcFactors*METTrigger')
stackPlotter.SetDataWeights(cuts.METTrigger)

stackPlotter.SetDefaultWeight(cuts.signalMV)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMV_' + expr,len(xArray)-1,array('d',xArray),"E_{T}^{miss} [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMV_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMV_' + expr,8,0,8,"Number of Jets", "Events",False)

xArray = [200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]

stackPlotter.SetDefaultWeight(cuts.signalMJ_inc)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMJ_inc_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMJ_inc_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultWeight(cuts.signalMJ)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMJ_' + expr,len(xArray)-1,array('d',xArray),"E_{T}^{miss} [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMJ_' + expr,20,100,500,"Leading jet p_{T} [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMJ_' + expr,8,0,8,"Number of Jets", "Events",False)


