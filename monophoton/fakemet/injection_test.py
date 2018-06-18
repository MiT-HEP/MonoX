import sys
import os
import struct

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

import ROOT

# usage injection_test.py <fakeMetRandom hist file> <gghg hist file with the signal distribution> <signal scale> <fakeMet norm> <output file name>

targSourceName = sys.argv[1] # fakeMetRandom hist file
sourceName = sys.argv[2] # gghg hist file
sigScale = float(sys.argv[3]) # signal scale
fakeNorm = float(sys.argv[4]) # fakeMet norm
outputName = sys.argv[5] # output file

dist = 'mtPhoMet'
signal = 'dph-nlo-125'
region = 'gghg'

source = ROOT.TFile.Open(sourceName)

out = ROOT.TFile.Open(outputName, 'recreate')
out.mkdir(dist)

source.cd(dist)
for key in ROOT.gDirectory.GetListOfKeys():
    name = key.GetName()
    if name in ['samples', 'data_obs']:
        continue

    out.cd(dist)
    hist = key.ReadObj()
    hist.Write()

outSamples = out.mkdir(dist + '/samples')

signalHist = None

source.cd(dist + '/samples')
samples = ROOT.gDirectory
for key in samples.GetListOfKeys():
    name = key.GetName()
    if name.endswith('_original'):
        continue

    out.cd(dist + '/samples')
    hist = key.ReadObj()

    if name.startswith(signal):
        hist.Scale(sigScale)

    if name == signal + '_' + region:
        signalHist = hist
        signalHist.SetDirectory(outSamples)

    hist.Write()

source.Close()

targSource = ROOT.TFile.Open(targSourceName)

bkgtotal = targSource.Get(dist + '/bkgtotal').Clone()
fakemet = targSource.Get(dist + '/fakemet').Clone()

fakeScale = fakeNorm / fakemet.GetSumOfWeights()

bkgtotal.Add(fakemet, fakeScale - 1.)

out.cd(dist)
data_obs = bkgtotal.Clone('data_obs')
data_obs.Reset()

# Get the random seed from /dev/random
random = ROOT.TRandom3(struct.unpack('<L', os.urandom(4))[0])

for iX in range(1, bkgtotal.GetNbinsX() + 1):
    x = bkgtotal.GetXaxis().GetBinCenter(iX)
    for _ in range(random.Poisson(bkgtotal.GetBinContent(iX) + signalHist.GetBinContent(iX))):
        data_obs.Fill(x)

data_obs.Write()

out.Close()
targSource.Close()
