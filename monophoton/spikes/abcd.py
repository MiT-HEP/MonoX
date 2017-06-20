import os
import sys

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

import ROOT

offtime = ROOT.TChain('events')
offtime.Add(config.skimDir + '/sph*_offtime.root')

target = ROOT.TChain('events')
target.Add(config.skimDir + '/sph-16*_trivialShower.root')

#offsel = 'cluster.isEB && cluster.rawPt > 175 && cluster.trackIso < 10. && cluster.mipEnergy < 4.9 && TMath::Abs(cluster.eta) > 0.05 && cluster.time > -15. && cluster.time < -10. && cluster.sieie < 0.0102 && met.met > 170.'
offsel = 'photons.isEB && photons.scRawPt > 175 && photons.mipEnergy < 4.9 && photons.time > -15. && photons.time < -10. && photons.sieie < 0.01002 && t1Met.pt > 170.'
nOffTrivial = offtime.GetEntries(offsel + ' && (photons.sieie < 0.001 || photons.sipip < 0.001)')
nOffPhysical = offtime.GetEntries(offsel + ' && photons.sieie > 0.001 && photons.sipip > 0.001')

print nOffTrivial, nOffPhysical

nInTrivial = target.GetEntries('photons.scRawPt[0] > 175. && t1Met.pt > 170 && t1Met.photonDPhi > 2. && t1Met.minJetDPhi > 0.5')

print nInTrivial, float(nInTrivial) * float(nOffPhysical) / float(nOffTrivial)
