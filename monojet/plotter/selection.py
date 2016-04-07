def build_selection(selection,bin0):

    selections = ['signal','Zmm','Wmn','gjets','Zee','Wen']
    
    snippets = {
        
        #** monojet
        'leading jet pT' :['jet1Pt>100.',selections],
        'leading jet eta':['abs(jet1Eta)<2.5',selections],        
#        'not monoV'      :['fatjet1PrunedM < 60 || fatjet1PrunedM > 110 || fatjet1tau21 > 0.5',selections],
        # Jet ID
        'jet cleaning'   :['jet1isMonoJetIdNew==1',selections],      
        'deltaPhi'       :['abs(minJetMetDPhi_withendcap)>0.5',['signal','Zmm','Wmn','Wen','gjets']],
        #'deltaPhi'       :['abs(minJetMetDPhi_clean)>0.65',['signal','Zmm','Wmn','Wen','gjets']],
        'tau veto'       :['n_tau==0',['signal','Zmm','Wmn','Wen','Zee']], 
        'lepton veto'    :['n_looselep==0',['signal','gjets']],
        'pho veto'       :['n_loosepho==0',['signal','Zmm','Wmn','Zee','Wen']],
        'btag veto'      :['n_bjetsMedium==0',selections],
        
        #'bins' : ['met<250.',selections],
        
        #** Control Regions

        'triggerSig' : ['(triggerFired[0]==1 || triggerFired[1]==1 || triggerFired[2]==1)',['signal','Zmm','Wmn']],        
        'triggerE' : ['(triggerFired[4]==1 || triggerFired[5]==1)',['Zee','Wen']],        
        'triggerG' : ['(triggerFired[11]==1 || triggerFired[12]==1 || triggerFired[13]==1)',['gjets']],
        'leading lep ID': ['n_tightlep > 0',['Wmn','Zmm','Wen','Wee']], 
        'Zmm'  : ['n_looselep == 2 && abs(dilep_m - 91) < 30 && (lep1PdgId*lep2PdgId == -169)',['Zmm']],
        'Zee'  : ['n_looselep == 2 && abs(dilep_m - 91) < 30 && (lep1PdgId*lep2PdgId == -121)',['Zee']],
        'Wmn'  : ['n_looselep == 1 && abs(lep1PdgId)==13 ',['Wmn']],
        'Wen'  : ['n_looselep == 1 && abs(lep1PdgId)==11 && trueMet>40.',['Wen']],

        'gjets': ['photonPt > 175 && abs(photonEta) < 1.4442 && n_mediumpho == 1 && n_loosepho == 1',['gjets']],                
        #'excitedquark' : ['n_cleanedjets==3',['gjets']],

        # monov
#        'monoV'    : ['fatjet1tau21 < 0.5 && fatjet1PrunedM > 60 && fatjet1PrunedM < 110',selections],
#        'monoVId'  : ['fatleading == 1 && fatjet1overlapB < 2',selections],
#        'monoVKin' : ['fatjet1Pt > 250 && fatjet1Eta < 2.5',selections]
        
        }

    selectionString = ''
    for cut in snippets:
        if selection in snippets[cut][1]: 
            selectionString += snippets[cut][0]+'&&'

    met  = 'met'

    analysis_bin = {}
    analysis_bin[0] = bin0

    selectionString+=met+'>'+str(analysis_bin[0])

    return selectionString

