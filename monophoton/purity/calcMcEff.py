#!/usr/bin/env python

import sys
import os
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config
#from selections import Version

ROOT.gSystem.Load(config.libsimpletree)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')

source = sys.argv[1]
loc = sys.argv[2]
pid = sys.argv[3]
chiso = sys.argv[4]
pt = sys.argv[5]
met = sys.argv[6]

inputKey = loc+'_'+pid+'_ChIso'+chiso+'_PhotonPt'+pt+'_Met'+met

versDir = os.path.join('/scratch5/ballen/hist/purity','testing','sieie')
plotDir = os.path.join(versDir,'Plots','SignalContam',source,inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)
filePath = os.path.join(plotDir, 'mceff.out')

tree = ROOT.TChain('events')
print config.skimDir
tree.Add(config.skimDir + '/gj-40_purity.root')
tree.Add(config.skimDir + '/gj-100_purity.root')
tree.Add(config.skimDir + '/gj-200_purity.root')
tree.Add(config.skimDir + '/gj-400_purity.root')
tree.Add(config.skimDir + '/gj-600_purity.root')

ROOT.gROOT.LoadMacro(thisdir + '/Calculator.cc+')

print tree.GetEntries()

calc = ROOT.Calculator()
calc.setMaxDR(0.2)
calc.setMaxDPt(0.2)

if loc == 'barrel':
    minEta = 0.
    maxEta = 1.5
elif loc == 'endcap':
    minEta = 1.5
    maxEta = 2.5
calc.setMinEta(minEta)
calc.setMaxEta(maxEta)

pids = pid.split('_')
if len(pids) > 1:
    pid = pids[0]
    extras = pids[1:]
elif len(pids) == 1:
    pid = pids[0]
    extras = []

idmap = { 'loose' : 0, 'medium' : 1, 'tight' : 2 }
calc.setWorkingPoint(idmap[pid])

(minPt, maxPt) = pt.split('to')
if maxPt == 'Inf':
    maxPt = 6500.
calc.setMinPhoPt(float(minPt))
calc.setMaxPhoPt(float(maxPt))

(minMet, maxMet) = met.split('to')
if maxMet == 'Inf':
    maxMet = 6500.
calc.setMinMet(float(minMet))
calc.setMaxMet(float(maxMet))

calc.calculate(tree)

output = file(filePath, 'w')

effs= []
for iEff in range(8):
    eff = calc.getEfficiency(iEff)
    string = "Efficiency %i is %f +%f -%f \n" % (iEff, eff[0], eff[1], eff[2])
    print string
    output.write(string)

output.close()

