import os

config = 'Monophoton2016'

# location of skim output from ssw2
skimDir = '/mnt/hadoop/scratch/' + os.environ['USER'] + '/' + config + '/skim'

# optionally copy to a local disk to speed up
localSkimDir = '/local/' + os.environ['USER'] + '/' + config + '/skim'

# where the various output plots and text files
histDir = '/data/t3home000/' + os.environ['USER'] + '/' + config

# panda library
libobjs = 'libPandaTreeObjects.so'
