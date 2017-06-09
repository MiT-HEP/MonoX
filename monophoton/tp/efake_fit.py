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

dataSource = 'sph' # sph or sel
#varType = 'kSCRawMass'
varType = 'kMass'
plotDir = 'efake/fit_' + binningName

# gets overwritten if len(sys.argv) == 7
tpconfs = {
    'ee': 0,
    'eg': 1,
    'pass': 2,
    'fail': 3
}

monophSel = 'probes.mediumZG && probes.mipEnergy < 4.9 && TMath::Abs(probes.time) < 3. && probes.sieie > 0.001 && probes.sipip > 0.001' 

try:
    os.makedirs(plotDir)
except OSError:
    pass

fitBins = getBinning(binningName)[2]

lumi = sum(allsamples[s].lumi for s in lumiSamples)

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

    tpconfs = {conf: tpconfs[conf]}
    fitBins = [(name, cut) for (name, cut) in fitBins if name == binName]
    
    runMode = 'batchtoy'
    pdf = 'default'

else:
    runMode = 'single'
    pdf = 'default'

    if len(sys.argv) > 3:
        if sys.argv[3] == 'altsig':
            pdf = 'altsig'
        elif sys.argv[3] == 'altbkg':
            # runMode single, bkgPdf alt
            pdf = 'altbkg'

    seed = 12345


sys.argv = []

import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load(config.libobjs)
e = ROOT.panda.Event
ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')
ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')
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


fitBinningT = (120, 60., 120.)
fitBinning = ROOT.RooUniformBinning(fitBinningT[1], fitBinningT[2], fitBinningT[0])
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

# template of templates. used in both runModes
template = ROOT.TH1D('template', '', *fitBinningT)

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
    nbkg = work.arg('nbkg')
    nsignal = work.arg('nsignal')
    if dataType == 'data':
        m0 = work.arg('m0')
        sigma = work.arg('sigma')
        alpha = work.arg('alpha')
        n = work.arg('n')

elif runMode == 'single':
    # workspace
    work = ROOT.RooWorkspace('work', 'work')
    
    mass = work.factory('mass[60., 120.]')
    mass.setUnit('GeV')
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

    # visualization
    canvas = RatioCanvas(lumi = lumi, sim = (dataType == 'mc'))
    canvas.titlePave.SetX2NDC(0.5)
    canvas.legend.setPosition(0.6, 0.7, 0.9, 0.9)
    canvas.legend.add('obs', title = 'Observed', opt = 'LP', color = ROOT.kBlack, mstyle = 8)
    canvas.legend.add('fit', title = 'Fit', opt = 'L', lcolor = ROOT.kBlue, lwidth = 2, lstyle = ROOT.kSolid)
    canvas.legend.add('bkg', title = 'Bkg component', opt = 'L', lcolor = ROOT.kGreen, lwidth = 2, lstyle = ROOT.kDashed)
    if dataType == 'mc':
        canvas.legend.add('mcbkg', title = 'Bkg (MC truth)', opt = 'LF', lcolor = ROOT.kRed, lwidth = 1, fcolor = ROOT.kRed, fstyle = 3003)

    # templates setup
    egPlotter = ROOT.MultiDraw()
    mgPlotter = ROOT.MultiDraw()

    if dataType == 'data':
        # target samples
        if dataSource == 'sph':
            samp = 'phdata'
        else:
            samp = 'eldata'

        for sname in skimConfig[samp][0]:
            egPlotter.addInputPath(config.skimDir + '/' + sname + '_tpeg.root')
    
        # background samples
        if dataSource == 'sph':
            samp = 'phdata'
        else:
            samp = 'mudata'

        for sname in skimConfig[samp][0]:
            mgPlotter.addInputPath(config.skimDir + '/' + sname + '_tpmg.root')

        # will need MC signal template
