#!/usr/bin/env python

import sys
import os
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas

nToys = 0

ptBinning = [40., 50., 60., 80., 100., 6500.]
#etaBinning = [0., 0.2, 0.4, 0.6, 1., 1.5]

fitBins = []
for iPt in range(len(ptBinning) - 1):
    repl = {'low': ptBinning[iPt], 'high': ptBinning[iPt + 1]}
    name = 'pt_{low:.0f}_{high:.0f}'.format(**repl)
    cut = 'probes.pt > {low:.0f} && probes.pt < {high:.0f}'.format(**repl)
    fitBins.append((name, cut))

dataType = sys.argv[1] # "data" or "mc"

try:
    # batch toy generation
    # args = <data/mc> <nToys> <ee/eg> <bin> <seed>
    nToys = int(sys.argv[2])
    conf = sys.argv[3]
    binName = sys.argv[4]
    seed = int(sys.argv[5])

    if conf not in ['ee', 'eg']:
        raise RuntimeError('Unknown conf ' + conf)

    if binName not in [name for (name, cut) in fitBins]:
        raise RuntimeError('Unknown fit bin ' + binName)

    confs = [conf]
    fitBins = [(name, cut) for (name, cut) in fitBins if name == binName]

    batchMode = True
except IndexError:
    seed = 12345

    confs = ['ee', 'eg']

    batchMode = False

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
if batchMode:
    outputName = outputDir + '/fityields_' + dataType + '_' + conf + '_' + binName + '_' + str(seed) + '.root'
else:
    outputName = outputDir + '/fityields_' + dataType + '.root'

fitBinning = ROOT.RooUniformBinning(60., 120., 60)
compBinning = ROOT.RooUniformBinning(81., 101., 20)

### Common setup ###

generator = ROOT.TemplateGenerator()

if not batchMode:
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


if dataType == 'data': # need MC input
    mcSource = ROOT.TFile.Open(outputDir + '/fityields_mc.root')
    mcWork = mcSource.Get('work')

initVals = {
    'nbkg': 100.,
    'nsignal': 100.
}
if dataType == 'data':
    initVals.update({
        'm0': 0.,
        'sigma': 1.,
        'alpha': 2.,
        'n': 1.5
    })

vTPconf = array.array('i', [0])
vBinName = array.array('c', '\0' * 128)
vRaw = array.array('d', [0.])
vParams = dict([(name, array.array('d', [0.])) for name in initVals])
vNz = array.array('d', [0.])
vToyNumber = array.array('i', [0])

outputFile = ROOT.TFile.Open(outputName, 'recreate')

yields = ROOT.TTree('yields', 'yields')

yields.Branch('tpconf', vTPconf, 'tpconf/I')
yields.Branch('binName', vBinName, 'binName/C')
yields.Branch('raw', vRaw, 'raw/D')
yields.Branch('nz', vNz, 'nz/D')
yields.Branch('toyNumber', vToyNumber, 'toyNumber/I') # -1 for nominal fit
for name, vParam in vParams.items():
    yields.Branch(name, vParam, name + '/D')

if batchMode:
    source = ROOT.TFile.Open(outputDir + '/fityields_' + dataType + '.root')

    sourceYields = source.Get('yields')
    sourceYields.SetBranchAddress('tpconf', vTPconf)
    sourceYields.SetBranchAddress('binName', vBinName)
    sourceYields.SetBranchAddress('raw', vRaw)
    sourceYields.SetBranchAddress('nz', vNz)
    for name, vParam in vParams.items():
        sourceYields.SetBranchAddress(name, vParam)

    work = source.Get('work')

    mass = work.arg('mass')
    mass.setBinning(fitBinning, 'fitWindow')
    mass.setBinning(compBinning, 'compWindow')
    massset = ROOT.RooArgSet(mass) # for convenience
    masslist = ROOT.RooArgList(mass) # for convenience
    nbkg = work.arg('nbkg')
    nsignal = work.arg('nsignal')
    if dataType == 'data':
        m0 = work.arg('m0')
        sigma = work.arg('sigma')
        alpha = work.arg('alpha')
        n = work.arg('n')

