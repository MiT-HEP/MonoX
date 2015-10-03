#! /usr/bin/python

import sys
import ROOT

ROOT.gROOT.LoadMacro('NeroTree.C+')
ROOT.gROOT.LoadMacro('MonoJetTree.cc+')
ROOT.gROOT.LoadMacro('NeroSlimmer.cc+')

ROOT.NeroSlimmer(sys.argv[1],sys.argv[2])
