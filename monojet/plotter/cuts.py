allMetCut = '(n_tau == 0 && n_bjetsMedium == 0 && abs(minJetMetDPhi_clean)>0.5 && met>200.0 && leadingJet_outaccp == 0)'

photonVeto = 'n_loosepho == 0'
leptonVeto = 'n_looselep == 0'
diLepton = 'n_looselep == 2 && abs(dilep_m - 91) < 30 && n_tightlep > 0'
singleLepton = 'n_looselep == 1 && n_tightlep > 0'
singlePhoton = 'photonPt > 175 && abs(photonEta) < 1.4442 && n_mediumpho == 1 && n_loosepho == 1'

METTrigger = '(triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)'
ETrigger   = '(triggerFired[4]==1) || (triggerFired[5]==1) || (triggerFired[11]==1 || triggerFired[12]==1 || triggerFired[13]==1)'
GTrigger   = '(triggerFired[11]==1 || triggerFired[12]==1 || triggerFired[13]==1)'

monoJet = 'jet1Pt > 100 && jet1isMonoJetIdNew == 1 && abs(jet1Eta) < 2.5'
monoV   = 'fatjet1Pt > 250 && fatjet1tau21 < 0.45 && abs(fatjet1PrunedM - 85) < 20 && fatjet1overlapB < 2 && fatjet1Eta < 2.5 && fatjet1MonojetId == 1'

topregion = 'n_mediumlep == 1 && n_looselep == 1 && trueMet > 30 && n_bjetsLoose > 1 && fatjet1overlapB < 1 && fatjet1Pt > 250 && fatjet1Eta < 2.5 && fatjet1MonojetId == 1'

Zee = str(allMetCut + '&&' + 
          photonVeto + '&&' + 
          diLepton + '&&' + 
#          ETrigger + '&&' + 
          'lep1PdgId*lep2PdgId == -121')

Zmm = str(allMetCut + '&&' + 
          photonVeto + '&&' + 
          diLepton + '&&' + 
#          METTrigger + '&&' + 
          'lep1PdgId*lep2PdgId == -169')

Wen = str(allMetCut + '&&' + 
          photonVeto + '&&' + 
          singleLepton + '&&' + 
          ETrigger + '&&' +
          'abs(lep1PdgId)==11 && trueMet>40')

Wmn = str(allMetCut + '&&' + 
          photonVeto + '&&' + 
          singleLepton + '&&' + 
          METTrigger + '&&' +
          'abs(lep1PdgId)==13')

gjet = str(allMetCut + '&&' + 
           leptonVeto + '&&' + 
           GTrigger + '&&' + 
           singlePhoton)

signal = str(allMetCut + '&&' + 
             leptonVeto + '&&' + 
             photonVeto + '&&' + 
             METTrigger)

Zll = '(' + Zee + ')||(' + Zmm + ')'

ZeeMJ  = Zee + '&&' + monoJet
ZmmMJ  = Zmm + '&&' + monoJet
ZllMJ  = Zll + '&&' + monoJet
WenMJ  = Wen + '&&' + monoJet
WmnMJ  = Wmn + '&&' + monoJet
gjetMJ = gjet + '&&' + monoJet

signalMJ_unblinded = signal + '&&' + monoJet
signalMJ = signalMJ_unblinded + '&&' + 'runNum == 1'

ZeeMV  = Zee + '&&' + monoV
ZmmMV  = Zmm + '&&' + monoV
ZllMV  = Zll + '&&' + monoV
WenMV  = Wen + '&&' + monoV
WmnMV  = Wmn + '&&' + monoV
gjetMV = gjet + '&&' + monoV
topMV  = photonVeto + '&&' + topregion + '&&' + monoV
top    = photonVeto + '&&' + topregion

signalMV_unblinded = signal + '&&' + monoV
signalMV = signalMV_unblinded + '&&' + 'runNum == 1'
