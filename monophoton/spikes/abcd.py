import ROOT

highmet = ROOT.TChain('events')
highmet.Add('/data/t3home000/yiiyama/simpletree/uncleanedSkimmed/sph*_highmet.root')

# Low MET has 0 contribution to < -10 ns
#lowmet = ROOT.TChain('events')
#lowmet.Add('/data/t3home000/yiiyama/simpletree/uncleanedSkimmed/sph*_lowmet.root')
#
#tLowmet = ROOT.TH1D('tLowmet', '', 100, -25., 25.)
#lowmet.Draw('cluster.time>>tLowmet', 'cluster.rawPt > 175 && cluster.trackIso < 10. && cluster.mipEnergy < 4.9 && cluster.sieie < 0.0102')

target = ROOT.TChain('events')
target.Add('/data/t3home000/yiiyama/studies/monophoton/skim/sph-16*_trivialShower.root')

#offtime = 'cluster.isEB && cluster.rawPt > 175 && cluster.trackIso < 10. && cluster.mipEnergy < 4.9 && TMath::Abs(cluster.eta) > 0.05 && cluster.time > -15. && cluster.time < -10. && cluster.sieie < 0.0102 && met.met > 170.'
offtime = 'cluster.isEB && cluster.rawPt > 175 && cluster.mipEnergy < 4.9 && TMath::Abs(cluster.eta) > 0.05 && cluster.time > -15. && cluster.time < -10. && cluster.sieie < 0.0102 && met.met > 170.'
offtime_narrow = highmet.GetEntries(offtime + ' && (cluster.sieie < 0.001 || cluster.sipip < 0.001)')
offtime_wide = highmet.GetEntries(offtime + ' && cluster.sieie > 0.001 && cluster.sipip > 0.001')

print offtime_wide, offtime_narrow

intime_narrow = target.GetEntries('photons.scRawPt[0] > 175. && t1Met.met > 170 && t1Met.photonDPhi > 2. && t1Met.minJetDPhi > 0.5')

print intime_narrow, float(intime_narrow) * float(offtime_wide) / float(offtime_narrow)
