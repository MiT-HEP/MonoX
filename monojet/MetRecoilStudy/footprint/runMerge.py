#! /usr/bin/python

import sys
import ROOT

ROOT.gROOT.LoadMacro('MonoJetReader.cc+')
ROOT.gROOT.LoadMacro('MergedTree.cc+')
ROOT.gROOT.LoadMacro('mergeData.cc+')

ROOT.mergeData()