#        mcSource = ROOT.TFile.Open(outputDir + '/fityields_mc_' + binningName + '_altbkg.root')
#        mcWork = mcSource.Get('work')

    else:
        for sname in skimConfig['mc'][0]:
            egPlotter.addInputPath(config.skimDir + '/' + sname + '/*_tpeg.root')
            mgPlotter.addInputPath(config.skimDir + '/' + sname + '/*_tpmg.root')
        for sname in skimConfig['mcgg'][0]:
            egPlotter.addInputPath(config.skimDir + '/' + sname + '/*_tpeg.root')

    objects = []
    
    # fill templates
    outputFile.cd()
    for binName, fitCut in fitBins:
        if dataType == 'mc':
            hsig = template.Clone('sig_%s' % binName)
            egPlotter.addPlot(hsig, 'tp.mass', fitCut + ' && TMath::Abs(probes.matchedGenId) == 11')

        for conf in tpconfs:
            htarg = template.Clone('target_%s_%s' % (conf, binName))
            objects.append(htarg)
            # unbinned fit
            # ttarg = ROOT.TTree('target_%s_%s' % (conf, binName), 'target')
            # objects.append(ttarg)
    
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
    
            egPlotter.addPlot(htarg, 'tp.mass', cut)
            # egPlotter.addTree(ttarg, cut)
            # egPlotter.addTreeBranch(ttarg, 'mass', 'tp.mass')

            if pdf != 'altbkg':
                hbkg = template.Clone('bkg_%s_%s' % (conf, binName))
                objects.append(hbkg)
                tbkg = ROOT.TTree('bkgtree_%s_%s' % (conf, binName), 'background')
                objects.append(tbkg)

                mgPlotter.addPlot(hbkg, 'tp.mass', cut)
                mgPlotter.addTree(tbkg, cut)
                mgPlotter.addTreeBranch(tbkg, 'mass', 'tp.mass')

            if dataType == 'mc':
                hmc = template.Clone('mcbkg_%s_%s' % (conf, binName))
                objects.append(hmc)

                egPlotter.addPlot(hmc, 'tp.mass', cut + ' && TMath::Abs(probes.matchedGenId) != 11')

    egPlotter.fillPlots()
    mgPlotter.fillPlots()

    outputFile.cd()
    outputFile.Write()

    # closes elif runMode == 'single'

# fit variables
mass.setBinning(fitBinning, 'fitWindow')
mass.setBinning(compBinning, 'compWindow')
massset = ROOT.RooArgSet(mass) # for convenience
masslist = ROOT.RooArgList(mass) # for convenience

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

### Convenience
def addToWS(obj):
    fcn = getattr(work, 'import')
    if obj.InheritsFrom(ROOT.RooAbsData.Class()):
        # need a dummy argument to execute the correct overload
        fcn(obj, ROOT.RooFit.Rename(obj.GetName()))
    else:
        fcn(obj, ROOT.RooFit.Silence())


### Run fits ###

for binName, fitCut in fitBins:
    print 'Run fits for', binName

    for iC, c in enumerate(binName):
        vBinName[iC] = c

    sigModelName = 'sigModel_' + binName

    if runMode == 'batchtoy':
        sigModel = work.pdf(sigModelName)

    elif runMode == 'single':
#        sigdataName = 'sigdata_' + binName
#
#        if dataType == 'mc':
#            # get signal template
#            hsig = outputFile.Get('sig_%s' + binName)
#    
#            sigdata = ROOT.RooDataHist(sigdataName, 'sig', masslist, hsig)
#            addToWS(sigdata)
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
#            addToWS(sigdata)
#
#            sigCore = work.factory('HistPdf::sigCore_' + binName + '({mass}, ' + sigdataName + ', 2)')
#            res = work.factory('Gaussian::res(mass, m0, sigma)')

        if pdf == 'altsig':
            sigModel = work.factory('BreitWigner::%s(mass, mZ, gammaZ)' % sigModelName)
        else:
            sigCore = work.factory('BreitWigner::sigCore_%s(mass, mZ, gammaZ)' % binName)
            res = work.factory('CBShape::res(mass, m0, sigma, alpha, n)')
            sigModel = work.factory('FCONV::%s(mass, sigCore_%s, res)' % (sigModelName, binName))

    print 'Made signal template.'

    intComp = sigModel.createIntegral(massset, 'compWindow')
    intFit = sigModel.createIntegral(massset, 'fitWindow')

    for conf, iconf in tpconfs.items():
        targName = 'target_%s_%s' % (conf, binName)
        modelName = 'model_%s_%s' % (conf, binName)

        if runMode == 'batchtoy':
            targ = work.data(targName)
            model = work.pdf(modelName)

            vals = {}
            iEntry = 0
            while iEntry != sourceYields.GetEntries():
                sourceYields.GetEntry(iEntry)
                iEntry += 1

                if vTPconf[0] == iconf and vBinName.tostring().startswith(binName):
                    for name, vParam in vParams.items():
                        vals[name] = vParam[0]

                    break

            else:
                raise RuntimeError('conf = %d and binName = %s not found in input tree' % (conf, binName))

        elif runMode == 'single':
            targName = 'target_%s_%s' % (conf, binName)
            htarg = outputFile.Get(targName)
            print 'htarg limits:', htarg.GetXaxis().GetXmin(), htarg.GetXaxis().GetXmax(), htarg.GetSumOfWeights()
            
            targHist = ROOT.RooDataHist(targName, 'target', masslist, htarg)
            targ = targHist

