#! /usr/bin/python

from ROOT import TFile
from CrombieTools.PlotTools.PlotHists import plotter
from CrombieTools.LoadConfig import cuts

from array import array

#signalFile = TFile('/afs/cern.ch/work/d/dabercro/public/Winter15/SkimOut_160212/monojet_JHUGen_Higgs_WH_125_10.root')
signalFile = TFile('/afs/cern.ch/work/d/dabercro/public/Winter15/SkimOut_160212/monojet_VectorMonoW_Mphi-200_Mchi-10_lep_gSM-1p0_gDM-1p0_13TeV.root')
#signalFile = TFile('/afs/cern.ch/work/d/dabercro/public/Winter15/SkimOut_160212/monojet_VectorMonoW_Mphi-2000_Mchi-150_lep_gSM-1p0_gDM-1p0_13TeV.root')

plotter.SetDefaultTree(signalFile.events)

plotter.AddLegendEntry('With Pileup Reweighting',1)
plotter.AddLegendEntry('Without Pileup Reweighting',2)
plotter.SetEventsPer(1.0)
plotter.SetDataIndex(0)
plotter.SetRatioIndex(1)

# plotter.SetPrintTests(True)
# plotter.SetNormalizedHists(True)

def plotPU(category):

    MJArray = [200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]
    MVArray = [250,300,350,400,500,600,1000]

    theArray = MJArray
    if category == 'monoV':
        theArray = MVArray

    plotter.ResetWeight()
    plotter.AddWeight(cuts.cut(category,'signal') + '* mcFactors')
    plotter.AddWeight(cuts.cut(category,'signal') + '* (lepton_SF * mcWeight)')

    plotter.SetDefaultExpr('met')
    plotter.MakeCanvas('~/www/plots/160308/' + category,len(theArray) - 1,array('d',theArray),'MET [GeV]','Events/GeV',True)
    plotter.SetDefaultExpr('npv')
    plotter.MakeCanvas('~/www/plots/160308/NPV_' + category,30,0,30,'NPV','Events',False)


if __name__ == '__main__':
    plotPU('monoJet')
    plotPU('monoV')
