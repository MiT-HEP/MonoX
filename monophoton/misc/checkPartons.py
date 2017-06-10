import sys
import os
import math
import ROOT as r 

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
import config

skim = sys.argv[1]

tree = r.TChain('events')
tree.Add(config.skimDir + '/' + skim + '.root')

dRPhoParton  = 'TMath::Sqrt(TMath::Power(photons.eta_[0] - genParticles.eta_, 2.) + TMath::Power(TVector2::Phi_mpi_pi(photons.phi_[0] - genParticles.phi_), 2.)) < 0.3'

print dRPhoParton

hist = r.TH1F("hist", "", 25, 0., 25.)

# tree.Draw('TMath::Abs(promptFinalStates.pid)>>hist', dRPhoParton + ' && photons.pt[0] > 140.')
tree.Draw('TMath::Abs(photons.matchedGenId[0])>>hist', 'photons.pt_[0] > 140.')

sys.stdin.readline()

"""
event = r.simpletree.Event()
event.setStatus(tree, False, {"*"})
event.setAddress(tree, {"run, lumi", "event", "weight", "promptFinalStates", "photons"})

iEntry = 0
while(tree.GetEntry(iEntry) > 0):
    iEntry += 1
    photons = event.photons
    partons = promptFinalStates
    
    for iPho in range(0, photons.size()):
        photon = photons[iPho]

        for iPart in range(0, partons.size()):
            parton = partons[iPart]

            if photon.dR2(parton) < 0.09:
                print "Photon matched to gen particle with pid: "+str(parton.pid)
                break
"""
