#!/usr/bin/env python

"""
Workspace constructor for simultaneous fit using combine

[Terminology]
 - region: Signal and control regions. Consists of an observation 1D histogram, (multiple) background histogram(s) that stack up to match the observation, and (multiple) signal histogram(s).
 - process: Background samples. If a background process appears in multiple regions, they must have a common name.
 - sample: (process, region)

[Interface]
Input: ROOT files with histograms (no directory structure).
Output: A ROOT file containing a RooWorkspace and printouts to stdout which should be pasted into a combine data card.

[Usage]
The script is driven by a parameter card, which is itself a python script defining several variables. An example is at monophoton/fit/parameters.py. Run the script with
 $ [set environment for CMSSW with combine installation]
 $ python workspace.py [parameters_path]
If parameters_path is not given, the parameters are taken from the file named parameters.py in the current directory.

[Parameter card instructions]
Specify the input file name format and the histogram naming schema as filename and histname parameters. Wildcards {region} and {process} should be used in the
naming patterns. The wildcards will be replaced by the list of regions and processes, also specified in the parameters section.
. Histogram naming conventions:
 Histograms for systematic variations must be named with a suffix _(nuisance name)(Up|Down) (e.g. z_signal_pdfUp for process z in the region signal with upward variation of pdf
 uncertainty).
Once inputs are defined, specify the links between samples and special treatments for various nuisances in a parameter card. Nuisance parameters are identified automatically from
the histogram names following the convention given above.
All nuisances where histograms are defined will be included in the workspace, regardless of whether they are "shape" or "scale" type nuisances. Thus the datacard will not contain
the nuisance-process matrix and instead will list all the nuisances as "param"s.
If the parameter card defines a variable cardname, data cards are written to the path specified in the variable, one card per signal model.
If the parameter card defines a variable plotOutname, a ROOT file is created under the given name with the visualization of the workspace content as TH1's.
"""

import os
import sys
import re
import math
import array
import pprint
import collections
import ROOT

from HiggsAnalysis.CombinedLimit.ModelTools import SafeWorkspaceImporter

if len(sys.argv) == 2:
    configPath = sys.argv[1]
else:
    print 'Using configuration ' + os.getcwd() + '/parameters.py'
    configPath = os.getcwd() + '/parameters.py'

execfile(configPath, {'__file__': os.path.realpath(configPath)})

from workspace_config import config

ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load('libRooFitCore.so')

# nuisances below this order are ignored
SMALLNUMBER = 1.e-3
# ignore statistical uncertainties from bins with content less than the cutoff (relative to the total content of the sample)
STATCUTOFF = 100.
# print the list of nuisance parameters at the end
PRINTNUISANCE = False

nuisances = []

def fct(*args):
    """
    Just a shorthand for workspace.factory
    """

    return workspace.factory(*args)

def nuisance(nuis, up, down = None):
    """
    Specific to symmetric log-normal nuisance (which is all we use in the end). Create the nuisance RooRealVar and return the variation
    """

    if down != None:
        a1 = (up - down) * 0.5
    else:
        a1 = up

    if not workspace.arg(nuis):
        fct('{nuis}[0,-5,5]'.format(nuis = nuis))
        nuisances.append(nuis)

    return a1, nuis

def nuisance_old(nuis, target, up, down, form):
    """
    *Obsolete*
    Define (if not defined already) a nuisance parameter and return a yield modifier function.
    """

    a1 = (up - down) * 0.5
    a2 = (up + down) * 0.5

    if not workspace.arg(nuis):
        fct('{nuis}[0,-5,5]'.format(nuis = nuis))
        nuisances.append(nuis)

    if target:
        target += '_'

    variationName = 'var_{target}{nuis}'.format(target = target, nuis = nuis)

    if form == 'lnN':
        var = fct('expr::{name}("TMath::Exp({a1}*@0)*({a1}*@0<0.) + (1.+{a1}*@0)*({a1}*@0>=0.)", {{{nuis}}})'.format(name = variationName, a1 = a1, nuis = nuis))
    elif form == 'quad':
        if abs(a2) < SMALLNUMBER:
            var = fct('expr::{name}("1.+{a1}*@0", {{{nuis}}})'.format(name = variationName, a1 = a1, nuis = nuis))
        else:
            var = fct('expr::{name}("1.+{a1}*@0+{a2}*@0*@0", {{{nuis}}})'.format(name = variationName, a1 = a1, a2 = a2, nuis = nuis))

    return var

