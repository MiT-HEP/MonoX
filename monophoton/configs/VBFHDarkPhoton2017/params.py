import os

_localdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(os.path.dirname(_localdir))

lumilist = basedir + '/data/lumis17_plain.txt'
datasetlist = basedir + '/data/datasets17.csv'

effectivelumi = {
    #'vbfTrigger': {
    #    'sph-17b': 0.
    #}
}

pureweight = basedir + '/data/pileup17.root'
