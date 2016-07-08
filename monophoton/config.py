skimDir = '/scratch5/ballen/hist/monophoton/skim/2016'
histDir = '/scratch5/ballen/hist/monophoton'
ntuplesDir = '/scratch5/yiiyama/hist/simpletree18/t2mit/'
dataNtuplesDir = ntuplesDir 
photonSkimDir = '/scratch5/yiiyama/hist/simpletree18/photonskim/'

import os
basedir = os.path.dirname(os.path.realpath(__file__))

# libsimpletree = 'libMitFlatDataFormats.so'
libsimpletree = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/obj/libsimpletree.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats'
