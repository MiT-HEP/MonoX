skimDir = '/scratch5/yiiyama/studies/monophoton16/skim'
#skimDir = '/scratch5/yiiyama/studies/monophoton/skim'
histDir = '/scratch5/yiiyama/studies/monophoton16'
ntuplesDir = '/scratch5/yiiyama/hist/simpletree18/t2mit/'
dataNtuplesDir = ntuplesDir
photonSkimDir = '/scratch5/yiiyama/hist/simpletree18/photonskim/'

import os
basedir = os.path.dirname(os.path.realpath(__file__))

libsimpletree = 'libMitFlatDataFormats.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats'
