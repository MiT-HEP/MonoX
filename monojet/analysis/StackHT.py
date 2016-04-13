#! /usr/bin/python

from CrombieTools.PlotTools.PlotStack import *
from array import array
import CrombieTools.LoadConfig, os

os.environ['CrombieInFilesDir'] = '/afs/cern.ch/work/d/dabercro/public/Winter15/SkimOut_160216'

SetupFromEnv()

plotter.SetIsCMSPrelim(True)
plotter.SetTreeName('events')
plotter.SetAllHistName('htotal')
plotter.AddDataFile('monojet_Data.root')
plotter.SetLegendLocation(plotter.kUpper,plotter.kRight,0.25,0.5)
plotter.SetEventsPer(1.0)
plotter.SetMinLegendFrac(0.03)
plotter.SetIgnoreInLinear(0.005)
plotter.SetRatioMinMax(0.5,1.5)
plotter.SetOthersColor(922)
plotter.SetRatioTitle('Data/Pred.')
plotter.SetRatioDivisions(504,False)
plotter.SetRatioGrid(1)
plotter.SetCanvasSize(600,700)
plotter.SetFontSize(0.03)
plotter.SetAxisTitleOffset(1.2)

regionList = ['signal','Zmm','Zee','Wmn','Wen']

def SetupArgs(theArray):
    return [
        ['ht_cleanedjets',len(theArray)-1,array('d',theArray),'HT [GeV]', 'Events Per GeV',True]
        ]
            

def RunPlots2(categories,regions):

    MJArray = [0, 50, 100, 140, 170., 200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]
    MVArray = [0,50,100,150,200,250,300,350,400,500,600,750,1000]

    anArray = MJArray

    if 'monoV' in categories:
        anArray = MVArray

    MakePlots(categories,regions,SetupArgs(anArray))

def RunPlots(regions):
    RunPlots2(['monoJet','monoJet_inc'],regions)
    RunPlots2(['monoV'],regions)

if __name__ == '__main__':
    RunPlots(regionList)
