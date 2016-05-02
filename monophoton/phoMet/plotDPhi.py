import os
import sys
import math
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config
from main.plotconfig import getConfig
from plotstyle import SimpleCanvas

import ROOT
ROOT.gROOT.SetBatch(True)

lumi = allsamples['sph-d3'].lumi + allsamples['sph-d4'].lumi
canvas =  SimpleCanvas(lumi = lumi)



samples = {'sph' : [ 'monoph', 'efake', 'hfake', 'halo', 'gjets'],
           'gj' : [ 'gjets' ],
           'qcd' : [ 'gjets' ], 
           'wlnu' : [ 'withel' ]
           }


for sample in samples:
    for region in samples[sample]:
        canvas.Clear()
        canvas.legend.Clear()
        canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)

        dataTree = ROOT.TChain('events')
        dataTree.Add('/scratch5/ballen/hist/monophoton/skim/'+sample+'-*_'+region+'.root')

        xString = "t1Met.photonDPhi"

        dataHist = ROOT.TH1D(sample+region, "", 30, 0., math.pi)
        dataHist.GetXaxis().SetTitle('#Delta#phi(#gamma, E_{T}^{miss})')
        dataHist.GetYaxis().SetTitle('Events / 0.10')
        dataHist.Sumw2()
        if sample == 'sph':
            dataTree.Draw(xString+">>"+sample+region, '(photons.pt[0] > 175. && t1Met.minJetDPhi > 0.5 && t1Met.met > 170.)', 'goff')
        else:
            dataTree.Draw(xString+">>"+sample+region, str(lumi)+'* weight * (photons.pt[0] > 175. && t1Met.minJetDPhi > 0.5 && t1Met.met > 170.)', 'goff')


        canvas.legend.add('data', title = sample+region, mcolor = ROOT.kRed, msize = 1, lcolor = ROOT.kRed, lwidth = 4)
        canvas.legend.apply('data', dataHist)
        canvas.addHistogram(dataHist, drawOpt = 'HIST')
        canvas.printWeb('monophoton/phoMet', 'dPhi'+'_'+sample+'_'+region, logy = False)


