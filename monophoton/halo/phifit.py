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

writePlot = True
nominalFit = True
toys = False
nToys = 1000

if writePlot:
    from plotstyle import SimpleCanvas
    canvas = SimpleCanvas()

work = ROOT.RooWorkspace('work', 'work')
phi = work.factory('phi[%f,%f]' % (-math.pi * 0.5, math.pi * 0.5))
phiset = ROOT.RooArgSet(phi)

dataTree = ROOT.TChain('events')
dataTree.Add(config.photonSkimDir + '/sph-16b2.root')
dataTree.SetEstimate(dataTree.GetEntries() + 1)

candTree = ROOT.TChain('events')
candTree.Add(config.skimDir + '/sph-16b2_monoph.root')
candTree.SetEstimate(candTree.GetEntries() + 1)

# fit to halo distribution and parametrize

nHalo = dataTree.Draw('TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(photons.phi + 0.005) - 1.570796)) - 1.570796', 'photons.mipEnergy > 4.9 && photons.isEB && photons.pt > 175. && t1Met.met > 140.', 'goff')

haloData = ROOT.RooDataSet('halo', 'halo', phiset)

print nHalo, 'halo events'
haloPhi = dataTree.GetV1()
for iHalo in range(nHalo):
    phi.setVal(haloPhi[iHalo])
    haloData.add(phiset)

base = work.factory('Uniform::base({phi})')
peak = work.factory('SUM::peak(p1[0.1,0.,1.]*Gaussian::peak1(phi, mean1[0.,-3.,3.], sigma1[0.1,0.,1.]),Gaussian::peak2(phi, mean2[0.,-3.,3.], sigma2[0.001,0.,0.1]))')
haloModel = work.factory('SUM::haloModel(fbase[0.1,0.,1.]*base, peak)')

haloModel.fitTo(haloData)

leaves = ROOT.RooArgSet()
haloModel.leafNodeServerList(leaves)
litr = leaves.fwdIterator()
while True:
    leaf = litr.next()
    if not leaf:
        break

    leaf.setConstant(True)

# fit to candidates

nTarg = candTree.Draw('TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(photons.phi + 0.005) - 1.570796)) - 1.570796', 'photons.pt[0] > 175. && t1Met.met > 170. && t1Met.minJetDPhi > 0.5 && t1Met.photonDPhi > 2.', 'goff')

targData = ROOT.RooDataSet('targ', 'targ', phiset)

print nTarg, 'target events'
targPhi = candTree.GetV1()
for iTarg in range(nTarg):
    phi.setVal(targPhi[iTarg])
    targData.add(phiset)

uniform = work.factory('Uniform::uniform({phi})')
model = work.factory('SUM::model(nhalo[0.5,0.,{maximum}]*haloModel, nuniform[{init},0.,{maximum}]*uniform)'.format(maximum = nTarg * 1.1, init = nTarg * 0.95))

if nominalFit:
    model.fitTo(targData)

    if writePlot:
        phi.setBins(20)
        frame = phi.frame()
        frame.SetTitle('')
        targData.plotOn(frame)
        model.plotOn(frame, ROOT.RooFit.LineColor(ROOT.kGreen))
        model.plotOn(frame, ROOT.RooFit.Components('uniform'), ROOT.RooFit.LineColor(ROOT.kBlue))

        canvas.Clear(full = True)

        canvas.legend.setPosition(0.7, 0.7, 0.9, 0.9)
        canvas.legend.add('fit', title = 'Fit result', lcolor = ROOT.kBlue, lwidth = 2, opt = 'L')
        canvas.legend.add('halo', title = 'Halo template', lcolor = ROOT.kGreen, lwidth = 1, opt = 'L')
        canvas.legend.add('obs', title = 'Data', mcolor = ROOT.kBlack, mstyle = 8, msize = 1, lcolor = ROOT.kBlack, lwidth = 1, opt = 'LP')

        canvas.addHistogram(frame)
        canvas.printWeb('monophoton/halo', 'fit', logy = False)

