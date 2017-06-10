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
If the parameter card defines a variable carddir, data cards are written to the path specified in the variable, one card per signal model.
If the parameter card defines a variable plotOutname, a ROOT file is created under the given name with the visualization of the workspace content as TH1's.

 Variables to be defined:
 <input>
  sourcedir - Where to find the ROOT files containing histograms.
  filename - Source file name format. Wildcards {region} and {process} can be used.
  histname - Format of histogram names to be found in the source files. Wildcards {region} and {process} can be used.
  signalHistname - Format of signal histogram names.
  binWidthNormalized - boolean specifying whether the input histograms are already bin-width normalized.
 <physics>
  regions - List of signal and control region names. Replaces the {region} wildcard in the input definitions.
  processes - Full list of process names. Not all processes have to appear in every region.
  signals - List of signal point names.
  links - List of links between samples. [(target process, target region), (source process, source region)].
 <nuisances>
  ignoredNuisances - For each (process, region), list the nuisances that can be found in the input files as histograms but should be ignored. {(process, region): [nuisance]}.
  scaleNuisances - List of nuisances that affect the normalization only. All of them must have corresponding histograms.
  ratioCorrelations - Nuisances are fully correlated between samples in a link by default. Use this to specify partial correlations. {((target sample), (source sample), nuisance): correlation}.
  deshapedNuisances - List of nuisances to be artificially bin-decorrelated. Systematic variations in this list will have nuisance a parameter for each bin.
  floats - List of samples with floating normalization but does not participate in any links.
 <optional>
  (customize) - A function that takes a RooWorkspace as the sole argument. Called at the end of workspace preparation to edit the workspace content.
  (carddir) - When given, data card files are produced and saved in this directory.
  (plotsOutname) - When given, a ROOT file with histograms visualizing the workspace content is created.
    (xtitle) - X axis title of the histograms.
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

sys.path.append(os.path.dirname(configPath))
config = __import__(os.path.basename(configPath).replace('.py', ''))

ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load('libRooFitCore.so')

# nuisances below this order are ignored
SMALLNUMBER = 1.e-3
# ignore statistical uncertainties from bins with content less than the cutoff (relative to the total content of the sample)
STATCUTOFF = 0.1
# print the list of nuisance parameters at the end
PRINTNUISANCE = False

workspace = ROOT.RooWorkspace('wspace')
wsimport = SafeWorkspaceImporter(workspace)

nuisances = []

def fct(*args):
    """
    Just a shorthand for workspace.factory
    """

    return workspace.factory(*args)

def nuisance(nuis, target, up, down, form):
    """
    Define (if not defined already) a nuisance parameter and return a yield modifier function.
    """

    a1 = (up - down) * 0.5
    a2 = (up + down) * 0.5

    if not workspace.arg(nuis):
        fct('{nuis}[0,-5,5]'.format(nuis = nuis))
        nuisances.append(nuis)

    if target:
        target += '_'

    modifierName = 'mod_{target}{nuis}'.format(target = target, nuis = nuis)

    if form == 'lnN':
        mod = fct('expr::{mod}("TMath::Exp({a1}*@0)", {{{nuis}}})'.format(mod = modifierName, a1 = a1, nuis = nuis))
    elif form == 'quad':
        if abs(a2) < SMALLNUMBER:
            mod = fct('expr::{mod}("1.+{a1}*@0", {{{nuis}}})'.format(mod = modifierName, a1 = a1, nuis = nuis))
        else:
            mod = fct('expr::{mod}("1.+{a1}*@0+{a2}*@0*@0", {{{nuis}}})'.format(mod = modifierName, a1 = a1, a2 = a2, nuis = nuis))

    return mod

