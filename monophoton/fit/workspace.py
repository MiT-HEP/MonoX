import sys
import re
import pprint
import collections
import ROOT

from HiggsAnalysis.CombinedLimit.ModelTools import SafeWorkspaceImporter

ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load('libRooFitCore.so')

outname = '/local/yiiyama/exec/ws.root'
sourcedir = '/data/t3home000/yiiyama/studies/monophoton/distributions'
hname = 'phoPtHighMet'
regions = ['monoph', 'monoel', 'monomu', 'diel','dimu']
sigregion = 'monoph'

links = [
    (('zg', 'diel'), ('zg', 'monoph')),
    (('zg', 'dimu'), ('zg', 'monoph')),
    (('wg', 'monoel'), ('wg', 'monoph')),
    (('wg', 'monomu'), ('wg', 'monoph')),
    (('wg', 'monoph'), ('zg', 'monoph'))
]

ignoredNuisances = {
    ('zg', 'diel'): ['gec', 'jec', 'leptonVetoSF', 'vgPDF', 'zgEWK'],
    ('zg', 'dimu'): ['gec', 'jec', 'leptonVetoSF', 'vgPDF', 'zgEWK'],
    ('wg', 'monoel'): ['gec', 'jec', 'leptonVetoSF', 'vgPDF', 'wgEWK'],
    ('wg', 'monomu'): ['gec', 'jec', 'leptonVetoSF', 'vgPDF', 'wgEWK']
}

scaleNuisances = ['lumi', 'photonSF', 'customIDSF', 'leptonVetoSF', 'egFakerate', 'haloNorm', 'spikeNorm', 'minorQCDScale']

workspace = ROOT.RooWorkspace('wspace')
wsimport = SafeWorkspaceImporter(workspace)

nuisances = []

def fct(*args):
    """
    Just a shorthand for workspace.factory
    """

    return workspace.factory(*args)

