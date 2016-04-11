#!/usr/bin/env python

import sys
import os
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotconfig import SimpleCanvas

dataType = sys.argv[1] # "data" or "mc"
try:
    seed = sys.argv[2]
except IndexError:
    seed = 12345

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load('libRooFit.so')
ROOT.gROOT.LoadMacro(basedir + '/misc/StaticShape.cc+')
ROOT.gROOT.LoadMacro(basedir + '/misc/KeysShape.cc+')
ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
ROOT.gROOT.LoadMacro(thisdir + '/TemplateGenerator.cc+')

inputDir = '/scratch5/yiiyama/studies/egfake_skim'
outputDir = '/scratch5/yiiyama/studies/egfake'
if seed != 12345:
    outputName = outputDir + '/fityields_' + dataType + '_' + str(seed) + '.root'
else:
    outputName = outputDir + '/fityields_' + dataType + '.root'

canvas = SimpleCanvas(lumi = allsamples['sel-d3'].lumi + allsamples['sel-d4'].lumi, sim = (datamc == 'mc'))
canvas.titlePave.SetX2NDC(0.5)

fitBinning = ROOT.RooUniformBinning(60., 120., 60)
compBinning = ROOT.RooUniformBinning(81., 101., 20)

ptBinning = [40., 50., 60., 80., 100., 6500.]
#ptBinning = [100., 6500.]
#etaBinning = [0., 0.2, 0.4, 0.6, 1., 1.5]

fitBins = []
for iPt in range(len(ptBinning) - 1):
    repl = {'low': ptBinning[iPt], 'high': ptBinning[iPt + 1]}
    name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
    cut = 'probes.pt > {low:.0f} && probes.pt < {high:.0f}'.format(**repl)
    fitBins.append((name, cut))

nToys = 100

### Common setup ###
generator = ROOT.TemplateGenerator()

if dataType == 'data':
    # target samples
    for sname in ['sel-d3', 'sel-d4']:
        generator.addInput(ROOT.kEG, inputDir + '/' + sname + '_eg.root')

    # background samples
    for sname in ['smu-d3', 'smu-d4']:
        generator.addInput(ROOT.kMG, inputDir + '/' + sname + '_mg.root')

else:
    for sname in ['dy-50', 'tt', 'wlnu-100', 'wlnu-200', 'wlnu-400', 'wlnu-600', 'ww', 'wz', 'zz']:
        generator.addInput(ROOT.kEG, inputDir + '/' + sname + '_eg.root')
        generator.addInput(ROOT.kMG, inputDir + '/' + sname + '_mg.root')

work = ROOT.RooWorkspace('work', 'work')

mass = work.factory('mass[60., 120.]')
mass.setUnit('GeV')
mass.setBinning(fitBinning, 'fitWindow')
mass.setBinning(compBinning, 'compWindow')
massset = ROOT.RooArgSet(mass) # for convenience
masslist = ROOT.RooArgList(mass) # for convenience
mZ = work.factory('mZ[91.2]')
gamma = work.factory('gamma[2.1]')
m0 = work.factory('m0[0., -10., 10.]')
sigma = work.factory('sigma[1., 0.001, 5.]')
alpha = work.factory('alpha[2., 0.01, 5.]')
n = work.factory('n[1.5, 1.01, 5.]')
nbkg = work.factory('nbkg[%f, 0., %f]' % (100., 10000000.))
nsignal = work.factory('nsignal[%f, 0., %f]' % (100., 10000000.))

initVals = {
    'm0': m0.getVal(),
    'sigma': sigma.getVal(),
    'alpha': alpha.getVal(),
    'n': n.getVal(),
    'nbkg': nbkg.getVal(),
    'nsignal': nsignal.getVal()
}

if dataType == 'data': # need MC input
    mcSource = ROOT.TFile.Open(outputDir + '/fityields_mc.root')

outputFile = ROOT.TFile.Open(outputName, 'recreate')

yields = ROOT.TTree('yields', 'yields')
vTPconf = array.array('i', [0])
vBinName = array.array('c', '\0' * 128)
vRaw = array.array('d', [0.])
vParams = dict([(name, array.array('d', [0.])) for name in initVals])
vNz = array.array('d', [0.])
vToyNumber = array.array('i', [0])
yields.Branch('tpconf', vTPconf, 'tpconf/I')
yields.Branch('binName', vBinName, 'binName/C')
yields.Branch('raw', vRaw, 'raw/D')
yields.Branch('nz', vNz, 'nz/D')
for name, vParam in vParams.items():
    yields.Branch(name, vParam, name + '/D')

if nToys != 0:
    yields.Branch('toyNumber', vToyNumber, 'toyNumber/I') # -1 for nominal fit

random = ROOT.TRandom3(seed)

### Common setup done ###

### Fitting routine ###
def runFit(targ, model, printLevel = 1, vals = None):
    for param, val in initVals.items():
        work.arg(param).setVal(val)

    work.arg('nsignal').setVal(targ.sumEntries() * 0.9)

    observables = model.getObservables(ROOT.RooArgSet(m0, sigma))
    print 'm0 =', observables.find('m0').getVal()
    print 'sigma =', observables.find('sigma').getVal()

    fitres = model.fitTo(targ, ROOT.RooFit.PrintLevel(printLevel), ROOT.RooFit.Save(True))

    if vals is not None: 
        for name in vals:
            vals[name] = work.arg(name).getVal()

    for name, vParam in vParams.items():
        vParam[0] = work.arg(name).getVal()

    return fitres.status()


