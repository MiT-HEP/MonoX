#! /usr/bin/python

from CrombieTools.PlotTools.PlotStack import *
from array import array

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

categories = ['monoJet']
regions    = ['signal']

xArray = [200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]

Exprs = [
    ['met',len(xArray)-1,array('d',xArray),'E_{T}^{miss} [GeV]', 'Events Per GeV',True],
    ['jet1Pt',20,100,500,'Leading jet p_{T} [GeV]', 'Events Per GeV',False],
    ['n_cleanedjets',8,0,8,'Number of Jets', 'Events',False],
    ]

for expr in Exprs:
    ## Add manipulation of format for each expr as needed
    MakePlots(categories,regions,expr)
