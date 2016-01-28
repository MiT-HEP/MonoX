#! /usr/bin/python

from StackPlotter import stackPlotter
from array import array
import cuts

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/CleanSkim/'

stackPlotter.SetTreeName('events')
stackPlotter.SetAllHist('htotal')
stackPlotter.SetLuminosity(2109.0)
stackPlotter.AddDataFile(directory + 'monojet_Data.root')
stackPlotter.ReadMCConfig('MCFiles.txt',directory)
stackPlotter.SetMCWeights("mcFactors")
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.SetDefaultExpr('met')
stackPlotter.SetEventsPer(1.0)
stackPlotter.SetRatioMinMax(0.5,1.5)

xArray = [200,250,300,350,400,500,600,1000]
outDir = '/afs/cern.ch/user/d/dabercro/www/monoV_160128/'

stackPlotter.SetDefaultWeight(cuts.ZmmMJ)
#stackPlotter.MakeCanvas(outDir + 'ZmmMJ_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.ZeeMJ)
#stackPlotter.MakeCanvas(outDir + 'ZeeMJ_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.WmnMJ)
#stackPlotter.MakeCanvas(outDir + 'WmnMJ_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.WenMJ)
#stackPlotter.MakeCanvas(outDir + 'WenMJ_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.gjetMJ)
#stackPlotter.MakeCanvas(outDir + 'gjetMJ_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

###

stackPlotter.SetDefaultWeight(cuts.ZmmMV)
#stackPlotter.MakeCanvas(outDir + 'ZmmMV_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.ZeeMV)
#stackPlotter.MakeCanvas(outDir + 'ZeeMV_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.WmnMV)
#stackPlotter.MakeCanvas(outDir + 'WmnMV_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.WenMV)
#stackPlotter.MakeCanvas(outDir + 'WenMV_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.gjetMV)
#stackPlotter.MakeCanvas(outDir + 'gjetMV_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.topMV)
#stackPlotter.MakeCanvas(outDir + 'topMV_met',len(xArray)-1,array('d',xArray),"MET [GeV]", "Events Per GeV",True)

stackPlotter.SetDefaultWeight(cuts.top)

stackPlotter.SetEventsPer(0.05)
stackPlotter.SetDefaultExpr('fatjet1tau21')
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
stackPlotter.MakeCanvas(outDir + 'top_tau21',20,0.0,1.0,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)

stackPlotter.SetEventsPer(1.0)
stackPlotter.SetDefaultExpr('fatjet1PrunedM')
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kRight,0.25,0.5)
stackPlotter.MakeCanvas(outDir + 'top_PrunedM',20,0,200,"m_{pruned} [GeV]", "Events Per GeV",False)

stackPlotter.SetDefaultWeight(cuts.top + '&& fatjet1tau21 < 0.45')
stackPlotter.MakeCanvas(outDir + 'top_PrunedM_cut',20,0,200,"m_{pruned} [GeV]", "Events Per GeV",False)

stackPlotter.SetDefaultWeight(cuts.top + '&& abs(fatjet1PrunedM - 85) < 20')
stackPlotter.SetDefaultExpr('fatjet1tau21')
stackPlotter.SetLegendLocation(stackPlotter.kUpper,stackPlotter.kLeft,0.25,0.5)
stackPlotter.MakeCanvas(outDir + 'top_tau21_cut',20,0.0,1.0,"#tau_{2}/#tau_{1}", "Events Per 0.05",False)
