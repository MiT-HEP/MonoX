#!/usr/bin/env python
import sys
import os
import math
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import SimpleCanvas
from datasets import allsamples
from main.plotconfig import VariableDef

import ROOT as r
r.gROOT.SetBatch(True)

lumi = allsamples['sel-d3'].lumi + allsamples['sel-d4'].lumi
canvas = SimpleCanvas(lumi = lumi)

probePixel = '!probe.pixelVeto'
zMassCut = 'z.mass > 81. && z.mass < 101.'
dPhiCut = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi[0])) > 3.'
metCut = 't1Met.met > 75.'

variables = [ VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [10 * x for x in range(0, 10)] + [100 + 20 * x for x in range(0,5)] + [200, 250, 300], unit = 'GeV', overflow = True),
              VariableDef('dPhi', '#Delta#phi(Z, jet)', 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi[0]))', (30, 0., math.pi) ),
              VariableDef('dPhiZMet', '#Delta#phi(Z, E_{T}^{miss})', 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi))', (30, 0., math.pi) )
              ]

cuts = [ dPhiCut, metCut, zMassCut ]

skims = [ 'zmumu_smu', 'zee_sel', 'zee_sph' ]

for skim in skims:
    dataTree = r.TChain('skim')
    dataTree.Add('/scratch5/ballen/hist/monophoton/phoMet/'+skim+'-*.root')
    print dataTree.GetEntries()

    cutString = ' && '.join(['(%s)' % c for c in cuts])
    print cutString

    for varDef in variables:
        canvas.Clear()
        canvas.legend.Clear()
        canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

        dataName = 'dataHist'+skim
        dataHist = varDef.makeHist(dataName)

        if varDef.unit != '':
            dataHist.GetXaxis().SetTitle(varDef.title + ' (' + varDef.unit +')')
        else:
            dataHist.GetXaxis().SetTitle(varDef.title)

        dataTree.Draw(varDef.expr+'>>'+varDef.name+'-'+dataName, 'weight * ('+cutString+')', 'goff')
        print dataHist.Integral()

        canvas.legend.add('data', title = 'Data '+skim, mcolor = r.kBlack, lcolor = r.kBlack, lwidth = 1)
        canvas.legend.apply('data', dataHist)
        canvas.addHistogram(dataHist, drawOpt = 'EP')

        canvas.ylimits = (0.001, -1.)

        canvas.printWeb('monophoton/phoMet', skim+'_'+varDef.name, logy = False)
