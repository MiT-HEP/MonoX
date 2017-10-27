#!/usr/bin/env python

import os
import sys
import array
import shutil
import math

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)

import ROOT

jobid = int(sys.argv[1])

dataset = 'GJets_HT-100To200'
#dataset = 'SingleMuon'

outdir = '/data/t3home000/yiiyama/spike_notopo/' + dataset
try:
    os.makedirs(outdir)
except OSError:
    pass

sourcelist = dataset + '.txt'
nperjob = 10

outputFile = ROOT.TFile.Open('%d.root' % jobid, 'recreate')

output = ROOT.TTree('hits', 'spike hits')

sieie = array.array('f', [0.])
sipip = array.array('f', [0.])
ieta = array.array('h', [0])
iphi = array.array('h', [0])
pedestal = array.array('d', [0.])
amps = array.array('d', [0.] * 10)
gainId = array.array('H', [0] * 10)
height = array.array('d', [0.])
alpha = array.array('d', [0.])
beta = array.array('d', [0.])
t0 = array.array('d', [0.])
chi2 = array.array('d', [0.])
torig = array.array('f', [0.])
saturated = array.array('B', [0])
weird = array.array('B', [0])
diweird = array.array('B', [0])

output.Branch('sieie', sieie, 'sieie/F')
output.Branch('sipip', sipip, 'sipip/F')
output.Branch('ieta', ieta, 'ieta/S')
output.Branch('iphi', iphi, 'iphi/S')
output.Branch('pedestal', pedestal, 'pedestal/D')
output.Branch('amps', amps, 'amps[10]/D')
output.Branch('gainId', gainId, 'gainId[10]/s')
output.Branch('height', height, 'height/D')
output.Branch('alpha', alpha, 'alpha/D')
output.Branch('beta', beta, 'beta/D')
output.Branch('t0', t0, 't0/D')
output.Branch('chi2', chi2, 'chi2/D')
output.Branch('torig', torig, 'torig/F')
output.Branch('saturated', saturated, 'saturated/B')
output.Branch('weird', weird, 'weird/B')
output.Branch('diweird', diweird, 'diweird/B')

tree = ROOT.TChain('outTree/hits')
with open(sourcelist) as table:
    iline = 0
    for line in table:
        iline += 1
        if iline == (jobid + 1) * nperjob:
            break
        elif iline > jobid * nperjob:
            tree.Add(line.strip())

adc = array.array('I', [0] * 10)
tree.SetBranchAddress('adc', adc)
tree.SetBranchAddress('gainId', gainId)
tree.SetBranchAddress('ieta', ieta)
tree.SetBranchAddress('iphi', iphi)
tree.SetBranchAddress('sieie', sieie)
tree.SetBranchAddress('sipip', sipip)
tree.SetBranchAddress('time', torig)
tree.SetBranchAddress('kWeird', weird)
tree.SetBranchAddress('kDiWeird', diweird)

gains = [0] * 10

func = ROOT.TF1('pulse', '[0] * TMath::Power(TMath::Max(0., 1. + (x - [3]) / [1] / [2]), [1]) * TMath::Exp(-(x - [3]) / [2])')

shownext = False

iEntry = 0
while tree.GetEntry(iEntry) > 0:
    iEntry += 1

    pedestal[0] = adc[0]
    ip = 1
    while abs(adc[ip] - pedestal[0]) < 10.:
        pedestal[0] = (pedestal[0] * ip + adc[ip]) / (ip + 1)
        ip += 1

    if ip >= 6:
        continue

    for isamp in xrange(10):
        if gainId[isamp] == 1:
            amps[isamp] = adc[isamp] - pedestal[0]
            gains[isamp] = 1
        elif gainId[isamp] == 2:
            amps[isamp] = (adc[isamp] - pedestal[0]) * 2.
            gains[isamp] = 2
        elif gainId[isamp] == 3 or gainId[isamp] == 0:
            amps[isamp] = (adc[isamp] - pedestal[0]) * 12.
            gains[isamp] = 12

    def tryfit(iq):
        graph = ROOT.TGraphErrors(10 - iq)
    
        for i in xrange(iq, 10):
            graph.SetPoint(i - iq, float(i), max(0., amps[i]))
            graph.SetPointError(i - iq, 0., 3. * gains[i])
    
        func.SetParameters(amps[iq + 2], 1., 1.7, iq + 1.5)
    
        return graph.Fit(func, 'S')

    fitres = tryfit(ip)
    
    badfit = (fitres.MinFcnValue() - amps[ip] ** 2 / (3. * gains[ip]) ** 2 > 1000.)
    if badfit and ip < 6:
        fitres = tryfit(ip + 1)
        badfit = (fitres.MinFcnValue() - amps[ip + 1] ** 2 / (3. * gains[ip + 1]) ** 2 > 1000.)

    if badfit:
        continue

    height[0] = func.GetParameter(0)
    alpha[0] = func.GetParameter(1)
    beta[0] = func.GetParameter(2)
    t0[0] = func.GetParameter(3)
    chi2[0] = fitres.MinFcnValue()

    imax = max(range(10), key = lambda i: adc[i])
    if float(adc[9]) / adc[imax] > 0.9:
        saturated[0] = 1
    else:
        saturated[0] = 0

#    if shownext or badfit:
#        shownext = False
#        print 'iEntry', iEntry
#        print 'ip', ip
#        print 'pedestal', pedestal[0]
#        print 'adc', adc
#        print 'gainId', gainId
#        print 'gains', gains
#        print 'amps', amps
#        print 'height', height[0]
#        print 'alpha', alpha[0]
#        print 'beta', beta[0]
#        print 't0', t0[0]
#        graph.Draw('AEP')
#        s = sys.stdin.readline()
#        if s.strip() == 'q':
#            break
#        elif s.strip() == 's':
#            shownext = True
#
#        continue

    output.Fill()

outputFile.cd()
outputFile.Write()
outputFile.Close()

shutil.copy('%d.root' % jobid, outdir)
