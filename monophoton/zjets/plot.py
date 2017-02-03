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


smuLumi = sum(allsamples[s].lumi for s in ['smu-16b-r', 'smu-16c-r', 'smu-16d-r', 'smu-16e-r', 'smu-16f-r', 'smu-16g-r', 'smu-16h'])
canvas = DataMCCanvas(lumi = smuLumi)

probePixel = '!probe.pixelVeto'
zMassCut = 'z.mass > 81. && z.mass < 101.'
dPhiCut = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi[0])) > 3.'
dPhiMetCut = 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi)) < 0.5'
jetPtCut = 'jets.pt[0] > 100.'
dPhiJetCut = 't1Met.minJetDPhi > 0.5'
monojetCut = 'jets.size == 1'
njetsCut = 'jets.size < 3'

variables = [ VariableDef('met', 'E_{T}^{miss}', 't1Met.met', [25 * x for x in range(2, 4)] + [100 + 50 * x for x in range(0, 8)], unit = 'GeV', overflow = True, logy = True),
              VariableDef('dPhi', '#Delta#phi(Z, jet)', 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - jets.phi))', (15, 0., math.pi) ),
              VariableDef('dPhiJetMet', '#Delta#phi(E_{T}^{miss}, jet)', 'TMath::Abs(TVector2::Phi_mpi_pi(t1Met.phi - jets.phi))', (15, 0., math.pi) ),
              VariableDef('dPhiZMet', '#Delta#phi(Z, E_{T}^{miss})', 'TMath::Abs(TVector2::Phi_mpi_pi(z.phi - t1Met.phi))', (15, 0., math.pi) ),
              VariableDef('jetPt', 'p_{T}^{j}', 'jets.pt[0]', (20, 0., 1000.), unit = 'GeV', applyFullSel = True, logy = True),
              VariableDef('jetEta', '#eta_{j}', 'jets.eta[0]', (10, -5., 5.), applyFullSel = True),
              VariableDef('jetPhi', '#phi_{j}', 'jets.phi[0]', (10, -math.pi, math.pi), applyFullSel = True),
              VariableDef('tagPt', 'p_{T}^{tag}', 'tag.pt[0]', (20, 0., 200.), unit = 'GeV', applyFullSel = True),
              VariableDef('tagEta', '#eta_{tag}', 'tag.eta[0]', (10, -2.5, 2.5), applyFullSel = True),
              VariableDef('tagPhi', '#phi_{tag}', 'tag.phi[0]', (10, -math.pi, math.pi), applyFullSel = True),
              VariableDef('probePt', 'p_{T}^{probe}', 'probe.pt[0]', (10, 0., 100.), unit = 'GeV', applyFullSel = True),
              VariableDef('probeEta', '#eta_{probe}', 'probe.eta[0]', (10, -2.5, 2.5), applyFullSel = True),
              VariableDef('probePhi', '#phi_{probe}', 'probe.phi[0]', (10, -math.pi, math.pi), applyFullSel = True),
              VariableDef('metPhi', '#phi_{E_{T}^{miss}}', 't1Met.phi', (10, -math.pi, math.pi), applyFullSel = True),
              VariableDef('zPt', 'p_{T}^{Z}', 'z.pt[0]', (20, 0., 1000.), unit = 'GeV', applyFullSel = True, logy = True),
              VariableDef('zEta', '#eta_{Z}', 'z.eta[0]', (10, -5., 5.), applyFullSel = True),
              VariableDef('zPhi', '#phi_{Z}', 'z.phi[0]', (10, -math.pi, math.pi), applyFullSel = True),
              VariableDef('zMass', 'm_{Z}', 'z.mass[0]', (10, 81., 101.), unit = 'GeV', applyFullSel = True)
              # VariableDef('njets', 'N_{jets}', 'jets.size', (6, 0., 6.), applyFullSel = True),
              # VariableDef('minDPhiJetMet', 'min #Delta#phi(jet, E_{T}^{miss})', 't1Met.minJetDPhi', (15, 0., math.pi))
              ]

baseCuts = [ dPhiCut, zMassCut ]

zSignCuts = [ ('os', 'z.oppSign == 1'), ('ss', 'z.oppSign == 0') ]

jetsCuts = [ # ('monojet30', [monojetCut]),
            ('monojet100', [monojetCut, jetPtCut]),
            # ('multijet', [jetPtCut]),
            # ('multijetdPhiCut', [jetPtCut, dPhiJetCut])
            ]

metValues = [ '050' ] # , '075', '100', '125', '150' ] #

skims = [ 'smu-16*_zmmJets', 'sel-16*_zeeJets' ] # , 's*-16*2-d_z*Jets' ]

samples = [ # ('qcd', ['qcd-200', 'qcd-300', 'qcd-500', 'qcd-700', 'qcd-1000', 'qcd-1500', 'qcd-2000'], r.TColor.GetColor(0xff, 0xaa, 0xcc)),
            ('w+jets', ['wlnu-100', 'wlnu-200', 'wlnu-400', 'wlnu-800', 'wlnu-1200', 'wlnu-2500'], r.TColor.GetColor(0xff, 0x44, 0x99)),
            ('diboson', ['ww', 'wz', 'zz'], r.TColor.GetColor(0xff, 0xee, 0x99)), 
            ('tt', ['tt'], r.TColor.GetColor(0x55, 0x44, 0xff)),
            ('z+jets', ['dy-50-100', 'dy-50-200', 'dy-50-400', 'dy-50-600', 'dy-50-800', 'dy-50-1200', 'dy-50-2500'], r.TColor.GetColor(0x99, 0xff, 0xaa)) 
            ]


for skim in skims:
    dataTree = r.TChain('events')
    dataTree.Add(config.skimDir+'/'+skim+'.root')
    print dataTree.GetEntries()

    skimm = skim.split('_')[1]

    mcTrees = []
    for group, slist, color in samples:
        mcTree = r.TChain('events')
        for sample in slist:
            mcTree.Add(config.skimDir+'/'+sample+'_'+skimm+'.root')
        mcTrees.append( (group, color, mcTree) )

    for metValue in metValues:
        metCut = 't1Met.met > '+metValue
        metCuts = baseCuts + [metCut]

        for jetsCut in jetsCuts:
            jetCuts = metCuts + jetsCut[1]

            for sign, cut in zSignCuts[:1]:
                signCuts = jetCuts + [cut]

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
                    canvas.addObs(dataHist, title = 'Data '+skimm)

                    for sample, color, mcTree in mcTrees:
                        mcName = sample+skimm
                        mcHist = varDef.makeHist(mcName)
                        mcTree.Draw(varDef.expr+'>>'+varDef.name+'-'+mcName, str(smuLumi)+' * weight * ('+cutString+')', 'goff')
                        canvas.addStacked(mcHist, title = sample, color = color)

                    # canvas.ylimits = (0.001, -1.)
                    canvas.xtitle = varDef.title
                    canvas.ytitle = 'Events'

                    if varDef.logy is None:
                        logy = False
                    else:
                        logy = varDef.logy

                    canvas.printWeb('monophoton/zjets/'+skim, skimm[:3]+'_'+jetsCut[0]+'_Met'+metValue+'_'+varDef.name, logy = logy)
