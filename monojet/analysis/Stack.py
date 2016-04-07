#! /usr/bin/python

from CrombieTools.PlotTools.PlotStack import *
from array import array

SetupFromEnv()

#plotter.AddFriend('postfit')

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
#regionList = ['signal']

def SetupArgs(theArray):
    return [
        ['met',len(theArray)-1,array('d',theArray),'E_{T}^{miss} [GeV]', 'Events Per GeV',True],
        ['jet1Pt',20,100,500,'Leading jet p_{T} [GeV]', 'Events Per GeV',False],
        ['n_cleanedjets',8,0,8,'Number of Jets', 'Events',False],
        ['fatjet1PrunedM',20,0,200,'Pruned Mass [GeV]', 'Events Per GeV',False]
        ]
            

def RunPlots2(categories,regions):

    MJArray = [200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]
#    MJArray = [200., 250., 300.0, 350.0, 400, 500, 600, 1000]
    MVArray = [250,300,350,400,500,600,750,1000]

    anArray = MJArray

    if 'monoV' in categories:
        anArray = MVArray

    MakePlots(categories,regions,SetupArgs(anArray))

    plotter.SetEventsPer(0.1)
    MakePlots(categories,regions,[['jet1Eta',25,-2.5,2.5,'Leading jet #eta','Events Per 0.1',False]])

    plotter.SetLegendLocation(plotter.kUpper,plotter.kLeft,0.25,0.5)
    MakePlots(categories,regions,[['minJetMetDPhi_clean',15,0,3.0,'#Delta #phi_{min}(j,E_{T}^{miss})', 'Events Per 0.1',False]])

    plotter.SetEventsPer(0.05)
    MakePlots(categories,regions,[['fatjet1tau21',20,0,1,'#tau_{2}/#tau_{1}', 'Events Per 0.05',False]])
    
    plotter.SetEventsPer(1.0)
    plotter.SetLegendLocation(plotter.kUpper,plotter.kRight,0.25,0.5)

def RunPlots(regions):
    RunPlots2(['monoJet','monoJet_inc'],regions)
    RunPlots2(['monoV'],regions)

if __name__ == '__main__':
    RunPlots(regionList)
