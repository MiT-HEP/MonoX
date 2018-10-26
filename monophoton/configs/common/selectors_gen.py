import importlib

import config

params = importlib.import_module('configs.' + config.config + '.params')

###############
## Modifiers ##
###############

def addPDFVariation(sample, selector):
    if 'amcatnlo' in sample.fullname or 'madgraph' in sample.fullname: # ouh la la..
        logger.info('Adding PDF variation for %s', sample.name)
        if 'znng' in sample.name or 'zllg' in sample.name:
            pdf = ROOT.NNPDFVariation()
            pdf.setRescale(0.0420942143487 / 0.0769709934685)
            selector.addOperator(pdf)
        elif 'wnlg' in sample.name or 'wglo' in sample.name:
            pdf = ROOT.NNPDFVariation()
            pdf.setRescale(0.0453828335472 / 0.0933792628506)
            selector.addOperator(pdf)
        else:
            selector.addOperator(ROOT.NNPDFVariation())

def addGenPhotonVeto(sample, selector):
    veto = ROOT.GenPhotonVeto()
    veto.setMinPt(130.)
    veto.setMinPartonDR(0.5)

    selector.addOperator(veto, 0)

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

#########################
## Modifier generators ##
#########################

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

