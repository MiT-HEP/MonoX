import os

# location of source panda files
ntuplesDir = '/mnt/hadoop/cms/store/user/paus'
# ntuplesDir = '/mnt/hadoop/scratch/yiiyama/pandaf' # for dph only

# location of skim output from ssw2
skimDir = '/mnt/hadoop/scratch/' + os.environ['USER'] + '/monophoton/skim'
# optionally copy to a local disk to speed up
localSkimDir = '/local/' + os.environ['USER'] + '/monophoton/skim'

# where the various output plots and text files
histDir = '/data/t3home000/' + os.environ['USER'] + '/monophoton'

# panda library
libobjs = 'libPandaTreeObjects.so'
