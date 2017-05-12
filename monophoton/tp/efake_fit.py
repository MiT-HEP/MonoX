#!/usr/bin/env python

import sys
import os
import array
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
from datasets import allsamples
from plotstyle import RatioCanvas
from tp.efake_conf import skimConfig, lumiSamples, outputDir, roofitDictsDir, getBinning

# set to nonzero if you want to run toys in runMode single too
nToys = 0

dataType = sys.argv[1] # "data" or "mc"
binningName = sys.argv[2] # see efake_conf

#varType = 'kSCRawMass'
varType = 'kMass'
plotDir = 'efake/fit_' + binningName

monophSel = 'probes.medium && probes.mipEnergy < 4.9 && TMath::Abs(probes.time) < 3. && probes.sieie > 0.001 && probes.sipip > 0.001' 

try:
    os.makedirs(plotDir)
except OSError:
    pass

fitBins = getBinning(binningName)[2]

lumi = sum(allsamples[s].lumi for s in lumiSamples)

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
    # confs = ['ee', 'eg', 'pass', 'fail']
    confs = ['pass', 'fail']

sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load(config.libobjs)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')
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


fitBinning = ROOT.RooUniformBinning(60., 120., 120)
compBinning = ROOT.RooUniformBinning(81., 101., 20)

### Common setup ###

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

weightExpr = 'weight' if dataType == 'mc' else '1'
#weightExpr = 'weight'

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
        for sname in skimConfig['phdata'][0]:
            generator.addInput(ROOT.kEG, config.skimDir + '/' + sname + '/*_tpeg.root')
    
        # background samples
        for sname in skimConfig['phdata'][0]:
            generator.addInput(ROOT.kMG, config.skimDir + '/' + sname + '/*_tpmg.root')

        # will need MC signal template
