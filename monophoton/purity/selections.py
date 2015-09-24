# Additional selections to apply
cutEventWeight = '(weight) *'

cutBarrel = '(TMath::Abs(selPhotons.eta) < 1.5)'
cutEndcap = '((TMath::Abs(selPhotons.eta) > 1.5) && (TMath::Abs(SelPhotons.eta) < 2.4))'
cutEoverH = '(selPhotons.hOverE < 0.05)'

cutChIsoBarrelVLoose = '(selPhotons.chIso < 4.44)'

cutSieieBarrelMedium = '(selPhotons.sieie < 0.0100)'
cutChIsoBarrelMedium = '(selPhotons.chIso < 1.31)'
cutNhIsoBarrelMedium = '(selPhotons.nhIso < (0.60 + TMath::Exp(0.0044*selPhotons.pt+0.5809)))'
cutPhIsoBarrelMedium = '(selPhotons.phIso < (1.33 + 0.0043*selPhotons.pt))'
cutSelBarrelMedium = '('+cutBarrel+' && '+cutEoverH+' && '+cutNhIsoBarrelMedium+' && '+cutPhIsoBarrelMedium+')'

cutMatchedToReal = '((TMath::Abs(selPhotons.matchedGen) == 22) && (!selPhotons.hadDecay))' 
cutMatchedToHadDecay = '((TMath::Abs(selPhotons.matchedGen) == 22) && (selPhotons.hadDecay))'

cutPhotonPt = [ ('PhotonPt20to60', '((selPhotons.pt > 20) && (selPhotons.pt < 60) )')
                ,('PhotonPt60to100', '((selPhotons.pt > 60) && (selPhotons.pt < 100) )')
                #    ,('PhotonPt100toInf', '((selPhotons.pt > 100))') ]
                ,('PhotonPt100to140', '((selPhotons.pt > 100) && (selPhotons.pt < 140) )')
                ,('PhotonPt140to180', '((selPhotons.pt > 140) && (selPhotons.pt < 180) )')
                ,('PhotonPt180toInf', '((selPhotons.pt > 180) )') ]

cutSingleMuon = '(muons.size == 1)'
cutElectronVeto = '(electrons.size == 0)'
cutTauVeto = '(ntau == 0)'
cutMet20 = '(t1Met.met > 20)'
cutWlike = '('+cutSingleMuon+' && '+cutElectronVeto+' && '+cutTauVeto+' && '+cutMet20+')'

selections = { 'medium_barrel_inclusive' : [ 
        cutEventWeight+'('+cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && !'+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')' ]
               ,'medium_barrel_Wlike' : [ 
        cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')' ]
               ,'vloose_barrel_Wlike' : [ 
        cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelVLoose+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && !'+cutChIsoBarrelVLoose+' && !'+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
        ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')'  ] }

for cut in cutPhotonPt:
    cuts = [ cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && !'+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutWlike+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')' ]
    selections['medium_barrel_Wlike_'+cut[0]] = cuts

for cut in cutPhotonPt:
    cuts = [ cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && !'+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && !'+cutChIsoBarrelMedium+' && !'+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToReal+')'
             ,cutEventWeight+'('+cutSelBarrelMedium+' && '+cut[1]+' && '+cutChIsoBarrelMedium+' && '+cutMatchedToHadDecay+')' ]
    selections['medium_barrel_'+cut[0]] = cuts
