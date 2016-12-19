"""
Workspace constructor for simultaneous fit using combine

[Terminology]
 - region: Signal and control regions. Consists of an observation 1D histogram, (multiple) background histogram(s) that stack up to match the observation, and (multiple) signal histogram(s).
 - process: Background samples. If a background process appears in multiple regions, they must have a common name.
 - sample: (process, region)

[Interface]
Input: ROOT files with histograms (no directory structure).
Output: A ROOT file containing a RooWorkspace and printouts to stdout which should be pasted into a combine data card.

[Instructions]
Specify the input file name format and the histogram naming schema as filename and histname parameters. Wildcards {region}, {process}, and {distribution} should be used in the
naming patterns. The wildcards will be replaced by the list of regions and processes and the name of the distribution, also specified in the parameters section. Histograms for
systematic variations must be named with a suffix _(nuisance name)(Up|Down) (e.g. z_signal_pdfUp for process z in the region signal with upward variation of pdf uncertainty).
Once inputs are defined, specify the links between samples and special treatments for various nuisances. Nuisance parameters are identified automatically from the histogram names
following the convention given above.
Usage is
 $ [set environment for CMSSW with combine installation]
 $ python workspace.py
At the moment, the tool does not write a data card. The user has to provide a card, to which the lines printed out by the tool should be appended. The second section of the card
should be of form
-----
shapes * * ws.root wspace:$PROCESS_$CHANNEL
-----
All nuisances where histograms are defined will be included in the workspace, regardless of whether they are "shape" or "scale" type nuisances. Those that are printed out by the
tool should therefore not be mentioned anywhere else in the data card.
Another feature that is lacking at the moment is the visualization of the workspace content. The only way to check how the links were implemented in the workspace is to do
wspace->Print()
in ROOT.
"""

import os
import sys
import re
import math
import pprint
import collections
import ROOT

from HiggsAnalysis.CombinedLimit.ModelTools import SafeWorkspaceImporter

sys.path.append(os.getcwd())
parapy = sys.argv[1]
config = __import__(parapy)

ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load('libRooFitCore.so')

# nuisances below this order are ignored
SMALLNUMBER = 1.e-3
# ignore statistical uncertainties from bins with content less than the cutoff (relative to the total content of the sample)
STATCUTOFF = 0.1

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

# fetch all source histograms first    
sources = {}
sourcePlots = {}
totals = {}

hstore = ROOT.gROOT.mkdir('hstore')

for region in config.regions:
    sourcePlots[region] = {}
    for process in config.processes:
        # rename 'data' to 'data_obs' (historical)
        if process == 'data':
            pname = 'data'
            process = 'data_obs'
        else:
            pname = process

        sourcePlots[region][process] = {}

        fname = config.sourcedir + '/' + config.filename.format(process = process, region = region, distribution = config.distribution)
        try:
            source = sources[fname]
        except KeyError:
            source = ROOT.TFile.Open(fname)
            sources[fname] = source
   
        # find all histograms matching the specified histogram name pattern + (_variation)
        for key in source.GetListOfKeys():
            matches = re.match(config.histname.format(process = pname, region = region, distribution = config.distribution) + '(_.+(?:Up|Down)|)', key.GetName())
            if matches is None:
                continue
        
            variation = matches.group(1)
        
            obj = key.ReadObj()
            obj.SetDirectory(hstore)

            if config.binWidthNormalized:
                for iX in range(1, obj.GetNbinsX() + 1):
                    cont = obj.GetBinContent(iX) * obj.GetXaxis().GetBinWidth(iX)
                    if process == 'data_obs':
                        cont = round(cont)

                    obj.SetBinContent(iX, cont) 

            if not variation:
                # name does not have _*Up or _*Down suffix -> is a nominal histogram
                sourcePlots[region][process]['nominal'] = obj
    
                if process != 'data_obs':
                    # background process
                    if region not in totals:
                        totals[region] = obj.Clone('total_' + region)
                    else:
                        totals[region].Add(obj)
            else:
                sourcePlots[region][process][variation[1:]] = obj

