from cuts import *

VBFSelection = 'jot1Pt > 80 && jot2Pt > 30'

def new_cut(category, region):
    return '((' + categoryCuts[category] + ') && (' + regionCuts[region] + ') && !(' + VBFSelection + '))'

cut = new_cut
