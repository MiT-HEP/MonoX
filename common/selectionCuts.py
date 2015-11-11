# Define the cuts used for the control regions in a central place

allSelections       = "(jet1isMonoJetId == 1 && n_tau == 0) && "
diLeptonSelection   = "(n_looselep == 2 && n_tightlep > 0 && n_loosepho == 0 && lep2Pt > 20 && abs(dilep_m - 91) < 30 && n_bjetsMedium == 0) && "
singLeptonSelection = "(n_looselep == 1 && n_tightlep == 1 && n_loosepho == 0 && n_bjetsMedium == 0) && "

ZmmSelection      = "(" + allSelections + diLeptonSelection + "(lep1PdgId*lep2PdgId == -169))"
ZeeSelection      = "(" + allSelections + diLeptonSelection + "(lep1PdgId*lep2PdgId == -121 && n_tightlep == 2 && lep2Pt > 40))"
WmnSelection      = "(" + allSelections + singLeptonSelection + "(abs(lep1PdgId) == 13))"
WenSelection      = "(" + allSelections + singLeptonSelection + "(abs(lep1PdgId) == 11))"
lepVeto           = "n_looselep == 0 && n_tau == 0"
phoSelection      = "(" + allSelections + "photonIsTight == 1 && " + lepVeto + ")"
phoLooseSelection = "(" + allSelections + "((photonIsTight == 1 || (photonPt < 175 && n_loosepho != 0)) && " + lepVeto + "))"
signalSelection   = "(" + allSelections + "(n_looselep == 0 && n_loosepho == 0 && n_tau == 0 && minJetMetDPhi > 0.4))"

skimmingSelection = "((" + ZmmSelection + " || " + ZeeSelection + " || " + WmnSelection + " || " + WenSelection + " || " + signalSelection + " || " + phoLooseSelection + ") && met > 50)"
