def build_selection(selection,bin0):

    selections = ['signal','Zmm','Wmn','gjets','Zee','Wen']
    
    snippets = {

        #** monojet
        'leading jet pT' :['jet1Pt>100.',selections],
        'leading jet eta':['abs(jet1Eta)<2.5',selections],
        'jet cleaning'   :['jet1isMonoJetId==1',selections],
        #'deltaPhi'       :['abs(minJetMetDPhi)>0.5',['signal']],
        #'deltaPhi'       :['abs(jet1DPhiMet)>0.4',['signal']],
        #'tau veto'       :['n_tau==0',selections], 
        'lepton veto'    :['n_looselep==0',['signal','gjets']],
        'pho veto'       :['n_loosepho==0',['signal','Zmm','Wmn','Zee','Wen']],
        'btag veto'      :['n_bjetsMedium==0',selections],
        
        #** Control Regions
        #'trigger' : ['(triggerFired[0]==1)',['signal','Zmm','Wmn']],
        #'triggerM' : ['(triggerFired[5]==1 || triggerFired[6]==1 )',['Zmm','Wmn']],
        'triggerE' : ['(triggerFired[3]==1)',['Zee','Wen']],
        #'triggerG' : ['(triggerFired[7]==1 || triggerFired[8]==1 || triggerFired[9]==1)',['gjets']],
        'leading lep ID': ['n_tightlep > 0',['Wmn','Zmm','Wen','Wee']], 
        'Zmm'  : ['n_looselep == 2 && abs(dilep_m - 91) < 30 && (lep1PdgId*lep2PdgId == -169)',['Zmm']],
        'Zee'  : ['n_tightlep == 2 && abs(dilep_m - 91) < 30 && (lep1PdgId*lep2PdgId == -121)',['Zee']],
        'Wmn'  : ['n_looselep == 1 && abs(lep1PdgId)==13 ',['Wmn']],
        'Wen'  : ['n_looselep == 1 && abs(lep1PdgId)==11 && abs(minJetUWDPhi)>0.5 && trueMet>40.',['Wen']],
        'gjets': ['photonPt > 175 && abs(photonEta) < 1.47  && n_tightpho == 1',['gjets']],        

        }

    selectionString = ''
    for cut in snippets:
        if selection in snippets[cut][1]: 
            selectionString += snippets[cut][0]+'&&'

    met  = 'met'
    metZ = 'u_magZ' 
    metW = 'u_magW'
    metG = 'u_magPho'

    analysis_bin = {}
    analysis_bin[0] = bin0

    if selection.find('Zmm')>-1 or selection.find('Zee')>-1: selectionString+=metZ+'>'+str(analysis_bin[0])
    elif selection.find('Wmn')>-1 or selection.find('Wen')>-1: selectionString+=metW+'>'+str(analysis_bin[0])
    elif selection.find('gjets')>-1: selectionString+=metG+'>'+str(analysis_bin[0])
    else: selectionString+=met+'>'+str(analysis_bin[0])

    return selectionString

