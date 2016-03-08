#! /usr/bin/python

from Stack import *

plotter.SetMinLegendFrac(0.0)

plotter.InsertTemplate("templates.root","hQCD_MonoJ_nominal","QCD")

theArray = [200., 230., 260.0, 290.0, 320.0, 350.0, 390.0, 430.0, 470.0, 510.0, 550.0, 590.0, 640.0, 690.0, 740.0, 790.0, 840.0, 900.0, 960.0, 1020.0, 1090.0, 1160.0, 1250.0]
args = ['met',len(theArray)-1,array('d',theArray),'E_{T}^{miss} [GeV]', 'Events Per GeV',True]

MakePlots(['monoJet','monoJet_inc'],['signal'],[args])

