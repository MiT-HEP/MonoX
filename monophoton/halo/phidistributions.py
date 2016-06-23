import os
import sys
sys.dont_write_bytecode = True
import math
import array
import ROOT
ROOT.gROOT.SetBatch(True)

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

from datasets import allsamples
from plotstyle import SimpleCanvas
import config

selection = '{sel} && photons.pt > 175. && t1Met.met > 140.'

def makeFullPlot(tree, name, sel):
    plot = ROOT.TH1D(name, ";#phi'", 40, -math.pi, math.pi)
    plot.Sumw2()
    plot.SetLineColor(ROOT.kBlack)
    plot.SetLineWidth(2)
    tree.Draw('TVector2::Phi_mpi_pi(photons.phi + 0.005)>>' + name, selection.format(sel = sel), 'goff')

    return plot

def makeFoldedPlot(tree, name, sel):
    plot = ROOT.TH1D(name, ";#phi''", 6, -math.pi * 0.5, math.pi * 0.5)
    plot.Sumw2()
    plot.SetLineColor(ROOT.kBlack)
    plot.SetLineWidth(2)
    tree.Draw('TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(photons.phi + 0.005) - 1.570796)) - 1.570796>>' + name, selection.format(sel = sel), 'goff')

    return plot

canvas = SimpleCanvas()
canvas.legend.setPosition(0.4, 0.7, 0.92, 0.92)
canvas.legend.SetTextSize(0.03)

outputFile = ROOT.TFile.Open(config.histDir + '/halo/phidistributions.root', 'recreate')

sph = allsamples['sph-16b2']
znng = allsamples['znng-130']

dataTree = ROOT.TChain('events')
dataTree.Add(config.photonSkimDir + '/sph-16b2.root')

dataTreeAll = ROOT.TChain('events')
dataTreeAll.Add(config.ntuplesDir + '/' + sph.book + '/' + sph.directory + '/*.root')

znngTree = ROOT.TChain('events')
znngTree.Add(config.photonSkimDir + '/znng-130.root')

## halo EB

phiHalo = makeFullPlot(dataTree, 'phiHalo', 'photons.mipEnergy > 4.9 && photons.isEB')
phiHalo.SetDirectory(outputFile)
outputFile.cd()
phiHalo.Write()

canvas.ylimits = (0., phiHalo.GetMaximum() * 1.5)

canvas.addHistogram(phiHalo)
canvas.printWeb('monophoton/halo', 'phiHalo', logy = False)

canvas.Clear()

phiHalo = makeFoldedPlot(dataTree, 'phiHalo', 'photons.mipEnergy > 4.9 && photons.isEB')
phiHalo.SetDirectory(outputFile)
outputFile.cd()
phiHalo.Write()

canvas.ylimits = (0., phiHalo.GetMaximum() * 1.5)

canvas.addHistogram(phiHalo)
canvas.printWeb('monophoton/halo', 'phiHaloFolded', logy = False)

canvas.Clear()

## halo EE

phiHaloEE = makeFullPlot(dataTreeAll, 'phiHalo', '!photons.isEB')
phiHaloEE.SetDirectory(outputFile)
outputFile.cd()
phiHaloEE.Write()

canvas.ylimits = (0., phiHaloEE.GetMaximum() * 1.5)

canvas.addHistogram(phiHaloEE)
canvas.printWeb('monophoton/halo', 'phiHaloEE', logy = False)

canvas.Clear()

# MIP tag

phiHaloEE = makeFullPlot(dataTreeAll, 'phiHalo', '!photons.isEB && photons.mipEnergy > 4.9')
phiHaloEE.SetDirectory(outputFile)
outputFile.cd()
phiHaloEE.Write()

canvas.ylimits = (0., phiHaloEE.GetMaximum() * 1.5)

canvas.addHistogram(phiHaloEE)
canvas.printWeb('monophoton/halo', 'phiHaloEEMIPtag', logy = False)

canvas.Clear()

## cand EB

phiCand = makeFullPlot(dataTree, 'phiHalo', 'photons.mipEnergy < 4.9 && photons.medium && photons.isEB')
phiCand.SetDirectory(outputFile)
outputFile.cd()
phiCand.Write()

canvas.ylimits = (0., phiCand.GetMaximum() * 1.5)

canvas.addHistogram(phiCand)
canvas.printWeb('monophoton/halo', 'phiCand', logy = False)

canvas.Clear()

phiCand = makeFoldedPlot(dataTree, 'phiHalo', 'photons.mipEnergy < 4.9 && photons.medium && photons.isEB')
phiCand.SetDirectory(outputFile)
outputFile.cd()
phiCand.Write()

canvas.ylimits = (0., phiCand.GetMaximum() * 1.5)

canvas.addHistogram(phiCand)
canvas.printWeb('monophoton/halo', 'phiCandFolded', logy = False)

canvas.Clear()

## znng EB

phiZnng = makeFullPlot(znngTree, 'phiHalo', 'photons.mipEnergy < 4.9 && photons.medium && photons.isEB')
phiZnng.SetDirectory(outputFile)
outputFile.cd()
phiZnng.Write()

canvas.ylimits = (0., phiZnng.GetMaximum() * 1.5)

canvas.addHistogram(phiZnng)
canvas.printWeb('monophoton/halo', 'phiZnng', logy = False)

canvas.Clear()

phiZnng = makeFoldedPlot(znngTree, 'phiHalo', 'photons.mipEnergy < 4.9 && photons.medium && photons.isEB')
phiZnng.SetDirectory(outputFile)
outputFile.cd()
phiZnng.Write()

canvas.ylimits = (0., phiZnng.GetMaximum() * 1.5)

canvas.addHistogram(phiZnng)
canvas.printWeb('monophoton/halo', 'phiZnngFolded', logy = False)

canvas.Clear()
