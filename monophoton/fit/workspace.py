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

links = {
    ('zg', 'diel'): ('zg', 'monoph'),
    ('zg', 'dimu'): ('zg', 'monoph'),
    ('wg', 'monoel'): ('wg', 'monoph'),
    ('wg', 'monomu'): ('wg', 'monoph')
}

ignoredNuisances = {
    ('zg', 'diel'): ['gec', 'jec', 'leptonVetoSF', 'vgPDF', 'zgEWK'],
    ('zg', 'dimu'): ['gec', 'jec', 'leptonVetoSF', 'vgPDF', 'zgEWK'],
    ('wg', 'monoel'): ['gec', 'jec', 'leptonVetoSF', 'vgPDF', 'wgEWK'],
    ('wg', 'monomu'): ['gec', 'jec', 'leptonVetoSF', 'vgPDF', 'wgEWK']
}

workspace = ROOT.RooWorkspace('wspace')
wsimport = SafeWorkspaceImporter(workspace)

nuisances = []

def fct(*args):
    global workspace
    return workspace.factory(*args)

def modifier(nuis, target, up, down, form):
    a1 = (up - down) * 0.5
    a2 = (up + down) * 0.5

    if not workspace.arg(nuis):
        fct('{nuis}[0,-5,5]'.format(nuis = nuis))
        nuisances.append(nuis)

    if target:
        target += '_'

    modifierName = 'mod_{target}{nuis}'.format(target = target, nuis = nuis)

    if form == 'lnN':
        fct('expr::{mod}("TMath::Exp({a1}*@0)", {{{nuis}}})'.format(mod = modifierName, a1 = a1, nuis = nuis))
    elif form == 'quad':
        if abs(a2) < 1.e-5:
            fct('expr::{mod}("1.+{a1}*@0", {{{nuis}}})'.format(mod = modifierName, a1 = a1, nuis = nuis))
        else:
            fct('expr::{mod}("1.+{a1}*@0+{a2}*@0*@0", {{{nuis}}})'.format(mod = modifierName, a1 = a1, a2 = a2, nuis = nuis))

    return modifierName

x = fct('x[-1.e+10,1.e+10]')

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

iteration = 0
done = False
while not done:

    done = True

    print 'Iteration {0}'.format(iteration)

    for region in regions:
        dataObsName = 'data_obs_' + region

        if workspace.data(dataObsName):
            # this region is fully constructed
            continue

        regionDone = True
        for sample, plots in sourcePlots[region].items():
            if sample == 'data_obs':
                continue

            try:
                linkKey = (sample, region)
                while linkKey in links:
                    linkKey = links[linkKey]
                    if workspace.arg('{0}_{1}_norm'.format(*linkKey)):
                        continue

                    # source of this bin is not constructed yet
                    regionDone = False
                    raise ReferenceError()

            except ReferenceError:
                # try again later
                continue

            # now construct the ParametricHist + norm
            bins = ROOT.RooArgList()

            nominal = plots['nominal']
            sampleName = sample + '_' + region

            print 'Constructing pdf for', sampleName

            if (sample, region) in links:
                print 'this sample in this region is a function of the yield in another (sample, region)'

                sbase = links[(sample, region)]
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

                    # "raw" yield (= base x tfactor)
                    fct('expr::raw_{bin}("@0*@1", {{{tf}, {baseBin}}})'.format(bin = binName, tf = tfName, baseBin = baseBinName))

                    # list of yield modifiers (switch to using RooArgList if the chained string becomes too long)
                    modifiers = '{'

                    # statistical uncertainty on tfactor
                    relerr = ratio.GetBinError(ibin) / rbin
                    modifiers += modifier('{tf}_stat'.format(tf = tfName), '', relerr, -relerr, 'quad')

                    # other systematic uncertainties on tfactor
                    # collect all variations on numerator and denominator
                    upVariations = set(v for v in plots.keys() if v.endswith('Up'))
                    upVariations |= set(v for v in sourcePlots[sbase[1]][sbase[0]].keys() if v.endswith('Up'))
                    
                    for variation in upVariations:
                        var = variation[:-2]

                        if var in ignoredNuisances[(sample, region)]:
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

                        modifiers += ',' + modifier(var, tfName, rup, rdown, 'lnN')
                    
                    modifiers += '}'
                    fct('prod::unc_{bin}({mod})'.format(bin = binName, mod = modifiers))
                    
                    # mu = raw x unc
                    bin = fct('prod::mu_{bin}(raw_{bin},unc_{bin})'.format(bin = binName))
                    bins.add(bin)

                ratio.Delete()

            elif (sample, region) in links.values():
                print 'this sample is the base of some other sample'
                # each bin must be described by a RooRealVar
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
                        bin = fct('mu_{bin}[0.]'.format(bin = binName))
                    else:
                        raw = fct('raw_{bin}[{val}]'.format(bin = binName, val = cval))
    
                        modifiers = '{'
    
                        # statistical uncertainty
                        #relerr = nominal.GetBinError(ibin) / cval
                        #modifiers += modifier('{bin}_stat'.format(bin = binName), '', relerr, -relerr, 'quad')
    
                        for variation in plots:
                            if not variation.endswith('Up'):
                                continue
    
                            var = variation[:-2]
    
                            dup = plots[var + 'Up'].GetBinContent(ibin) / cval - 1.
                            ddown = plots[var + 'Down'].GetBinContent(ibin) / cval - 1.
    
                            modifiers += ',' + modifier(var, binName, dup, ddown, 'lnN')
                        
                        modifiers += '}'
                        fct('prod::unc_{bin}({mod})'.format(bin = binName, mod = modifiers))
    
                        # mu = raw x unc
                        bin = fct('prod::mu_{bin}(raw_{bin},unc_{bin})'.format(bin = binName))

                    bins.add(bin)

            # compile the bins into a parametric hist pdf and a norm
            shape = ROOT.RooParametricHist(sampleName, sampleName, x, bins, nominal)
            wsimport(shape)
            if bins.getSize() > 1:
                binNames = ','.join(bins.at(ib).GetName() for ib in range(bins.getSize()))
                fct('sum::{sample}_norm({binNames})'.format(sample = sampleName, binNames = binNames))
            else:
                fct('expr::{sample}_norm("@0", {{{bin}}})'.format(sample = sampleName, bin = bins.at(0).GetName()))

        if regionDone:
            data_obs = ROOT.RooDataHist(dataObsName, dataObsName, ROOT.RooArgList(x), sourcePlots[region]['data_obs']['nominal'])
            wsimport(data_obs)

        else:
            done = False

workspace.writeToFile(outname)

for n in sorted(nuisances):
    print n, 'param 0 1'
