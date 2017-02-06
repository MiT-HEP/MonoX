import os

# tier3 set up
skimDir = '/data/t3home000/' + os.environ['USER'] + '/studies/monophoton/skim'
histDir = '/data/t3home000/' + os.environ['USER'] + '/studies/monophoton'
ntuplesDir = '/data/t3serv014/yiiyama/hist/simpletree19/t2mit/'
dataNtuplesDir = ntuplesDir
photonSkimDir = '/mnt/hadoop/scratch/yiiyama/photonskim'

libsimpletree = 'libMitFlatDataFormats.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats'
