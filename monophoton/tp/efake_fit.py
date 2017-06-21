#!/usr/bin/env python

import sys
import os
import array
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
import utils
from datasets import allsamples
from tp.efake_conf import skimConfig, lumiSamples, outputDir, roofitDictsDir, getBinning
import tp.efake_plot as efake_plot

dataType = sys.argv[1] # "data" or "mc"
binningName = sys.argv[2] # see efake_conf

dataSource = 'sph' # sph or sel
# panda::XPhoton::IDTune
itune = 2

#tpconfs = ['ee', 'eg', 'pass', 'fail']
tpconfs = ['ee', 'eg']

monophSel = 'probes.mediumX[][%d] && probes.mipEnergy < 4.9 && TMath::Abs(probes.time) < 3. && probes.sieie > 0.001 && probes.sipip > 0.001' % itune

fitBins = getBinning(binningName)[2]

lumi = sum(allsamples[s].lumi for s in lumiSamples)

efake_plot.lumi = lumi
efake_plot.plotDir = 'efake/fit_' + binningName

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load('libRooFit.so')
ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')
ROOT.gSystem.Load(roofitDictsDir + '/libCommonRooFit.so') # defines KeysShape

### Files ###

outputName = outputDir + '/fityields_' + dataType + '_' + binningName + '.root'

tmpOutName = '/tmp/' + os.environ['USER'] + '/efake/' + os.path.basename(outputName)
try:
    os.makedirs(os.path.dirname(tmpOutName))
except OSError:
    pass

if os.path.exists(outputName):
    # make a backup
    shutil.copy(outputName, outputName.replace('.root', '_old.root'))

outputFile = ROOT.TFile.Open(tmpOutName, 'recreate')

### Setup ###

print 'Starting common setup.'

fitBinningT = (120, 60., 120.)
fitBinning = ROOT.RooUniformBinning(fitBinningT[1], fitBinningT[2], fitBinningT[0])
compBinning = ROOT.RooUniformBinning(81., 101., 20)

initVals = {
    'nbkg': 100.,
    'nsignal': 100.
}
if dataType == 'data':
    initVals.update({
        'mZ': 91.2,
        'gammaZ': 2.5,
        'm0': 0.,
        'sigma': 1.,
        'alpha': 2.,
        'n': 1.5
    })

# template of templates. used in both runModes
template = ROOT.TH1D('template', '', *fitBinningT)

# workspace
work = ROOT.RooWorkspace('work', 'work')

# convenience
def addToWS(obj):
    fcn = getattr(work, 'import')
    if obj.InheritsFrom(ROOT.RooAbsData.Class()):
        # need a dummy argument to execute the correct overload
        fcn(obj, ROOT.RooFit.Rename(obj.GetName()))
    else:
        fcn(obj, ROOT.RooFit.Silence())

mass = work.factory('mass[60., 120.]')
mass.setUnit('GeV')
mass.setBinning(fitBinning, 'fitWindow')
mass.setBinning(compBinning, 'compWindow')

weight = work.factory('weight[-1000000000., 1000000000.]')
ntarg = work.factory('ntarg[0., 100000000.]')
nbkg = work.factory('nbkg[0., 100000000.]')
nsignal = work.factory('nsignal[0., 100000000.]')
nZ = work.factory('nZ[0., 100000000.]')
mZ = work.factory('mZ[91.2, 86., 96.]')
gammaZ = work.factory('gammaZ[2.5, 1., 5.]')
m0 = work.factory('m0[-10., 10.]')
sigma = work.factory('sigma[0.001, 5.]')
alpha = work.factory('alpha[0.01, 5.]')
n = work.factory('n[1.01, 5.]')

tpconf = work.factory('tpconf[ee=0, eg=1, pass=2, fail=3]')
binName = work.factory('binName[]')
for ibin, (bin, _) in enumerate(fitBins):
    binName.defineType(bin, ibin)

# smearing parameters are unused in dataType == mc but we'll just leave them here
nompset = ROOT.RooArgSet(tpconf, binName, ntarg, nbkg, nsignal, nZ, mZ, gammaZ, m0)
nompset.add(sigma)
nompset.add(alpha)
nompset.add(n)
altsigpset = ROOT.RooArgSet(tpconf, binName, nbkg, nsignal, mZ, gammaZ)
altbkgpset = ROOT.RooArgSet(tpconf, binName, nbkg, nsignal, mZ, gammaZ, m0)
altbkgpset.add(sigma)
altbkgpset.add(alpha)
altbkgpset.add(n)

