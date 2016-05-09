skimDir = '/scratch5/ballen/hist/monophoton/skim'
histDir = '/home/ballen/cms/root'
ntuplesDir = '/scratch5/yiiyama/hist/simpletree12/t2mit/filefi/042/'
phskimDir = '/scratch5/yiiyama/hist/simpletree12/phskim/'

import os
thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

libsimpletree = 'libMitFlatDataFormats.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats'
