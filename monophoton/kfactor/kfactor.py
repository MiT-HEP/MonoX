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

def makeZGWGHistograms(sname, binning):
    sample = allsamples[sname]

    tree = ROOT.TChain('events')
    for fname in sample.files():
        tree.Add(fname)

    lo = ROOT.TH1D('lo', '', len(binning) - 1, binning)

    ROOT.makeZGWGHistograms(tree, lo)
#    tree.Draw('TMath::Min(partons.pt_, 999.9)>>lo', 'partons.pdgid == 22 && TMath::Abs(partons.eta_) < 1.4442', 'goff')

    lo.Scale(1000. * sample.crosssection / sample.sumw, 'width') # nnlo file given in dsigma / dpT (fb / GeV)

    outFile.cd()
    kfactor = ROOT.TH1D(sname, '', len(binning) - 1, binning)
    kfactorUp = ROOT.TH1D(sname + '_scaleUp', '', len(binning) - 1, binning)
    kfactorDown = ROOT.TH1D(sname + '_scaleDown', '', len(binning) - 1, binning)

    return lo, kfactor, kfactorUp, kfactorDown


outFile = ROOT.TFile.Open(basedir + '/data/kfactor.root', 'recreate')

print 'gjets'

func = ROOT.TF1('gjets', '[0] - [1] * x', 160., 1000.)
func.SetParameters(1.71691, 0.00122061)
func.Write('gj-40')
func.Write('gj-100')
func.Write('gj-200')
func.Write('gj-400')
func.Write('gj-600')

# the input file from Grazzini has a 1000- bin but has the same cross section as 700-1000.
# guessing this means that the calculation was only up to 1000 GeV
binning = array.array('d', [175., 190., 250., 400., 700., 1000.])

print 'znng & zllg'

lo, kfactor, kfactorUp, kfactorDown = makeZGWGHistograms('znng-130-o', binning)

with open(basedir + '/data/raw/znng_grazzini.dat') as source:
    source.readline()
    iX = 1
    for line in source:
        words = line.split()
        kfactor.SetBinContent(iX, float(words[1]) * 3.) # three neutrino flavors
        kfactorDown.SetBinContent(iX, float(words[3]) * 3.)
        kfactorUp.SetBinContent(iX, float(words[5]) * 3.)

        if iX == lo.GetNbinsX():
            break

        iX += 1

kfactor.Divide(lo)
kfactorUp.Divide(lo)
kfactorDown.Divide(lo)

lo.Delete()

kfactor.Write()
kfactorUp.Write()
kfactorDown.Write()

kfactor.Write('zllg-130-o')
kfactorUp.Write('zllg-130-o_scaleUp')
kfactorDown.Write('zllg-130-o_scaleDown')

kfactor.Write('zllg-300-o')
kfactorUp.Write('zllg-300-o_scaleUp')
kfactorDown.Write('zllg-300-o_scaleDown')

print 'wnlg'

lo, kfactor, kfactorUp, kfactorDown = makeZGWGHistograms('wnlg-130-o', binning)

with open(basedir + '/data/raw/wmnlg_grazzini.dat') as source:
    source.readline()
    iX = 1
    for line in source:
        words = line.split()
        kfactor.SetBinContent(iX, float(words[1]) * 3.)
        kfactorDown.SetBinContent(iX, float(words[3]) * 3.)
        kfactorUp.SetBinContent(iX, float(words[5]) * 3.)

        if iX == lo.GetNbinsX():
            break

        iX += 1

with open(basedir + '/data/raw/wpnlg_grazzini.dat') as source:
    source.readline()
    iX = 1
    for line in source:
        words = line.split()
        kfactor.SetBinContent(iX, kfactor.GetBinContent(iX) + float(words[1]) * 3.)
        kfactorDown.SetBinContent(iX, kfactorDown.GetBinContent(iX) + float(words[3]) * 3.)
        kfactorUp.SetBinContent(iX, kfactorUp.GetBinContent(iX) + float(words[5]) * 3.)

        if iX == lo.GetNbinsX():
            break

        iX += 1

kfactor.Divide(lo)
kfactorUp.Divide(lo)
kfactorDown.Divide(lo)

kfactor.Write()
kfactorUp.Write()
kfactorDown.Write()

outFile.Close()
