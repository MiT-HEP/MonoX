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

TEMPLATEONLY = False
FITPSEUDODATA = True

from datasets import allsamples
from plotstyle import SimpleCanvas
import config

# targnames: sample names for target trees (monoph skim)
# halonames: sample names for halo templates (can be a photon skim)
targnames = ['sph-16b-m', 'sph-16c-m', 'sph-16d-m', 'sph-16e-m', 'sph-16f-m', 'sph-16g-m', 'sph-16h-m']
targs = [allsamples[sname] for sname in targnames]

# TTree expression
phivar = 'TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(photons.phi_[0] + 0.005) - 1.570796)) - 1.570796'

candSelection = 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.minJetDPhi > 0.5 && t1Met.photonDPhi > 2.'

dataLumi = sum(s.lumi for s in targs)

# Canvas
from plotstyle import SimpleCanvas
canvas = SimpleCanvas()
plotName = 'fit'

# workspace and the main variable
work = ROOT.RooWorkspace('work', 'work')
phi = work.factory('phi[%f,%f]' % (-math.pi * 0.5, math.pi * 0.5))
phiset = ROOT.RooArgSet(phi)

# trees for templates
haloTree = ROOT.TChain('events')
for sample in targs:
    haloTree.Add(config.skimDir + '/' + sample.name + '_haloNoShowerCut.root')
haloTree.SetEstimate(haloTree.GetEntries() + 1)

mcTree = ROOT.TChain('events')
mcTree.Add(config.skimDir + '/znng-130-o_monoph.root')

### Raw phi distributions

# Halo
haloTree.Draw('photons.phi_[0]>>haloTemp(40,-{pi},{pi})'.format(pi = math.pi), candSelection, 'goff')

haloTemp = ROOT.gDirectory.Get('haloTemp')
haloTemp.SetLineColor(ROOT.kBlack)
haloTemp.SetLineWidth(2)
haloTemp.SetTitle(';#phi\'')

canvas.lumi = dataLumi
canvas.addHistogram(haloTemp)
canvas.xtitle = '#phi\''
canvas.printWeb('monophoton/halo', 'haloTemp', logy = False)
canvas.Clear()

# MC
mcTree.Draw('photons.phi_[0]>>mcTemp(40,-{pi},{pi})'.format(pi = math.pi), candSelection, 'goff')

mcTemp = ROOT.gDirectory.Get('mcTemp')
mcTemp.SetLineColor(ROOT.kBlack)
mcTemp.SetLineWidth(2)
mcTemp.SetTitle(';#phi\'')

canvas.lumi = -1.
canvas.sim = True
canvas.addHistogram(mcTemp)
canvas.printWeb('monophoton/halo', 'mcTemp', logy = False, ymax = 1200.)
canvas.Clear()

canvas.sim = False

### Fit to halo distribution and parametrize

# first get the halo phi values
nHalo = haloTree.Draw(phivar + '>>haloTemp(40,-{pi2},{pi2})'.format(pi2 = math.pi * 0.5), candSelection, 'goff')
print nHalo, 'halo events'

haloTemp = ROOT.gDirectory.Get('haloTemp')
haloTemp.SetLineColor(ROOT.kBlack)
haloTemp.SetLineWidth(2)
haloTemp.SetTitle(';#phi\'')

canvas.addHistogram(haloTemp)
canvas.xtitle = '#phi\''
canvas.printWeb('monophoton/halo', 'phiHaloFolded', logy = False)
canvas.Clear()

# dump them into a RooDataSet
haloData = ROOT.RooDataSet('halo', 'halo', phiset)
haloPhi = haloTree.GetV1()
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

if TEMPLATEONLY:
    sys.exit(0)

# NOW WE DO THE HALO EXTRACTION FIT

canvas.lumi = dataLumi

# fix the halo template parameters
leaves = ROOT.RooArgSet()
haloModel.leafNodeServerList(leaves)
litr = leaves.fwdIterator()
while True:
    leaf = litr.next()
    if not leaf:
        break

    leaf.setConstant(True)

# fit with halo + uniform
uniform = work.factory('Uniform::uniform({phi})')
model = work.factory('SUM::model(nhalo[0.5,0.,1000.]*haloModel, nuniform[1000.,0.,1000.]*uniform)')

if FITPSEUDODATA:
    nTarg = 400. * dataLumi / 12900.
    nHalo = 5.5 * dataLumi / 12900.

    work.arg('nhalo').setVal(nHalo)
    work.arg('nuniform').setVal(nTarg - nHalo)

    targData = model.generate(phiset, nTarg)

else:
    candTree = ROOT.TChain('events')
    for sample in targs:
        candTree.Add(config.skimDir + '/' + sample.name + '_monoph.root')
    candTree.SetEstimate(candTree.GetEntries() + 1)

    ### Fit to candidates
    
    # candidate phi values
    nTarg = candTree.Draw(phivar, candSelection, 'goff')
    print nTarg, 'target events'
    
    # dump into a RooDataSet
    targData = ROOT.RooDataSet('targ', 'targ', phiset)
    targPhi = candTree.GetV1()
    for iTarg in range(nTarg):
        phi.setVal(targPhi[iTarg])
        targData.add(phiset)

work.arg('nhalo').setMax(nTarg * 1.1)
work.arg('nuniform').setMax(nTarg * 1.1)
work.arg('nuniform').setVal(nTarg)

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

if not FITPSEUDODATA:
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
