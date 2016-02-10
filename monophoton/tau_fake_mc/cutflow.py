import sys
import os
import ROOT

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
maindir = basedir+"/main"
sys.path.append(basedir)
sys.path.append(maindir)
from plotstyle import *
from datasets import allsamples
import config

ROOT.gROOT.SetBatch(True)

sampleNames = ['wlnu-100', 'wlnu-200', 'wlnu-400', 'wlnu-600']

tree = ROOT.TChain('events')

for sName in sampleNames:
    sPath = config.skimDir + '/' + sName + '_tau.root'
    tree.Add(sPath)

cutNames = [ 'tau matched', 'isEB', 'pT > 175', 'pass hOverE', 'pass nhIso', 'pass chIso', 'pass phIso', 'pass sieie <', 'pass eveto', 'pass sieie >', 'pass s4', 'pass mip energy', 'pass time' ]

hist = ROOT.TH1F("yield", "yield", 1, 0., 1.)


baselineCuts = [ '', 't1Met.iso', 't1Met.iso && tauVeto', 't1Met.iso && tauVeto && t1Met.met > 140' ]
yields = []
for baselineCut in baselineCuts:
    print "==============================================="
    print "Raw MC event yields for photons matched to taus"
    print "With following selecetion applied: "+baselineCut
    print "==============================================="
    temp = []
    for iC in range(0,13):
        if baselineCut:
            idCutString = baselineCut+' && photons.id > '+str(iC) 
        else:
            idCutString = 'photons.id > '+str(iC)
        tree.Draw("0.5>>yield", idCutString)
        counts = hist.GetBinContent(1)
        if iC:
            print '%20s & %10d & %10.4f \\\\' % (cutNames[iC], counts, counts / temp[0] * 100.)
        else: 
            print '%20s & %10d & %10.4f \\\\' % (cutNames[iC], counts, 100.)
        temp.append(counts)
    yields.append(temp)


