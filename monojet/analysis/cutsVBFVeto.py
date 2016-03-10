from cuts import *

VBFSelection = 'jet1Pt > 80 && jet2Pt > 70 && vectorSumMass(jet1Pt, jet1Eta, jet1Phi, jet1M, jet2Pt, jet2Eta, jet2Phi, jet2M) > 1100 && abs(jet1Eta - jet2Eta) > 3.6 && minJetMetDPhi_clean > 2.3'

regionCuts['signal'] += ' && !(' + VBFSelection + ')'