# Workspace construction start

x = fct('x[-1.e+10,1.e+10]')

# will construct the workspace iteratively to resolve links
iteration = 0
done = False
while not done:

    done = True

    print 'Iteration {0}'.format(iteration)
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

            if len(plots) == 0:
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

            print 'Constructing pdf for', sampleName

            # there are three different types of samples
            # 1. link target: mu is TF x someone else's mu
            # 2. link source: mu is its own, but has no uncertainty assigned
            # 3. independent: mu is its own and has uncertainties

            sbase = linkSource(sample)
            if sbase is not None:
                print 'this sample is a function of the yields in', sbase

                try:
                    # check for source recursively
                    source = sbase
                    while source is not None:
                        if not workspace.arg('{0}_{1}_norm'.format(*source)):
                            # source of this sample is not constructed yet
                            raise ReferenceError()

                        source = linkSource(source)

                except ReferenceError:
                    print 'but source', source, 'is not constructed yet.'
                    # try again in a later iteration
                    regionDone = False
                    continue

                sbaseName = '{0}_{1}'.format(*sbase)

                numer = nominal
                basePlots = sourcePlots[sbase[1]][sbase[0]]
                denom = basePlots['nominal']

                ratio = numer.Clone('ratio')
                ratio.Divide(denom)
                
                for ibin in range(1, nominal.GetNbinsX() + 1):
                    rbin = ratio.GetBinContent(ibin)

                    if rbin == 0.:
                        print 'WARNING: {region} {process} bin{ibin} has tf = 0'.format(region = region, process = process, ibin = ibin)
                        bin = fct('mu_{bin}[0.]')
                        bins.add(bin)
                        continue

                    binName = sampleName + '_bin{0}'.format(ibin)
                    baseBinName = sbaseName + '_bin{0}'.format(ibin)
                    
                    tfName = binName + '_tf'

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

                        if (sample, sbase, var) in config.partialCorrelation:
                            # need to split the nuisance into correlated and anti-correlated
                            # assuming no scaleNuisance is partially correlated
                            correlation = config.partialCorrelation[(sample, sbase, var)]
                            raup = numerUp / denomDown / rbin - 1.
                            radown = numerDown / denomUp / rbin - 1.

                            if abs(rup) > SMALLNUMBER or abs(rdown) > SMALLNUMBER:
                                coeff = (1. + correlation) * 0.5
                                modifiers.append(nuisance(var + '_corr', tfName, coeff * rup, coeff * rdown, 'lnN'))

                            if abs(raup) > SMALLNUMBER or abs(radown) > SMALLNUMBER:
                                coeff = (1. - correlation) * 0.5
                                modifiers.append(nuisance(var + '_acorr', tfName, coeff * raup, coeff * radown, 'lnN'))

                        else:
                            if abs(rup) < SMALLNUMBER and abs(rdown) < SMALLNUMBER:
                                # fully correlated uncertainty that affects the numerator and denominator identically
                                continue
    
                            if var in config.scaleNuisances:
                                normModifiers[var] = nuisance(var, '{sample}_norm'.format(sample = sampleName), rup, rdown, 'lnN')
                            else:
                                if var in config.decorrelatedNuisances:
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
                print 'this sample is a base of some other sample'
                # each bin must be described by a free-floating RooRealVar
                # uncertainties are all casted on tfactors

                for ibin in range(1, nominal.GetNbinsX() + 1):
                    bin = fct('mu_{sample}_bin{bin}[{val},0.,{max}]'.format(sample = sampleName, bin = ibin, val = nominal.GetBinContent(ibin), max = nominal.GetMaximum() * 10.))
                    bins.add(bin)

            else:
                print 'this sample does not participate in constraints'

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
                                if var in config.decorrelatedNuisances:
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

workspace.writeToFile(config.outname)

# print out nuisance lines for the datacard
for n in sorted(nuisances):
    print n, 'param 0 1'
