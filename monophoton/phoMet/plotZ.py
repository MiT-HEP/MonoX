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
metCut = 't1Met.met > 50.'
dPhiMetCut = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi)) < 0.5'
jetPtCut = 'jets.pt[0] > 100.'
dPhiJetCut = 't1Met.minJetDPhi > 0.5'
njetsCut = 'jets.size == 1'

variables = [ VariableDef('Met', 'E_{T}^{miss}', 't1Met.met', [10 * x for x in range(0, 10)] + [100 + 20 * x for x in range(0,5)] + [200, 250, 300], unit = 'GeV', overflow = True),
              VariableDef('dPhi', '#Delta#phi(Z, jet)', 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi))', (15, 0., math.pi) ),
              VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, jet)', 'TMath::Abs(TVector2::Phi_mpi_pi(t1Met.phi - jets.phi))', (15, 0., math.pi) ),
              VariableDef('dPhiZMet', '#Delta#phi(Z, E_{T}^{miss})', 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi))', (15, 0., math.pi) ),
              VariableDef('jetEta', '|#eta_{j}|', 'TMath::Abs(jets.eta[0])', (10, 0., 5.), applyFullSel = True),
              # VariableDef('njets', 'N_{jets}', 'jets.size', (6, 0., 6.), applyFullSel = True),
              VariableDef('minDPhiJetMet', 'min #Delta#phi(jet, E_{T}^{miss})', 't1Met.minJetDPhi', (15, 0., math.pi))
              ]

cuts = [ dPhiCut, metCut, zMassCut, njetsCut ]

zSignCuts = [ ('os', 'z.oppSign == 1'), ('ss', 'z.oppSign == 0') ]

skims = [ 'zmumu_smu', 'zee_sel', 'z*_s*' ]

for skim in skims:
    dataTree = r.TChain('skim')
    dataTree.Add('/scratch5/ballen/hist/monophoton/phoMet/'+skim+'-*.root')
    print dataTree.GetEntries()
    
    for sign, cut in zSignCuts[:1]:
        signCuts = cuts + [cut]

        for varDef in variables:
            if varDef.applyFullSel:
                varCuts = signCuts + [ dPhiMetCut ]
            else:
                varCuts = signCuts

            cutString = ' && '.join(['(%s)' % c for c in varCuts])
            print cutString

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

            canvas.printWeb('monophoton/phoMet/'+skim, sign+'_monojet30_'+varDef.name, logy = False)
