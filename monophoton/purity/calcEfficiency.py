#!/usr/bin/env python

import sys
import os
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
import selections as s

ROOT.gROOT.LoadMacro(thisdir + '/Calculator.cc+')

loc = sys.argv[1] # barrel or endcap
wp = sys.argv[2] # (loose|medium|tight)
pt = sys.argv[3] # Inclusive or (Min)to(Max)
met = sys.argv[4] # Inclusive or (Min)to(Max)

try:
    era = sys.argv[5]
except:
    era = 'Spring15'

inputKey = era+'_'+loc+'_'+wp+'_PhotonPt'+pt+'_Met'+met

versDir = s.versionDir
plotDir = os.path.join(versDir,inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)
"""
else:
    shutil.rmtree(outDir)
    os.makedirs(outDir)
"""
treeFilePath = os.path.join(plotDir, 'mceff.root')
filePath = os.path.join(plotDir, 'mceff.out')

tree = ROOT.TChain('events')
print config.skimDir
# tree.Add(config.skimDir + '/gj-40_purity.root')
# tree.Add(config.skimDir + '/gj-100_purity.root')
# tree.Add(config.skimDir + '/gj-200_purity.root')
# tree.Add(config.skimDir + '/gj-400_purity.root')
# tree.Add(config.skimDir + '/gj-600_purity.root')
tree.Add(config.skimDir + '/znng-130-o_purity.root')
#tree.Add(config.skimDir + '/zllg-130-o_purity.root')
#tree.Add(config.skimDir + '/wnlg-130-o_purity.root')
"""
for samp in ['dma', 'dmv']:
    tree.Add(config.skimDir + '/' + samp + '-500-1_purity.root')
    tree.Add(config.skimDir + '/' + samp + '-1000-1_purity.root')
    tree.Add(config.skimDir + '/' + samp + '-1000-150_purity.root')
    tree.Add(config.skimDir + '/' + samp + '-2000-1_purity.root')
    tree.Add(config.skimDir + '/' + samp + '-2000-500_purity.root')
    tree.Add(config.skimDir + '/' + samp + '-10000-1_purity.root')
    tree.Add(config.skimDir + '/' + samp + '-10000-10_purity.root')
    tree.Add(config.skimDir + '/' + samp + '-10000-50_purity.root')
    tree.Add(config.skimDir + '/' + samp + '-10000-150_purity.root')
"""

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

calc.setWorkingPoint(getattr(ROOT.Calculator, 'WP' + wp))
calc.setEra(getattr(ROOT.Calculator, era))

if pt == 'Inclusive':
    minPt = 175.
    maxPt = 6500.
else:
    (minPt, maxPt) = pt.split('to')
if maxPt == 'Inf':
    maxPt = 6500.
calc.setMinPhoPt(float(minPt))
calc.setMaxPhoPt(float(maxPt))

if met == 'Inclusive':
    minMet = 175.
    maxMet = 6500.
else:
    (minMet, maxMet) = met.split('to')
if maxMet == 'Inf':
    maxMet = 6500.
calc.setMinMet(float(minMet))
calc.setMaxMet(float(maxMet))

outputFile = ROOT.TFile.Open(treeFilePath, 'recreate')

nGen = calc.calculate(tree, outputFile)

outputFile.cd()
outputFile.Write()

print filePath
output = file(filePath, 'w')

cutTree = outputFile.Get('cutflow')
nMatched = cutTree.GetEntries('Match')
nUnmatched = cutTree.GetEntries('!Match')

eff = float(nMatched) / nGen
errh = ROOT.TEfficiency.ClopperPearson(nGen, nMatched, 0.6827, True) - eff
errl = eff - ROOT.TEfficiency.ClopperPearson(nGen, nMatched, 0.6827, False)

string = "Matching efficiency is %f +%f -%f \n" % (eff, errh, errl)
print string.strip('\n')
output.write(string)

cuts =[
  "HoverE",
  "Sieie",
  "NHIso",
  "PhIso",
  "CHIso",
  "Eveto",
#  "Spike",
#  "Halo",
  "CHMaxIso"
]

sequential = ['Match']
for cut in cuts:
    sequential.append(cut)

    nSelected = cutTree.GetEntries(' && '.join(sequential))

    eff = float(nSelected) / nMatched
    errh = ROOT.TEfficiency.ClopperPearson(nMatched, nSelected, 0.6827, True) - eff
    errl = eff - ROOT.TEfficiency.ClopperPearson(nMatched, nSelected, 0.6827, False)
    
    string = "Efficiency after %s cut is %f +%f -%f \n" % (cut, eff, errh, errl)
    print string.strip('\n')
    output.write(string)

sequential = ['!Match']
for cut in cuts:
    sequential.append(cut)

    nSelected = cutTree.GetEntries(' && '.join(sequential))

    eff = float(nSelected) / nUnmatched
    errh = ROOT.TEfficiency.ClopperPearson(nUnmatched, nSelected, 0.6827, True) - eff
    errl = eff - ROOT.TEfficiency.ClopperPearson(nUnmatched, nSelected, 0.6827, False)
    
    string = "Fake rate after %s cut is %f +%f -%f \n" % (cut, eff, errh, errl)
    print string.strip('\n')
    output.write(string)

output.close()
print 'Closed'

calc = None
print 'Done'

sys.exit(0)
