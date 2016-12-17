#!/usr/bin/env python

import sys
import os
sys.dont_write_bytecode = True
import math
import array
import shutil
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from datasets import allsamples
from plotstyle import SimpleCanvas
import config

# set up a workspace and the main variable
work = ROOT.RooWorkspace('work', 'work')
phi = work.factory('phi[%f,%f]' % (-math.pi * 0.5, math.pi * 0.5))
phiset = ROOT.RooArgSet(phi)

# TTree expression
phimpipi = 'TVector2::Phi_mpi_pi(photons.phi + 0.005)'
phivar = 'TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(photons.phi + 0.005) - 1.570796)) - 1.570796'

# targnames: sample names for target trees (monoph skim)
# halonames: sample names for halo templates (can be a photon skim)
targnames = ['sph-16b-r', 'sph-16c-r', 'sph-16d-r', 'sph-16e-r', 'sph-16f-r', 'sph-16g-r', 'sph-16h1', 'sph-16h2', 'sph-16h3']
#targnames = ['sph-16b-r', 'sph-16c-r', 'sph-16d-r']
halonames = targnames
targs = [allsamples[sname] for sname in targnames]
halos = [allsamples[sname] for sname in halonames]

#lumi = sum(t.lumi for t in targs)
lumi = sum(allsamples[sname].lumi for sname in ['sph-16b-r', 'sph-16c-r', 'sph-16d-r'])
lumi += sum(allsamples[sname].lumi for sname in ['sph-16e-r', 'sph-16f-r', 'sph-16g-r', 'sph-16h1', 'sph-16h2', 'sph-16h3']) / 4.

dataTree = ROOT.TChain('events')
for sample in halos:
    dataTree.Add(config.photonSkimDir + '/' + sample.name + '.root')
#    dataTree.Add(config.dataNtuplesDir + '/' + sample.book + '/' + sample.fullname + '/*.root')
dataTree.SetEstimate(dataTree.GetEntries() + 1)

candTree = ROOT.TChain('events')
for sample in targs:
    print config.skimDir + '/' + sample.name + '_monoph.root'
    candTree.Add(config.skimDir + '/' + sample.name + '_monoph.root')
candTree.SetEstimate(candTree.GetEntries() + 1)

# Canvas
from plotstyle import SimpleCanvas
canvas = SimpleCanvas(lumi = lumi)
plotName = 'fit'

### fit to halo distribution and parametrize

# draw
dataTree.Draw(phimpipi + '>>haloTemp(40,-{pi},{pi})'.format(pi = math.pi), 'photons.mipEnergy > 4.9 && photons.isEB && photons.scRawPt > 175. && t1Met.met > 140. && photons.chWorstIso < 1.37 && photons.nhIso < 1.06', 'goff')

haloTemp = ROOT.gDirectory.Get('haloTemp')
haloTemp.SetLineColor(ROOT.kBlack)
haloTemp.SetLineWidth(2)
haloTemp.SetTitle(';#phi\'')

canvas.addHistogram(haloTemp)
canvas.xtitle = '#phi\''
canvas.printWeb('monophoton/halo', 'haloTemp', logy = False)
canvas.Clear()

# first get the halo phi values
nHalo = dataTree.Draw(phivar + '>>haloTemp(40,-{pi},{pi})'.format(pi = math.pi), 'photons.mipEnergy > 4.9 && photons.isEB && photons.scRawPt > 175. && t1Met.met > 140. && photons.chWorstIso < 1.37 && photons.nhIso < 1.06', 'goff')
print nHalo, 'halo events'

# dump them into a RooDataSet
haloData = ROOT.RooDataSet('halo', 'halo', phiset)
haloPhi = dataTree.GetV1()
for iHalo in range(nHalo):
    phi.setVal(haloPhi[iHalo])
    haloData.add(phiset)

# then fit with gaus + gaus + uniform
base = work.factory('Uniform::base({phi})')
peak = work.factory('SUM::peak(p1[0.1,0.,1.]*Gaussian::peak1(phi, mean1[0.,-3.,3.], sigma1[0.1,0.,1.]),Gaussian::peak2(phi, mean2[0.,-3.,3.], sigma2[0.001,0.,0.1]))')
haloModel = work.factory('SUM::haloModel(fbase[0.1,0.,1.]*base, peak)')

