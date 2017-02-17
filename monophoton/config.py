import os

# tier3 set up
skimDir = '/data/t3home000/' + os.environ['USER'] + '/studies/test/skim'
histDir = '/data/t3home000/' + os.environ['USER'] + '/studies/test'
ntuplesDir = '/mnt/hadoop/scratch/yiiyama/panda'
dataNtuplesDir = ntuplesDir
photonSkimDir = '/data/t3home000/yiiyama/studies/test/photonskim'

libobjs = 'libPandaTreeObjects.so'
libutils = 'libPandaTreeUtils.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/PandaTree'
