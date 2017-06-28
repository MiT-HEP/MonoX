#!/usr/bin/env python

import sys
import os
sys.dont_write_bytecode = True
import math
import array
import shutil
import ROOT
ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

TEMPLATEONLY = False
FITPSEUDODATA = True

from datasets import allsamples
from plotstyle import SimpleCanvas
import config
import utils

ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)
ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')

targs = allsamples.getmany('sph-16*')
dataLumi = sum(s.lumi for s in targs)

### Canvas
from plotstyle import SimpleCanvas
canvas = SimpleCanvas()
canvas.lumi = dataLumi

### Make templates
# Visualization
def plotHist(hist):
    canvas.addHistogram(hist)
    canvas.xtitle = '#phi\''
    canvas.printWeb('monophoton/halo', hist.GetName(), logy = False)
    canvas.Clear()

outputFile = ROOT.TFile.Open(config.histDir + '/halo/phifit.root', 'recreate')

templates = {}
trees = {}

haloPlotter = ROOT.MultiDraw()
mcPlotter = ROOT.MultiDraw()
for sample in targs:
    haloPlotter.addInputPath(utils.getSkimPath(sample.name, 'halo'))

mcPlotter.addInputPath(utils.getSkimPath('znng-130-o', 'monoph'))
mcPlotter.setConstantWeight(dataLumi)

haloPlotter.setBaseSelection('photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.minJetDPhi > 0.5 && t1Met.photonDPhi > 2.')
mcPlotter.setBaseSelection('photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.minJetDPhi > 0.5 && t1Met.photonDPhi > 2.')

foldedPhi = 'TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(photons.phi_[0] + 0.005) - {halfpi})) - {halfpi}'.format(halfpi = math.pi * 0.5)

empty = ROOT.TH1D('empty', ';#phi\'', 40, -math.pi, math.pi)
empty.SetLineColor(ROOT.kBlack)
empty.SetLineWidth(2)

outputFile.cd()

plot = empty.Clone('mcTemp')
mcPlotter.addPlot(plot, foldedPhi)
templates['mcTemp'] = plot

mcPlotter.fillPlots()

plot = empty.Clone('haloTemp')
haloPlotter.addPlot(plot, foldedPhi, 'photons.mipEnergy[0] > 4.9 && metFilters.globalHalo16')
templates['haloTemp'] = plot

tree = ROOT.TTree('haloTempTree', 'halo')
haloPlotter.addTree(tree, 'photons.mipEnergy[0] > 4.9 && metFilters.globalHalo16')
haloPlotter.addTreeBranch(tree, 'phi', foldedPhi)
trees['haloTemp'] = tree

plot = empty.Clone('haloTempVar1')
haloPlotter.addPlot(plot, foldedPhi, 'photons.sieie[0] < 0.015 && photons.mipEnergy[0] > 4.9 && metFilters.globalHalo16')
templates['haloTempVar1'] = plot

tree = ROOT.TTree('haloTempVar1Tree', 'halo')
haloPlotter.addTree(tree, 'photons.sieie[0] < 0.015 && photons.mipEnergy[0] > 4.9 && metFilters.globalHalo16')
haloPlotter.addTreeBranch(tree, 'phi', foldedPhi)
trees['haloTempVar1'] = tree

plot = empty.Clone('haloTempVar2')
haloPlotter.addPlot(plot, foldedPhi, 'photons.sieie[0] > 0.015 && photons.mipEnergy[0] > 4.9 && metFilters.globalHalo16')
templates['haloTempVar2'] = plot

tree = ROOT.TTree('haloTempVar2Tree', 'halo')
haloPlotter.addTree(tree, 'photons.sieie[0] > 0.015 && photons.mipEnergy[0] > 4.9 && metFilters.globalHalo16')
haloPlotter.addTreeBranch(tree, 'phi', foldedPhi)
trees['haloTempVar2'] = tree

