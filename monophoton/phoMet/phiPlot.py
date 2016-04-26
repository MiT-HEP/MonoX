#!/usr/bin/env python
import sys
import os
import math
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import DataMCCanvas, SimpleCanvas
from datasets import allsamples
from main.plotconfig import VariableDef

import ROOT as r
r.gROOT.SetBatch(True)

def ColorGrad():
    ncontours = 999
    stops = (0.0,1.0)
    red   = (1.0,0.0)
    green = (1.0,0.0)
    blue  = (1.0,1.0)
    
    sa = array.array('d', stops)
    ra = array.array('d', red)
    ga = array.array('d', green)
    ba = array.array('d', blue)

    npoints = len(sa)
    r.TColor.CreateGradientColorTable(npoints, sa, ra, ga, ba, ncontours)
    r.gStyle.SetNumberContours(ncontours)
    r.gStyle.SetPaintTextFormat(".0f")

dataTree = r.TChain('skim')
dataTree.Add('/scratch5/ballen/hist/monophoton/phoMet/phi_sph-*.root')
# dataTree.Add('/scratch5/ballen/hist/monophoton/phoMet/phi_sel-*.root')

samples = [ ('dy-50', r.TColor.GetColor(0x99, 0xee, 0xff)), 
            ('gj', r.TColor.GetColor(0xff, 0xaa, 0xcc))
            ]

mcTrees = []
for sample, color in samples:
    mcTree = r.TChain('skim')
    mcTree.Add('/scratch5/ballen/hist/monophoton/phoMet/phi_'+sample+'*.root')
    mcTrees.append( (sample, color, mcTree) )

lumi = allsamples['sph-d3'].lumi + allsamples['sph-d4'].lumi
# canvas = DataMCCanvas(lumi = lumi)
canvas = SimpleCanvas(lumi = lumi)

probeEtaCuts = [ ('TMath::Abs(probe.eta) < 0.8', 'low'), ('TMath::Abs(probe.eta > 0.8)', 'high') ] 
recoilCuts = [ ('recoil.pt > %i.' % pt, 'recoil'+str(pt)) for pt in [170, 200, 250, 300, 400] ]
probeObjectCuts = [ ('probe.isPhoton && probe.pixelVeto && tag.pixelVeto', 'diphoton'), 
                    ('probe.isPhoton && !probe.pixelVeto && !tag.pixelVeto', 'dielectron'), 
                    ('tag.pixelVeto && !probe.isPhoton', 'gammajet') ]

njetsCut = 'njets < 2'
tagEtaCut = 'TMath::Abs(tag.eta) < 0.2'

metCut = 't1Met.met > 100.'
dPhiCut = 'TMath::Abs(TVector2::Phi_mpi_pi(tag.phi - probe.phi)) > 3.'
unbalancedCut = 'TMath::Abs(probe.pt - tag.pt) > 150'
probeLooseCut = 'probe.loose == 1'
probeNhIsoCut = 'probe.nhIso < 1.06'

cuts = [ dPhiCut, probeLooseCut ]

variables = [ VariableDef('ptDiff', '|p_{T}^{tag} - p_{T}^{probe}|', 'TMath::Abs(probe.pt - tag.pt)', (20, 0., 500.), unit = 'GeV'),
              VariableDef('ptDiffOverMet', '|p_{T}^{tag} - p_{T}^{probe}| / E_T^{miss}', 'TMath::Abs(probe.pt - tag.pt) / t1Met.met', (50, 0., 5.), cut = metCut),
              VariableDef('met', 'E_{T}^{miss}', 't1Met.met', (20, 0., 500.), unit = 'GeV'),
              VariableDef('metLargePtDiff', 'E_{T}^{miss}', 't1Met.met', (20, 0., 500.), unit = 'GeV', cut = unbalancedCut),
              VariableDef('dPhiMetTag', '#Delta#phi(E_{T}^{miss}, tag)', 'TMath::Abs(TVector2::Phi_mpi_pi(tag.phi - t1Met.phi))', (30, 0., math.pi)),
              VariableDef('dPhiMetTagLargePtDiff', '#Delta#phi(E_{T}^{miss}, tag)', 'TMath::Abs(TVector2::Phi_mpi_pi(tag.phi - t1Met.phi))', (30, 0., math.pi), cut = unbalancedCut),
              VariableDef('dPhiMetProbe', '#Delta#phi(E_{T}^{miss}, probe)', 'TMath::Abs(TVector2::Phi_mpi_pi(probe.phi - t1Met.phi))', (30, 0., math.pi)),
              VariableDef('dPhiMetProbeLargePtDiff', '#Delta#phi(E_{T}^{miss}, probe)', 'TMath::Abs(TVector2::Phi_mpi_pi(probe.phi - t1Met.phi))', (30, 0., math.pi), cut = unbalancedCut),
              VariableDef('njets', '# of jets', 'njets', (8, 0., 8.)),
              VariableDef('njetsLargePtDiff', '# of jets', 'njets', (8, 0., 8.), cut = unbalancedCut),
              # VariableDef('tagPixelVeto', 'Tag Pixel Veto', 'tag.pixelVeto', (2, 0., 2.)),
              # VariableDef('probePixelVeto', 'Probe Pixel Veto', 'probe.pixelVeto', (2, 0., 2.)),
              # VariableDef('probeIsPhoton', 'Probe Is Photon', 'probe.isPhoton', (2, 0., 2.))
              ]
