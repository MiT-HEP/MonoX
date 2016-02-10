allCut = 'n_tau == 0 && abs(minJetMetDPhi_clean) > 0.5 && leadingJet_outaccp == 0'
zeeAll = 'n_tau == 0 && leadingJet_outaccp == 0'
metCut = 'met > 200'

btagVeto = 'n_bjetsMedium == 0'
#btagVeto = 'n_bjetsMedium != -2'
photonVeto = 'n_loosepho == 0'
leptonVeto = 'n_looselep == 0'
diLepton = 'n_looselep == 2 && abs(dilep_m - 90) < 30 && n_tightlep > 0'
singleLepton = 'n_looselep == 1 && n_tightlep == 1'
singlePhoton = 'photonPt > 175 && abs(photonEta) < 1.4442 && n_mediumpho == 1 && n_loosepho == 1'

METTrigger = '(triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)'
GTrigger   = '(triggerFired[11]==1 || triggerFired[12]==1 || triggerFired[13]==1)'
ETrigger   = '((triggerFired[4]==1 || triggerFired[5]==1) || ' + GTrigger + ')'
MuTrigger  = '(triggerFired[8]==1 || triggerFired[9]==1 || triggerFired[10]==1)'

monoJet     = 'jet1Pt > 100 && jet1isMonoJetIdNew == 1 && abs(jet1Eta) < 2.4'
monoVSimple = 'fatjet1Pt > 250 && fatjet1tau21 < 0.6 && met > 250'
monoVNoMass = monoVSimple + ' && abs(fatjet1Eta) < 2.4 && jet1isMonoJetIdNew == 1'
monoV       = monoVNoMass + ' && fatjet1PrunedM < 105 && fatjet1PrunedM > 62'
#monoVeto    = monoV
monoVeto    = 'fatjet1Pt > 250 && fatjet1PrunedM > 62 && met > 250 && fatjet1tau21 < 0.6 && abs(fatjet1Eta) < 2.4'

topSimple = 'n_tightlep == 1 && n_looselep == 1 && trueMet > 30 && n_bjetsMedium != 0'
topregion = topSimple + ' && n_bjetsLoose > 1 && fatjet1overlapB < 1 && fatjet1Pt > 250 && fatjet1Eta < 2.4 && fatjet1MonojetId == 1'
toprecoil = topSimple + ' && n_bjetsLoose > 1 '

Zee = str(zeeAll + ' && ' + 
          metCut + ' && ' + 
          btagVeto + ' && ' + 
          photonVeto + ' && ' + 
          diLepton + ' && ' + 
#          ETrigger + ' && ' + 
          'lep1PdgId*lep2PdgId == -121')

Zmm = str(allCut + ' && ' + 
          metCut + ' && ' + 
          btagVeto + ' && ' + 
          photonVeto + ' && ' + 
          diLepton + ' && ' + 
#          METTrigger + ' && ' + 
          'lep1PdgId*lep2PdgId == -169')

Wen = str(allCut + ' && ' + 
          metCut + ' && ' + 
          btagVeto + ' && ' + 
          photonVeto + ' && ' + 
          singleLepton + ' && ' + 
          'lep1Pt > 40 && ' +
#          ETrigger + ' && ' +
          'abs(lep1PdgId) == 11 && trueMet > 50')

Wmn = str(allCut + ' && ' + 
          metCut + ' && ' + 
          btagVeto + ' && ' + 
          photonVeto + ' && ' + 
          singleLepton + ' && ' + 
#          METTrigger + ' && ' +
          'abs(lep1PdgId) == 13')

gjet = str(allCut + ' && ' + 
           metCut + ' && ' + 
           btagVeto + ' && ' + 
           leptonVeto + ' && ' + 
#           GTrigger + ' && ' + 
           singlePhoton)

signal = str(allCut + ' && ' + 
             metCut + ' && ' + 
             btagVeto + ' && ' + 
             leptonVeto + ' && ' + 
#             METTrigger + ' && ' + 
             photonVeto)

Zll = '((' + Zee + ') || (' + Zmm + '))'
Wln = '((' + Wen + ') || (' + Wmn + '))'

top = str(allCut + ' && ' +
          photonVeto + ' && ' +
#          METTrigger + ' && ' +
          metCut + ' && ' +
          topregion)

