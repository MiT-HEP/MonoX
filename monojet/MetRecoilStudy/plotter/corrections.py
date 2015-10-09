#! /usr/bin/python

import ROOT

ROOT.gROOT.LoadMacro('RecoilCorrector.cc+')
ROOT.gROOT.LoadMacro('applyRecoilCorrections.cc+')



ROOT.applyRecoilCorrections('fileList.txt','fitResults.root','gjets','gjets')
