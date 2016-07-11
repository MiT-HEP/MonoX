import os
import sys
import ROOT as r

limitsPath = '/scratch5/ballen/hist/monophoton/limits/dmv'

for tfile in sorted(os.listdir(limitsPath)):
    (model, mmed, mdm, var, method) = tfile.split('-')
    if not 'ProfileLikelihood' in method:
    # if not 'Asymptotic' in method:
        continue
    
    limitFile = r.TFile(limitsPath + '/' + tfile)
    limitTree = limitFile.Get("limit")

    limitBranch = limitTree.GetBranch("limit");
    limitBranch.GetEntry(0);
    # limitBranch.GetEntry(2);
    signif = limitBranch.GetLeaf("limit").GetValue()

    print "%7s %6s %5s %25s %6.3f" % (model, mmed, mdm, var, signif)