topMet = str(allCut + ' && ' +
          photonVeto + ' && ' +
#          METTrigger + ' && ' +
          metCut + ' && ' +
          toprecoil)

ZeeMJ_inc  = Zee + ' && ' + monoJet
ZmmMJ_inc  = Zmm + ' && ' + monoJet
ZllMJ_inc  = Zll + ' && ' + monoJet
WenMJ_inc  = Wen + ' && ' + monoJet
WmnMJ_inc  = Wmn + ' && ' + monoJet
WlnMJ_inc  = Wln + ' && ' + monoJet
gjetMJ_inc = gjet + ' && ' + monoJet

signalMJ_inc_unblinded = signal + ' && ' + monoJet
signalMJ_inc = signalMJ_inc_unblinded + ' && ' + 'runNum == 1'

ZeeMJ  = ZeeMJ_inc + ' && !(' + monoVeto + ')'
ZmmMJ  = ZmmMJ_inc + ' && !(' + monoVeto + ')'
ZllMJ  = ZllMJ_inc + ' && !(' + monoVeto + ')'
WenMJ  = WenMJ_inc + ' && !(' + monoVeto + ')'
WmnMJ  = WmnMJ_inc + ' && !(' + monoVeto + ')'
WlnMJ  = WlnMJ_inc + ' && !(' + monoVeto + ')'
gjetMJ = gjetMJ_inc + ' && !(' + monoVeto + ')'

signalMJ_unblinded = signalMJ_inc_unblinded + ' && !(' + monoVeto + ')'
signalMJ = signalMJ_inc + ' && !(' + monoVeto + ')'

ZeeMV  = Zee + ' && ' + monoV
ZmmMV  = Zmm + ' && ' + monoV
ZllMV  = Zll + ' && ' + monoV
WenMV  = Wen + ' && ' + monoV
WmnMV  = Wmn + ' && ' + monoV
WlnMV  = Wln + ' && ' + monoV
gjetMV = gjet + ' && ' + monoV
topMV  = top + ' && ' + monoV

signalMV_unblinded = signal + ' && ' + monoV
signalMV = signalMV_unblinded + ' && ' + 'runNum == 1'

ZeeMVNoMass  = Zee + ' && ' + monoVNoMass
ZmmMVNoMass  = Zmm + ' && ' + monoVNoMass
ZllMVNoMass  = Zll + ' && ' + monoVNoMass
WenMVNoMass  = Wen + ' && ' + monoVNoMass
WmnMVNoMass  = Wmn + ' && ' + monoVNoMass
WlnMVNoMass  = Wln + ' && ' + monoVNoMass
gjetMVNoMass = gjet + ' && ' + monoVNoMass
topMVNoMass  = top + ' && ' + monoVNoMass

signalMVNoMass_unblinded = signal + ' && ' + monoVNoMass
signalMVNoMass = signalMVNoMass_unblinded + ' && ' + 'runNum == 1'

ZeeMVSimple  = Zee + ' && ' + monoVSimple + ' && ' + monoJet
ZmmMVSimple  = Zmm + ' && ' + monoVSimple + ' && ' + monoJet
ZllMVSimple  = Zll + ' && ' + monoVSimple + ' && ' + monoJet
WenMVSimple  = Wen + ' && ' + monoVSimple + ' && ' + monoJet
WmnMVSimple  = Wmn + ' && ' + monoVSimple + ' && ' + monoJet
WlnMVSimple  = Wln + ' && ' + monoVSimple + ' && ' + monoJet
gjetMVSimple = gjet + ' && ' + monoVSimple + ' && ' + monoJet
topMVSimple  = top + ' && ' + monoVSimple + ' && ' + monoJet

signalMVSimple_unblinded = signal + ' && ' + monoVSimple + ' && ' + monoJet
signalMVSimple = signalMVSimple_unblinded + ' && ' + 'runNum == 1'

topMu  = topMet + ' && abs(lep1PdgId) == 13 && ' + singleLepton + ' && ' + monoV
topEle = topMet + ' && abs(lep1PdgId) == 11 && ' + singleLepton + ' && ' + monoV

topMJMu  = topMet + ' && abs(lep1PdgId) == 13 && ' + singleLepton + ' && ' + monoJet
topMJEle = topMet + ' && abs(lep1PdgId) == 11 && ' + singleLepton + ' && ' + monoJet
