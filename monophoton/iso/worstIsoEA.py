# DO NOT USE - this is flawed.

import os
import sys
import shutil
import ROOT

NENTRIES = -1

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from datasets import allsamples
import config

sphSamples = allsamples.getmany('sph-16*')

tree = ROOT.TChain('skimmedEvents')
for sample in sphSamples:
    tree.Add('/data/t3home000/yiiyama/studies/monophoton/efake_skim/' + sample.name + '_eg.root')

rhoBins = [0., 5., 7., 9.] + [10. + x for x in range(8)] + [18., 20., 23., 30., 35.]

outputFile = ROOT.TFile.Open(config.histDir + '/worstIsoEA.root', 'recreate')
graph = ROOT.TGraphErrors(len(rhoBins) - 1)

for iP in range(len(rhoBins) - 1):
    rhoMin = rhoBins[iP]
    rhoMax = rhoBins[iP + 1]

    print rhoMin, rhoMax

    tree.Draw('rho>>rho%d(35, 0., 35.)' % iP, 'probes.nhIso < 1.06 && probes.phIso < 0.28 && probes.sieie < 0.0102 && probes.hOverE < 0.05 && !probes.csafeVeto && tp.mass > 81. && tp.mass < 101. && rho > %f && rho < %f' % (rhoMin, rhoMax), 'goff')
    rhodist = ROOT.gDirectory.Get('rho%d' % iP)
    x = rhodist.GetMean()
    
    nSel = tree.Draw('probes.chIsoMax>>iso%d(300, 0., 30.)' % iP, 'probes.nhIso < 1.06 && probes.phIso < 0.28 && probes.sieie < 0.0102 && probes.hOverE < 0.05 && !probes.csafeVeto && tp.mass > 81. && tp.mass < 101. && rho > %f && rho < %f' % (rhoMin, rhoMax), 'goff')
    isodist = ROOT.gDirectory.Get('iso%d' % iP)
    outputFile.cd()
    isodist.Write()

    ylow = -1.
    y = -1.
    yhigh = -1.

    iBin = 1
    while iBin != isodist.GetNbinsX() + 1:
        frac = isodist.Integral(1, iBin) / isodist.GetSumOfWeights()
        if ylow < 0. and frac > 0.75:
            ylow = isodist.GetXaxis().GetBinCenter(iBin)
        if y < 0. and frac > 0.8:
            y = isodist.GetXaxis().GetBinCenter(iBin)
        if yhigh < 0. and frac > 0.85:
            yhigh = isodist.GetXaxis().GetBinCenter(iBin)

        iBin += 1

    graph.SetPoint(iP, x, y)
    graph.SetPointError(iP, 0., 0.5 * (yhigh - ylow))

outputFile.cd()
graph.Write('graph')

line = ROOT.TF1('line', 'pol1(0)')
line.SetParameters(2., 0.1)

graph.Fit(line)

outputFile.cd()
line.Write('fit')
