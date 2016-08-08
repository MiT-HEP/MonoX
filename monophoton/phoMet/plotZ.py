#!/usr/bin/env python
import sys
import os
import math
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import DataMCCanvas
from datasets import allsamples
from main.plotconfig import VariableDef
import config

import ROOT as r
r.gROOT.SetBatch(True)

lumi = min(config.jsonLumi, allsamples['smu-16b2-d'].lumi + allsamples['smu-16c2-d'].lumi + allsamples['smu-16d2-d'].lumi)
canvas = DataMCCanvas(lumi = lumi)

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

baseCuts = [ dPhiCut, metCut, zMassCut ]

zSignCuts = [ ('os', 'z.oppSign == 1'), ('ss', 'z.oppSign == 0') ]

jetsCuts = [ ('monojet30', [njetsCut]),
            ('monojet100', [njetsCut, jetPtCut]),
            ('multijet', [jetPtCut]),
            ('multijetdPhiCut', [jetPtCut, dPhiJetCut])
            ]

skims = [ 'smu-16*2-d_zmmJets', 'sel-16*2-d_zeeJets', 's*-16*2-d_z*Jets' ]

samples = [ ('zllg', r.TColor.GetColor(0xff, 0x99, 0x33)), 
            ('ttg', r.TColor.GetColor(0xbb, 0xaa, 0xff)), 
            ('wglo', r.TColor.GetColor(0x99, 0xee, 0xff)),
            ('wlnu-', r.TColor.GetColor(0xff, 0xee, 0x99)), 
            ('tt', r.TColor.GetColor(0xff, 0xaa, 0xcc)),
            ('dy-50-', r.TColor.GetColor(0x99, 0xff, 0xaa)) 
            ]


for skim in skims:
    dataTree = r.TChain('events')
    dataTree.Add(config.skimDir+'/'+skim+'.root')
    print dataTree.GetEntries()

    skimm = skim.split('_')[1]

    mcTrees = []
    for sample, color in samples:
        mcTree = r.TChain('events')
        mcTree.Add(config.skimDir+'/'+sample+'*_'+skimm+'.root')
        mcTrees.append( (sample, color, mcTree) )

    for jetsCut in jetsCuts:
        cuts = baseCuts + jetsCut[1]
            
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

                dataCutString = cutString + ' && !(run > %s)' % config.runCutOff

                dataTree.Draw(varDef.expr+'>>'+varDef.name+'-'+dataName, 'weight * ('+cutString+')', 'goff')
                print dataHist.Integral()
                canvas.addObs(dataHist, title = 'Data '+skimm)

                for sample, color, mcTree in mcTrees:
                    mcName = sample+skimm
                    mcHist = varDef.makeHist(mcName)
                    mcTree.Draw(varDef.expr+'>>'+varDef.name+'-'+mcName, str(lumi)+' * weight * ('+cutString+')', 'goff')
                    canvas.addStacked(mcHist, title = sample, color = color)

                # canvas.ylimits = (0.001, -1.)
                canvas.xtitle = varDef.title
                canvas.ytitle = 'Events'

                canvas.printWeb('monophoton/phoMet/'+skim, sign+'_'+jetsCut[0]+'_'+varDef.name, logy = True)
