categories = ['monoJet_inc','monoV','monoJet']
regions    = ['signal','Zmm','Zee','Wmn','Wen','gjets']

allCut = 'n_tau == 0 && abs(minJetMetDPhi_clean) > 0.5 && leadingJet_outaccp == 0'
zeeAll = 'n_tau == 0 && leadingJet_outaccp == 0'
metCut = 'met > 200'

bVeto = 'n_bjetsMedium == 0'
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
monoVSimple = 'fatjet1Pt > 250 && fatjet1tau21 < 0.6 && met > 250 && ' + monoJet
monoVNoMass = monoVSimple + ' && jet1isMonoJetIdNew == 1' # && abs(fatjet1Eta) < 2.4
monoV       = monoVNoMass + ' && fatjet1PrunedM < 105 && fatjet1PrunedM > 62'
#monoVeto    = monoV
monoVeto    = 'fatjet1Pt > 250 && fatjet1PrunedM > 62 && met > 250 && fatjet1tau21 < 0.6 && abs(fatjet1Eta) < 2.4 && fatjet1PrunedM < 105'

topSimple = 'n_tightlep == 1 && n_looselep == 1 && trueMet > 30 && n_bjetsMedium != 0'
#topregion = topSimple + ' && n_bjetsLoose > 1 && fatjet1DRLooseB > 1.2 && fatjet1Pt > 250 && fatjet1Eta < 2.4 && fatjet1MonojetId == 1'
topregion = topSimple + ' && n_bjetsLoose > 1 && fatjet1overlapB < 1 && fatjet1Pt > 250 && fatjet1Eta < 2.4 && fatjet1MonojetId == 1'
toprecoil = topSimple + ' && n_bjetsLoose > 1 '

Zee_noBVeto = str(zeeAll + ' && ' + 
          metCut + ' && ' + 
          photonVeto + ' && ' + 
          diLepton + ' && ' + 
          ETrigger + ' && ' + 
          'lep1PdgId*lep2PdgId == -121')

Zmm_noBVeto = str(allCut + ' && ' + 
          metCut + ' && ' + 
          photonVeto + ' && ' + 
          diLepton + ' && ' + 
          'lep1PdgId*lep2PdgId == -169')

Wen_noBVeto = str(allCut + ' && ' + 
          metCut + ' && ' + 
          photonVeto + ' && ' + 
          singleLepton + ' && ' + 
          'lep1Pt > 40 && ' +
          ETrigger + ' && ' +
          'abs(lep1PdgId) == 11 && trueMet > 50')

Wmn_noBVeto = str(allCut + ' && ' + 
          metCut + ' && ' + 
          photonVeto + ' && ' + 
          singleLepton + ' && ' + 
          'abs(lep1PdgId) == 13')

gjet_noBVeto = str(allCut + ' && ' + 
           metCut + ' && ' + 
           leptonVeto + ' && ' + 
           GTrigger + ' && ' + 
           singlePhoton)

signal_noBVeto = str(allCut + ' && ' + 
             metCut + ' && ' + 
             leptonVeto + ' && ' + 
             photonVeto)

signal = signal_noBVeto + ' && ' + bVeto
Zmm = Zmm_noBVeto + ' && ' + bVeto
Zee = Zee_noBVeto + ' && ' + bVeto
Wmn = Wmn_noBVeto + ' && ' + bVeto
Wen = Wen_noBVeto + ' && ' + bVeto
gjet = gjet_noBVeto + ' && ' + bVeto

Zll = '((' + Zee + ') || (' + Zmm + '))'
Wln = '((' + Wen + ') || (' + Wmn + '))'

top = str(allCut + ' && ' +
          photonVeto + ' && ' +
          metCut + ' && ' +
          topregion)

categoryCuts = {
    'monoJet_inc' : monoJet,
    'monoV' : monoV,
    'monoJet' : monoJet + ' && !(' + monoVeto + ')',
    }

regionCuts = {
    'signal_noBVeto' : signal_noBVeto,
    'Zmm_noBVeto' : Zmm_noBVeto,
    'Zee_noBVeto' : Zee_noBVeto,
    'Wmn_noBVeto' : Wmn_noBVeto,
    'Wen_noBVeto' : Wen_noBVeto,
    'gjets_noBVeto' : gjet_noBVeto,
    'signal' : signal,
    'Zmm' : Zmm,
    'Zee' : Zee,
    'Wmn' : Wmn,
    'Wen' : Wen,
    'gjets' : gjet,
    'Zll' : Zll,
    'Wln' : Wln,
    'tt'  : top
    }

#defaultMCWeight = 'mcFactors * postfit'
defaultMCWeight = 'mcFactors'

additionKeys = ['signal','Zmm','Wmn','tt']
additions    = { # key : [Data,MC]
    'signal' :  [METTrigger,'METTrigger'],
    'Zmm' :     [METTrigger,'METTrigger'],
    'Wmn' :     [METTrigger,'METTrigger'],
    'tt'  :     [METTrigger,'METTrigger'],
    'default' : ['1',defaultMCWeight]
    }

def cut(category, region):
    return '((' + categoryCuts[category] + ') && (' + regionCuts[region] + '))'

def dataMCCuts(region, isData):
    key = 'default'
    index = 1
    if region in additionKeys:
        key = region

    if isData:
        index = 0

    if key == 'default' or index == 0:
        return '(' + additions[key][index] + ')'
    else:
        return '((' + additions[key][index] + ')*(' + defaultMCWeight + '))'