def modRelUncert2(var):
    # stat uncertainty of TFs have two parameters
    # allow for general case of N parameters
    relUncert2 = 0.
    iparam = 0
    p = var.getParameter(iparam)
    while p:
        p.setVal(1.)
        d = var.getVal() - 1.
        p.setVal(0.)

        relUncert2 += d * d

        iparam += 1
        p = var.getParameter(iparam)

    return relUncert2

def linkSource(target):
    """
    Find the source sample of the target sample
    """

    try:
        source = next(l[1] for l in config.links if l[0] == target)
    except StopIteration:
        return None

    if source[1] not in config.regions:
        raise RuntimeError('{0} linked from invalid sample {1}'.format(target, source))

    return source

def isLinkSource(source):
    """
    Check if sample is a source of a valid sample
    """

    targets = [l[0] for l in config.links if l[1] == source]
    for target in targets:
        if target[1] in config.regions:
            return True

    return False

def openHistSource(config, process, region, sources):
    fname = config.sourcename.format(process = process, region = region)
    try:
        source = sources[fname]
    except KeyError:
        source = ROOT.TFile.Open(fname)
        sources[fname] = source

    return source

def denormalize(hist, makeInt = False):
    for iX in range(1, hist.GetNbinsX() + 1):
        cont = hist.GetBinContent(iX) * hist.GetXaxis().GetBinWidth(iX)
        if makeInt:
            cont = round(cont)

        hist.SetBinContent(iX, cont)

def fetchHistograms(config, sourcePlots, totals, hstore):
    sources = {}

    for region in config.regions:
        sourcePlots[region] = collections.defaultdict(dict)

        # data histogram
        sourceDir = openHistSource(config, config.data, region, sources)

        histname = config.histname.format(process = config.data, region = region)

        hist = sourceDir.Get(histname)
        if not hist:
            print histname, 'not found'
            sys.exit(1)

        hist.SetDirectory(hstore)

        if config.binWidthNormalized:
            denormalize(hist, makeInt = True)

        # name does not have _*Up or _*Down suffix -> is a nominal histogram
        sourcePlots[region]['data_obs']['nominal'] = hist
        
        # background and signal histograms
        for process in config.bkgProcesses + config.signals:
            sourceDir = openHistSource(config, process, region, sources)

            if process in config.signals and config.signalHistname:
                histname = config.signalHistname.format(process = process, region = region)
            else:
                histname = config.histname.format(process = process, region = region)

            if '/' in histname:
                # to automatically find all the variations, we need to do an "ls" of the directory
                sourceDir = sourceDir.GetDirectory(os.path.dirname(histname))
                histname = os.path.basename(histname)

            # find all histograms matching the specified histogram name pattern + (_variation)
            for key in sourceDir.GetListOfKeys():
                matches = re.match(histname + '(_.+(?:Up|Down)|)$', key.GetName())
                if matches is None:
                    continue

                variation = matches.group(1)

                hist = key.ReadObj()
                hist.SetDirectory(hstore)

                if config.binWidthNormalized:
                    denormalize(hist)

                if not variation:
                    # name does not have _*Up or _*Down suffix -> is a nominal histogram
                    sourcePlots[region][process]['nominal'] = hist

                    if region not in totals:
                        totals[region] = hist.Clone('total_' + region)
                        totals[region].SetDirectory(hstore)
                    else:
                        totals[region].Add(hist)
                else:
                    sourcePlots[region][process][variation[1:]] = hist

    for source in sources.values():
        source.Close()

    sources = {}

    # make sure all signal processes appear at least in one region
    for process in config.signals:
        for region in config.regions:
            if process in sourcePlots[region]:
                break
        else:
            raise RuntimeError('Signal process ' + process + ' was not found in any of the regions.')


