import os
import sys
import re
import math
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
import utils
from datasets import allsamples

import ROOT

arun = array.array('I', [0])
alumi = array.array('I', [0])
aevent = array.array('I', [0])
aeta = array.array('f', [0.] * 10)
aphi = array.array('f', [0.] * 10)

positions = {}
#for sname in ['sph-16b-m', 'sph-16c-m', 'sph-16d-m', 'sph-16e-m', 'sph-16f-m', 'sph-16g-m', 'sph-16h-m']:
for sname in ['sph-16b-m', 'sph-16c-m', 'sph-16d-m']:
    positions[sname] = {}

    source = ROOT.TFile.Open(utils.getSkimPath(sname, 'monoph'))
    tree = source.Get('events')
    tree.Draw('>>elist', 'photons.scRawPt[0] > 175. && t1Met.pt > 170. && t1Met.photonDPhi > 0.5 && t1Met.minJetDPhi > 0.5', 'entrylist')
    elist = ROOT.gDirectory.Get('elist')
    tree.SetEntryList(elist)

    tree.SetBranchAddress('runNumber', arun)
    tree.SetBranchAddress('lumiNumber', alumi)
    tree.SetBranchAddress('eventNumber', aevent)
    tree.SetBranchAddress('photons.eta_', aeta)
    tree.SetBranchAddress('photons.phi_', aphi)

    ientry = 0
    while True:
        ilocal = tree.GetEntryNumber(ientry)
        if ilocal < 0:
            break

        ientry += 1

        tree.GetEntry(ilocal)
        
        positions[sname][(arun[0], alumi[0], aevent[0])] = (aeta[0], aphi[0])

    print sname, len(positions[sname]), 'photons'

    source.Close()


outTrees = {}
outFiles = []

aieta = array.array('h', [0])
aiphi = array.array('h', [0])

sourcedir = '/mnt/hadoop/scratch/yiiyama/spike_event'
for fname in os.listdir(sourcedir):
    if 'Run2016B' in fname:
        sname = 'sph-16b-m'
    elif 'Run2016C' in fname:
        sname = 'sph-16c-m'
    elif 'Run2016D' in fname:
        sname = 'sph-16d-m'
    elif 'Run2016E' in fname:
        sname = 'sph-16e-m'
    elif 'Run2016F' in fname:
        sname = 'sph-16f-m'
    elif 'Run2016G' in fname:
        sname = 'sph-16g-m'
    elif 'Run2016H' in fname:
        sname = 'sph-16h-m'

    if sname not in ['sph-16b-m', 'sph-16c-m', 'sph-16d-m']:
        continue

    matches = re.match('.+AOD_([0-9]+)_([0-9]+)_([0-9]+)[.]root', fname)
    event = (int(matches.group(1)), int(matches.group(2)), int(matches.group(3)))
    position = positions[sname][event]
#    print event, position

    source = ROOT.TFile.Open(sourcedir + '/' + fname)
    tree = source.Get('outTree/hits')

    if sname not in outTrees:
        outFile = ROOT.TFile.Open(config.histDir + '/spikes/hits_' + sname + '.root', 'recreate')
        outFiles.append(outFile)
        outTree = tree.CloneTree(0)
        outTrees[sname] = outTree

    tree.SetBranchAddress('ieta', aieta)
    tree.SetBranchAddress('iphi', aiphi)

    ientry = 0
    while tree.GetEntry(ientry) > 0:
        ientry += 1
        eta = aieta[0] * 0.0174
        phi = (aiphi[0] - 10) / 180. * math.pi
        deta = position[0] - eta
        dphi = position[1] - phi
        while dphi > math.pi:
            dphi -= 2. * math.pi
        while dphi < -math.pi:
            dphi += 2. * math.pi

        if deta * deta + dphi * dphi < 0.01:
            tree.CopyAddresses(outTrees[sname])
            outTrees[sname].Fill()
            break
    else:
        print 'Matching photon not found for event', event

    tree.CopyAddresses(outTrees[sname], True)

    source.Close()

for tree in outTrees.itervalues():
    outFile = tree.GetCurrentFile()
    outFile.cd()
    tree.Write()
    outFile.Close()
