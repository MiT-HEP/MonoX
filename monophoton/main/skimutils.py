import logging

logger = logging.getLogger(__name__)

class ApplyModifier(object):
    def __init__(self, selector, modifier):
        self.selector = selector
        self.modifier = modifier

    def __call__(self, sample, rname):
        return self.modifier(self.selector(sample, rname))

class MakeSelectors(object):
    """
    Apply modifier functions to selector configurations
    """

    def __init__(self, selectors):
        self.selectors = selectors

    def __call__(self, sels, *mods):
        """
        @param sels    String name of the selector function, (name, function name), or (name, ApplyModifier)
        @param mods    Modifier functions
        """
    
        result = []
        for sel in sels:
            if type(sel) is str:
                entry = (sel, getattr(self.selectors, sel))
            else:
                name = sel[0]
                if type(sel[1]) is str:
                    fct = getattr(self.selectors, sel[1])
                else:
                    fct = sel[1]

                entry = (sel, fct)

            for mod in mods:
                entry = (entry[0], ApplyModifier(entry[1], mod))

            result.append(entry)
    
        return result

# avoid auto-deletion by python
_garbage = []

# Other weights
def getFromFile(path, name, newname = ''):
    import ROOT

    if newname == '':
        newname = name

    obj = ROOT.gROOT.Get(newname)
    if obj:
        return obj

    f = ROOT.TFile.Open(path)
    orig = f.Get(name)
    if not orig:
        return None

    ROOT.gROOT.cd()
    obj = orig.Clone(newname)

    f.Close()

    logger.debug('Picked up %s from %s', name, path)
    
    _garbage.append(obj)

    return obj
