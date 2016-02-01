import sys
import os
import array
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples

sourceDir = '/scratch5/yiiyama/hist/simpletree11a/t2mit/filefi/042'

loSample = allsamples['znng-130']

tree = ROOT.TChain('events')
tree.Add(sourceDir + '/' + loSample.directory + '/simpletree_*.root')

# the input file from Grazzini has a 1000- bin but has the same cross section as 700-1000.
# guessing this means that the calculation was only up to 1000 GeV
binning = array.array('d', [175., 190., 250., 400., 700., 1000.])

lodist = ROOT.TH1D('lo', '', len(binning) - 1, binning)
tree.Draw('partons.pt>>lo', 'partons.pid == 22 && partons.status == 1 && TMath::Abs(partons.eta) < 1.4442', 'goff')

lodist.Scale(loSample.crosssection / tree.GetEntries())
lodist.Scale(1000., 'width') # fb / GeV

lolist = [lodist.GetBinContent(iX) for iX in range(1, len(binning))]

nnlolist = []
with open(basedir + '/data/znng_grazzini.dat') as source:
    source.readline()
    for line in source:
        xsec = float(line.split()[1])
        nnlolist.append(xsec * 3.) # three neutrino flavors

print lolist
print nnlolist

with open(basedir + '/data/znng_kfactor.dat', 'w') as output:
    for iPt in range(len(binning) - 1):
        output.write('%.0f %f\n' % (binning[iPt], nnlolist[iPt] / lolist[iPt]))
