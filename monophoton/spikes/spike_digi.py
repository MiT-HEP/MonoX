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
pedestal = array.array('d', [0.])
amplitude = array.array('d', [0.])
jitter = array.array('d', [0.])
sieie = array.array('d', [0.])
outputTree.Branch('adc', adc, 'adc[10]/D')
outputTree.Branch('pedestal', pedestal, 'pedestal/D')
outputTree.Branch('amplitude', amplitude, 'amplitude/D')
outputTree.Branch('jitter', jitter, 'jitter/D')
outputTree.Branch('sieie', sieie, 'sieie/D')

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events

scHandle, scLabel = Handle('std::vector<reco::SuperCluster>'), 'particleFlowSuperClusterECALGSFixed:particleFlowSuperClusterECALBarrel'
urHandle, urLabel = Handle('EcalUncalibratedRecHitCollection'), 'ecalGlobalUncalibRecHitSelectedDigis:EcalUncalibRecHitsEB'
dgHandle, dgLabel = Handle("EBDigiCollection"), "selectDigi:selectedEcalEBDigiCollection"

scPositions = dict()
for fname in os.listdir(config.histDir + '/findSpikes'):
    with open(config.histDir + '/findSpikes/' + fname) as posSource:
        for line in posSource:
            try:
                eventId, eta, phi, s = line.split()[1:5]
            except:
                print line
                raise

            scPositions[tuple(map(int, eventId.split(':')))] = (float(eta), float(phi), float(s))

events = Events(source)

for event in events:
    eid = event.object().id()
    eventId = (eid.run(), eid.luminosityBlock(), eid.event())
    print eventId
    position = scPositions[eventId]
    sieie[0] = position[2]

    event.getByLabel(scLabel, scHandle)
    scs = scHandle.product()

    seedId = 0

    for sc in scs:
        dEta = sc.eta() - position[0]
        dPhi = ROOT.TVector2.Phi_mpi_pi(sc.phi() - position[1])

        if dEta * dEta + dPhi * dPhi < 0.04:
            seedId = sc.seed().seed().rawId()
            break

    if seedId == 0:
        print 'Cluster not found in', eventId
        continue

    event.getByLabel(urLabel, urHandle)
    urechits = urHandle.product()

    for ur in urechits:
        if ur.id().rawId() == seedId:
            break
    else:
        print 'Urechit not found in', eventId
        continue

    pedestal[0] = ur.pedestal()
    amplitude[0] = ur.amplitude()
    jitter[0] = ur.jitter()

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