nomparams = ROOT.RooDataSet('params_nominal', 'Nominal params', nompset)
altsigparams = ROOT.RooDataSet('params_altsig', 'Altsig params', altsigpset)
altbkgparams = ROOT.RooDataSet('params_altbkg', 'Altbkg params', altbkgpset)

print 'Finished common setup.'

### Fill template histograms ###

print 'Starting template preparation.'

# templates setup
egPlotter = ROOT.MultiDraw()
mgPlotter = ROOT.MultiDraw()

if dataType == 'data':
    egPlotter.setWeightBranch('')
    mgPlotter.setWeightBranch('')

    # target samples
    if dataSource == 'sph':
        egSamp = 'phdata'
        mgSamp = 'phdata'
    else:
        egSamp = 'eldata'
        mgSamp = 'mudata'

    for sname in skimConfig[egSamp][0]:
        egPlotter.addInputPath(utils.getSkimPath(sname, 'tpeg'))

    for sname in skimConfig[mgSamp][0]:
        mgPlotter.addInputPath(utils.getSkimPath(sname, 'tpmg'))

    if dataSource == 'sel':
        egPlotter.setBaseSelection('tags.pt_ > 40.')
        mgPlotter.setBaseSelection('tags.pt_ > 40.')

    mcSource = ROOT.TFile.Open(outputDir + '/fityields_mc_' + binningName + '.root')
    mcWork = mcSource.Get('work')

else:
    trigsource = ROOT.TFile.Open(basedir + '/data/trigger_efficiency.root')
    eleTrigEff = trigsource.Get('electron_sel/leppt/el27_eff')
    muTrigEff = trigsource.Get('muon_smu/leppt/mu24ortrk24_eff')
    if not eleTrigEff or not muTrigEff:
        raise RuntimeError('Trigger efficiency source not found')

    egPlotter.setConstantWeight(lumi)
    mgPlotter.setConstantWeight(lumi)
    
    for sname in skimConfig['mc'][0]:
        egPlotter.addInputPath(utils.getSkimPath(sname, 'tpeg'))
        mgPlotter.addInputPath(utils.getSkimPath(sname, 'tpmg'))

    egPlotter.setReweight('tags.pt_', eleTrigEff)
    mgPlotter.setReweight('tags.pt_', muTrigEff)

    if dataSource == 'sel':
        egPlotter.setBaseSelection('tags.pt_ > 40.')
        mgPlotter.setBaseSelection('tags.pt_ > 40.')

#    for sname in skimConfig['mcgg'][0]:
#        egPlotter.addInputPath(utils.getSkimPath(sname, 'tpeg'))

objects = []

# fill templates
outputFile.cd()
for bin, fitCut in fitBins:
    if dataType == 'mc':
        hsig = template.Clone('sig_' + bin)
        objects.append(hsig)
        egPlotter.addPlot(hsig, 'tp.mass', fitCut + ' && TMath::Abs(probes.matchedGenId) == 11 && sample == 1')

    for conf in tpconfs:
        suffix = conf + '_' + bin

        htarg = template.Clone('target_' + suffix)
        objects.append(htarg)
        # unbinned fit
        # ttarg = ROOT.TTree('target_' + suffix, 'target')
        # objects.append(ttarg)

        if conf == 'ee':
            # target is a histogram with !csafeVeto
            # perform binned max L fit
            cut = 'probes.mediumX[][{itune}] && !probes.csafeVeto && ({fitCut})'.format(itune = itune, fitCut = fitCut)
        elif conf == 'eg':
            # target is a tree with pixelVeto
            # also perform binned max L fit
            cut = 'probes.mediumX[][{itune}] && probes.pixelVeto && ({fitCut})'.format(itune = itune, fitCut = fitCut)
        elif conf == 'pass':
            cut = '({monophSel}) && ({fitCut})'.format(monophSel = monophSel, fitCut = fitCut)
        elif conf == 'fail':
            cut = '!({monophSel}) && ({fitCut})'.format(monophSel = monophSel, fitCut = fitCut)
        else:
            cut = '({fitCut})'.format(fitCut = fitCut)

        egPlotter.addPlot(htarg, 'tp.mass', cut)
        # if doing unbinned fits, make a tree
        # egPlotter.addTree(ttarg, cut)
        # egPlotter.addTreeBranch(ttarg, 'mass', 'tp.mass')

        if conf == 'eg' or conf == 'ee':
            # background is approximately lepton flavor symmetric - will use muon templates
            hbkg = template.Clone('bkg_' + suffix)
            objects.append(hbkg)
            tbkg = ROOT.TTree('bkgtree_' + suffix, 'background')
            objects.append(tbkg)
    
            mgPlotter.addPlot(hbkg, 'tp.mass', cut + ' && !probes.hasCollinearL')
            mgPlotter.addTree(tbkg, cut + ' && !probes.hasCollinearL')
            mgPlotter.addTreeBranch(tbkg, 'mass', 'tp.mass')

        if dataType == 'mc':
            hmcbkg = template.Clone('mcbkg_' + suffix)
            objects.append(hmcbkg)
            tmcbkg = ROOT.TTree('mcbkgtree_' + suffix, 'truth background')
            objects.append(tmcbkg)

            egPlotter.addPlot(hmcbkg, 'tp.mass', cut + ' && !(TMath::Abs(probes.matchedGenId) == 11 && sample == 1)')
            egPlotter.addTree(tmcbkg, cut + ' && !(TMath::Abs(probes.matchedGenId) == 11 && sample == 1)')
            egPlotter.addTreeBranch(tmcbkg, 'mass', 'tp.mass')

