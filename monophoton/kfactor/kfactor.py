### NOTE
### This is an updated version of the script that produces kfactors separately for W+gamma and W-gamma.
### As long as there is a file kfactor_signed.root in data, kfactor.root is made with the previous
### version of the script that mixed the signs.
### Once we are ready to switch to the signed version, we should replace kfactor.root with kfactor_signed.root
### and update selectors.py.

import sys
import os
import array
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

ROOT.gSystem.Load('libPandaTreeObjects.so')
e = ROOT.panda.Event

ROOT.gROOT.LoadMacro('makeZGWGHistograms.cc+')

outFile = ROOT.TFile.Open(basedir + '/data/kfactor.root', 'recreate')

# the input file from Grazzini has a 1000- bin but has the same cross section as 700-1000.
# guessing this means that the calculation was only up to 1000 GeV
binning = array.array('d', [175., 190., 250., 400., 700., 1000.])

## ZG LO histogram

sample = allsamples['znng-130-o']

tree = ROOT.TChain('events')
for fname in sample.files():
    tree.Add(fname)

zglo = ROOT.TH1D('zglo', '', len(binning) - 1, binning)

ROOT.makeZGWGHistograms(tree, zglo)

zglo.Scale(1000. * sample.crosssection / sample.sumw, 'width') # nnlo file given in dsigma / dpT (fb / GeV)

zglo.Write()

## WG LO histograms

sample = allsamples['wnlg-130-o']

tree = ROOT.TChain('events')
for fname in sample.files():
    tree.Add(fname)

wpglo = ROOT.TH1D('wpglo', '', len(binning) - 1, binning)
wmglo = ROOT.TH1D('wmglo', '', len(binning) - 1, binning)

ROOT.makeZGWGHistograms(tree, wpglo, wmglo)

wpglo.Scale(1000. * sample.crosssection / sample.sumw, 'width') # nnlo file given in dsigma / dpT (fb / GeV)
wmglo.Scale(1000. * sample.crosssection / sample.sumw, 'width') # nnlo file given in dsigma / dpT (fb / GeV)

zglo.Write()

## Start writing factors

print 'znng & zllg'

sname = 'znng-130-o'

outFile.cd()
kfactor = ROOT.TH1D(sname, '', len(binning) - 1, binning)
kfactorUp = ROOT.TH1D(sname + '_scaleUp', '', len(binning) - 1, binning)
kfactorDown = ROOT.TH1D(sname + '_scaleDown', '', len(binning) - 1, binning)

with open(basedir + '/data/raw/znng_grazzini.dat') as source:
    source.readline()
    iX = 1
    for line in source:
        words = line.split()
        kfactor.SetBinContent(iX, float(words[1]) * 3.) # three neutrino flavors
        kfactorDown.SetBinContent(iX, float(words[3]) * 3.)
        kfactorUp.SetBinContent(iX, float(words[5]) * 3.)

        if iX == zglo.GetNbinsX():
            break

        iX += 1

kfactor.Divide(zglo)
kfactorUp.Divide(zglo)
kfactorDown.Divide(zglo)

kfactor.Write()
kfactorUp.Write()
kfactorDown.Write()

kfactor.Write('zllg-130-o')
kfactorUp.Write('zllg-130-o_scaleUp')
kfactorDown.Write('zllg-130-o_scaleDown')

kfactor.Write('zllg-300-o')
kfactorUp.Write('zllg-300-o_scaleUp')
kfactorDown.Write('zllg-300-o_scaleDown')

print 'wnlg_m'

sname = 'wnlg-130-o_m'

outFile.cd()
kfactor = ROOT.TH1D(sname, '', len(binning) - 1, binning)
kfactorUp = ROOT.TH1D(sname + '_scaleUp', '', len(binning) - 1, binning)
kfactorDown = ROOT.TH1D(sname + '_scaleDown', '', len(binning) - 1, binning)

with open(basedir + '/data/raw/wmnlg_grazzini.dat') as source:
    source.readline()
    iX = 1
    for line in source:
        words = line.split()
        kfactor.SetBinContent(iX, float(words[1]) * 3.)
        kfactorDown.SetBinContent(iX, float(words[3]) * 3.)
        kfactorUp.SetBinContent(iX, float(words[5]) * 3.)

        if iX == wmglo.GetNbinsX():
            break

        iX += 1

kfactor.Divide(wmglo)
kfactorUp.Divide(wmglo)
kfactorDown.Divide(wmglo)

kfactor.Write()
kfactorUp.Write()
kfactorDown.Write()

print 'wnlg_p'

sname = 'wnlg-130-o_p'

outFile.cd()
kfactor = ROOT.TH1D(sname, '', len(binning) - 1, binning)
kfactorUp = ROOT.TH1D(sname + '_scaleUp', '', len(binning) - 1, binning)
kfactorDown = ROOT.TH1D(sname + '_scaleDown', '', len(binning) - 1, binning)

with open(basedir + '/data/raw/wpnlg_grazzini.dat') as source:
    source.readline()
    iX = 1
    for line in source:
        words = line.split()
        kfactor.SetBinContent(iX, float(words[1]) * 3.)
        kfactorDown.SetBinContent(iX, float(words[3]) * 3.)
        kfactorUp.SetBinContent(iX, float(words[5]) * 3.)

        if iX == wpglo.GetNbinsX():
            break

        iX += 1

kfactor.Divide(wpglo)
kfactorUp.Divide(wpglo)
kfactorDown.Divide(wpglo)

kfactor.Write()
kfactorUp.Write()
kfactorDown.Write()

print 'gjets'

func = ROOT.TF1('gjets', '[0] - [1] * x', 160., 1000.)
func.SetParameters(1.71691, 0.00122061)
func.Write('gj-40')
func.Write('gj-100')
func.Write('gj-200')
func.Write('gj-400')
func.Write('gj-600')

outFile.Close()
