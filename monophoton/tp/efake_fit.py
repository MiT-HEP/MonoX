#!/usr/bin/env python

import sys
import os
import array
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
from plotstyle import SimpleCanvas
from tp.efake_conf import skimDir, outputDir, roofitDictsDir, getBinning

# set to nonzero if you want to run toys in runMode single too
nToys = 0

dataType = sys.argv[1] # "data" or "mc"
binningName = sys.argv[2] # see efake_conf

fitBins = getBinning(binningName)[2]

# switching runMode
runMode = 'single'
pdf = 'default'

if len(sys.argv) == 7:
    # batch toy generation
    # args = <data/mc> <binningName> <nToys> <ee/eg> <bin> <seed>
    nToys = int(sys.argv[3])
    conf = sys.argv[4]
    binName = sys.argv[5]
    seed = int(sys.argv[6])

    if conf not in ['ee', 'eg']:
        raise RuntimeError('Unknown conf ' + conf)

    if binName not in [name for (name, cut) in fitBins]:
        raise RuntimeError('Unknown fit bin ' + binName)

    confs = [conf]
    fitBins = [(name, cut) for (name, cut) in fitBins if name == binName]
    
    runMode = 'batchtoy'

else:
    if len(sys.argv) > 3:
        if sys.argv[3] == 'altsig':
            pdf = 'altsig'
        elif sys.argv[3] == 'altbkg':
            # runMode single, bkgPdf alt
            pdf = 'altbkg'

    seed = 12345
    confs = ['ee', 'eg']

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
ROOT.gROOT.LoadMacro(thisdir + '/TemplateGenerator.cc+')
ROOT.gSystem.Load(roofitDictsDir + '/libCommonRooFit.so') # defines KeysShape

if runMode == 'batchtoy':
    outputName = outputDir + '/toys_' + dataType + '_' + conf + '_' + binName + '_' + str(seed) + '.root'
else:
    if pdf == 'default':
        outputName = outputDir + '/fityields_' + dataType + '_' + binningName + '.root'
    elif pdf == 'altbkg':
        outputName = outputDir + '/fityields_' + dataType + '_' + binningName + '_altbkg.root'
    elif pdf == 'altsig':
        outputName = outputDir + '/fityields_' + dataType + '_' + binningName + '_altsig.root'


fitBinning = ROOT.RooUniformBinning(60., 120., 60)
compBinning = ROOT.RooUniformBinning(81., 101., 20)

### Common setup ###

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
vSeed = array.array('i', [seed])

if os.path.exists(outputName):
    # make a backup
    shutil.copy(outputName, outputName.replace('.root', '_old.root'))

outputFile = ROOT.TFile.Open(outputName, 'recreate')

yields = ROOT.TTree('yields', 'yields')

yields.Branch('tpconf', vTPconf, 'tpconf/I')
yields.Branch('binName', vBinName, 'binName/C')
yields.Branch('raw', vRaw, 'raw/D')
yields.Branch('nz', vNz, 'nz/D')
yields.Branch('toyNumber', vToyNumber, 'toyNumber/I') # -1 for nominal fit
yields.Branch('seed', vSeed, 'seed/I')
for name, vParam in vParams.items():
    yields.Branch(name, vParam, name + '/D')

# template generator
# mainly used in runMode single, but batchtoy mode also uses it to make empty histograms
generator = ROOT.TemplateGenerator()

if runMode == 'batchtoy':
    source = ROOT.TFile.Open(outputDir + '/fityields_' + dataType + '_' + binningName + '.root')

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