#        mcSource = ROOT.TFile.Open(outputDir + '/fityields_mc_' + binningName + '_altbkg.root')
#        mcWork = mcSource.Get('work')

    else:
        for sname in skimConfig['mc'][0]:
            generator.addInput(ROOT.kEG, config.skimDir + '/' + sname + '/*_tpeg.root')
            generator.addInput(ROOT.kMG, config.skimDir + '/' + sname + '/*_tpmg.root')
        for sname in skimConfig['mcgg'][0]:
            generator.addInput(ROOT.kEG, config.skimDir + '/' + sname + '/*_tpeg.root')

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
    if pdf == 'altsig':
        mZ = work.factory('mZ[91.2, 86., 96.]')
        gammaZ = work.factory('gammaZ[2.5, 1., 5.]')
    else:
        mZ = work.factory('mZ[91.2]')
        gammaZ = work.factory('gammaZ[2.5]')

    m0 = work.factory('m0[-10., 10.]')
    sigma = work.factory('sigma[0.001, 5.]')
    alpha = work.factory('alpha[0.01, 5.]')
    n = work.factory('n[1.01, 5.]')

    canvas = RatioCanvas(lumi = lumi, sim = (dataType == 'mc'))
    canvas.titlePave.SetX2NDC(0.5)
    canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
    canvas.legend.add('obs', title = 'Observed', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
    canvas.legend.add('fit', title = 'Fit', opt = 'L', lcolor = ROOT.kBlue, lwidth = 2, lstyle = ROOT.kSolid)
    canvas.legend.add('bkg', title = 'Bkg component', opt = 'L', lcolor = ROOT.kGreen, lwidth = 2, lstyle = ROOT.kDashed)
    if dataType == 'mc':
        canvas.legend.add('mcbkg', title = 'Bkg (MC truth)', opt = 'LF', lcolor = ROOT.kRed, lwidth = 1, fcolor = ROOT.kRed, fstyle = 3003)

random = ROOT.TRandom3(seed)

### Common setup done ###
print 'Finished common setup.'

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
    print 'Run fits for', binName

    for iC, c in enumerate(binName):
        vBinName[iC] = c

    sigModelName = 'sigModel_' + binName

    if runMode == 'batchtoy':
        sigModel = work.pdf(sigModelName)

    elif runMode == 'single':
        sigdataName = 'sigdata_' + binName

#        if dataType == 'mc':
#            hsigName = 'sig_' + binName
#    
#            # make signal template
#            generator.setTemplateBinning(ROOT.RooUniformBinning(20., 160., 140), getattr(ROOT, varType)) # avoid boundary effect
#            hsig = generator.makeTemplate(ROOT.kEG, hsigName, 'sample == 1 && TMath::Abs(probes.matchedGen) == 11 && ({fitCut})'.format(fitCut = fitCut), getattr(ROOT, varType))
#
#            hsig.SetDirectory(outputFile)
#            outputFile.cd()
#            hsig.Write()
#    
#            sigdata = ROOT.RooDataHist(sigdataName, 'sig', masslist, hsig)
#            getattr(work, 'import')(sigdata, ROOT.RooFit.Rename(sigdataName)) # Rename: dummy argument to trigger dataset import (as opposed to generic object import)
#    
#            # no smearing
#            sigModel = work.factory('HistPdf::' + sigModelName + '({mass}, ' + sigdataName + ', 2)')
#
#        else:
#            sigdata = mcWork.data(sigdataName)
#            if not sigdata:
#                print 'No dataset ' + sigdataName + ' found in ' + mcSource.GetName() + '.'
#                sys.exit(1)
#
#            getattr(work, 'import')(sigdata, ROOT.RooFit.Rename(sigdataName))
#
#            sigCore = work.factory('HistPdf::sigCore_' + binName + '({mass}, ' + sigdataName + ', 2)')
#            res = work.factory('Gaussian::res(mass, m0, sigma)')

        if pdf == 'altsig':
            sigModel = work.factory('BreitWigner::' + sigModelName + '(mass, mZ, gammaZ)')
        else:
            sigCore = work.factory('BreitWigner::sigCore_' + binName + '(mass, mZ, gammaZ)')
            res = work.factory('CBShape::res(mass, m0, sigma, alpha, n)')
            sigModel = work.factory('FCONV::' + sigModelName + '(mass, sigCore_' + binName + ', res)')

    print 'Made signal template.'

    intComp = sigModel.createIntegral(massset, 'compWindow')
    intFit = sigModel.createIntegral(massset, 'fitWindow')

    generator.setTemplateBinning(fitBinning, getattr(ROOT, varType)) # avoid boundary effect

    for conf in confs:
        targName = 'target_' + conf + '_' + binName
        modelName = 'model_' + conf + '_' + binName

        if conf == 'ee':
            tpconf = 0
        elif conf == 'eg':
            tpconf = 1
        elif conf == 'pass':
            tpconf = 2
        elif conf == 'fail':
            tpconf = 3
        else:
            tpconf = 4

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
                # target is a histogram with !csafeVeto
                # perform binned max L fit
                cut = 'probes.medium && !probes.csafeVeto && ({fitCut})'.format(fitCut = fitCut)
            elif conf == 'eg':
                # target is a tree with pixelVeto
                # perform unbinned max L fit
                cut = 'probes.medium && probes.pixelVeto && ({fitCut})'.format(fitCut = fitCut)
            elif conf == 'pass':
                cut = '({monophSel}) && ({fitCut})'.format(monophSel = monophSel, fitCut = fitCut)
            elif conf == 'fail':
                cut = '!({monophSel}) && ({fitCut})'.format(monophSel = monophSel, fitCut = fitCut)
            else:
                cut = '({fitCut})'.format(fitCut = fitCut)

            if tpconf < 4: # conf is in [ ee, eg, pass, fail]
                # USING BINNED FIT FOR ALL
                htarg = generator.makeTemplate(ROOT.kEG, targName, cut, getattr(ROOT, varType))
                htarg.SetDirectory(outputFile)
                outputFile.cd()
                htarg.Write()

                print 'htarg limits:', htarg.GetXaxis().GetXmin(), htarg.GetXaxis().GetXmax(), htarg.GetSumOfWeights()
            
                targ = ROOT.RooDataHist(targName, 'target', masslist, htarg)
                targHist = targ

            else:
                ttarg = generator.makeUnbinnedTemplate(ROOT.kEG, 'targtree_' + binName, cut, getattr(ROOT, varType))
                
                # histogram for record purpose
                htarg = generator.makeEmptyTemplate(targName, getattr(ROOT, varType))
                ttarg.Draw('mass>>' + targName, weightExpr, 'goff')
                for iX in range(1, htarg.GetNbinsX() + 1):
                    if htarg.GetBinContent(iX) < 0.:
                        htarg.SetBinContent(iX, 0.)
                        htarg.SetBinError(iX, 0.)
                    elif htarg.GetBinContent(iX) - htarg.GetBinError(iX) < 0.:
                        htarg.SetBinError(iX, htarg.GetBinContent(iX))

                htarg.SetDirectory(outputFile)
                outputFile.cd()
                htarg.Write()

                if dataType == 'mc':
                    targ = ROOT.RooDataSet(targName, 'target', ttarg, ROOT.RooArgSet(mass, weight), '', 'weight')
                else:
                    targ = ROOT.RooDataSet(targName, 'target', ttarg, ROOT.RooArgSet(mass))

                targHist = ROOT.RooDataHist(targName, 'target', masslist, htarg)
    
            getattr(work, 'import')(targ, ROOT.RooFit.Rename(targName))

            vRaw[0] = targ.sumEntries()

            print 'Made target template.'

            bkgModelName = 'bkgModel_' + conf + '_' + binName

            if pdf == 'altbkg':
                slope = ROOT.RooRealVar('slope', 'slope', 0., -100., 100.)
                bkgModel = ROOT.RooPolynomial(bkgModelName, 'bkgModel', mass, ROOT.RooArgList(slope))

            else:
                tbkg = generator.makeUnbinnedTemplate(ROOT.kMG, 'bkgtree_' + binName, cut, getattr(ROOT, varType))
        
                # histogram for record purpose
                bkgName = 'bkg_' + conf + '_' + binName
                hbkg = generator.makeEmptyTemplate(bkgName, getattr(ROOT, varType))
                tbkg.Draw('mass>>' + bkgName, weightExpr, 'goff')
                for iX in range(1, hbkg.GetNbinsX() + 1):
                    if hbkg.GetBinContent(iX) < 0.:
                        hbkg.SetBinContent(iX, 0.)
                        hbkg.SetBinError(iX, 0.)
                    elif hbkg.GetBinContent(iX) - hbkg.GetBinError(iX) < 0.:
                        hbkg.SetBinError(iX, hbkg.GetBinContent(iX))
    
                hbkg.SetDirectory(outputFile)
                hbkg.Write()

                if dataType == 'mc':
                    bkgModel = ROOT.KeysShape(bkgModelName, 'bkgModel', mass, tbkg, 'weight', 0.5, 8)
                else:
                    bkgModel = ROOT.KeysShape(bkgModelName, 'bkgModel', mass, tbkg, '', 0.5, 8)

            getattr(work, 'import')(bkgModel, ROOT.RooFit.Silence())
   
            print 'Made background template.'

            # full fit PDF
            model = work.factory('SUM::' + modelName + '(nbkg * ' + bkgModelName + ', nsignal * ' + sigModelName + ')')
    
            print 'Made fit model.'

            # nominal fit
            vals = dict(initVals)
            runFit(targ, model, vals = vals)

            print 'Finished fit.'

            # save result
            vNz[0] = vals['nsignal'] * (intComp.getVal() / intFit.getVal())
            vToyNumber[0] = -1

            vTPconf[0] = tpconf
        
            yields.Fill()

            if dataType == 'mc':
                # MC-truth background
                hmcbkgName = 'mcbkg_' + conf + '_' + binName
    
                hmcbkg = generator.makeTemplate(ROOT.kEG, hmcbkgName, 'TMath::Abs(probes.matchedGen) != 11 && ({cut})'.format(cut = cut), getattr(ROOT, varType))
                
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
    
            canvas.Clear()
            canvas.addHistogram(frame, clone = True, drawOpt = '')
            if dataType == 'mc':
                canvas.legend.apply('mcbkg', hmcbkg)
                canvas.addHistogram(hmcbkg)

            canvas.Update(rList = [], logy = False)

            frame.Print()

            # adding ratio pad
            fitcurve = frame.findObject(modelName + '_Norm[mass]')
            dHist = targHist.createHistogram('dHist', mass)

            print fitcurve

            rdata = ROOT.TGraphErrors(dHist.GetNbinsX())
            for iP in range(rdata.GetN()):
                x = dHist.GetXaxis().GetBinCenter(iP + 1)
                nData = dHist.GetBinError(iP + 1)
                statErr = dHist.GetBinContent(iP + 1)
                nFit = fitcurve.interpolate(x)
                print x, nData, statErr, nFit
                print (nData - nFit) / nFit
                print (nData - nFit) / statErr
                rdata.SetPoint(iP, x, (nData - nFit) / nFit)
                # rdata.SetPointError(iP, 0., dmet.GetBinError(iP + 1) / norm)

            rdata.SetMarkerStyle(8)
            rdata.SetMarkerColor(ROOT.kBlack)
            rdata.SetLineColor(ROOT.kBlack)

            canvas.ratioPad.cd()

            rframe = ROOT.TH1F('rframe', '', 1, fitBinning.lowBound(), fitBinning.highBound())
            rframe.GetYaxis().SetRangeUser(-2., 2.)
            rframe.Draw()

            line = ROOT.TLine(fitBinning.lowBound(), 0., fitBinning.highBound(), 0.)
            line.SetLineWidth(2)
            line.SetLineColor(ROOT.kBlue)
            line.Draw()

            rdata.Draw('EP')

            canvas._needUpdate = False

            if pdf == 'altbkg':
                canvas.printWeb(plotDir, 'fit_' + dataType + '_altbkg_' + conf + '_' + binName, logy = False)
            elif pdf == 'altsig':
                canvas.printWeb(plotDir, 'fit_' + dataType + '_altsig_' + conf + '_' + binName, logy = False)
            else:
                canvas.printWeb(plotDir, 'fit_' + dataType + '_' + conf + '_' + binName, logy = False)

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
                htarg = generator.makeEmptyTemplate('htarg', getattr(ROOT, varType))
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

work = None
outputFile.Close()