else:
    work = ROOT.RooWorkspace('work', 'work')
    
    mass = work.factory('mass[60., 120.]')
    mass.setUnit('GeV')
    mass.setBinning(fitBinning, 'fitWindow')
    mass.setBinning(compBinning, 'compWindow')
    massset = ROOT.RooArgSet(mass) # for convenience
    masslist = ROOT.RooArgList(mass) # for convenience
    nbkg = work.factory('nbkg[0., 1000000000.]')
    nsignal = work.factory('nsignal[0., 1000000000.]')
    if dataType == 'data':
        m0 = work.factory('m0[-10., 10.]')
        sigma = work.factory('sigma[0.001, 5.]')
        alpha = work.factory('alpha[0.01, 5.]')
        n = work.factory('n[1.01, 5.]')

    canvas = SimpleCanvas(lumi = allsamples['sel-d3'].lumi + allsamples['sel-d4'].lumi, sim = (dataType == 'mc'))
    canvas.titlePave.SetX2NDC(0.5)

random = ROOT.TRandom3(seed)

### Common setup done ###

### Fitting routine ###
def runFit(targ, model, printLevel = 1, vals = None):
    for param, val in initVals.items():
        work.arg(param).setVal(val)

    work.arg('nsignal').setVal(targ.sumEntries() * 0.9)

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

    sigModelName = 'sigModel_' + binName

    if batchMode:
        sigModel = work.pdf(sigModelName)

    else:
        sigdataName = 'sigdata_' + binName

        if dataType == 'mc':
            hsigName = 'sig_' + binName
    
            # make signal template
            generator.setTemplateBinning(ROOT.RooUniformBinning(20., 160., 140)) # avoid boundary effect
            hsig = generator.makeTemplate(ROOT.kEG, hsigName, 'sample == 1 && TMath::Abs(probes.matchedGen) == 11 && ({fitCut})'.format(fitCut = fitCut))
    
            hsig.SetDirectory(outputFile)
            outputFile.cd()
            hsig.Write()
    
            sigdata = ROOT.RooDataHist(sigdataName, 'sig', masslist, hsig)
            getattr(work, 'import')(sigdata, ROOT.RooFit.Rename(sigdataName)) # Rename: dummy argument to trigger dataset import (as opposed to generic object import)
    
            # no smearing
            sigModel = work.factory('HistPdf::' + sigModelName + '({mass}, ' + sigdataName + ', 2)')
    
        else:
            sigdata = mcWork.data(sigdataName)
            getattr(work, 'import')(sigdata, ROOT.RooFit.Rename(sigdataName))

            sigCore = work.factory('HistPdf::sigCore_' + binName + '({mass}, ' + sigdataName + ', 2)')
            res = work.factory('CBShape::res(mass, m0, sigma, alpha, n)')
    #        res = work.factory('Gaussian::res(mass, m0, sigma)')
            sigModel = work.factory('FCONV::' + sigModelName + '(mass, sigCore_' + binName + ', res)')

    intComp = sigModel.createIntegral(massset, 'compWindow')
    intFit = sigModel.createIntegral(massset, 'fitWindow')

    for conf in confs:
        targName = 'target_' + conf + '_' + binName
        modelName = 'model_' + conf + '_' + binName

        if conf == 'ee':
            tpconf = 0
            # target is a histogram with !pixelVeto
            # perform binned max L fit

        else:
            tpconf = 1
            # target is a tree with pixelVeto
            # perform unbinned max L fit

        if batchMode:
            targ = work.data(targName)
            model = work.pdf(modelName)

            vals = {}
            iEntry = 0
            while iEntry != sourceYields.GetEntries():
                sourceYields.GetEntry(iEntry)
                iEntry += 1

                if vTPconf[0] == tpconf and vBinName.tostring().strip('\0') == binName:
                    for name, vParam in vParams.items():
                        vals[name] = vParam[0]

                    break

        else:
            if conf == 'ee':
                cut = 'probes.medium && !probes.pixelVeto && ({fitCut})'.format(fitCut = fitCut)
    
                htarg = generator.makeTemplate(ROOT.kEG, targName, cut)
                htarg.SetDirectory(outputFile)
                outputFile.cd()
                htarg.Write()
            
                targ = ROOT.RooDataHist(targName, 'target', masslist, htarg)

            else:
                cut = 'probes.medium && probes.pixelVeto && ({fitCut})'.format(fitCut = fitCut)
                
                ttarg = generator.makeUnbinnedTemplate(ROOT.kEG, 'targtree_' + binName, cut)
                
                # histogram for record purpose
                htarg = generator.makeEmptyTemplate(targName)
                ttarg.Draw('mass>>' + targName, 'weight', 'goff')
                htarg.SetDirectory(outputFile)
                outputFile.cd()
                htarg.Write()
    
                targ = ROOT.RooDataSet(targName, 'target', ttarg, massset)
    
            getattr(work, 'import')(targ, ROOT.RooFit.Rename(targName))

            vRaw[0] = targ.sumEntries()
        
            tbkg = generator.makeUnbinnedTemplate(ROOT.kMG, 'bkgtree_' + binName, cut)
    
            # histogram for record purpose
            bkgName = 'bkg_' + conf + '_' + binName
            hbkg = generator.makeEmptyTemplate(bkgName)
            tbkg.Draw('mass>>' + bkgName, 'weight', 'goff')
            hbkg.SetDirectory(outputFile)
            hbkg.Write()
    
            bkgModelName = 'bkgModel_' + conf + '_' + binName
    
            bkgModel = ROOT.KeysShape(bkgModelName , 'bkgModel', mass, tbkg, '', 0.5, 1 if batchMode else 8)
            getattr(work, 'import')(bkgModel, ROOT.RooFit.RecycleConflictNodes())
    
            # full fit PDF
            model = work.factory('SUM::' + modelName + '(nbkg * ' + bkgModelName + ', nsignal * ' + sigModelName + ')')
    
            # nominal fit
            vals = dict(initVals)
        
            runFit(targ, model, vals = vals)
    
            # save result
            vNz[0] = vals['nsignal'] * (intComp.getVal() / intFit.getVal())
            vToyNumber[0] = -1

            vTPconf[0] = tpconf
        
            yields.Fill()

            # plot fit
            frame = mass.frame(ROOT.RooFit.Range('fitWindow'), ROOT.RooFit.Bins(mass.getBins('fitWindow')))
            targ.plotOn(frame)
            model.plotOn(frame)
            model.plotOn(frame, ROOT.RooFit.Components(bkgModelName), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kGreen))
            frame.SetTitle('')
    
            canvas.addHistogram(frame)
            canvas.printWeb('efake', 'fit_' + dataType + '_' + conf + '_' + binName, logy = False)

        # run toys
        nNominal = vals['nsignal'] + vals['nbkg']

        ROOT.RooMsgService.instance().setStreamStatus(1, False)

        iToy = 0
        while iToy < nToys:
            iToy += 1

            for param, val in vals.items():
                work.arg(param).setVal(val)

            toydata = model.generate(massset, random.Poisson(nNominal))

            if conf == 'ee':
                htarg = generator.makeEmptyTemplate('htarg')
                toydata.fillHistogram(htarg, masslist)
                targ = ROOT.RooDataHist('target', 'target', masslist, htarg)
                htarg.Delete()
            else:
                targ = toydata

            status = runFit(targ, model, printLevel = -1)

            vRaw[0] = targ.sumEntries()
            
            toydata.IsA().Destructor(toydata)

            if status != 0:
                continue
            
            vNz[0] = nsignal.getVal() * (intComp.getVal() / intFit.getVal())
    
            vToyNumber[0] = iToy

            vTPconf[0] = tpconf

            yields.Fill()

        ROOT.RooMsgService.instance().setStreamStatus(1, True)
        
    
outputFile.cd()
yields.Write()
if not batchMode:
    work.Write()
outputFile.Close()
