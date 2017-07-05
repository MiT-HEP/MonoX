import os
import sys

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
import utils
from datasets import allsamples

import ROOT

offtime = ROOT.TChain('events')
for sample in allsamples.getmany('sph-16*'):
    offtime.Add(utils.getSkimPath(sample.name, 'offtime'))

target = ROOT.TChain('events')
for sample in allsamples.getmany('sph-16*'):
    target.Add(utils.getSkimPath(sample.name, 'trivialShower'))

offsel = 'TMath::Abs(photons.scEta) < 1.4442 && photons.scRawPt > 175 && photons.mipEnergy < 4.9 && photons.time > -12.5 && photons.time < -10. && (photons.mediumX[][2] || (photons.type == 2 && photons.trackIso < 5.)) && photons.sieie < 0.0104 && photons.hOverE < 0.026 && t1Met.pt > 170. && t1Met.photonDPhi > 0.5 && t1Met.minJetDPhi > 0.5'
nOffTrivial = offtime.GetEntries(offsel + ' && (photons.sieie < 0.001 || photons.sipip < 0.001)')
nOffIntermediate = offtime.GetEntries(offsel + ' && photons.sieie > 0.001 && photons.sipip > 0.001 && photons.sieie < 0.008 && photons.sipip < 0.008')
nOffPhysical = offtime.GetEntries(offsel + ' && photons.sieie > 0.001 && photons.sipip > 0.001 && (photons.sieie > 0.008 || photons.sipip > 0.008)')

print '[-15 ns < t < -10 ns]'
print ' (A) sieie < 0.001 || sipip < 0.001 =>', nOffTrivial
print ' (A\') 0.001 < sieie < 0.008 && 0.001 < sipip < 0.008 =>', nOffIntermediate
print ' (B) sieie > 0.001 && sipip > 0.001 && (sieie > 0.008 || sipip > 0.008) =>', nOffPhysical

insel = 'photons.scRawPt > 175. && t1Met.pt > 170 && t1Met.photonDPhi > 0.5 && t1Met.minJetDPhi > 0.5'
nInTrivial = target.GetEntries(insel + ' && (photons.sieie < 0.001 || photons.sipip < 0.001)')
nInIntermediate = target.GetEntries(insel + ' && photons.sieie > 0.001 && photons.sipip > 0.001 && photons.sieie < 0.008 && photons.sipip < 0.008')

print '[-3 ns < t < 3 ns]'
print ' (C) sieie < 0.001 || sipip < 0.001 =>', nInTrivial
print ' (C\') 0.001 < sieie < 0.008 && 0.001 < sipip < 0.008 =>', nInIntermediate

print 'D = C x B/A =', float(nInTrivial + nInIntermediate) * float(nOffPhysical) / float(nOffTrivial + nOffIntermediate)
