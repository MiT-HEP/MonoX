import os

# tier3 set up
skimDir = '/mnt/hadoop/scratch/' + os.environ['USER'] + '/monophoton/skim'
histDir = '/data/t3home000/' + os.environ['USER'] + '/studies/monophoton_panda'
ntuplesDir = '/mnt/hadoop/cms/store/user/paus'
#ntuplesDir = '/mnt/hadoop/scratch/yiiyama'
dataNtuplesDir = ntuplesDir

#libobjs = os.environ['CMSSW_BASE'] + '/src/PandaTree/lib/libpanda.so'
libobjs = 'libPandaTreeObjects.so'
libutils = 'libPandaTreeUtils.so'
dataformats = os.environ['CMSSW_BASE'] + '/src/PandaTree'