egPlotter.fillPlots()
mgPlotter.fillPlots()

outputFile.cd()
outputFile.Write()

print 'Finished template preparation.'

### Run fits ###

# fit variables
massset = ROOT.RooArgSet(mass) # for convenience
masslist = ROOT.RooArgList(mass) # for convenience

for bin, fitCut in fitBins:
    print 'Run fits for', bin

    binName.setLabel(bin)

    sigModelName = 'sigModel_' + bin
    sigDataName = 'sigData_' + bin

    if dataType == 'mc':
        # get signal template
        hsig = outputFile.Get('sig_' + bin)

        sigData = ROOT.RooDataHist('sigData_' + bin, 'sig', masslist, hsig)
        addToWS(sigData)

        # no smearing
        sigModel = work.factory('HistPdf::sigModel_{bin}({{mass}}, sigData_{bin}, 2)'.format(bin = bin))

    else:
        if dataSource == 'sph':
            altsigModel = work.factory('BreitWigner::altsigModel_{bin}(mass, mZ, gammaZ)'.format(bin = bin))

        elif dataSource == 'sel':
            sigData = mcWork.data(sigDataName)
            if not sigData:
                print 'No dataset ' + sigDataName + ' found in ' + mcSource.GetName() + '.'
                sys.exit(1)

            addToWS(sigData)

            altsigModel = work.factory('HistPdf::altsigModel_{bin}({{mass}}, sigData_{bin}, 2)'.format(bin = bin))

        addToWS(altsigModel)

        res = work.factory('CBShape::res(mass, m0, sigma, alpha, n)')
        sigModel = work.factory('FCONV::sigModel_{bin}(mass, altsigModel_{bin}, res)'.format(bin = bin))

    print 'Made sigModel_' + bin

    intComp = sigModel.createIntegral(massset, 'compWindow')
    intFit = sigModel.createIntegral(massset, 'fitWindow')

    for conf in tpconfs:
        tpconf.setLabel(conf)

        suffix = conf + '_' + bin

        htarg = outputFile.Get('target_' + suffix)
        print 'htarg limits:', htarg.GetXaxis().GetXmin(), htarg.GetXaxis().GetXmax(), htarg.GetSumOfWeights()

        ntarg.setVal(htarg.GetSumOfWeights())
        
        targHist = ROOT.RooDataHist('target_' + suffix, 'target', masslist, htarg)
        targ = targHist