def ratioStatNuisance(numerName, denomName, nRelErr, dRelErr):
    """
    Define nuisance parameters for the numerator and the denominator of a ratio, and return a lnN yield modifier.
    """

    dNuis = '{denom}_stat'.format(denom = denomName)
    if not workspace.arg(dNuis):
        fct('{nuis}[0.,-5.,5.]'.format(nuis = dNuis))
        nuisances.append(dNuis)

    nNuis = '{numer}_stat'.format(numer = numerName)
    fct('{nuis}[0.,-5.,5.]'.format(nuis = nNuis))
    nuisances.append(nNuis)

    modifierName = 'mod_{numer}_{denom}_stat'.format(numer = numerName, denom = denomName)

    mod = fct('expr::{mod}("TMath::Exp({n}*@0+{d}*@1)", {{{nNuis}, {dNuis}}})'.format(mod = modifierName, n = nRelErr, d = dRelErr, nNuis = nNuis, dNuis = dNuis))

    return mod

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

def fetchHistograms(_config, _sourcePlots, _totals, _hstore):
    sources = {}

    for region in _config.regions:
        _sourcePlots[region] = collections.defaultdict(dict)

        histnames = []

        for process in _config.processes:
            fname = _config.sourcedir + '/' + _config.filename.format(process = process, region = region)
            try:
                source = sources[fname]
            except KeyError:
                source = ROOT.TFile.Open(fname)
                sources[fname] = source

            sourceDir = source

            histname = _config.histname.format(process = process, region = region)
            if '/' in histname:
                sourceDir = source.GetDirectory(os.path.dirname(histname))
                histname = os.path.basename(histname)

            # find all histograms matching the specified histogram name pattern + (_variation)
            for key in sourceDir.GetListOfKeys():
                matches = re.match(histname + '(_.+(?:Up|Down)|)', key.GetName())
                if matches is None:
                    continue

                histnames.append(key.GetName())

                variation = matches.group(1)

                obj = key.ReadObj()
                obj.SetDirectory(_hstore)

                if _config.binWidthNormalized:
                    for iX in range(1, obj.GetNbinsX() + 1):
                        cont = obj.GetBinContent(iX) * obj.GetXaxis().GetBinWidth(iX)
                        if process == 'data_obs':
                            cont = round(cont)

                        obj.SetBinContent(iX, cont) 

                if not variation:
                    # name does not have _*Up or _*Down suffix -> is a nominal histogram
                    _sourcePlots[region][process]['nominal'] = obj

                    if process != 'data_obs':
                        # background process
                        if region not in _totals:
                            _totals[region] = obj.Clone('total_' + region)
                            _totals[region].SetDirectory(_hstore)
                        else:
                            _totals[region].Add(obj)
                else:
                    _sourcePlots[region][process][variation[1:]] = obj

        for process in _config.signals:
            fname = _config.sourcedir + '/' + _config.filename.format(process = process, region = region)
            try:
                source = sources[fname]
            except KeyError:
                source = ROOT.TFile.Open(fname)
                sources[fname] = source

            sourceDir = source

            histname = _config.signalHistname.format(process = process, region = region)

            obj = sourceDir.Get(histname)
            if not obj:
                continue

            histnames.append(histname)

            obj.SetDirectory(_hstore)

            if _config.binWidthNormalized:
                for iX in range(1, obj.GetNbinsX() + 1):
                    cont = obj.GetBinContent(iX) * obj.GetXaxis().GetBinWidth(iX)
                    if process == 'data_obs':
                        cont = round(cont)

                    obj.SetBinContent(iX, cont) 

            # name does not have _*Up or _*Down suffix -> is a nominal histogram
            _sourcePlots[region][process]['nominal'] = obj

    for source in sources.values():
        source.Close()

    # make sure all signal processes appear at least in one region
    for process in _config.signals:
        for region in _config.regions:
            if process in _sourcePlots[region]:
                break
        else:
            raise RuntimeError('Signal process ' + process + ' was not found in any of the regions.')


