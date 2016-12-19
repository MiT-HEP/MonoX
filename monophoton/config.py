import os

# tier3 set up
skimDir = '/data/t3home000/ballen/hist/monophoton/skim'
histDir = '/data/t3home000/ballen/hist/monophoton'
ntuplesDir = '/data/t3serv014/yiiyama/hist/simpletree19/t2mit/'
dataNtuplesDir = ntuplesDir
photonSkimDir = '/data/t3home000/yiiyama/simpletree19/photonskim_newCH'

libsimpletree = 'libMitFlatDataFormats.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats'
