skimDir = '/afs/cern.ch/user/b/ballen/cms/hist/monophoton/skim/2016'
histDir = '/home/ballen/cms/hist'
# ntuplesdDir = '/afs/cern.ch/user/b/ballen/eos/cms/store/user/zdemirag/'
ntuplesDir = '/eos/cms/store/user/zdemirag/'
# ntuplesDir = '/afs/cern.ch/user/b/ballen/cernbox/user/s/snarayan/'
dataNtuplesDir = ntuplesDir 
photonSkimDir = ''

import os
basedir = os.path.dirname(os.path.realpath(__file__))

import json
# 274421 ~ june 10 ~ 2.3/fb unblind - fully unblinded
# 274443 ~ june 16 ~ 2.8/fb unblind - 2.4/fb blind
# 275125 ~ june 22 ~ 4.1/fb unblind - 2.7/fb blind
# 275583 ~ july 08 ~ 5.5/fb unblund - !! not full json lumi
blindCutOff = '274421'
runCutOff = '275583'
jsonLumi = 0.
jsonLumiBlinded = 0.
with open(basedir + '/data/lumis.txt') as lumiFile:
    lumiList = json.load(lumiFile)

for run in lumiList:
    if int(run) > int(runCutOff):
        continue
    jsonLumi += lumiList[run]["integrated"]
    if int(run) > int(blindCutOff):
        jsonLumiBlinded += lumiList[run]["integrated"] / 4.
    else:
        jsonLumiBlinded += lumiList[run]["integrated"]

# Temporary fix to match lumis used at preapproval
# jsonLumiBlinded = 2182.5
# jsonLumi = 2566.7

# libsimpletree = 'libMitFlatDataFormats.so'
libsimpletree = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/obj/libsimpletree.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats'

libnerocore = 'libNeroProducerCore.so'
nerocorepath = os.environ['CMSSW_BASE'] + '/src/NeroProducer/Core/'