# unbinned fit
#            ttarg = outputFile.Get(targName)
#            if dataType == 'mc':
#                targ = ROOT.RooDataSet(targName, 'target', ttarg, ROOT.RooArgSet(mass, weight), '', 'weight')
#            else:
#                targ = ROOT.RooDataSet(targName, 'target', ttarg, ROOT.RooArgSet(mass))

            addToWS(targ)

            vRaw[0] = targ.sumEntries()

            print 'Made target.'

            bkgModelName = 'bkgModel_%s_%s' % (conf, binName)

            if pdf == 'altbkg':
                slope = ROOT.RooRealVar('slope', 'slope', 0., -100., 100.)
                bkgModel = ROOT.RooPolynomial(bkgModelName, 'bkgModel', mass, ROOT.RooArgList(slope))

            else:
                tbkg = outputFile.Get('bkgtree_%s_%s' % (conf, binName))

                if dataType == 'mc':
                    bkgModel = ROOT.KeysShape(bkgModelName, 'bkgModel', mass, tbkg, 'weight', 0.5, 8)
                else:
                    bkgModel = ROOT.KeysShape(bkgModelName, 'bkgModel', mass, tbkg, '', 0.5, 8)

            addToWS(bkgModel)
   
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

            vTPconf[0] = iconf
        
            yields.Fill()

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
                hmcbkg = outputFile.Get('mcbkg_%s_%s' % (conf, binName))
                canvas.legend.apply('mcbkg', hmcbkg)
                canvas.addHistogram(hmcbkg)

            canvas.Update(rList = [], logy = False)

            frame.Print()

            # adding ratio pad
            fitcurve = frame.findObject(modelName + '_Norm[mass]')

            rdata = ROOT.TGraphErrors(htarg.GetNbinsX())

            for iP in range(rdata.GetN()):
                x = htarg.GetXaxis().GetBinCenter(iP + 1)
                nData = htarg.GetBinContent(iP + 1)
                statErr = htarg.GetBinError(iP + 1)
                nFit = fitcurve.interpolate(x)
                if statErr > 0.:
                    rdata.SetPoint(iP, x, (nData - nFit) / statErr)
                else:
                    rdata.SetPoint(iP, x, (nData - nFit))
                # rdata.SetPointError(iP, 0., dmet.GetBinError(iP + 1) / norm)

            rdata.SetMarkerStyle(8)
            rdata.SetMarkerColor(ROOT.kBlack)
            rdata.SetLineColor(ROOT.kBlack)

            canvas.ratioPad.cd()
            canvas.rtitle = '(data - fit) / #sigma_{data}'

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

            rframe.Delete()

        # closes elif runMode == 'single'

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
                htarg = template.Clone('htarg')
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

            vTPconf[0] = iconf

            yields.Fill()

        ROOT.RooMsgService.instance().setStreamStatus(1, True)
        
    
outputFile.cd()
yields.Write()
if runMode == 'single':
    work.Write()

work = None
outputFile.Close()
