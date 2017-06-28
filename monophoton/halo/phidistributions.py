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
import utils

ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')
ROOT.gSystem.Load(config.libobjs)
e = ROOT.panda.Event

plots = []

def addPlot(plotter, name, sel = ''):
    fullPlot = ROOT.TH1D(name + 'Full', ";#phi'", 40, -math.pi, math.pi)
    plots.append(fullPlot)
    fullPlot.Sumw2()
    fullPlot.SetLineColor(ROOT.kBlack)
    fullPlot.SetLineWidth(2)
    plotter.addPlot(fullPlot, 'TVector2::Phi_mpi_pi(photons.phi_[0] + 0.005)', sel)

    foldedPlot = ROOT.TH1D(name + 'Folded', ";#phi''", 15, 0., math.pi * 0.5)
    plots.append(foldedPlot)
    foldedPlot.Sumw2()
    foldedPlot.SetLineColor(ROOT.kBlack)
    foldedPlot.SetLineWidth(2)
    plotter.addPlot(foldedPlot, 'TMath::Abs(TMath::Abs(TVector2::Phi_mpi_pi(TVector2::Phi_mpi_pi(photons.phi_[0] + 0.005) - 1.570796)) - 1.570796)', sel)


outputFile = ROOT.TFile.Open(config.histDir + '/halo/phidistributions.root', 'recreate')

haloPlotter = ROOT.MultiDraw()
emjetPlotter = ROOT.MultiDraw()
mcPlotter = ROOT.MultiDraw()

for sample in allsamples.getmany('sph-16*'):
    haloPlotter.addInputPath(utils.getSkimPath(sample.name, 'halo'))
    emjetPlotter.addInputPath(utils.getSkimPath(sample.name, 'emjet'))

mcPlotter.addInputPath(utils.getSkimPath('znng-130-o', 'monoph'))

haloPlotter.setBaseSelection('t1Met.pt > 170.')
mcPlotter.setBaseSelection('t1Met.pt > 170.')

tune = 'panda::XPhoton::kGJetsCWIso'
ROOT.gROOT.ProcessLine('int itune = %s;' % tune)
itune = ROOT.itune

ROOT.gROOT.ProcessLine('double cutvalue;')
ROOT.gROOT.ProcessLine("cutvalue = panda::XPhoton::hOverECuts[%s][0][2];" % tune)
noniso = 'photons.hOverE[0] < %f' % ROOT.cutvalue
ROOT.gROOT.ProcessLine("cutvalue = panda::XPhoton::sieieCuts[%s][0][2];" % tune)
noniso += ' && photons.sieie[0] < %f' % ROOT.cutvalue
ROOT.gROOT.ProcessLine("cutvalue = panda::XPhoton::chIsoCuts[%s][0][2];" % tune)
noniso += ' && photons.chIsoMaxX[0][%d] < %f' % (itune, ROOT.cutvalue)
ROOT.gROOT.ProcessLine("cutvalue = panda::XPhoton::nhIsoCuts[%s][0][2];" % tune)
noniso += ' && (photons.nhIsoX[0][%d] > %f' % (itune, ROOT.cutvalue)
ROOT.gROOT.ProcessLine("cutvalue = panda::XPhoton::phIsoCuts[%s][0][2];" % tune)
noniso += ' || photons.phIsoX[0][%d] > %f)' % (itune, ROOT.cutvalue)

outputFile.cd()

addPlot(haloPlotter, 'phiHalo', 'photons.sieie[0] > 0.015 && photons.mipEnergy[0] > 4.9 && metFilters.globalHalo16')
addPlot(emjetPlotter, 'phiCand', noniso)
addPlot(mcPlotter, 'phiZnng')

haloPlotter.fillPlots()
emjetPlotter.fillPlots()
mcPlotter.fillPlots()

canvas = SimpleCanvas()
canvas.legend.setPosition(0.4, 0.7, 0.92, 0.92)
canvas.legend.SetTextSize(0.03)

for plot in plots:
    canvas.Clear()
    canvas.ylimits = (0., plot.GetMaximum() * 1.5)
    canvas.addHistogram(plot)
    canvas.printWeb('monophoton/halo', plot.GetName(), logy = False)
