import os

_localdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(os.path.dirname(_localdir))

lumilist = basedir + '/data/lumis16_plain.txt'
datasetlist = basedir + '/data/datasets16.csv'

effectivelumi = {
    'vbfTrigger': {
        'sph-16b-m': 4778.,
        'sph-16c-m': 2430.,
        'sph-16d-m': 4044.,
        'sph-16e-m': 3284.,
        'sph-16f-m': 2292.,
        'sph-16g-m': 5190.,
        'sph-16h-m': 5470.
    }
}

pureweight = basedir + '/data/pileup16_vbf75.root'
