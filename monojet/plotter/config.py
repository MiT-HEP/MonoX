# Pick one of these three. 
# Cannot run all at the same time because they open different sets of files

channel_list  = ['signal']
#channel_list  = ['Wmn','Zmm']
#channel_list  = ['Wen','Zee']
#channel_list  = ['gjets']

# This is where the plots are output
folder = '/afs/cern.ch/user/d/dabercro/www/monoV_160126'

# This is a list of variables plotted
variable_list = []
variable_list.append('met')
#variable_list.append('fatjet1tau21')
#variable_list.append('fatjet1PrunedM')
#variable_list.append('fatjet1SoftDropM')
#variable_list.append('dilep_m')
#variable_list.append('mt')

# Can be a list including any of the following:
# 'met'
# 'jetpt'
# 'jet2pt'
# 'lep1Pt'
# 'lep2Pt'
# 'lep1PdgId'
# 'lep2PdgId'
# 'jet1DPhiMet'
# 'dPhi_j1j2'
# 'njets'
# 'njetsclean'
# 'njets_linear'
# 'njetsclean_linear'
# 'n_looselep'
# 'n_loosepho'
# 'n_mediumpho'
# 'n_tau'
# 'n_bjetsMedium'
# 'npv'
# 'phoPt'
# 'phoPhi'
# 'metRaw'
# 'genmet'
# 'trueMet'
# 'mt'
# 'u_magW'
# 'dphilep_truemet'
# 'minJetMetDPhi'
# 'mt_new'
# 'dilep_m'
# 'dilep_pt'
# 'dRjlep'
# 'dRjlep2'
# 'dRplep'
# 'jet1Phi'
# 'phoEta'
# 'lep1Eta'
# 'dilepEta'
# 'jet1Eta'
# 'ht'
# 'ht_cleaned'
