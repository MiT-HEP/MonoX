from cuts import *

VBFSelection = 'IsVBF == 1'

def new_cut(category, region):
    return '((' + categoryCuts[category] + ') && (' + regionCuts[region] + ') && !(' + VBFSelection + '))'

cut = new_cut
