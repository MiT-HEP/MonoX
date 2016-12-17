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

loc = sys.argv[1]
pid = sys.argv[2]
pt = sys.argv[3]
met = sys.argv[4]

try:
    era = sys.argv[5]
except:
    era = 'Spring15'

inputKey = era+'_'+loc+'_'+pid+'_PhotonPt'+pt+'_Met'+met

versDir = os.path.join('/data/t3home000/ballen/hist/purity', s.Version)
plotDir = os.path.join(versDir,inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)
"""
else:
    shutil.rmtree(outDir)
    os.makedirs(outDir)
"""
filePath = os.path.join(plotDir, 'mceff.out')

tree = ROOT.TChain('events')
print config.skimDir
# tree.Add(config.skimDir + '/gj-40_purity.root')
# tree.Add(config.skimDir + '/gj-100_purity.root')
# tree.Add(config.skimDir + '/gj-200_purity.root')
# tree.Add(config.skimDir + '/gj-400_purity.root')
# tree.Add(config.skimDir + '/gj-600_purity.root')
tree.Add(config.skimDir + '/znng-130_purity.root')
tree.Add(config.skimDir + '/dmv-500-1_purity.root')
tree.Add(config.skimDir + '/dmv-1000-1_purity.root')
tree.Add(config.skimDir + '/dmv-2000-1_purity.root')


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

pids = pid.split('-')
if len(pids) > 1:
    pid = pids[0]
    extras = pids[1:]
elif len(pids) == 1:
    pid = pids[0]
    extras = []

idmap = { 'loose' : 0, 'medium' : 1, 'tight' : 2, 'highpt' : 3 }
calc.setWorkingPoint(idmap[pid])
if 'pixel' in extras:
    calc.applyPixelVeto()
if 'monoph' in extras:
    calc.applyMonophID()
if 'worst' in extras:
    calc.applyWorstIso()

if era == 'Spring16':
    calc.setEra(1)

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

calc.calculate(tree)

print filePath
output = file(filePath, 'w')

cuts = ['match', 'hOverE', 'sieie', 'nhIso', 'phIso', 'chIso', 'eveto', 'spike', 'halo', 'worst']
effs= []
for iEff, cut in enumerate(cuts):
    if not 'pixel' in extras and cut == 'eveto':
        print 'blah'
        break
    if not 'monoph' in extras and cut == 'spike':
        break
    if not 'worst' in extras and cut == 'worst':
        break

    eff = calc.getEfficiency(iEff)
    string = "Efficiency after %6s cut is %f +%f -%f \n" % (cut, eff[0], eff[1], eff[2])
    print string.strip('\n')
    output.write(string)

output.close()
print 'Closed'

calc = None
print 'Done'

sys.exit(0)
