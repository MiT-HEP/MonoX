import sys
import os
import array
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import config

ROOT.gROOT.LoadMacro("PhaseSpaceChopper.cc+")
ROOT.gROOT.LoadMacro("translate.cc+")
chopper = ROOT.PhaseSpaceChopper()

sample = sys.argv[1]

loSample = allsamples[sample]

#tree = ROOT.TChain('events')
#tree.Add(config.ntuplesDir + '/' + loSample.directory + '/simpletree_*.root')

#ROOT.translate(tree, '/scratch5/yiiyama/studies/monophoton/' + sample + '_genphotons.root', ROOT.kPostShower)
#sys.exit(0)

tree = ROOT.TChain('events')
tree.Add('/scratch5/yiiyama/studies/monophoton/' + sample + '_lhephotons.root')

if sample == 'znng-130':
    # the input file from Grazzini has a 1000- bin but has the same cross section as 700-1000.
    # guessing this means that the calculation was only up to 1000 GeV
    binning = array.array('d', [175., 190., 250., 400., 700., 1000.])
elif sample == 'wnlg-130':
    binning = array.array('d', [175., 1000.])

etaBinning = array.array('d', [-1.4442, 1.4442])
chopper.setBinning('eta', 1, etaBinning)
chopper.setBinning('pt', len(binning) - 1, binning)
chopper.chop(tree)
chopper.dump()
sys.exit(0)

lodist = ROOT.TH1D('lo', '', len(binning) - 1, binning)
#tree.Draw('partons.pt>>lo', 'partons.pid == 22 && partons.status == 1 && TMath::Abs(partons.eta) < 1.4442', 'goff')
#tree.Draw('partonFinalStates.pt>>lo', 'partonFinalStates.pid == 22 && TMath::Abs(partonFinalStates.eta) < 1.4442', 'goff')

lodist.Scale(loSample.crosssection / tree.GetEntries())

nnlolist = []

if sample == 'znng-130':
    lodist.Scale(1000., 'width') # nnlo file given in fb / GeV

    with open(basedir + '/data/znng_grazzini.dat') as source:
        source.readline()
        for line in source:
            words = line.split()
            xsec, xsecdown, xsecup = float(words[1]), float(words[3]), float(words[5])
            nnlolist.append((xsec * 3., xsecdown * 3., xsecup * 3.)) # three neutrino flavors

elif sample == 'wnlg-130':
    lodist.Scale(1000.) # nnlo file given in fb

    xsec = 0.
    xsecdown = 0.
    xsecup = 0.
    with open(basedir + '/data/wnlg_grazzini.dat') as source:
        source.readline()
        for line in source:
            words = line.split()
            xsec += float(words[1]) * 3.
            xsecdown += float(words[2]) * 3.
            xsecup += float(words[3]) * 3.

    nnlolist = [(xsec, xsecdown, xsecup)] # single bin

lolist = [lodist.GetBinContent(iX) for iX in range(1, len(binning))]

print lolist

#with open(basedir + '/data/' + sample + '_kfactor.dat', 'w') as output:
#    for iPt in range(len(binning) - 1):
#        output.write('%.0f %f %f %f\n' % (binning[iPt], nnlolist[iPt][0] / lolist[iPt], nnlolist[iPt][1] / lolist[iPt], nnlolist[iPt][2] / lolist[iPt]))
