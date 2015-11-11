import os
import json
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))

ROOT.gROOT.LoadMacro(thisdir + '/GoodLumiFilter.cc+')

def makeGoodLumiFilter(jsonPath):
    goodLumi = ROOT.GoodLumiFilter()

    with open(jsonPath) as source:
        lumiList = json.loads(source.read())

        for run, lumiranges in lumiList.items():
            for lumirange in lumiranges:
                lumirange[1] += 1
                for lumi in range(*tuple(lumirange)):
                    goodLumi.addLumi(int(run), lumi)

    return goodLumi
