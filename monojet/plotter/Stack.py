#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array
import cuts
import os

#directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/CleanMETSkim/'
directory = '/Users/dabercro/GradSchool/Winter15/CleanMETSkim_160201/'

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
stackPlotter.SetRatioMinMax(0.5,1.5)

xArray = [250,300,350,400,500,600,1000]
outDir = 'pwots'

if not os.path.exists(outDir):
    os.makedirs(outDir)
if not os.path.exists(outDir + 'rootFiles'):
    os.makedirs(outDir + 'rootFiles')
##

stackPlotter.SetRatioMinMax(0.5,1.5)

########## MET Trigger stuff

stackPlotter.SetDefaultWeight(cuts.signalMJ)
stackPlotter.SetMCWeights('mcFactors*METTrigger')
stackPlotter.SetDataWeights(cuts.METTrigger)
#stackPlotter.SetDumpFileName(outDir + 'rootFiles/signal_region.root')
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMJ_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMJ_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMJ_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMJ_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetDefaultWeight(cuts.ZmmMJ)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMJ_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetDefaultWeight(cuts.WmnMJ)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMJ_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


########## Ending MET Trigger region

stackPlotter.SetDataWeights('')
stackPlotter.SetMCWeights('mcFactors')


stackPlotter.SetDefaultWeight(cuts.gjetMJ + ' && ' + cuts.GTrigger)
#stackPlotter.SetDumpFileName(outDir + 'rootFiles/gamma_region.root')
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMJ_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMJ_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMJ_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMJ_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetDefaultWeight(cuts.ZeeMJ + ' && ' + cuts.ETrigger)
#stackPlotter.SetDumpFileName(outDir + 'rootFiles/Zee_region.root')
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMJ_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetDefaultWeight(cuts.WenMJ + ' && ' + cuts.ETrigger)
#stackPlotter.SetDumpFileName(outDir + 'rootFiles/Wen_region.root')
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMJ_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMJ_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMJ_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMJ_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMJ_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


########## MET Trigger stuff

stackPlotter.SetDefaultWeight(cuts.signalMV)
stackPlotter.SetMCWeights('mcFactors*METTrigger')
stackPlotter.SetDataWeights(cuts.METTrigger)
#stackPlotter.SetDumpFileName(outDir + 'rootFiles/signal_region.root')
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMV_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMV_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMV_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'signalMV_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetDefaultWeight(cuts.ZmmMV)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMV_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMV_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMV_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZmmMV_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetDefaultWeight(cuts.WmnMV)
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMV_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMV_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMV_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WmnMV_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


########## Ending MET Trigger region

stackPlotter.SetDataWeights('')
stackPlotter.SetMCWeights('mcFactors')


stackPlotter.SetDefaultWeight(cuts.gjetMV + ' && ' + cuts.GTrigger)
#stackPlotter.SetDumpFileName(outDir + 'rootFiles/gamma_region.root')
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMV_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMV_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMV_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'gjetMV_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetDefaultWeight(cuts.ZeeMV + ' && ' + cuts.ETrigger)
#stackPlotter.SetDumpFileName(outDir + 'rootFiles/Zee_region.root')
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMV_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMV_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMV_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'ZeeMV_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)


stackPlotter.SetDefaultWeight(cuts.WenMV + ' && ' + cuts.ETrigger)
#stackPlotter.SetDumpFileName(outDir + 'rootFiles/Wen_region.root')
expr = 'met'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMV_' + expr,len(xArray)-1,array('d',xArray),"|U| [GeV]", "Events Per GeV",True)
expr = 'jet1Pt'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMV_' + expr,20,0,200,"Leading jet Mass [GeV]", "Events Per GeV",False)
expr = 'n_cleanedjets'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMV_' + expr,8,0,8,"Number of Jets", "Events",False)
expr = 'fatjet1PrunedM'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMV_' + expr,20,0,200,"Pruned Mass [GeV]", "Events Per GeV",False)
stackPlotter.SetEventsPer(0.05)
expr = 'fatjet1tau21'
stackPlotter.SetDefaultExpr(expr)
stackPlotter.MakeCanvas(outDir + 'WenMV_' + expr,20,0,1,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
stackPlotter.SetEventsPer(1.0)