haloPlotter.fillPlots()

if not TEMPLATEONLY and not FITPSEUDODATA:
    candPlotter = ROOT.MultiDraw()
    for sample in targs:
        candPlotter.addInputPath(utils.getSkimPath(sample.name, 'monoph'))

    candPlotter.setBaseSelection('photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.minJetDPhi > 0.5 && t1Met.photonDPhi > 2.')

    plot = empty.Clone('cand')
    candPlotter.addPlot(plot, foldedPhi)
    templates['cand'] = plot

    tree = ROOT.TTree('candTree', 'halo')
    haloPlotter.addTree(tree)
    haloPlotter.addTreeBranch(tree, 'phi', foldedPhi)
    trees['cand'] = tree

    candPlotter.fillPlots()

for hist in templates.values():
    outputFile.cd()
    hist.Write()

    plotHist(hist)

### Halo template parametrization
# workspace and the main variable
work = ROOT.RooWorkspace('work', 'work')
phi = work.factory('phi[%f,%f]' % (-math.pi * 0.5, math.pi * 0.5))
phiset = ROOT.RooArgSet(phi)

# we use gaus + gaus + uniform
base = work.factory('Uniform::base({phi})')
peak = work.factory('SUM::peak(p1[0.1,0.,1.]*Gaussian::peak1(phi, mean1[0.,-3.,3.], sigma1[0.1,0.,1.]),Gaussian::peak2(phi, mean2[0.,-3.,3.], sigma2[0.001,0.,0.1]))')
haloModel = work.factory('SUM::haloModel(fbase[0.1,0.,1.]*base, peak)')

phi.setRange('low', -math.pi * 0.5, -0.5)
phi.setRange('mid', -0.5, 0.5)
phi.setRange('high', 0.5, math.pi * 0.5)

outint = haloModel.createIntegral(phiset, ROOT.RooFit.Range('low'), ROOT.RooFit.Range('high'))
inint = haloModel.createIntegral(phiset, ROOT.RooFit.Range('mid'))

# Visualization
def plotFit(data, name):
    frame = phi.frame()
    frame.SetTitle('')
    frame.GetXaxis().SetTitle('#phi\'')
    data.plotOn(frame)
    haloModel.plotOn(frame)
    canvas.addHistogram(frame)
    canvas.printWeb('monophoton/halo', 'tempfit_' + name, logy = False)
    canvas.Clear()

haloData = ROOT.RooDataSet('haloData', 'haloData', trees['haloTemp'], phiset)
haloModel.fitTo(haloData)
plotFit(haloData, 'nominal')

tf = outint.getVal() / inint.getVal()
print 'Out / In (|phi| <> 0.5) transfer factor:', tf

tfMin = tf
tfMax = tf

haloDataVar1 = ROOT.RooDataSet('haloDataVar1', 'haloData', trees['haloTempVar1'], phiset)
haloModel.fitTo(haloDataVar1)
plotFit(haloDataVar1, 'var1')

tf = outint.getVal() / inint.getVal()
if tf < tfMin:
    tfMin = tf
if tf > tfMax:
    tfMax = tf

haloDataVar2 = ROOT.RooDataSet('haloDataVar2', 'haloData', trees['haloTempVar2'], phiset)
haloModel.fitTo(haloDataVar2)
plotFit(haloDataVar2, 'var2')

tf = outint.getVal() / inint.getVal()
if tf < tfMin:
    tfMin = tf
if tf > tfMax:
    tfMax = tf

print 'Transfer factor uncertainty:', (tfMax - tfMin) * 0.5


if TEMPLATEONLY:
    sys.exit(0)

### Halo extraction fits

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

    fitName = 'toy'

else:
    targData = ROOT.RooDataSet('candData', 'candData', trees['cand'], phiset)

    fitName = 'data'

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
canvas.printWeb('monophoton/halo', 'fit_' + fitName, logy = False)

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
