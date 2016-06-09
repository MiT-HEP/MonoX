skimDir = '/afs/cern.ch/user/b/ballen/cms/hist/monophoton/skim/2016'
histDir = '/home/ballen/cms/root'
ntuplesDir = '/afs/cern.ch/user/b/ballen/eos/cms/store/user/zdemirag/'
dataNtuplesDir = ntuplesDir # .replace('13c', '14') 
phskimDir = '/scratch5/ballen/hist/simpletree17/phskim/'
webDir = '/afs/cern.ch/user/b/ballen/public_html/cmsplots/monophoton'

import os
basedir = os.path.dirname(os.path.realpath(__file__))

libsimpletree = 'libMitFlatDataFormats.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats'

libnerocore = 'libNeroProducerCore.so'
nerocorepath = os.environ['CMSSW_BASE'] + '/src/NeroProducer/Core/'

# libsimpletree = basedir + '/MitFlat/DataFormats/obj/libsimpletree.so'
# dataformats = basedir + '/MitFlat/DataFormats'