if __name__ == '__main__':

    ## INPUT
    # fetch all source histograms first    

    sourcePlots = {}
    totals = {}

    hstore = ROOT.gROOT.mkdir('hstore')

    print 'Retrieving all histograms from', config.sourcedir

    fetchHistograms(config, sourcePlots, totals, hstore)

    ## WORKSPACE

    ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

    x = fct('x[-1.e+10,1.e+10]')

    # binning
    h = sourcePlots[config.regions[0]]['data_obs']['nominal']
    x.setBinning(ROOT.RooBinning(h.GetNbinsX(), h.GetXaxis().GetXbins().GetArray()), 'default')

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

                        if rbin == 0.:
                            print '    WARNING: {region} {process} bin{ibin} has tf = 0'.format(region = region, process = process, ibin = ibin)
                            bin = fct('mu_{bin}[0.]')
                            bins.add(bin)
                            continue

                        binName = sampleName + '_bin{0}'.format(ibin)
                        baseBinName = sbaseName + '_bin{0}'.format(ibin)

                        # tfName = binName + '_tf'
                        tfName = sampleName + '_' + sbaseName + '_bin{0}'.format(ibin) + '_tf'

                        # nominal tfactor (constant)
                        fct('{tf}[{val}]'.format(tf = tfName, val = rbin))

                        # list of yield modifiers (switch to using RooArgList if the chained string becomes too long)
                        modifiers = []

                        # statistical uncertainty on tfactor
                        binRelErr = nominal.GetBinError(ibin) / nominal.GetBinContent(ibin)
                        baseRelErr = denom.GetBinError(ibin) / denom.GetBinContent(ibin)
                        modifiers.append(ratioStatNuisance(binName, baseBinName, binRelErr, baseRelErr))

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
                                        modifiers.append(nuisance(var + '_corr', tfName, coeff * rup, coeff * rdown, 'lnN'))

                                if abs(raup) > SMALLNUMBER or abs(radown) > SMALLNUMBER:
                                    coeff = (1. - correlation) * 0.5
                                    if coeff != 0.:
                                        modifiers.append(nuisance(var + '_acorr', tfName, coeff * raup, coeff * radown, 'lnN'))

                            else:
                                if abs(rup) < SMALLNUMBER and abs(rdown) < SMALLNUMBER:
                                    # fully correlated uncertainty that affects the numerator and denominator identically
                                    continue

                                if var in config.scaleNuisances:
                                    normModifiers[var] = nuisance(var, '{sample}_norm'.format(sample = sampleName), rup, rdown, 'lnN')
                                else:
                                    if var in config.deshapedNuisances:
                                        # this nuisance is artificially decorrelated among bins
                                        # calling "corr"Uncert function, but in reality this results in one nuisance per bin
                                        var = var + '_bin{ibin}'.format(ibin = ibin)

                                    modifiers.append(nuisance(var, tfName, rup, rdown, 'lnN'))

                        if len(modifiers) > 0:
                            # "raw" yield (= base x tfactor)
                            fct('expr::raw_{bin}("@0*@1", {{{tf}, mu_{baseBin}}})'.format(bin = binName, tf = tfName, baseBin = baseBinName))
                            fct('prod::unc_{bin}({mod})'.format(bin = binName, mod = ','.join(m.GetName() for m in modifiers)))

                            # mu = raw x unc
                            bin = fct('prod::mu_{bin}(raw_{bin},unc_{bin})'.format(bin = binName))
                        else:
                            bin = fct('expr::mu_{bin}("@0*@1", {{{tf}, mu_{baseBin}}})'.format(bin = binName, tf = tfName, baseBin = baseBinName))

                        bins.add(bin)

                    ratio.Delete()

                elif isLinkSource(sample):
                    print '    this sample is a base of some other sample'
                    # each bin must be described by a free-floating RooRealVar
                    # uncertainties are all casted on tfactors

                    for ibin in range(1, nominal.GetNbinsX() + 1):
                        bin = fct('mu_{sample}_bin{bin}[{val},0.,{max}]'.format(sample = sampleName, bin = ibin, val = nominal.GetBinContent(ibin), max = nominal.GetMaximum() * 10.))
                        bins.add(bin)

                else:
                    print '    this sample does not participate in constraints'

                    if sample in config.floats:
                        normName = '{0}_{1}_freenorm'.format(*sample)
                        normModifiers[normName] = fct('{norm}[1.,0.,1000.]'.format(norm = normName))

                    for ibin in range(1, nominal.GetNbinsX() + 1):
                        binName = sampleName + '_bin{0}'.format(ibin)

                        cval = nominal.GetBinContent(ibin)
                        if cval == 0.:
                            # bin content is 0
                            bin = fct('mu_{bin}[0.]'.format(bin = binName))
                        else:

                            modifiers = []

                            # statistical uncertainty - often not considered
                            relErr = nominal.GetBinError(ibin) / cval
                            if relErr > SMALLNUMBER and cval / totals[region].GetBinContent(ibin) > STATCUTOFF:
                                modifiers.append(nuisance('{bin}_stat'.format(bin = binName), '', relErr, -relErr, 'lnN'))

                            for variation in plots:
                                if not variation.endswith('Up'):
                                    continue

                                var = variation[:-2]

                                if sample in config.ignoredNuisances and var in config.ignoredNuisances[sample]:
                                    continue

                                if var in config.scaleNuisances and (var in normModifiers or sample in config.floats):
                                    continue

                                dup = plots[var + 'Up'].GetBinContent(ibin) / cval - 1.
                                ddown = plots[var + 'Down'].GetBinContent(ibin) / cval - 1.

                                if abs(dup - ddown) < SMALLNUMBER:
                                    continue

                                if var in config.scaleNuisances:
                                    if sample not in config.floats:
                                        # if this sample is freely floating, scale modifiers are unnecessary degrees of freedom
                                        normModifiers[var] = nuisance(var, '{sample}_norm'.format(sample = sampleName), dup, ddown, 'lnN')
                                else:
                                    if var in config.deshapedNuisances:
                                        # this nuisance is artificially decorrelated among bins
                                        # treat each (variation name)_(bin name) as a variation name
                                        var = var + '_bin{ibin}'.format(ibin = ibin)

                                    modifiers.append(nuisance(var, binName, dup, ddown, 'lnN'))

                            if len(modifiers) > 0:
                                raw = fct('raw_{bin}[{val}]'.format(bin = binName, val = cval))
                                fct('prod::unc_{bin}({mod})'.format(bin = binName, mod = ','.join(m.GetName() for m in modifiers)))

                                # mu = raw x unc
                                bin = fct('prod::mu_{bin}(raw_{bin},unc_{bin})'.format(bin = binName))
                            else:
                                bin = fct('mu_{bin}[{val}]'.format(bin = binName, val = cval))

                        bins.add(bin)

                    # close switch between the three types of samples

                # now compile the bins into a parametric hist pdf and a norm
                shape = ROOT.RooParametricHist(sampleName, sampleName, x, bins, nominal)
                wsimport(shape)

                if len(normModifiers) > 0:
                    normName = 'rawnorm'
                else:
                    # if there is no normModifier, RooAddition of the bins is the norm
                    normName = 'norm'

                if bins.getSize() > 1:
                    binNames = ','.join(bins.at(ib).GetName() for ib in range(bins.getSize()))
                    fct('sum::{sample}_{norm}({binNames})'.format(sample = sampleName, norm = normName, binNames = binNames))
                else:
                    fct('expr::{sample}_{norm}("@0", {{{bin}}})'.format(sample = sampleName, norm = normName, bin = bins.at(0).GetName()))

                if len(normModifiers) > 0:
                    fct('prod::unc_{sample}_norm({mod})'.format(sample = sampleName, mod = ','.join(m.GetName() for m in normModifiers.values())))
                    fct('expr::{sample}_norm("@0*@1", {{{sample}_rawnorm, unc_{sample}_norm}})'.format(sample = sampleName))

            if regionDone:
                # All processes in the region are constructed. Add the observed RooDataHist.
                data_obs = ROOT.RooDataHist(dataObsName, dataObsName, ROOT.RooArgList(x), sourcePlots[region]['data_obs']['nominal'])
                wsimport(data_obs)

            else:
                done = False

    if hasattr(config, 'customize'):
        config.customize(workspace)

    if PRINTNUISANCE:
        for n in sorted(nuisances):
            print n, 'param 0 1'

    workspace.writeToFile(config.outname)

    print 'Workspace written to', config.outname

    signalRegion = ''
    ## DATACARDS
    if hasattr(config, 'carddir'):
        print 'Writing data cards'

        if not os.path.isdir(config.carddir):
            os.makedirs(config.carddir)

        # sort samples

        samples = {}
        procIds = {}

        for region, procPlots in sourcePlots.items():
            samples[region] = []

            # sort processes by expectation
            def compProc(p, q):
                if procPlots[p]['nominal'].GetSumOfWeights() > procPlots[q]['nominal'].GetSumOfWeights():
                    return -1
                else:
                    return 1

            procs = sorted(procPlots.keys(), compProc)

            for p in procs:
                if p in config.signals:
                    signalRegion = region
                else:
                    samples[region].append(p)
                    if p not in procIds:
                        procIds[p] = len(procIds) + 1

        # define datacard template

        hrule = '-' * 140

        lines = [
            'imax * number of bins',
            'jmax * number of processes minus 1',
            'kmax * number of nuisance parameters',
            hrule,
            'shapes * * ' + os.path.realpath(config.outname) + ' wspace:$PROCESS_$CHANNEL',
            hrule,
        ]

        line = 'bin          ' + ('%9s' % signalRegion) + ''.join(sorted(['%9s' % r for r in samples if r != signalRegion]))
        lines.append(line)

        line = 'observation  ' + ''.join('%9.1f' % o for o in [-1.] * len(samples))
        lines.append(line)

        lines.append(hrule)

        # columns for all background processes and yields
        columns = []

        for proc in samples[signalRegion]:
            columns.append((signalRegion, proc, str(procIds[proc])))

        for region in sorted(samples.keys()):
            if region == signalRegion:
                continue

            for proc in samples[region]:
                columns.append((region, proc, str(procIds[proc])))

        # now loop over signal models and write a card per model
        for signal in config.signals:
            cardcolumns = list(columns)
            cardlines = list(lines)

            # insert the signal expectation as the first column
            cardcolumns.insert(0, (signalRegion, signal, str(-1)))

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
                for s in config.signals:
                    if s != signal and nuisance.startswith(s):
                        break
                else:
                    # no other signal name matched -> nuisance either not related to signal or related to this signal model
                    cardlines.append(nuisance + ' param 0 1')

            with open(config.carddir + '/' + signal + '.dat', 'w') as datacard:
                for line in cardlines:
                    if '{signal}' in line:
                        line = line.format(signal = signal)

                    datacard.write(line + '\n')
            
            print ' ', signal

        print 'Cards saved to', config.carddir

    ## PLOTS
    if hasattr(config, 'plotsOutname'):
        print 'Visualizing workspace'

        def modRelUncert2(mod):
            # stat uncertainty of TFs have two parameters
            # allow for general case of N parameters
            relUncert2 = 0.
            iparam = 0
            p = mod.getParameter(iparam)
            while p:
                p.setVal(1.)
                d = mod.getVal() - 1.
                p.setVal(0.)

                relUncert2 += d * d

                iparam += 1
                p = mod.getParameter(iparam)

            return relUncert2

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

            hnominal = None
            huncert = None
            isTF = False

            hmods = {}
            normMods = {}

            unc = workspace.function('unc_' + pdf.GetName() + '_norm')
            if unc:
                # normalization given to this PDF has associated uncertainties

                # loop over all modifiers
                mods = unc.components()
                modItr = mods.iterator()
                while True:
                    mod = modItr.Next()
                    if not mod:
                        break

                    uncertName = mod.GetName().replace('mod_' + pdf.GetName() + '_norm_', '')
                    normMods[uncertName] = mod
                    hmods[uncertName] = ROOT.TH1D(pdf.GetName() + '_' + uncertName, '', len(binning) - 1, binning)

            for ibin in range(1, len(binning)):
                binName = pdf.GetName() + '_bin' + str(ibin)

                # if mu is a RooRealVar -> simplest case; static PDF
                # if mu = raw x unc and raw is a RooRealVar -> dynamic PDF, not linked
                # if mu = raw x unc and raw is a function -> linked from another sample

                if not workspace.var('mu_' + binName) and not workspace.var('raw_' + binName):
                    # raw is tf x another mu -> plot the TF

                    (samp, region, bin) = binName.split('_')
                    sample = (samp, region)
                    sbase = linkSource(sample)
                    sbaseName = '{0}_{1}'.format(*sbase)
                    tfName = samp + '_' + region + '_' + sbaseName 

                    if hnominal is None:
                        hnominal = ROOT.TH1D('tf_' + tfName, ';' + config.xtitle, len(binning) - 1, binning)
                        huncert = hnominal.Clone(hnominal.GetName() + '_uncertainties')
                        isTF = True

                    tf = workspace.var(tfName + '_' + bin + '_tf')
                    val = tf.getVal()

                    # TF is historically plotted inverted
                    hnominal.SetBinContent(ibin, 1. / val)
                    huncert.SetBinContent(ibin, 1. / val)

                else:
                    if hnominal is None:
                        hnominal = pdf.createHistogram(pdf.GetName(), x, ROOT.RooFit.Binning('default'))
                        for iX in range(1, hnominal.GetNbinsX() + 1):
                            hnominal.SetBinError(iX, 0.)

                        hnominal.SetName(pdf.GetName())
                        hnominal.GetXaxis().SetTitle(config.xtitle)
                        hnominal.GetYaxis().SetTitle('Events / GeV')
                        huncert = hnominal.Clone(pdf.GetName() + '_uncertainties')

                    val = hnominal.GetBinContent(ibin)

                totalUncert2 = 0.

                for uncertName, mod in normMods.items():
                    uncert2 = modRelUncert2(mod) * val
                    hmods[uncertName].SetBinContent(ibin, math.sqrt(uncert2))

                    totalUncert2 += uncert2

                unc = workspace.function('unc_' + binName)
                if unc:
                    # loop over all modifiers for this bin
                    mods = unc.components()
                    modItr = mods.iterator()
                    while True:
                        mod = modItr.Next()
                        if not mod:
                            break

                        uncert2 = modRelUncert2(mod) * val

                        if uncert2 > 1000.:
                            print modRelUncert2(mod), val, pdf.GetName(), mod.GetName()

                        if mod.GetName().endswith('_stat'):
                            if isTF: # nominal is 1/value
                                hnominal.SetBinError(ibin, math.sqrt(uncert2) / val / val)
                            else:
                                hnominal.SetBinError(ibin, math.sqrt(uncert2))
                        else:
                            uncertName = mod.GetName().replace('mod_' + binName + '_', '')
                            if uncertName not in hmods:
                                hmods[uncertName] = ROOT.TH1D(pdf.GetName() + '_' + uncertName, '', len(binning) - 1, binning)

                            hmods[uncertName].SetBinContent(ibin, math.sqrt(uncert2))

                        # total uncertainty includes stat
                        totalUncert2 += uncert2

                if isTF:
                    huncert.SetBinError(ibin, math.sqrt(totalUncert2) / val / val)
                else:
                    huncert.SetBinError(ibin, math.sqrt(totalUncert2))

            hasUncert = sum(huncert.GetBinError(iX) for iX in range(1, huncert.GetNbinsX() + 1)) != 0.

            plotsFile.cd()
            hnominal.SetDirectory(plotsFile)
            hnominal.Write()
            if hasUncert:
                huncert.SetDirectory(plotsFile)
                huncert.Write()
            for h in hmods.values():
                h.SetDirectory(plotsFile)
                h.Write()

        allData = workspace.allData()
        """
        dataItr = allData.iterator()
        while True:
            data = dataItr.Next()
            if not pdf:
                break
        """
        for data in allData:
            hnominal = None

            if signalRegion in data.GetName():
                continue

            hData = data.createHistogram(data.GetName(), x, ROOT.RooFit.Binning('default'))
            hData.SetDirectory(plotsFile)
            hData.Write()

        plotsFile.Close()

        print 'Histograms saved to', config.plotsOutname
