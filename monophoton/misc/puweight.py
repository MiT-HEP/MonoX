import sys
import os
import imp
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

sample = allsamples['gj-400']

dataSource = ROOT.TFile.Open(sys.argv[1])
mcScenario = sys.argv[2]
outputFile = ROOT.TFile.Open(sys.argv[3], 'recreate')

# not the most proper way to import a module from a string, but who cares
exec('from SimGeneral.MixingModule.mix_' + mcScenario + '_cfi import mix')
npvs = mix.input.nbPileupEvents.probFunctionVariable.value() # list of integers
probs = mix.input.nbPileupEvents.probValue.value() # list of integers

mcProb = dict(zip(npvs, probs))

mcDist = ROOT.TH1D('mc', '', 1000, 0., 80.)

for bin in range(1, mcDist.GetNbinsX() + 1):
    npv = int(mcDist.GetXaxis().GetBinCenter(bin))
    try:
        mcDist.SetBinContent(bin, mcProb[npv])
    except KeyError:
        pass

mcDist.Scale(1. / mcDist.GetSumOfWeights())

dataDist = dataSource.Get('pileup').Clone('data')
dataDist.Sumw2()
dataDist.Scale(1. / dataDist.GetSumOfWeights())

dataDist.Write()
mcDist.Write()

puweight = dataDist.Clone('puweight')

puweight.Divide(mcDist)
puweight.Write()

outputFile.Close()