vars2D = [ ('ratioVsMinDPhi', ''),
           ('ratioVsMinDPhiLargePtDiff', unbalancedCut),
           ('ratioVsMinDPhiMet100', 't1Met.met > 100.'),
           ('ratioVsMinDPhiMet100LargePtDiff', 't1Met.met > 100. && '+unbalancedCut)
           ]


for probeCut in probeObjectCuts:
    probeCuts = list(cuts) + [probeCut[0]]
    
    for varDef in variables:
        allCuts = list(probeCuts)
        if varDef.cut != '':
            allCuts.append(varDef.cut)
            
        cutString = ' && '.join(['(%s)' % c for c in allCuts])
        print cutString
            
        label = varDef.name+'_'+probeCut[1]
            
        canvas.Clear()
        canvas.legend.Clear()
        canvas.legend.setPosition(0.1, 0.7, 0.9, 0.9)

        dataName = 'data_'+probeCut[1]
        dataHist = varDef.makeHist(dataName)
        if varDef.unit != '':
            dataHist.GetXaxis().SetTitle(varDef.title + ' (' + varDef.unit +')')
        else:
            dataHist.GetXaxis().SetTitle(varDef.title)
        dataTree.Draw(varDef.expr+'>>'+varDef.name+'-'+dataName, 'weight * ('+cutString+')')
        # canvas.addObs(dataHist, title = 'Data')
        canvas.legend.add('data', title = '#Delta#phi(tag,probe) > 3. && '+varDef.cut, mcolor = r.kBlack, lcolor = r.kBlack, lwidth = 1)
        canvas.legend.apply('data', dataHist)
        canvas.addHistogram(dataHist, drawOpt = 'EP')

        # sys.stdin.readline()
        """
        for sample, color, mcTree in mcTrees:
            mcName = sample+'_'+label
            mcHist = varDef.makeHist(mcName)
            mcTree.Draw(varDef.expr+'>>'+mcName, str(lumi)+' * weight * ('+cutString+')')

            canvas.addStacked(mcHist, title = sample, color = color)
        """
        
        canvas.ylimits = (0.5, -1.)

        canvas.printWeb('monophoton/phoMet/'+probeCut[1], label, logy = False)

    for var in vars2D:
        allCuts = list(probeCuts)
        if var[1] != '':
            allCuts.append(var[1])
            
        cutString = ' && '.join(['(%s)' % c for c in allCuts])
        print cutString
            
        label = var[0]+'_'+probeCut[1]

        canvas.Clear(xmax = 0.90)
        canvas.legend.Clear()
        canvas.legend.setPosition(0.1, 0.7, 0.9, 0.9)

        xString = "TMath::Min( TMath::Abs(TVector2::Phi_mpi_pi(t1Met.phi - tag.phi)), TMath::Abs(TVector2::Phi_mpi_pi(t1Met.phi - probe.phi)))"
        yString = "( TMath::Abs( tag.pt - probe.pt ) / t1Met.met )"

        dataHist = r.TH2D(label, "", 30, 0., math.pi, 12, 0., 2.4)
        dataHist.GetXaxis().SetTitle('min(#Delta#phi(tag, E_{T}^{miss}), #Delta#phi(probe, E_{T}^{miss}))')
        dataHist.GetYaxis().SetTitle('|(p_{T}^{tag} - p_{T}^{probe}) / E_{T}^{miss}|')
        dataHist.Sumw2()
        dataTree.Draw(yString+":"+xString+">>"+label, cutString, 'goff')

        # canvas.legend.add('data', title = '#Delta#phi(tag,probe) > 3. && '+var[1], mcolor = r.kBlue, lcolor = r.kBlue, lwidth = 1)

        ColorGrad()
        canvas.addHistogram(dataHist, drawOpt = 'COLZ TEXT')
        canvas.printWeb('monophoton/phoMet/'+probeCut[1], label, logy = False)
