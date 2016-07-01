skimDir = '/afs/cern.ch/user/b/ballen/cms/hist/monophoton/skim/2016'
histDir = '/home/ballen/cms/hist'
ntuplesDir = '/afs/cern.ch/user/b/ballen/eos/cms/store/user/zdemirag/'
# ntuplesDir = '/afs/cern.ch/user/b/ballen/cernbox/user/s/snarayan/'
dataNtuplesDir = ntuplesDir 
photonSkimDir = ''

import os
basedir = os.path.dirname(os.path.realpath(__file__))

libsimpletree = 'libMitFlatDataFormats.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats'

libnerocore = 'libNeroProducerCore.so'
nerocorepath = os.environ['CMSSW_BASE'] + '/src/NeroProducer/Core/'