if __name__ == '__main__':

    ## INPUT
    # fetch all source histograms first    

    sourcePlots = {}
    totals = {} # {region: background total}

    hstore = ROOT.gROOT.mkdir('hstore')

    fetchHistograms(config, sourcePlots, totals, hstore)

    ## WORKSPACE

    workspace = ROOT.RooWorkspace('wspace')
    wsimport = SafeWorkspaceImporter(workspace)

    ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

    x = fct('{xname}[-1.e+10,1.e+10]'.format(xname = config.xname))
    x.SetTitle(config.xtitle)
    x.setUnit(config.xunit)

    # binning
    h = sourcePlots[config.regions[0]]['data_obs']['nominal']
    xaxis = h.GetXaxis()
    if xaxis.GetXbins().GetSize():
        x.setBinning(ROOT.RooBinning(h.GetNbinsX(), xaxis.GetXbins().GetArray()), 'default')
    else:
        x.setBinning(ROOT.RooBinning(h.GetNbinsX(), xaxis.GetXmin(), xaxis.GetXmax()), 'default')

    print 'Constructing the workspace'

    # will construct the workspace iteratively to resolve links
    iteration = 0
    done = False
    while not done:

        done = True

        print '<Iteration {0}>'.format(iteration)
        iteration += 1

        for region in config.regions:
            dataObsName = 'data_obs_' + region

            if workspace.data(dataObsName):
                # data_obs DataHist is added to the workspace only when all background & signal PDFs are constructed.
                # -> this region is fully constructed
                continue

            regionDone = True
            for process, plots in sourcePlots[region].items():
                if process == 'data_obs':
                    continue

                sample = (process, region)
                sampleName = '{0}_{1}'.format(*sample)

                if workspace.arg(sampleName + '_norm'):
                    # this (process, region) is constructed already
                    continue

                # now construct the ParametricHist + norm
                bins = ROOT.RooArgList()
                # collect nuisances that affect the overall normalization
                normModifiers = {}

                nominal = plots['nominal']

                print '  Constructing pdf for', sampleName

                # there are three different types of samples
                # 1. link target: mu is TF x someone else's mu
                # 2. link source: mu is its own, but has no uncertainty assigned
                # 3. independent: mu is its own and has uncertainties

                sbase = linkSource(sample)
                if sbase is not None:
                    print '    this sample is a function of the yields in', sbase

                    try:
                        # check for source recursively
                        source = sbase
                        while source is not None:
                            if not workspace.arg('{0}_{1}_norm'.format(*source)):
                                # source of this sample is not constructed yet
                                raise ReferenceError()

                            source = linkSource(source)

                    except ReferenceError:
                        print '    but source', source, 'is not constructed yet.'
                        # try again in a later iteration
                        regionDone = False
                        continue

                    sbaseName = '{0}_{1}'.format(*sbase)
                    # sampleName = sampleName + '_' + sbaseName

                    numer = nominal
                    basePlots = sourcePlots[sbase[1]][sbase[0]]
                    denom = basePlots['nominal']

                    ratio = numer.Clone('ratio')
                    ratio.Divide(denom)

                    for ibin in range(1, nominal.GetNbinsX() + 1):
                        rbin = ratio.GetBinContent(ibin)

                        binName = sampleName + '_bin{0}'.format(ibin)
                        baseBinName = sbaseName + '_bin{0}'.format(ibin)

                        if rbin == 0.:
                            print '    WARNING: {region} {process} bin{ibin} has tf = 0'.format(region = region, process = process, ibin = ibin)
                            bin = fct('mu_{bin}[0.]'.format(bin = binName))
                            bins.add(bin)
                            continue

                        # tfName = binName + '_tf'
                        tfName = sampleName + '_' + sbaseName + '_bin{0}'.format(ibin) + '_tf'

                        # nominal tfactor (constant)
                        fct('{tf}[{val}]'.format(tf = tfName, val = rbin))

                        # list of yield modifiers (switch to using RooArgList if the chained string becomes too long)
                        modifiers = []

                        # statistical uncertainty on tfactor
                        binRelErr = nominal.GetBinError(ibin) / nominal.GetBinContent(ibin)
                        baseRelErr = denom.GetBinError(ibin) / denom.GetBinContent(ibin)

                        modifiers.append(nuisance(baseBinName + '_stat', baseRelErr))
                        modifiers.append(nuisance(binName + '_stat', binRelErr))

                        # other systematic uncertainties on tfactor
                        # collect all variations on numerator and denominator
                        upVariations = set(v for v in plots.keys() if v.endswith('Up'))
                        upVariations |= set(v for v in basePlots.keys() if v.endswith('Up'))

                        for variation in upVariations:
                            var = variation[:-2]

                            if sample in config.ignoredNuisances and var in config.ignoredNuisances[sample]:
                                continue

                            if var in config.scaleNuisances and var in normModifiers:
                                # this uncertainty is non-shape and is taken care of already
                                continue

                            if var + 'Up' in plots:
                                numerUp = plots[var + 'Up'].GetBinContent(ibin)
                                numerDown = plots[var + 'Down'].GetBinContent(ibin)
                            else:
                                numerUp = numer.GetBinContent(ibin)
                                numerDown = numer.GetBinContent(ibin)

                            if var + 'Up' in basePlots:
                                denomUp = basePlots[var + 'Up'].GetBinContent(ibin)
                                denomDown = basePlots[var + 'Down'].GetBinContent(ibin)
                            else:
                                denomUp = denom.GetBinContent(ibin)
                                denomDown = denom.GetBinContent(ibin)

                            rup = numerUp / denomUp / rbin - 1.
                            rdown = numerDown / denomDown / rbin - 1.

                            if (sample, sbase, var) in config.ratioCorrelations:
                                # need to split the nuisance into correlated and anti-correlated
                                # assuming no scaleNuisance is partially correlated
                                correlation = config.ratioCorrelations[(sample, sbase, var)]
                                raup = numerUp / denomDown / rbin - 1.
                                radown = numerDown / denomUp / rbin - 1.

                                if var in config.deshapedNuisances:
                                    # this nuisance is artificially decorrelated among bins
                                    # calling "corr"Uncert function, but in reality this results in one nuisance per bin
                                    var = var + '_bin{ibin}'.format(ibin = ibin)

                                if abs(rup) > SMALLNUMBER or abs(rdown) > SMALLNUMBER:
                                    coeff = (1. + correlation) * 0.5
                                    if coeff != 0.:
                                        modifiers.append(nuisance(var + '_corr', coeff * rup, coeff * rdown))

                                if abs(raup) > SMALLNUMBER or abs(radown) > SMALLNUMBER:
                                    coeff = (1. - correlation) * 0.5
                                    if coeff != 0.:
                                        modifiers.append(nuisance(var + '_acorr', coeff * raup, coeff * radown))

                            else:
                                if abs(rup) < SMALLNUMBER and abs(rdown) < SMALLNUMBER:
                                    # fully correlated uncertainty that affects the numerator and denominator identically
                                    continue

                                if var in config.scaleNuisances:
                                    # this is a bin-independent modifier
                                    if var not in normModifiers:
                                        normModifiers[var] = nuisance(var, rup, rdown)
                                else:
                                    if var in config.deshapedNuisances:
                                        # this nuisance is artificially decorrelated among bins
                                        # calling "corr"Uncert function, but in reality this results in one nuisance per bin
                                        var = var + '_bin{ibin}'.format(ibin = ibin)

                                    modifiers.append(nuisance(var, rup, rdown))

                        if len(modifiers) > 0:
                            # "raw" yield (= base x tfactor)
                            fct('expr::raw_{bin}("@0*@1", {{{tf}, mu_{baseBin}}})'.format(bin = binName, tf = tfName, baseBin = baseBinName))

                            procnorm = ROOT.ProcessNormalization('mod_{bin}'.format(bin = binName), 'mod_{bin}'.format(bin = binName))
                            for m in modifiers:
                                procnorm.addLogNormal(1. + m[0], workspace.var(m[1]))

                            wsimport(procnorm)

                            # mu = raw x mod
                            bin = fct('prod::mu_{bin}(raw_{bin},mod_{bin})'.format(bin = binName))
                        else:
                            bin = fct('expr::mu_{bin}("@0*@1", {{{tf}, mu_{baseBin}}})'.format(bin = binName, tf = tfName, baseBin = baseBinName))

                        bins.add(bin)

                    ratio.Delete()

                elif isLinkSource(sample):
                    print '    this sample is a base of some other sample'
                    # each bin must be described by a free-floating RooRealVar unless this is a fixed base
                    # uncertainties are all casted on tfactors

                    if sample in config.staticBase:
                        print '      with a static shape'
                        fct('mu_{sample}_scale[1.,0.,10.]'.format(sample = sampleName))
                        # bin mu is raw x norm
                        for ibin in range(1, nominal.GetNbinsX() + 1):
                            fct('rawmu_{sample}_bin{bin}[{val}]'.format(sample = sampleName, bin = ibin, val = nominal.GetBinContent(ibin)))
                            bin = fct('prod::mu_{sample}_bin{bin}(rawmu_{sample}_bin{bin},mu_{sample}_scale)'.format(sample = sampleName, bin = ibin))
                            bins.add(bin)
                    else:
                        for ibin in range(1, nominal.GetNbinsX() + 1):
                            bin = fct('mu_{sample}_bin{bin}[{val},0.,{max}]'.format(sample = sampleName, bin = ibin, val = nominal.GetBinContent(ibin), max = nominal.GetMaximum() * 10.))
                            bins.add(bin)

                else:
                    print '    this sample does not participate in constraints'

                    for ibin in range(1, nominal.GetNbinsX() + 1):
                        binName = sampleName + '_bin{0}'.format(ibin)

                        cval = nominal.GetBinContent(ibin)
                        if cval <= 0.:
                            # bin content is 0
                            bin = fct('mu_{bin}[0.]'.format(bin = binName))
                        else:
                            modifiers = []

                            # statistical uncertainty - often not considered
                            relErr = nominal.GetBinError(ibin) / cval
                            bkgTotal = totals[region].GetBinContent(ibin)
                            if relErr > SMALLNUMBER and (bkgTotal <= 0. or cval / bkgTotal > STATCUTOFF):
                                modifiers.append(nuisance('{bin}_stat'.format(bin = binName), relErr))

                            for variation in plots:
                                if not variation.endswith('Up'):
                                    continue

                                var = variation[:-2]

                                try:
                                    if var in config.ignoredNuisances[sample]:
                                        continue
                                except KeyError:
                                    pass

                                dup = plots[var + 'Up'].GetBinContent(ibin) / cval - 1.
                                ddown = plots[var + 'Down'].GetBinContent(ibin) / cval - 1.

                                if abs(dup - ddown) < SMALLNUMBER:
                                    continue

                                if var in config.scaleNuisances:
                                    # this is a bin-independent variation
                                    if var in normModifiers:
                                        # we took care of this already
                                        continue

                                    if sample[0] in config.floatProcesses:
                                        # if this sample is freely floating; scale modifiers are unnecessary degrees of freedom
                                        continue

                                    normModifiers[var] = nuisance(var, dup, ddown)
                                else:
                                    if var in config.deshapedNuisances:
                                        # this nuisance is artificially decorrelated among bins
                                        # treat each (variation name)_(bin name) as a variation name
                                        var += '_bin{ibin}'.format(ibin = ibin)

                                    modifiers.append(nuisance(var, dup, ddown))

                            if len(modifiers) > 0:
                                raw = fct('raw_{bin}[{val}]'.format(bin = binName, val = cval))

                                procnorm = ROOT.ProcessNormalization('mod_{bin}'.format(bin = binName), 'mod_{bin}'.format(bin = binName))
                                for m in modifiers:
                                    procnorm.addLogNormal(1. + m[0], workspace.var(m[1]))

                                wsimport(procnorm)

                                bin = fct('prod::mu_{bin}(raw_{bin},mod_{bin})'.format(bin = binName))
                            else:
                                bin = fct('mu_{bin}[{val}]'.format(bin = binName, val = cval))

                        bins.add(bin)

                    # close switch between the three types of samples

                # now compile the bins into a parametric hist pdf and a norm
                shape = ROOT.RooParametricHist(sampleName, sampleName, x, bins, nominal)
                wsimport(shape)

                if sample[0] in config.floatProcesses:
                    print '      normalization is floated'
                    normName = 'rawnorm'
                    fct('mod_{sample}_norm[1.,0.,100.]'.format(sample = sampleName))

                elif len(normModifiers) > 0:
                    normName = 'rawnorm'
                    procnorm = ROOT.ProcessNormalization('mod_{sample}_norm'.format(sample = sampleName), 'mod_{sample}_norm'.format(sample = sampleName))
                    for m in normModifiers.values():
                        procnorm.addLogNormal(1. + m[0], workspace.var(m[1]))

                    wsimport(procnorm)

                else:
                    # if there is no normModifier, RooAddition of the bins is the norm
                    normName = 'norm'

                if bins.getSize() > 1:
                    binNames = ','.join(bins.at(ib).GetName() for ib in range(bins.getSize()))
                    fct('sum::{sample}_{norm}({binNames})'.format(sample = sampleName, norm = normName, binNames = binNames))
                else:
                    fct('expr::{sample}_{norm}("@0", {{{bin}}})'.format(sample = sampleName, norm = normName, bin = bins.at(0).GetName()))

                if normName == 'rawnorm':
                    fct('expr::{sample}_norm("@0*@1", {{{sample}_rawnorm, mod_{sample}_norm}})'.format(sample = sampleName))
            
            # / for process, plots in sourcePlots[region].items():

            if regionDone:
                # All processes in the region are constructed. Add the observed RooDataHist.
                data_obs = ROOT.RooDataHist(dataObsName, dataObsName, ROOT.RooArgList(x), sourcePlots[region]['data_obs']['nominal'])
                wsimport(data_obs)

            else:
                done = False

    if PRINTNUISANCE:
        for n in sorted(nuisances):
            print n, 'param 0 1'

    if not os.path.isdir(os.path.dirname(os.path.realpath(config.outname))):
        os.makedirs(os.path.dirname(os.path.realpath(config.outname)))

    workspace.writeToFile(config.outname)

    print 'Workspace written to', config.outname

    wsimport = None
    wssource = ROOT.TFile.Open(config.outname)
    workspace = wssource.Get('wspace')

    x = workspace.var(config.xname)

    ## DATACARDS
    if config.cardname:
        print 'Writing data cards'

        carddir = os.path.dirname(os.path.realpath(config.cardname))
        if not os.path.isdir(carddir):
            os.makedirs(carddir)

        # sort samples

        samplesByRegion = {} # names of background samples by region
        procIds = {}
        signalRegions = set()

        maxRegionNameLength = 0

        for region, procPlots in sourcePlots.items():
            samplesByRegion[region] = []

            # sort processes by expectation
            def compProc(p, q):
                if procPlots[p]['nominal'].GetSumOfWeights() > procPlots[q]['nominal'].GetSumOfWeights():
                    return -1
                else:
                    return 1

            procs = sorted(procPlots.keys(), compProc)

            for p in procs:
                if p == 'data_obs':
                    continue
                elif p in config.signals:
                    signalRegions.add(region)
                else:
                    samplesByRegion[region].append(p)
                    if p not in procIds:
                        procIds[p] = len(procIds) + 1

            if len(region) > maxRegionNameLength:
                maxRegionNameLength = len(region)

        print 'signalRegions', list(signalRegions)

        # define datacard template

        hrule = '-' * 140

        # combine likes to have relative path to the workspace (matters when using combineCards.py)
        ws_abs_path = os.path.realpath(config.outname)
        ws_path = os.path.relpath(ws_abs_path, carddir)

        lines = [
            'imax * number of bins',
            'jmax * number of processes minus 1',
            'kmax * number of nuisance parameters',
            hrule,
            'shapes * * %s wspace:$PROCESS_$CHANNEL' % ws_path,
            hrule,
        ]

        colw = max(maxRegionNameLength + 1, 9)

        # list of regions, signal regions first
        line = 'bin          ' + ''.join(sorted('%{w}s'.format(w = colw) % r for r in signalRegions)) + ''.join(sorted('%{w}s'.format(w = colw) % r for r in samplesByRegion if r not in signalRegions))
        lines.append(line)

        # number of observed events in each region (set to -1 - combine will read it from workspace)
        line = 'observation  ' + ''.join('%{w}.1f'.format(w = colw) % o for o in [-1.] * len(samplesByRegion))
        lines.append(line)

        lines.append(hrule)

        # columns for all background processes and yields
        columns = []

        # signal region first
        for region in signalRegions:
            for proc in samplesByRegion[region]:
                columns.append((region, proc, str(procIds[proc])))

        for region in sorted(samplesByRegion):
            if region in signalRegions:
                continue

            for proc in samplesByRegion[region]:
                columns.append((region, proc, str(procIds[proc])))

        # now loop over signal models and write a card per model
        for signal in config.signals:
            cardcolumns = list(columns)
            cardlines = list(lines)

            # insert the signal expectation as the first column
            ic = 0
            for region in signalRegions:
                # skip to the first column of the region
                while columns[ic][0] != region:
                    ic += 1
                
                cardcolumns.insert(ic, (region, signal, str(-1)))

            for ih, heading in enumerate(['bin', 'process', 'process']):
                line = '%13s' % heading
                for column in cardcolumns:
                    w = max(len(s) for s in column)
                    line += ('%{width}s'.format(width = w + 1)) % column[ih]
                cardlines.append(line)

            line = 'rate         '
            for column in cardcolumns:
                w = max(len(s) for s in column)
                line += ('%{width}.1f'.format(width = w + 1)) % 1.
            cardlines.append(line)

            cardlines.append(hrule)

            for nuisance in sorted(nuisances):
                # remove nuisances related to other signal models
                matched_other_signal = False
                for s in config.signals:
                    if s != signal and nuisance.startswith(s):
                        matched_other_signal = True
                        break

                if matched_other_signal:
                    continue
                
                if nuisance in config.flatParams:
                    cardlines.append(nuisance + ' flatParam 0 1')
                else:
                    cardlines.append(nuisance + ' param 0 1')

            cardname = config.cardname.format(signal = signal)

            with open(cardname, 'w') as datacard:
                for line in cardlines:
                    if '{signal}' in line:
                        line = line.format(signal = signal)

                    datacard.write(line + '\n')
            
            print ' ', signal, '-->', cardname

    ## PLOTS
    if config.plotsOutname:
        print 'Visualizing workspace'

        plotsFile = ROOT.TFile.Open(config.plotsOutname, 'recreate')

        xbinning = x.getBinning('default')
        boundaries = xbinning.array()
        binning = array.array('d', [boundaries[i] for i in range(xbinning.numBoundaries())])

        allPdfs = workspace.allPdfs()
        pdfItr = allPdfs.iterator()
        while True:
            pdf = pdfItr.Next()
            if not pdf:
                break

            hvars = {}
            normVars = {}

            # cannot do this any more with ProcessNormalization
            #mod = workspace.function('mod_' + pdf.GetName() + '_norm')
            #if mod:
            #    # normalization given to this PDF has associated variations
            #
            #    # loop over all variations
            #    variations = mod.components()
            #    varItr = variations.iterator()
            #    while True:
            #        var = varItr.Next()
            #        if not var:
            #            break
            #
            #        varName = var.GetName().replace('var_' + pdf.GetName() + '_norm_', '')
            #        normVars[varName] = var
            #        hvars[varName] = ROOT.TH1D(pdf.GetName() + '_' + varName, '', len(binning) - 1, binning)

            # test to determine PDF type
            # if mu is a RooRealVar -> simplest case; static PDF
            # if mu = raw x mod and raw is a RooRealVar -> dynamic PDF, not linked
            # if mu = raw x mod and raw is a function -> linked from another sample

            bin1Name = '%s_bin1' % pdf.GetName()

            if not workspace.var('mu_' + bin1Name) and not workspace.var('raw_' + bin1Name) and not workspace.var('mu_' + pdf.GetName() + '_scale'):
                samp, region = pdf.GetName().split('_')
                sample = (samp, region)
                sbase = linkSource(sample)
                sbaseName = '{0}_{1}'.format(*sbase)

                tfName = samp + '_' + region + '_' + sbaseName 
                # raw is tf x another mu -> plot the TF
                hnominal = ROOT.TH1D('tf_' + tfName, ';' + config.xtitle, len(binning) - 1, binning)
                huncert = hnominal.Clone(hnominal.GetName() + '_uncertainties')
                isTF = True

            else:
                # otherwise plot the distribution
                hnominal = ROOT.TH1D(pdf.GetName(), ';' + config.xtitle, len(binning) - 1, binning)
                hnominal.GetXaxis().SetTitle(config.xtitle)
                hnominal.GetYaxis().SetTitle('Events / GeV')
                huncert = hnominal.Clone(hnominal.GetName() + '_uncertainties')
                isTF = False

                # pdf.createHistogram returns something very weird
                # hnominal = pdf.createHistogram(pdf.GetName(), x, ROOT.RooFit.Binning('default'))
                for iX in range(1, hnominal.GetNbinsX() + 1):
                    # has to be a RooParametricHist
                    hnominal.SetBinContent(iX, workspace.arg('mu_%s_bin%d' % (pdf.GetName(), iX)).getVal())

            # hnominal: nominal value +- stat uncertainty
            # huncert: nominal value +- stat + syst uncertainty

            for ibin in range(1, len(binning)):
                binName = '%s_bin%d' % (pdf.GetName(), ibin)

                if isTF:
                    tf = workspace.var('%s_bin%d_tf' % (tfName, ibin))
                    val = tf.getVal()

                    # TF is historically plotted inverted
                    hnominal.SetBinContent(ibin, 1. / val)
                    huncert.SetBinContent(ibin, 1. / val)

                else:
                    val = hnominal.GetBinContent(ibin)

                totalUncert2 = 0.

                for varName, var in normVars.items():
                    if varName.startswith('freenorm'):
                        # don't plot free normalizations
                        continue

                    # modRelUncert2 is used for convenience - all vars here should have a single parameter.
                    # also, TF-based pdf should not have norm mods - OK to not consider "if isTF".
                    uncert2 = modRelUncert2(var) * val * val
                    hvars[varName].SetBinContent(ibin, math.sqrt(uncert2))

                    totalUncert2 += uncert2

                # switched to ProcessNormalization; cannot draw systematic uncertainties any more..
                #mod = workspace.function('mod_' + binName)
                #if mod:
                #    # loop over all variations for this bin
                #    variations = mod.components()
                #    varItr = variations.iterator()
                #    while True:
                #        var = varItr.Next()
                #        if not var:
                #            break
                #
                #        uncert2 = modRelUncert2(var) * val * val
                #
                #        if uncert2 > 1000.:
                #            print modRelUncert2(var), val, pdf.GetName(), var.GetName()
                #
                #        if var.GetName().endswith('_stat'):
                #            if isTF: # nominal is 1/value - d(1/f) = -df/f^2.
                #                if val > 0.:
                #                    hnominal.SetBinError(ibin, math.sqrt(uncert2) / val / val)
                #                else:
                #                    hnominal.SetBinError(ibin, 0.)
                #            else:
                #                hnominal.SetBinError(ibin, math.sqrt(uncert2))
                #        else:
                #            varName = var.GetName().replace('var_' + binName + '_', '')
                #            if varName not in hvars:
                #                hvars[varName] = ROOT.TH1D(pdf.GetName() + '_' + varName, '', len(binning) - 1, binning)
                #
                #            if isTF:
                #                hvars[varName].SetBinContent(ibin, math.sqrt(uncert2) / val / val)
                #            else:
                #                hvars[varName].SetBinContent(ibin, math.sqrt(uncert2))
                #
                #        # total uncertainty includes stat
                #        totalUncert2 += uncert2

                if isTF:
                    if val > 0.:
                        huncert.SetBinError(ibin, math.sqrt(totalUncert2) / val / val)
                    else:
                        huncert.SetBinError(ibin, 0.)
                else:
                    huncert.SetBinError(ibin, math.sqrt(totalUncert2))

            hasUncert = sum(huncert.GetBinError(iX) for iX in range(1, huncert.GetNbinsX() + 1)) != 0.

            plotsFile.cd()
            hnominal.SetDirectory(plotsFile)
            hnominal.Write()
            if hasUncert:
                huncert.SetDirectory(plotsFile)
                huncert.Write()
            for h in hvars.values():
                h.SetDirectory(plotsFile)
                h.Write()

            hvars.clear()
            normVars.clear()

        allData = workspace.allData()
        """
        dataItr = allData.iterator()
        while True:
            data = dataItr.Next()
            if not pdf:
                break
        """
        for data in allData:
            hData = data.createHistogram(data.GetName(), x, ROOT.RooFit.Binning('default'))
            hData.SetDirectory(plotsFile)
            hData.Write()

        workspace = None
        wssource.Close()

        plotsFile.Close()

        print 'Histograms saved to', config.plotsOutname
