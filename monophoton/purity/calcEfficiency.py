#!/usr/bin/env python

import sys
import os
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
import selections as s
from plotstyle import WEBDIR

OVERWRITE = True

ROOT.gROOT.LoadMacro(thisdir + '/Calculator.cc+')

loc = sys.argv[1] # barrel or endcap
wp = sys.argv[2] # (loose|medium|tight)
pt = sys.argv[3] # Inclusive or (Min)to(Max)
met = sys.argv[4] # Inclusive or (Min)to(Max)

try:
    era = sys.argv[5]
except:
    era = 'Spring16'

inputKey = era+'_'+loc+'_'+wp+'_PhotonPt'+pt+'_Met'+met

versDir = os.path.join(s.versionDir,inputKey)
if not os.path.exists(versDir):
    os.makedirs(versDir)

plotDir = WEBDIR + '/purity/' + s.Version + '/' + inputKey
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

treeFilePath = os.path.join(versDir, 'mceff.root')
filePath = os.path.join(plotDir, 'mceff.out')

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

wps = wp.split('-')
wp = wps[0]
extras = wps[1:]

calc.setWorkingPoint(getattr(ROOT.Calculator, 'WP' + wp))
eraEnum = getattr(ROOT.panda.XPhoton, 'k' + era)
calc.setEra(eraEnum)

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

treeDict = {}

gj04Tree = ROOT.TChain('events')
gj04Tree.Add(config.skimDir + '/gj04-*_emjet.root')
treeDict['gj04'] = gj04Tree

wlnunTree = ROOT.TChain('events')
wlnunTree.Add(config.skimDir + '/wlnun-*_emjet.root')
wlnunTree.Add(config.skimDir + '/tt_emjet.root')
treeDict['wlnun'] = wlnunTree

# tree.Add(config.skimDir + '/znng-130-o_emjet.root')
# tree.Add(config.skimDir + '/zllg-130-o_emjet.root')
# tree.Add(config.skimDir + '/wnlg-130-o_emjet.root')

dynTree = ROOT.TChain('events')
dynTree.Add(config.skimDir + '/dyn-50@_emjet.root')
dynTree.Add(config.skimDir + '/dyn-50-*_emjet.root')
# treeDict['dyn'] = dynTree

topTree = ROOT.TChain('events')
topTree.Add(config.skimDir + '/tt_emjet.root')
topTree.Add(config.skimDir + '/st*_emjet.root')
# treeDict['top'] = topTree

"""
for samp in ['dma', 'dmv']:
    tree.Add(config.skimDir + '/' + samp + '-500-1_emjet.root')
    tree.Add(config.skimDir + '/' + samp + '-1000-1_emjet.root')
    tree.Add(config.skimDir + '/' + samp + '-1000-150_emjet.root')
    tree.Add(config.skimDir + '/' + samp + '-2000-1_emjet.root')
    tree.Add(config.skimDir + '/' + samp + '-2000-500_emjet.root')
    tree.Add(config.skimDir + '/' + samp + '-10000-1_emjet.root')
    tree.Add(config.skimDir + '/' + samp + '-10000-10_emjet.root')
    tree.Add(config.skimDir + '/' + samp + '-10000-50_emjet.root')
    tree.Add(config.skimDir + '/' + samp + '-10000-150_emjet.root')
"""
print filePath
print treeFilePath
output = file(filePath, 'w')
if OVERWRITE:
    if os.path.exists(treeFilePath):
        os.remove(treeFilePath)

if os.path.exists(treeFilePath):
    outputFile = ROOT.TFile.Open(treeFilePath, 'read')
else:
    outputFile = ROOT.TFile.Open(treeFilePath, 'recreate')

for tname, tree in sorted(treeDict.iteritems()):
    print tname, tree.GetEntries()

    try:
        print 'Reading cutflow tree from existing file', treeFilePath

        cutTree = outputFile.Get('cutflow_' + tname)
        nMatched = cutTree.GetEntries('Match')

        for key in outputFile.GetListOfKeys():
            name = key.GetName()
            if name.startswith('gen='):
                nGen = int(name[name.find('=') + 1:])
                break

    except:
        nGen = calc.calculate(tree, outputFile, tname)

        outputFile.cd()
        outputFile.Write()
        cutTree = outputFile.Get('cutflow_' + tname)    

    hYield = ROOT.TH1F('hYield', 'Yields', 1, 0., 1.)

    nMatched = cutTree.GetEntries('Match')
    nUnmatched = cutTree.GetEntries('!Match')

    eff = float(nMatched) / nGen
    errh = ROOT.TEfficiency.ClopperPearson(nGen, nMatched, 0.6827, True) - eff
    errl = eff - ROOT.TEfficiency.ClopperPearson(nGen, nMatched, 0.6827, False)

    string = tname + " matching efficiency is %f +%f -%f \n" % (eff, errh, errl)
    print string.strip('\n')
    output.write(string)

    cutTree.Draw('0.5>>hYield', 'weight * Match', 'E')
    nMatched = hYield.Integral()
    hYield.Reset()

    """
    cutTree.Draw('0.5>>hYield', 'weight * !Match', 'E')
    nUnmatched = hYield.Integral()
    hYield.Reset()
    """

    cuts =[
      "HoverE",
      "Sieie",
      "NHIso",
      "PhIso",
      "CHIso",
    ]

    if 'pixel' in extras:
        cuts.append("Eveto")

    if 'monoph' in extras:
        cuts.append("Spike")
        cuts.append("Halo")

    #  "CHMaxIso"

    sequential = ['Match']
    for cut in cuts:
        sequential.append(cut)

        drawString = 'weight * (' + ' && '.join(sequential) + ')'
        cutTree.Draw('0.5>>hYield', drawString, 'E')
        nSelected = hYield.Integral()
        nErr = hYield.GetBinError(1)
        hYield.Reset()

        eff = float(nSelected) / nMatched

        errh = ROOT.TEfficiency.ClopperPearson(nMatched, nSelected, 0.6827, True) - eff
        errl = eff - ROOT.TEfficiency.ClopperPearson(nMatched, nSelected, 0.6827, False)

        string = tname + " efficiency after %s cut is %f +%f -%f (%f +-%f passing events) \n" % (cut, eff, errh, errl, nSelected, nErr)
        print string.strip('\n')
        output.write(string)

    sequential = ['!Match']
    for cut in cuts:
        sequential.append(cut)

        nSelected = cutTree.GetEntries(' && '.join(sequential))

        eff = float(nSelected) / nUnmatched
        errh = ROOT.TEfficiency.ClopperPearson(nUnmatched, nSelected, 0.6827, True) - eff
        errl = eff - ROOT.TEfficiency.ClopperPearson(nUnmatched, nSelected, 0.6827, False)

        string = tname + " fake rate after %s cut is %f +%f -%f \n" % (cut, eff, errh, errl)
        print string.strip('\n')
        output.write(string)

output.close()

calc = None
print 'Done'

sys.exit(0)
