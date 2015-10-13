#! /usr/bin/python

import ROOT

ROOT.gROOT.LoadMacro('RecoilCorrector.cc+')
ROOT.gROOT.LoadMacro('applyRecoilCorrections.cc+')

ROOT.applyRecoilCorrections('list.txt','fitResults.root','Zmm','Zmm',False)