# unbinned fit
#        ttarg = outputFile.Get(targName)
#        if dataType == 'mc':
#            targ = ROOT.RooDataSet(targName, 'target', ttarg, ROOT.RooArgSet(mass, weight), '', 'weight')
#        else:
#            targ = ROOT.RooDataSet(targName, 'target', ttarg, ROOT.RooArgSet(mass))

        addToWS(targ)

        print 'Made target_' + suffix

        tbkg = outputFile.Get('bkgtree_' + suffix)

        if dataType == 'mc':
            altbkgModel = ROOT.KeysShape('altbkgModel_' + suffix, 'altbkgModel', mass, tbkg, 'weight', 0.3, 8)
            addToWS(altbkgModel)

            tmcbkg = outputFile.Get('mcbkgtree_' + suffix)
            bkgModel = ROOT.KeysShape('bkgModel_' + suffix, 'bkgModel', mass, tmcbkg, 'weight', 0.3, 8)
            addToWS(bkgModel)

            hmubkg = altbkgModel.createHistogram('hmubkg', mass, ROOT.RooFit.Binning(fitBinning))
            hmubkg.SetName('hmubkg_' + suffix)
            hmubkg.Scale(1. / hmubkg.GetSumOfWeights())
            helbkg = bkgModel.createHistogram('helbkg', mass, ROOT.RooFit.Binning(fitBinning))
            helbkg.SetName('helbkg_' + suffix)
            helbkg.Scale(1. / helbkg.GetSumOfWeights())

            elmuscale = helbkg.Clone('elmuscale_' + suffix)
            elmuscale.Divide(hmubkg)

            outputFile.cd()
            hmubkg.SetDirectory(outputFile)
            hmubkg.Write()
            helbkg.SetDirectory(outputFile)
            helbkg.Write()
            elmuscale.SetDirectory(outputFile)
            elmuscale.Write()

            scaleHist = ROOT.RooDataHist('elmuscaleData_' + suffix, 'elmuscale', masslist, elmuscale)
            scalePdf = ROOT.RooHistPdf('elmuscale_' + suffix, 'elmuscale', massset, scaleHist, 2)
            addToWS(scaleHist)
            addToWS(scalePdf)

        else:
            altbkgModel = ROOT.KeysShape('altbkgModel_' + suffix, 'altbkgModel', mass, tbkg, '', 0.3, 8)
            addToWS(altbkgModel)

            scalePdf = mcWork.pdf('elmuscale_' + suffix)
            addToWS(scalePdf)

            bkgModel = work.factory('PROD::bkgModel_{suffix}(altbkgModel_{suffix}, elmuscale_{suffix})'.format(suffix = suffix))
            addToWS(bkgModel)

        print 'Made bkgModel_' + suffix

        # full fit PDF
        model = work.factory('SUM::model_{suffix}(nbkg * bkgModel_{suffix}, nsignal * sigModel_{bin})'.format(suffix = suffix, bin = bin))
        addToWS(model)

        print 'Made model_' + suffix

        if dataType == 'mc':
            hmcbkg = outputFile.Get('mcbkg_' + suffix)
        else:
            hmcbkg = None

        # nominal fit
        mZ.setConstant()
        gammaZ.setConstant()

        for vname, val in initVals.items():
            work.var(vname).setVal(val)
        nsignal.setVal(targ.sumEntries() * 0.9)
    
        model.fitTo(targ, ROOT.RooFit.SumW2Error(True), ROOT.RooFit.Save(True))

        nZ.setVal(nsignal.getVal() * (intComp.getVal() / intFit.getVal()))

        nomparams.add(nompset)

        efake_plot.plotFit(mass, targHist, model, dataType, suffix, hmcbkg = hmcbkg, alt = '')

        # altbkg fit
        model = work.factory('SUM::model_altbkg_{suffix}(nbkg * altbkgModel_{suffix}, nsignal * sigModel_{bin})'.format(suffix = suffix, bin = bin))

        for vname, val in initVals.items():
            work.var(vname).setVal(val)
        nsignal.setVal(targ.sumEntries() * 0.9)
    
        model.fitTo(targ, ROOT.RooFit.SumW2Error(True), ROOT.RooFit.Save(True))

        altbkgparams.add(altbkgpset)

        efake_plot.plotFit(mass, targHist, model, dataType, suffix, bkgModel = 'altbkgModel', hmcbkg = hmcbkg, alt = 'altbkg')

        if dataType == 'data':
            # altsig fit
            mZ.setConstant(False)
            gammaZ.setConstant(False)
    
            model = work.factory('SUM::model_altsig_{suffix}(nbkg * bkgModel_{suffix}, nsignal * altsigModel_{bin})'.format(suffix = suffix, bin = bin))
    
            for vname, val in initVals.items():
                work.var(vname).setVal(val)
            nsignal.setVal(targ.sumEntries() * 0.9)
        
            model.fitTo(targ, ROOT.RooFit.SumW2Error(True), ROOT.RooFit.Save(True))
    
            altsigparams.add(altsigpset)
    
            efake_plot.plotFit(mass, targHist, model, dataType, suffix, hmcbkg = hmcbkg, alt = 'altsig')

addToWS(nomparams)
addToWS(altsigparams)
addToWS(altbkgparams)

outputFile.cd()
work.Write()

work = None
outputFile.Close()

shutil.copy(tmpOutName, outputName)
