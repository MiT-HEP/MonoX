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

cutNames = [ 'tau matched', 'isEB', 'pT > 175', 'pass hOverE', 'pass nhIso', 'pass chIso', 'pass chWorstIso', 'pass phIso', 'pass sieie <', 'pass eveto', 'pass sieie >', 'pass s4', 'pass mip energy', 'pass time' ]

hist = ROOT.TH1F("yield", "yield", 1, 0., 1.)

lumi = 2239.9
baselineCuts = [ '', 't1Met.iso', 't1Met.iso && t1Met.met > 170', 't1Met.iso && tauVeto && t1Met.met > 170' ]
yields = []
for baselineCut in baselineCuts:
    print "==============================================="
    print "Raw and weighted MC event yields for photons matched to taus"
    print "With following selecetion applied: "+baselineCut
    print "==============================================="
    print '%20s & %10s & %10s & %10s & %10s \\\\' % ('cut', 'raw yield', 'raw eff', 'weightyeild', 'weight eff')
    temp = []
    for iC, cutName in enumerate(cutNames):
        if baselineCut:
            idCutString = baselineCut+' && photons.id > '+str(iC) 
        else:
            idCutString = 'photons.id > '+str(iC)
        tree.Draw("0.5>>yield", idCutString)
        counts = hist.GetBinContent(1)

        weightedCutString = '(%.1f) * weight * (%s)' % (lumi, idCutString) 
        tree.Draw("0.5>>yield", weightedCutString)
        weightedCounts = hist.GetBinContent(1)

        if iC:
            print '%20s & %10d & %10.4f & %10.2f & %10.4f \\\\' % (cutName, counts, counts / temp[0][0] * 100., weightedCounts, weightedCounts / temp[0][1] * 100.)
        else: 
            print '%20s & %10d & %10.4f & %10.2f & %10.4f \\\\' % (cutName, counts, 100., weightedCounts, 100.)
        temp.append( (counts, weightedCounts) )
    yields.append(temp)


