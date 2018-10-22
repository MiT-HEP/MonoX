import importlib
import logging

import config

logger = logging.getLogger(__name__)

params = importlib.import_module('configs.' + config.config + '.params')

######################
## Selector control ##
######################

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
                entry = sel

            for mod in mods:
                entry = (entry[0], ApplyModifier(entry[1], mod))

            result.append(entry)
    
        return result

#######################
## Utility functions ##
#######################

# avoid auto-deletion by python
_garbage = []

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

######################
## Common modifiers ##
######################

def addPUWeight(sample, selector):
    pufileName = params.pureweight

    pudir = ROOT.gROOT.GetDirectory('puweight')

    if not pudir:
        pudir = ROOT.gROOT.mkdir('puweight')
        logger.info('Loading PU weights from %s', pufileName)
        f = ROOT.TFile.Open(pufileName)
        for k in f.GetListOfKeys():
            if k.GetName().startswith('puweight_'):
                logger.info('Saving PU weights %s into ROOT/%s', k.GetName(), 'puweight')
                pudir.cd()
                obj = k.ReadObj().Clone(k.GetName().replace('puweight_', ''))
                _garbage.append(obj)
        
        f.Close()

    for hist in pudir.GetList():
        if hist.GetName() in sample.fullname:
            logger.info('Using PU weights %s/%s for %s', 'puweight', hist.GetName(), sample.name)
            selector.addOperator(ROOT.PUWeight(hist))
            break
    else:
        raise RuntimeError('Pileup profile for ' + sample.name + ' not defined')

################################
## Common modifier generators ##
################################

def ptTruncator(minimum = 0., maximum = -1.):
    def addPtCut(sample, selector):
        truncator = ROOT.PhotonPtTruncator()
        truncator.setPtMin(minimum)
        if maximum > 0.:
            truncator.setPtMax(maximum)

        selector.addOperator(truncator, 0)

    return addPtCut

def htTruncator(minimum = 0., maximum = -1.):
    def addHtCut(sample, selector):
        truncator = ROOT.HtTruncator()
        truncator.setHtMin(minimum)
        if maximum > 0.:
            truncator.setHtMax(maximum)

        selector.addOperator(truncator, 0)

    return addHtCut

def genBosonPtTruncator(minimum = 0., maximum = -1.):
    def addGenBosonPtCut(sample, selector):
        truncator = ROOT.GenBosonPtTruncator()
        truncator.setPtMin(minimum)
        if maximum > 0.:
            truncator.setPtMax(maximum)

        selector.addOperator(truncator, 0)

    return addGenBosonPtCut

