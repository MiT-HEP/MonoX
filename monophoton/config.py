skimDir = '/scratch5/yiiyama/studies/monophoton/skim'
histDir = '/scratch5/yiiyama/studies/monophoton'
ntuplesDir = '/scratch5/yiiyama/hist/simpletree17/t2mit/'
dataNtuplesDir = ntuplesDir # when updating only data trees etc.
phskimDir = '/scratch5/yiiyama/hist/simpletree13c/phskim/'

import os
basedir = os.path.dirname(os.path.realpath(__file__))

#libsimpletree = basedir + '/MitFlat/DataFormats/obj/libsimpletree.so'
#dataformats = basedir + '/MitFlat/DataFormats'

libsimpletree = 'libMitFlatDataFormats.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats'