if toys:
    hypo = float(sys.argv[1])

    outfile = ROOT.TFile.Open('toys.root', 'recreate')
    ROOT.TObjString(str(hypo)).Write('hypothesis')

    toyTree = ROOT.TTree('toys', 'toys')
    a_nll = array.array('d', [0.])
    a_fhalo = array.array('d', [0.])
    toyTree.Branch('nll', a_nll, 'nll/D')
    toyTree.Branch('fhalo', a_fhalo, 'fhalo/D')

    # observed
    fhalo.setVal(hypo)
    nll = model.createNLL(targData).getVal()

    if writePlot:
        frame = phi.frame()
        targData.plotOn(frame)
        model.plotOn(frame)
        
        canvas.Clear(full = True)
        canvas.addHistogram(frame)
        canvas.printWeb('monophoton/halo', 'hypo', logy = False)

    fhalo.setVal(hypo / 2.)
    fhalo.setMax(hypo)
    result = model.fitTo(targData, ROOT.RooFit.Save(True))
#    print 'Obs NLL', nll, 'minNLL', result.minNll()
    obs = 2. * (nll - result.minNll())

    psig = 0.
#    pbkg = 0.

    hsig = ROOT.TH1D('hsig', '', 100, 0., 2.)
#    hbkg = ROOT.TH1D('hbkg', '', 100, 0., 2.)

    iToy = 0
    while iToy < nToys:
        iToy += 1

        fhalo.setVal(hypo)
        sigtoy = model.generate(phiset, nTarg)

        fhalo.setVal(hypo)
        nll = model.createNLL(sigtoy)
        signll = nll.getVal()

        fhalo.setVal(hypo / 2.)
        fhalo.setMax(hypo)
        result = model.fitTo(sigtoy, ROOT.RooFit.Verbose(False), ROOT.RooFit.PrintLevel(-1), ROOT.RooFit.Save(True))
#        print 'Toy', iToy, ' sig NLL', signll, 'minNLL', result.minNll()

        if writePlot and iToy == 1:
            frame = phi.frame()
            sigtoy.plotOn(frame)
            model.plotOn(frame)
            
            canvas.Clear(full = True)
            canvas.addHistogram(frame)
            canvas.printWeb('monophoton/halo', 'sigtoy', logy = False)

        sig = 2. * (signll - result.minNll())
        hsig.Fill(sig)

        if sig > obs:
            psig += 1.

        # now fit with no bound on fhalo
        fhalo.setMax(1.)
        model.fitTo(sigtoy, ROOT.RooFit.Verbose(False), ROOT.RooFit.PrintLevel(-1), ROOT.RooFit.Save(True))
#        print 'Toy', iToy, ' sig NLL', nll, 'minNLL', result.minNll()

        a_nll[0] = nll.getVal()
        a_fhalo[0] = fhalo.getVal()
        toyTree.Fill()

#        fhalo.setVal(0.)
#        bkgtoy = model.generate(phiset, nTarg)
#
#        fhalo.setVal(hypo)
#        nll = model.createNLL(bkgtoy).getVal()
#
#        fhalo.setVal(hypo / 2.)
#        result = model.fitTo(bkgtoy, ROOT.RooFit.Verbose(False), ROOT.RooFit.PrintLevel(-1), ROOT.RooFit.Save(True))
#        print 'Toy', iToy, ' bkg NLL', nll, 'minNLL', result.minNll()

#        bkg = 2. * (nll - result.minNll())
#        hbkg.Fill(bkg)

#        if bkg > obs:
#            pbkg += 1.

#        frame = phi.frame()
#        toydata.plotOn(frame)
#        model.plotOn(frame)
        
#        canvas.Clear(full = True)
#        canvas.addHistogram(frame)
#        canvas.printWeb('monophoton/halo', 'toy' + str(iToy), logy = False)

#    if pbkg != 0.:
#        cls = psig / pbkg
#    else:
#        cls = 'inf'

#    print hypo, psig / nToys, pbkg / nToys, cls
    print hypo, psig / nToys

    toyTree.Write()

    if writePlot:
#        hbkg.SetLineColor(ROOT.kRed)
    
        canvas.Clear(full = True)
        canvas.addHistogram(hsig)
#        canvas.addHistogram(hbkg)
        canvas.printWeb('monophoton/halo', 'pmu')