haloModel.fitTo(haloData)

# draw
frame = phi.frame()
frame.SetTitle('')
frame.GetXaxis().SetTitle('#phi\'')
haloData.plotOn(frame)
haloModel.plotOn(frame)
canvas.addHistogram(frame)
canvas.printWeb('monophoton/halo', 'phiHaloFoldedFit', logy = False)
canvas.Clear()

# fix the halo template parameters
leaves = ROOT.RooArgSet()
haloModel.leafNodeServerList(leaves)
litr = leaves.fwdIterator()
while True:
    leaf = litr.next()
    if not leaf:
        break

    leaf.setConstant(True)

### MC flat distribution
# draw
#mcTree = ROOT.TChain('events')
#mcTree.Add(config.skimDir + '/znng-130_monoph.root')
#mcTree.Draw(phimpipi + '>>mcTemp(40,-{pi},{pi})'.format(pi = math.pi), 'photons.scRawPt[0] > 175. && t1Met.met > 170. && t1Met.minJetDPhi > 0.5 && t1Met.photonDPhi > 2.', 'goff')
#
#mcTemp = ROOT.gDirectory.Get('mcTemp')
#mcTemp.SetLineColor(ROOT.kBlack)
#mcTemp.SetLineWidth(2)
#mcTemp.SetTitle(';#phi\'')

#lumi = canvas.lumi
#canvas.lumi = -1.
#canvas.addHistogram(mcTemp)
#canvas.printWeb('monophoton/halo', 'mcTemp', logy = False)
#canvas.Clear()
#canvas.lumi = lumi

### fit to candidates

# candidate phi values
nTarg = candTree.Draw(phivar, 'photons.scRawPt[0] > 175. && t1Met.met > 170. && t1Met.minJetDPhi > 0.5 && t1Met.photonDPhi > 2. && (run <= 276811 || event % 4 == 0)', 'goff')
print nTarg, 'target events'

# dump into a RooDataSet
targData = ROOT.RooDataSet('targ', 'targ', phiset)
targPhi = candTree.GetV1()
for iTarg in range(nTarg):
    phi.setVal(targPhi[iTarg])
    targData.add(phiset)

# fit with halo + uniform
uniform = work.factory('Uniform::uniform({phi})')
model = work.factory('SUM::model(nhalo[0.5,0.,{maximum}]*haloModel, nuniform[{init},0.,{maximum}]*uniform)'.format(maximum = nTarg * 1.1, init = nTarg * 0.95))

model.fitTo(targData)

# plot
nbins = 25

phi.setBins(nbins)
frame = phi.frame()
frame.SetTitle('')
targData.plotOn(frame)
model.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kGreen))
model.plotOn(frame, ROOT.RooFit.Components('uniform'), ROOT.RooFit.LineColor(ROOT.kBlue))

canvas.Clear(full = True)

canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
canvas.legend.add('fit', title = 'Uniform', lcolor = ROOT.kBlue, lwidth = 2, opt = 'L')
canvas.legend.add('halo', title = 'Halo template', lcolor = ROOT.kGreen, lwidth = 1, opt = 'L')
canvas.legend.add('obs', title = 'Data', mcolor = ROOT.kBlack, mstyle = 8, msize = 1, lcolor = ROOT.kBlack, lwidth = 1, opt = 'LP')

canvas.ytitle = 'Events / (#pi/%d)' % nbins

canvas.addHistogram(frame)
canvas.printWeb('monophoton/halo', plotName, logy = False)

# generate 10 toy distributions - does your target distribution look "normal"?

for iT in range(10):
    toyData = model.generate(phiset, nTarg)
    
    frame = phi.frame()
    frame.SetTitle('')
    toyData.plotOn(frame)
    
    canvas.Clear(full = True)
    canvas.ytitle = 'Events / (#pi/25)'
    canvas.addHistogram(frame)
    canvas.printWeb('monophoton/halo', 'toy%d' % iT, logy = False)