### Run on ee and eg ###

for binName, fitCut in fitBins:
    for iC, c in enumerate(binName):
        vBinName[iC] = c

    if dataType == 'mc':
        # make signal template
        generator.setTemplateBinning(ROOT.RooUniformBinning(20., 160., 140)) # avoid boundary effect
        hsig = generator.makeTemplate(ROOT.kEG, 'sig_' + binName, 'sample == 1 && TMath::Abs(probes.matchedGen) == 11 && ({fitCut})'.format(fitCut = fitCut))

        hsig.SetDirectory(outputFile)
        hsig.Write()

    else:
        # retrieve signal template from MC output
        hsig = mcSource.Get('sig_' + binName)

    sigdata = ROOT.RooDataHist('sigdata', 'sig', masslist, hsig)
    if dataType == 'mc':
        # no smearing
        sigModel = ROOT.RooHistPdf('sigModel', 'sigCore', massset, sigdata, 2)
    else:
        sigCore = ROOT.RooHistPdf('sigCore', 'sigCore', massset, sigdata, 2)
        res = ROOT.RooCBShape('res', 'res', mass, m0, sigma, alpha, n)
#        res = ROOT.RooGaussian('res', 'res', mass, m0, sigma)
        sigModel = ROOT.RooFFTConvPdf('sigModel', 'sigModel', mass, sigCore, res)

    intComp = sigModel.createIntegral(massset, 'compWindow')
    intFit = sigModel.createIntegral(massset, 'fitWindow')

    for conf in ['ee', 'eg']:
        if conf == 'ee':
            # ee: tpconf = 0
            # target is a histogram with !pixelVeto
            # perform binned max L fit
            vTPconf[0] = 0
            cut = 'probes.medium && !probes.pixelVeto && ({fitCut})'.format(fitCut = fitCut)

            htarg = generator.makeTemplate(ROOT.kEG, 'targ_' + conf + '_' + binName, cut)
            htarg.SetDirectory(outputFile)
            htarg.Write()
        
            targ = ROOT.RooDataHist('target', 'target', masslist, htarg)
        else:
            # ee: tpconf = 1
            # target is a tree with pixelVeto
            # perform unbinned max L fit
            vTPconf[0] = 1
            cut = 'probes.medium && probes.pixelVeto && ({fitCut})'.format(fitCut = fitCut)
            
            ttarg = generator.makeUnbinnedTemplate(ROOT.kEG, 'targtree_' + binName, cut)
            
            # histogram for record purpose
            hname = 'targ_' + conf + '_' + binName
            htarg = hsig.Clone(hname)
            htarg.Reset()
            ttarg.Draw('mass>>' + hname, 'weight', 'goff')
            htarg.SetDirectory(outputFile)
            htarg.Write()

            targ = ROOT.RooDataSet('target', 'target', ttarg, massset)

        vRaw[0] = targ.sumEntries()
    
        tbkg = generator.makeUnbinnedTemplate(ROOT.kMG, 'bkgtree_' + binName, cut)

        # histogram for record purpose
        hname = 'bkg_' + conf + '_' + binName
        hbkg = hsig.Clone(hname)
        hbkg.Reset()
        tbkg.Draw('mass>>' + hname, 'weight', 'goff')
        hbkg.SetDirectory(outputFile)
        hbkg.Write()
    
        bkgModel = ROOT.KeysShape('bkgModel', 'bkgModel', mass, tbkg, '', 0.5, 8)
    
        # full fit PDF
        model = ROOT.RooAddPdf('model', 'model', ROOT.RooArgList(bkgModel, sigModel), ROOT.RooArgList(nbkg, nsignal))

        # nominal fit
        vals = dict(initVals)
    
        runFit(targ, model, vals = vals)

        # save result
        vNz[0] = nsignal.getVal() * (intComp.getVal() / intFit.getVal())
        vToyNumber[0] = -1
    
        yields.Fill()

        # plot fit
        frame = mass.frame(ROOT.RooFit.Range('fitWindow'), ROOT.RooFit.Bins(mass.getBins('fitWindow')))
        targ.plotOn(frame)
        model.plotOn(frame)
        model.plotOn(frame, ROOT.RooFit.Components('bkgModel'), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kGreen))
        frame.SetTitle('')

        canvas.addHistogram(frame)
        canvas.printWeb('efake', 'fit_' + conf + '_' + binName)

        # run toys
        nNominal = nsignal.getVal() + nbkg.getVal()

        ROOT.RooMsgService.instance().setStreamStatus(1, False)
    
        iToy = 0
        while iToy < nToys:
            iToy += 1

            for param, val in vals.items():
                work.arg(param).setVal(val)

            toydata = model.generate(massset, random.Poisson(nNominal))

            if conf == 'ee':
                htarg.Reset()
                toydata.fillHistogram(htarg, masslist)
                targ = ROOT.RooDataHist('target', 'target', masslist, htarg)
            else:
                targ = toydata

            status = runFit(targ, model, printLevel = -1)
            if status != 0:
                continue
            
            vRaw[0] = targ.sumEntries()
            vNz[0] = nsignal.getVal() * (intComp.getVal() / intFit.getVal())
    
            vToyNumber[0] = iToy

            yields.Fill()

        ROOT.RooMsgService.instance().setStreamStatus(1, True)

outputFile.cd()
yields.Write()
outputFile.Close()
