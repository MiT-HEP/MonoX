allCut = 'n_tau == 0 && abs(minJetMetDPhi_clean) > 0.5 && leadingJet_outaccp == 0'
metCut = 'met > 200'

btagVeto = 'n_bjetsMedium == 0'
photonVeto = 'n_loosepho == 0'
leptonVeto = 'n_looselep == 0'
diLepton = 'n_looselep == 2 && abs(dilep_m - 90) < 30 && n_tightlep > 0'
singleLepton = 'n_looselep == 1 && n_tightlep == 1'
singlePhoton = 'photonPt > 175 && abs(photonEta) < 1.4442 && n_mediumpho == 1 && n_loosepho == 1'

METTrigger = '(triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)'
GTrigger   = '(triggerFired[11]==1 || triggerFired[12]==1 || triggerFired[13]==1)'
ETrigger   = '((triggerFired[4]==1 || triggerFired[5]==1) || ' + GTrigger + ')'
MuTrigger  = '(triggerFired[8]==1 || triggerFired[9]==1 || triggerFired[10]==1)'

monoJet = 'jet1Pt > 100 && jet1isMonoJetIdNew == 1 && abs(jet1Eta) < 2.5'
monoV   = 'fatjet1Pt > 250 && fatjet1tau21 < 0.6 && abs(fatjet1PrunedM - 85) < 20 && fatjet1overlapB < 2 && abs(fatjet1Eta) < 2.5 && jet1isMonoJetIdNew == 1'

topregion = 'n_mediumlep == 1 && n_looselep == 1 && trueMet > 50 && n_bjetsLoose > 1 && fatjet1overlapB < 1 && fatjet1Pt > 250 && fatjet1Eta < 2.5 && fatjet1MonojetId == 1'

Zee = str(allCut + ' && ' + 
          metCut + ' && ' + 
          btagVeto + ' && ' + 
          photonVeto + ' && ' + 
          diLepton + ' && ' + 
          ETrigger + ' && ' + 
          'lep1PdgId*lep2PdgId == -121')

Zmm = str(allCut + ' && ' + 
          metCut + ' && ' + 
          btagVeto + ' && ' + 
          photonVeto + ' && ' + 
          diLepton + ' && ' + 
          METTrigger + ' && ' + 
          'lep1PdgId*lep2PdgId == -169')

Wen = str(allCut + ' && ' + 
          metCut + ' && ' + 
          btagVeto + ' && ' + 
          photonVeto + ' && ' + 
          singleLepton + ' && ' + 
          ETrigger + ' && ' +
          'abs(lep1PdgId) == 11 && trueMet > 40')

Wmn = str(allCut + ' && ' + 
          metCut + ' && ' + 
          btagVeto + ' && ' + 
          photonVeto + ' && ' + 
          singleLepton + ' && ' + 
          METTrigger + ' && ' +
          'abs(lep1PdgId) == 13')

gjet = str(allCut + ' && ' + 
           metCut + ' && ' + 
           btagVeto + ' && ' + 
           leptonVeto + ' && ' + 
           GTrigger + ' && ' + 
           singlePhoton)

signal = str(allCut + ' && ' + 
             metCut + ' && ' + 
             btagVeto + ' && ' + 
             leptonVeto + ' && ' + 
             METTrigger + ' && ' + 
             photonVeto)

Zll = '(' + Zee + ') || (' + Zmm + ')'

top = str(allCut + ' && ' +
          photonVeto + ' && ' +
          METTrigger + ' && ' +
          metCut + ' && ' +
#          '(' + ETrigger + ' || ' + GTrigger + ') && lep1Pt > 25 && ' + 
          topregion)

ZeeMJ  = Zee + ' && ' + monoJet
ZmmMJ  = Zmm + ' && ' + monoJet
ZllMJ  = Zll + ' && ' + monoJet
WenMJ  = Wen + ' && ' + monoJet
WmnMJ  = Wmn + ' && ' + monoJet
gjetMJ = gjet + ' && ' + monoJet

signalMJ_unblinded = signal + ' && ' + monoJet
signalMJ = signalMJ_unblinded + ' && ' + 'runNum == 1'

ZeeMV  = Zee + ' && ' + monoV
ZmmMV  = Zmm + ' && ' + monoV
ZllMV  = Zll + ' && ' + monoV
WenMV  = Wen + ' && ' + monoV
WmnMV  = Wmn + ' && ' + monoV
gjetMV = gjet + ' && ' + monoV
topMV  = top + ' && ' + monoV

signalMV_unblinded = signal + ' && ' + monoV
signalMV = signalMV_unblinded + ' && ' + 'runNum == 1'
