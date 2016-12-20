#!/usr/bin/env python

import os
import sys
import shutil
import json

thisdir = os.path.dirname(os.path.realpath(__file__))

import ROOT

sname = sys.argv[1]

jsonPath = '/cvmfs/cvmfs.cmsaf.mit.edu/hidsk0001/cmsprod/cms/json/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt'

ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
ROOT.gROOT.LoadMacro(thisdir + '/skimUncleaned.cc+')
ROOT.gROOT.LoadMacro(thisdir + '/../../common/GoodLumiFilter.cc+')

goodLumi = ROOT.GoodLumiFilter()

with open(jsonPath) as source:
    lumiList = json.loads(source.read())

    for run, lumiranges in lumiList.items():
        for lumirange in lumiranges:
            lumirange[1] += 1
            for lumi in range(*tuple(lumirange)):
                goodLumi.addLumi(int(run), lumi)

source = ROOT.TFile.Open('/data/t3home000/yiiyama/simpletree/uncleaned/' + sname + '.root')
outputFile = ROOT.TFile.Open('/tmp/' + sname + '.root', 'recreate')

input = source.Get('events')

ROOT.skimUncleaned(input, outputFile, goodLumi)

outputFile.Close()
source.Close()

shutil.move('/tmp/' + sname + '.root', '/data/t3home000/yiiyama/simpletree/uncleanedSkimmed')