elif runMode == 'single':
    if dataType == 'data':
        # target samples
        for sname in ['sel-d3', 'sel-d4']:
            generator.addInput(ROOT.kEG, skimDir + '/' + sname + '_eg.root')
    
        # background samples
        for sname in ['smu-d3', 'smu-d4']:
            generator.addInput(ROOT.kMG, skimDir + '/' + sname + '_mg.root')

        # will need MC signal template
        mcSource = ROOT.TFile.Open(outputDir + '/fityields_mc_' + binningName + '.root')
        mcWork = mcSource.Get('work')

    else:
        for sname in ['dy-50', 'tt', 'wlnu-100', 'wlnu-200', 'wlnu-400', 'wlnu-600', 'ww', 'wz', 'zz']:
            generator.addInput(ROOT.kEG, skimDir + '/' + sname + '_eg.root')
            generator.addInput(ROOT.kMG, skimDir + '/' + sname + '_mg.root')

    work = ROOT.RooWorkspace('work', 'work')
    
    mass = work.factory('mass[60., 120.]')
    mass.setUnit('GeV')
    mass.setBinning(fitBinning, 'fitWindow')
    mass.setBinning(compBinning, 'compWindow')
    massset = ROOT.RooArgSet(mass) # for convenience
    masslist = ROOT.RooArgList(mass) # for convenience
    weight = work.factory('weight[-1000000000., 1000000000.]')
    nbkg = work.factory('nbkg[0., 1000000.]')
    nsignal = work.factory('nsignal[0., 1000000.]')
    if dataType == 'data':
        m0 = work.factory('m0[-10., 10.]')
        sigma = work.factory('sigma[0.001, 5.]')
        alpha = work.factory('alpha[0.01, 5.]')
        n = work.factory('n[1.01, 5.]')

    canvas = SimpleCanvas(lumi = allsamples['sel-d3'].lumi + allsamples['sel-d4'].lumi, sim = (dataType == 'mc'))
    canvas.titlePave.SetX2NDC(0.5)
    canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
    canvas.legend.add('obs', title = 'Observed', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
    canvas.legend.add('fit', title = 'Fit', opt = 'L', lcolor = ROOT.kBlue, lwidth = 2, lstyle = ROOT.kSolid)
    canvas.legend.add('bkg', title = 'Bkg component', opt = 'L', lcolor = ROOT.kGreen, lwidth = 2, lstyle = ROOT.kDashed)
    if dataType == 'mc':
        canvas.legend.add('mcbkg', title = 'Bkg (MC truth)', opt = 'LF', lcolor = ROOT.kRed, lwidth = 1, fcolor = ROOT.kRed, fstyle = 3003)

random = ROOT.TRandom3(seed)

### Common setup done ###

### Fitting routine ###
def runFit(targ, model, printLevel = 1, vals = None):
    for param, val in initVals.items():
        work.arg(param).setVal(val)

    work.arg('nsignal').setVal(targ.sumEntries() * 0.9)

    fitres = model.fitTo(targ, ROOT.RooFit.PrintLevel(printLevel), ROOT.RooFit.SumW2Error(True), ROOT.RooFit.Save(True))

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

    if runMode == 'batchtoy':
        sigModel = work.pdf(sigModelName)

    elif runMode == 'single':
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
            if not sigdata:
                print 'No dataset ' + sigdataName + ' found in ' + mcSource.GetName() + '.'
                sys.exit(1)

            getattr(work, 'import')(sigdata, ROOT.RooFit.Rename(sigdataName))

            sigCore = work.factory('HistPdf::sigCore_' + binName + '({mass}, ' + sigdataName + ', 2)')
            if pdf == 'altsig':
                res = work.factory('Gaussian::res(mass, m0, sigma)')
            else:
                res = work.factory('CBShape::res(mass, m0, sigma, alpha, n)')

            sigModel = work.factory('FCONV::' + sigModelName + '(mass, sigCore_' + binName + ', res)')

    intComp = sigModel.createIntegral(massset, 'compWindow')
    intFit = sigModel.createIntegral(massset, 'fitWindow')

    for conf in confs:
        targName = 'target_' + conf + '_' + binName
        modelName = 'model_' + conf + '_' + binName

        if conf == 'ee':
            tpconf = 0
        else:
            tpconf = 1

        if runMode == 'batchtoy':
            targ = work.data(targName)
            model = work.pdf(modelName)

            vals = {}
            iEntry = 0
            while iEntry != sourceYields.GetEntries():
                sourceYields.GetEntry(iEntry)
                iEntry += 1

                if vTPconf[0] == tpconf and vBinName.tostring().startswith(binName):
                    for name, vParam in vParams.items():
                        vals[name] = vParam[0]

                    break

            else:
                raise RuntimeError('tpconf = %d and binName = %s not found in input tree' % (tpconf, binName))

        elif runMode == 'single':
            if conf == 'ee':
                # target is a histogram with !pixelVeto
                # perform binned max L fit
                cut = 'probes.medium && !probes.pixelVeto && ({fitCut})'.format(fitCut = fitCut)
            else:
                # target is a tree with pixelVeto
                # perform unbinned max L fit
                cut = 'probes.medium && probes.pixelVeto && ({fitCut})'.format(fitCut = fitCut)

            if conf == 'ee' or conf == 'eg':
                # USING BINNED FIT FOR ALL
                htarg = generator.makeTemplate(ROOT.kEG, targName, cut)
                htarg.SetDirectory(outputFile)
                outputFile.cd()
                htarg.Write()
            
                targ = ROOT.RooDataHist(targName, 'target', masslist, htarg)
                targHist = targ

            else:
                ttarg = generator.makeUnbinnedTemplate(ROOT.kEG, 'targtree_' + binName, cut)
                
                # histogram for record purpose
                htarg = generator.makeEmptyTemplate(targName)
                ttarg.Draw('mass>>' + targName, 'weight', 'goff')
                for iX in range(1, htarg.GetNbinsX() + 1):
                    if htarg.GetBinContent(iX) < 0.:
                        htarg.SetBinContent(iX, 0.)
                        htarg.SetBinError(iX, 0.)
                    elif htarg.GetBinContent(iX) - htarg.GetBinError(iX) < 0.:
                        htarg.SetBinError(iX, htarg.GetBinContent(iX))

                htarg.SetDirectory(outputFile)
                outputFile.cd()
                htarg.Write()
    
                targ = ROOT.RooDataSet(targName, 'target', ttarg, ROOT.RooArgSet(mass, weight), '', 'weight')
                targHist = ROOT.RooDataHist(targName, 'target', masslist, htarg)
    
            getattr(work, 'import')(targ, ROOT.RooFit.Rename(targName))

            vRaw[0] = targ.sumEntries()

            bkgModelName = 'bkgModel_' + conf + '_' + binName

            if pdf == 'altbkg':
                slope = ROOT.RooRealVar('slope', 'slope', 0., -100., 100.)
                bkgModel = ROOT.RooPolynomial(bkgModelName, 'bkgModel', mass, ROOT.RooArgList(slope))

            else:
                tbkg = generator.makeUnbinnedTemplate(ROOT.kMG, 'bkgtree_' + binName, cut)
        
                # histogram for record purpose
                bkgName = 'bkg_' + conf + '_' + binName
                hbkg = generator.makeEmptyTemplate(bkgName)
                tbkg.Draw('mass>>' + bkgName, 'weight', 'goff')
                for iX in range(1, hbkg.GetNbinsX() + 1):
                    if hbkg.GetBinContent(iX) < 0.:
                        hbkg.SetBinContent(iX, 0.)
                        hbkg.SetBinError(iX, 0.)
                    elif hbkg.GetBinContent(iX) - hbkg.GetBinError(iX) < 0.:
                        hbkg.SetBinError(iX, hbkg.GetBinContent(iX))
    
                hbkg.SetDirectory(outputFile)
                hbkg.Write()

                bkgModel = ROOT.KeysShape(bkgModelName , 'bkgModel', mass, tbkg, 'weight', 0.5, 8)

            getattr(work, 'import')(bkgModel, ROOT.RooFit.Silence())
   
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

            if dataType == 'mc':
                # MC-truth background
                hmcbkgName = 'mcbkg_' + conf + '_' + binName
    
                hmcbkg = generator.makeTemplate(ROOT.kEG, hmcbkgName, 'TMath::Abs(probes.matchedGen) != 11 && ({cut})'.format(cut = cut))
                
                hmcbkg.SetDirectory(outputFile)
                outputFile.cd()
                hmcbkg.Write()

            # plot fit
            frame = mass.frame(ROOT.RooFit.Range('fitWindow'), ROOT.RooFit.Bins(mass.getBins('fitWindow')))
            targHist.plotOn(frame)
            model.plotOn(frame)
            model.plotOn(frame, ROOT.RooFit.Components(bkgModelName), ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kGreen))
            frame.SetTitle('')
            frame.SetMinimum(0.)
    
            canvas.addHistogram(frame)
            if dataType == 'mc':
                canvas.legend.apply('mcbkg', hmcbkg)
                canvas.addHistogram(hmcbkg)

            if pdf == 'altbkg':
                canvas.printWeb('efake', 'fit_' + dataType + '_altbkg_' + conf + '_' + binName, logy = False)
            elif pdf == 'altsig':
                canvas.printWeb('efake', 'fit_' + dataType + '_sigbkg_' + conf + '_' + binName, logy = False)
            else:
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
if runMode == 'single':
    work.Write()
outputFile.Close()