def modifier(nuis, target, up, down, form):
    """
    Construct a modifier function for a nuisance.
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
        if abs(a2) < 1.e-5:
            mod = fct('expr::{mod}("1.+{a1}*@0", {{{nuis}}})'.format(mod = modifierName, a1 = a1, nuis = nuis))
        else:
            mod = fct('expr::{mod}("1.+{a1}*@0+{a2}*@0*@0", {{{nuis}}})'.format(mod = modifierName, a1 = a1, a2 = a2, nuis = nuis))

    return mod

def statUncert(binName, baseBinName, binRelErr, baseRelErr):
    baseStat = '{base}_stat'.format(base = baseBinName)
    if not workspace.arg(baseStat):
        workspace.arg('{baseStat}[0.,-5.,5.]'.format(baseStat = baseStat))
        nuisances.append(baseStat)

    stat = '{bin}_stat'.format(bin = binName)
    workspace.arg('{stat}[0.,-5.,5.]'.format(stat = stat))
    nuisances.append(stat)

    bound2 = math.pow(binRelErr * 10., 2.)
    baseBound2 = math.pow(baseRelErr * 10., 2.)

    return fct('expr::{bin}_tf_stat("1.+TMath::Sqrt({bound2}*{stat}*{stat}+{baseBound2}*{baseStat}*{baseStat})")'.format(bin = binName, stat = stat, baseStat = baseStat, bound2 = bound2, baseBound2 = baseBound2))

def linkSource(target):
    """
    Find the source (sample, region) of the target (sample, region)
    """

    try:
        source = next(l[1] for l in links if l[0] == target)
    except StopIteration:
        return None

    if source[1] not in regions:
        raise RuntimeError('{0} linked from invalid sample {1}'.format(target, source))

    return source

def isLinkSource(source):
    """
    Check if (sample, region) is a source of a valid (sample, region)
    """

    targets = [l[0] for l in links if l[1] == source]
    for target in targets:
        if target[1] in regions:
            return True

    return False

# fetch all source histograms first    
sources = {}
sourcePlots = {}
for region in regions:
    source = ROOT.TFile.Open('{0}/{1}_{2}.root'.format(sourcedir, region, hname))
    sourcePlots[region] = collections.defaultdict(dict)
    for key in source.GetListOfKeys():
        matches = re.match(hname + '-([^_]+)(_.+(?:Up|Down)|)', key.GetName())
        if matches is None:
            continue
    
        sample = matches.group(1)
        if sample == 'data':
            sample = 'data_obs'

        variation = matches.group(2)
    
        obj = key.ReadObj()
        if not variation:
            sourcePlots[region][sample]['nominal'] = obj
        else:
            sourcePlots[region][sample][variation[1:]] = obj

    sources[region] = source

x = fct('x[-1.e+10,1.e+10]')

# will construct the workspace iteratively to resolve links
iteration = 0
done = False
while not done:

    done = True

    print 'Iteration {0}'.format(iteration)
    iteration += 1

    for region in regions:
        dataObsName = 'data_obs_' + region

        if workspace.data(dataObsName):
            # data_obs DataHist is added to the workspace only when all background & signal PDFs are constructed.
            # -> this region is fully constructed
            continue

        regionDone = True
        for sample, plots in sourcePlots[region].items():
            if sample == 'data_obs':
                continue

            if workspace.arg('{0}_{1}_norm'.format(sample, region)):
                # this (sample, region) is constructed already
                continue

            # now construct the ParametricHist + norm
            bins = ROOT.RooArgList()
            # collect nuisances that affect the overall normalization
            normModifiers = {}

            nominal = plots['nominal']
            sampleName = sample + '_' + region

            print 'Constructing pdf for', sampleName

            # there are three different types of samples
            # 1. link target: mu is TF x someone else's mu
            # 2. link source: mu is its own, but has no uncertainty assigned
            # 3. independent: mu is its own and has uncertainties

            sbase = linkSource((sample, region))
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

                numer = nominal
                denom = sourcePlots[sbase[1]][sbase[0]]['nominal']

                ratio = numer.Clone('ratio')
                ratio.Divide(denom)
                
                for ibin in range(1, nominal.GetNbinsX() + 1):
                    rbin = ratio.GetBinContent(ibin)

                    if rbin == 0.:
                        print 'WARNING: {region} {sample} bin{ibin} has tf = 0'.format(region = region, sample = sample, ibin = ibin)
                        bin = fct('mu_{bin}[0.]')
                        bins.add(bin)
                        continue

                    binName = '{0}_{1}_bin{2}'.format(sample, region, ibin)
                    baseBinName = 'mu_{0}_{1}_bin{2}'.format(*(sbase + (ibin,)))
                    
                    tfName = binName + '_tf'

                    # nominal tfactor (constant)
                    fct('{tf}[{val}]'.format(tf = tfName, val = rbin))

                    # list of yield modifiers (switch to using RooArgList if the chained string becomes too long)
                    modifiers = []

                    # statistical uncertainty on tfactor
                    binRelErr = nominal.GetBinError(ibin) / nominal.GetBinContent(ibin)
                    baseRelErr = denom.GetBinError(ibin) / denom.GetBinContent(ibin)
                    modifiers.append(statUncert(binName, baseBinName, binRelErr, baseRelErr))

                    # other systematic uncertainties on tfactor
                    # collect all variations on numerator and denominator
                    upVariations = set(v for v in plots.keys() if v.endswith('Up'))
                    upVariations |= set(v for v in sourcePlots[sbase[1]][sbase[0]].keys() if v.endswith('Up'))

                    for variation in upVariations:
                        var = variation[:-2]

                        if (sample, region) in ignoredNuisances and var in ignoredNuisances[(sample, region)]:
                            continue

                        if var in scaleNuisances and var in normModifiers:
                            # this uncertainty is non-shape and is taken care of already
                            continue

                        if var + 'Up' in plots:
                            numerUp = plots[var + 'Up'].GetBinContent(ibin)
                            numerDown = plots[var + 'Down'].GetBinContent(ibin)
                        else:
                            numerUp = numer.GetBinContent(ibin)
                            numerDown = numer.GetBinContent(ibin)

                        if var + 'Up' in sourcePlots[sbase[1]][sbase[0]]:
                            denomUp = sourcePlots[sbase[1]][sbase[0]][var + 'Up'].GetBinContent(ibin)
                            denomDown = sourcePlots[sbase[1]][sbase[0]][var + 'Down'].GetBinContent(ibin)
                        else:
                            denomUp = denom.GetBinContent(ibin)
                            denomDown = denom.GetBinContent(ibin)
                        
                        rup = numerUp / denomUp / rbin - 1.
                        rdown = numerDown / denomDown / rbin - 1.
                        if abs(rup) < 1.e-3 and abs(rdown) < 1.e-3:
                            # fully correlated uncertainty - cancels out
                            continue

                        if var in scaleNuisances:
                            normModifiers[var] = modifier(var, '{sample}_norm'.format(sample = sampleName), rup, rdown, 'lnN')
                        else:
                            modifiers.append(modifier(var, tfName, rup, rdown, 'lnN'))
                    
                    if len(modifiers) > 0:
                        # "raw" yield (= base x tfactor)
                        fct('expr::raw_{bin}("@0*@1", {{{tf}, {baseBin}}})'.format(bin = binName, tf = tfName, baseBin = baseBinName))
                        fct('prod::unc_{bin}({mod})'.format(bin = binName, mod = ','.join(m.GetName() for m in modifiers)))
                    
                        # mu = raw x unc
                        bin = fct('prod::mu_{bin}(raw_{bin},unc_{bin})'.format(bin = binName))
                    else:
                        bin = fct('expr::mu_{bin}("@0*@1", {{{tf}, {baseBin}}})'.format(bin = binName, tf = tfName, baseBin = baseBinName))

                    bins.add(bin)

                ratio.Delete()

            elif isLinkSource((sample, region)):
                print 'this sample is a base of some other sample'
                # each bin must be described by a free-floating RooRealVar
                # uncertainties are all casted on tfactors

                for ibin in range(1, nominal.GetNbinsX() + 1):
                    binName = '{0}_{1}_bin{2}'.format(sample, region, ibin)

                    bin = fct('mu_{bin}[{val},0.,{max}]'.format(bin = binName, val = nominal.GetBinContent(ibin), max = nominal.GetMaximum() * 10.))
                    bins.add(bin)

            else:
                print 'this sample does not participate in constraints'

                for ibin in range(1, nominal.GetNbinsX() + 1):
                    binName = '{0}_{1}_bin{2}'.format(sample, region, ibin)

                    cval = nominal.GetBinContent(ibin)
                    if cval == 0.:
                        # bin content is 0
                        bin = fct('mu_{bin}[0.]'.format(bin = binName))
                    else:
   
                        modifiers = []
    
                        # statistical uncertainty
                        #relerr = nominal.GetBinError(ibin) / cval
                        #modifiers.append(modifier('{bin}_stat'.format(bin = binName), '', relerr, -relerr, 'quad'))
    
                        for variation in plots:
                            if not variation.endswith('Up'):
                                continue
    
                            var = variation[:-2]

                            if (sample, region) in ignoredNuisances and var in ignoredNuisances[(sample, region)]:
                                continue

                            if var in scaleNuisances and var in normModifiers:
                                continue
    
                            dup = plots[var + 'Up'].GetBinContent(ibin) / cval - 1.
                            ddown = plots[var + 'Down'].GetBinContent(ibin) / cval - 1.
    
                            if var in scaleNuisances:
                                normModifiers[var] = modifier(var, '{sample}_norm'.format(sample = sampleName), dup, ddown, 'lnN')
                            else:
                                modifiers.append(modifier(var, binName, dup, ddown, 'lnN'))
                        
                        if len(modifiers) > 0:
                            raw = fct('raw_{bin}[{val}]'.format(bin = binName, val = cval))
                            fct('prod::unc_{bin}({mod})'.format(bin = binName, mod = ','.join(m.GetName() for m in modifiers)))
        
                            # mu = raw x unc
                            bin = fct('prod::mu_{bin}(raw_{bin},unc_{bin})'.format(bin = binName))
                        else:
                            bin = fct('mu_{bin}[{val}]'.format(bin = binName, val = cval))

                    bins.add(bin)

                # switch between the three types of samples

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
            # All samples in the region are constructed. Add the observed RooDataHist.
            data_obs = ROOT.RooDataHist(dataObsName, dataObsName, ROOT.RooArgList(x), sourcePlots[region]['data_obs']['nominal'])
            wsimport(data_obs)

        else:
            done = False

workspace.writeToFile(outname)

# print out nuisance lines for the datacard
for n in sorted(nuisances):
    print n, 'param 0 1'
