#! /usr/bin/python

import sys
import ROOT

ROOT.gROOT.LoadMacro('MonoJetReader.cc+')
ROOT.gROOT.LoadMacro('MergedTree.cc+')
ROOT.gROOT.LoadMacro('mergeData.cc+')

inFolder = '/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesSkimmedV7'

ROOT.mergeData(inFolder)
