#! /usr/bin/python

import ROOT
from ROOT import TFile
from HistPlotter import histPlotter as plotter
from array import array
import cuts
import math, os

plotter.SetDrawFirst(1)

def returnBkgd(fileNames):
    toReturn = []
    counting = 0
    for fileName in fileNames:
        aFile = TFile(fileName)
        ROOT.gROOT.cd()
        toReturn.append(aFile.Get('Z #rightarrow ll').Clone(fileName + 'Histum' + str(counting)))
        counting += 1
        toReturn.append(aFile.Get('Z #rightarrow #nu#nu').Clone(fileName + 'Histum' + str(counting)))
        counting += 1
        toReturn.append(aFile.Get('QCD').Clone(fileName + 'Histum' + str(counting)))
        counting += 1
        toReturn.append(aFile.Get('#gamma + jets').Clone(fileName + 'Histum' + str(counting)))
        counting += 1
        toReturn.append(aFile.Get('top').Clone(fileName + 'Histum' + str(counting)))
        counting += 1
        toReturn.append(aFile.Get('Di-boson').Clone(fileName + 'Histum' + str(counting)))
        counting += 1
    ##
    return toReturn
#    return []
##

plotter.SetCanvasSize(600,700)
plotter.SetAxisMinMax(0.055,0.18)
plotter.SetRatioMinMax(0.0,2.0)

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/Correct_w_MJ/'

uncFile_ewk = TFile('/afs/cern.ch/user/z/zdemirag/public/forDan/wtoz_ewkunc.root')
uncFile     = TFile('/afs/cern.ch/user/z/zdemirag/public/forDan/wtoz_unc.root')

uncertainties = [
    uncFile_ewk.w_ewkcorr_overz_Upcommon,
    uncFile.znlo012_over_wnlo012_pdfUp,
    uncFile.znlo012_over_wnlo012_renScaleUp,
    uncFile.znlo012_over_wnlo012_facScaleUp
]

outDir = '~/www/monoV_160210/'
#outDir = '~/public/dump/'

gammaMCFile = TFile(directory + 'merged/monojet_WJets.root')
print gammaMCFile.GetName()
zeeMCFile   = TFile(directory + 'merged/monojet_DY.root')
print zeeMCFile.GetName()
dataFile    = TFile(directory + 'monojet_Data.root')
print dataFile.GetName()

xArray = [200,250,300,350,400,500,600,1000]

backgrounds = returnBkgd(['dump/WmnMJ.root','dump/WenMJ.root'])
#backgrounds = returnBkgd(['dump/WmnMJ.root'])

plotter.SetLumiLabel('2.24')
plotter.SetIsCMSPrelim(True)
plotter.SetLegendLocation(plotter.kUpper,plotter.kRight)
plotter.SetDefaultExpr('met')
plotter.SetEventsPer(1.0)

plotter.AddTreeWeight(zeeMCFile.events,'(' + cuts.ZllMJ + ')*mcFactors*XSecWeight')
plotter.AddTreeWeight(dataFile.events,cuts.ZllMJ)
zPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

plotter.ResetTree()
plotter.ResetWeight()

plotter.AddTreeWeight(gammaMCFile.events,'(' + cuts.WlnMJ + ')*mcFactors*XSecWeight')
plotter.AddTreeWeight(dataFile.events,cuts.WlnMJ)

gammaPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

for backgd in backgrounds:
    gammaPlots[1].Add(backgd,-1.0)
##

plotter.AddLegendEntry('MC',2)
plotter.AddLegendEntry('Data',1)

plotter.SetDataIndex(1)
plotter.SetRatioIndex(0)

ratio = plotter.MakeRatio(zPlots,gammaPlots)

for iBin in range(len(xArray)):
    if iBin == 0:
        continue
    sumw2 = math.pow(ratio[0].GetBinError(iBin),2)
    for uncert in uncertainties:
        sumw2 += math.pow(ratio[0].GetBinContent(iBin) * (uncert.GetBinContent(iBin) - 1),2)
    ##
    ratio[0].SetBinError(iBin,math.sqrt(sumw2))
##

plotter.MakeCanvas(outDir + 'WZ_ratio_ZllMJ_met',ratio,'|U| [GeV]','Yield Ratio (Zll/Wln)')

plotter.SetRatioMinMax(0.5,1.5)
plotter.MakeCanvas(outDir + 'WZ_ratio_ZllMJ_met_zoomzoom',ratio,'|U| [GeV]','Yield Ratio (Zll/Wln)')
plotter.SetRatioMinMax(0.0,2.0)

plotter.ResetTree()
plotter.ResetWeight()

## Mono V

backgrounds = returnBkgd(['dump/WmnMV.root','dump/WenMV.root'])
#backgrounds = returnBkgd(['dump/WmnMV.root'])

xArray = [250,300,350,400,500,600,1000]

plotter.SetAxisMinMax(0.0,0.0)

plotter.AddTreeWeight(zeeMCFile.events,'(' + cuts.ZllMV + ')*mcFactors*XSecWeight')
plotter.AddTreeWeight(dataFile.events,cuts.ZllMV)
zPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

plotter.ResetTree()
plotter.ResetWeight()


plotter.AddTreeWeight(gammaMCFile.events,'(' + cuts.WlnMV + ')*mcFactors*XSecWeight')
plotter.AddTreeWeight(dataFile.events,cuts.WlnMV)

gammaPlots = plotter.MakeHists(len(xArray)-1,array('d',xArray))

for backgd in backgrounds:
    gammaPlots[1].Add(backgd,-1.0)
##

ratio = plotter.MakeRatio(zPlots,gammaPlots)

for iBin in range(len(xArray)):
    if iBin == 0:
        continue
    sumw2 = math.pow(ratio[0].GetBinError(iBin),2)
    for uncert in uncertainties:
        sumw2 += math.pow(ratio[0].GetBinContent(iBin) * (uncert.GetBinContent(iBin+1) - 1),2)
    ##
    ratio[0].SetBinError(iBin,math.sqrt(sumw2))
##

plotter.MakeCanvas(outDir + 'WZ_ratio_ZllMV_met',ratio,'|U| [GeV]','Yield Ratio (Zll/Wln)')
