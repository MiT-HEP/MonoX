import math
import array
import os
import sys

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

source = sys.argv[1]
output = sys.argv[2]

import ROOT

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.FWLiteEnabler.enable()

outputFile = ROOT.TFile.Open(output, 'recreate')
outputTree = ROOT.TTree('digiTree', 'digis')
adc = array.array('d', [0.] * 10)
energy = array.array('d', [0.])
time = array.array('d', [0.])
outputTree.Branch('adc', adc, 'adc[10]/D')
outputTree.Branch('energy', energy, 'energy/D')
outputTree.Branch('time', time, 'time/D')

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events

scHandle, scLabel = Handle('std::vector<reco::SuperCluster>'), 'particleFlowSuperClusterECAL:particleFlowSuperClusterECALBarrel'
urHandle, urLabel = Handle('EcalRecHitCollection'), 'reducedEcalRecHitsEB'
dgHandle, dgLabel = Handle("EBDigiCollection"), "selectDigi:selectedEcalEBDigiCollection"

events = Events(source)

for event in events:
    eid = event.object().id()
    eventId = (eid.run(), eid.luminosityBlock(), eid.event())

    event.getByLabel(scLabel, scHandle)
    scs = scHandle.product()

    seedId = 0

    for sc in scs:
        if sc.energy() / math.cosh(sc.eta()) > 150.:
            seedId = sc.seed().seed().rawId()
            break
    else:
        continue

    event.getByLabel(urLabel, urHandle)
    urechits = urHandle.product()

    for ur in urechits:
        if ur.id().rawId() == seedId:
            break
    else:
        print 'Urechit not found in', eventId
        continue

    energy[0] = ur.energy()
    time[0] = ur.time()

    event.getByLabel(dgLabel, dgHandle)
    digis = dgHandle.product()

    for d in xrange(digis.size()):
        digi = digis[d]
        if digi.id() == seedId:
            break
    else:
        print 'Digi not found in', eventId
        continue

    frame = ROOT.EBDataFrame(digi)
    for i in xrange(10):
        eff = float(frame.sample(i).adc())
        if frame.sample(i).gainId() == 2:
            eff *= 2.
        elif frame.sample(i).gainId() == 3:
            eff *= 12.

        adc[i] = eff

    outputTree.Fill()

outputFile.cd()
outputTree.Write()
outputFile.Close()
