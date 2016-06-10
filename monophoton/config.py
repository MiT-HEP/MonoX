skimDir = '/scratch5/ballen/hist/monophoton/skim/2016'
histDir = '/home/ballen/cms/root'
ntuplesDir = '/scratch5/ballen/hist/simpletree17/t2mit/'
dataNtuplesDir = ntuplesDir # .replace('13c', '14') 
phskimDir = '/scratch5/ballen/hist/simpletree17/phskim/'
webDir = '/home/ballen/public_html/cmsplots/monophoton'

import os
basedir = os.path.dirname(os.path.realpath(__file__))

# libsimpletree = 'libMitFlatDataFormats.so'
# dataformats = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats'

libsimpletree = basedir + '/MitFlat/DataFormats/obj/libsimpletree.so'
dataformats = basedir + '/MitFlat/DataFormats'
