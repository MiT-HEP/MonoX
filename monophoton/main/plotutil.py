import sys
import array
import copy
import re

argv = list(sys.argv)
sys.argv = []
import ROOT
black = ROOT.kBlack # need to load something from ROOT to actually import
sys.argv = argv

class GroupSpec(object):
    def __init__(self, name, title, samples = [], region = '', count = 0., color = ROOT.kBlack, scale = 1.):
        self.name = name
        self.title = title
        self.samples = samples
        self.region = region
        self.count = count
        self.color = color
        self.scale = scale # use for ad-hoc scaling of histograms
        self.variations = []


class VariableDef(object):
    def __init__(self, name, title, expr, binning, unit = '', cut = '', applyBaseline = True, applyFullSel = False, blind = None, overflow = False, logy = None, ymax = -1.):
        self.name = name
        self.title = title
        self.unit = unit
        self.expr = expr
        self.cut = cut
        self.applyBaseline = applyBaseline
        self.applyFullSel = applyFullSel
        self.binning = binning
        self.blind = blind
        self.overflow = overflow
        self.logy = logy
        self.ymax = ymax

    def clone(self, name, **keywords):
        for vname in ['title', 'unit', 'expr', 'cut', 'applyBaseline', 'applyFullSel', 'binning', 'blind', 'overflow', 'logy', 'ymax']:
            if vname not in keywords:
                keywords[vname] = copy.copy(getattr(self, vname))

        vardef = VariableDef(name, **keywords)

        return vardef

    def ndim(self):
        if type(self.expr) is tuple:
            return len(self.expr)
        else:
            return 1

    def xlimits(self):
        if self.ndim() == 1:
            binning = self.binning
        else:
            binning = self.binning[0]

        if type(binning) is list:
            return binning[0], binning[-1]
        elif type(binning) is tuple:
            return binning[1], binning[2]
    
    def fullyBlinded(self):
        if not self.blind:
            return False

        if self.blind == 'full':
            return True

        xlow, xhigh = self.xlimits()
        return self.blind[0] <= xlow and self.blind[1] >= xhigh

    def histName(self, hname):
        return self.name + '-' + hname

    def makeHist(self, hname, outDir = None):
        """
        Make an empty histogram from the specifications.
        """

        gd = ROOT.gDirectory    
        if outDir:
            outDir.cd()
        else:
            ROOT.gROOT.cd()

        ndim = self.ndim()

        if ndim == 1:
            if type(self.binning) is list:
                nbins = len(self.binning) - 1
                arr = array.array('d', self.binning)
    
            elif type(self.binning) is tuple:
                nbins = self.binning[0]
                arr = array.array('d', [self.binning[1] + (self.binning[2] - self.binning[1]) / nbins * i for i in range(nbins + 1)])
    
            if self.overflow:
                lastbinWidth = (arr[-1] - arr[0]) / 30.
                arr += array.array('d', [self.binning[-1] + lastbinWidth])
    
            hist = ROOT.TH1D(self.histName(hname), '', nbins, arr)
    
        else:
            args = []
    
            for binning in self.binning:
                if type(binning) is list:
                    nbins = len(binning) - 1
                    arr = array.array('d', binning)
    
                elif type(binning) is tuple:
                    nbins = binning[0]
                    arr = array.array('d', [binning[1] + (binning[2] - binning[1]) / nbins * i for i in range(nbins + 1)])
                    
                args += [nbins, arr]
    
            if self.ndim() == 2:
                pprint(args)
                print " "
                hist = ROOT.TH2D(self.histName(hname), '', *tuple(args))
                pprint(hist)
            elif self.ndim() == 3:
                # who would do this??
                hist = ROOT.TH3D(self.histName(hname), '', *tuple(args))
            else:
                # I appreciate this error message
                raise RuntimeError('What are you thinking')
            
        gd.cd()

        hist.Sumw2()
        return hist

    def formSelection(self, plotConfig, prescale = 1, replacements = []):
        cuts = []
        if self.applyBaseline:
            cuts.append(plotConfig.baseline)
    
        if self.cut:
            cuts.append(self.cut)
    
        if self.applyFullSel:
            cuts.append(plotConfig.fullSelection)
    
        if prescale > 1 and self.blind is None:
            cuts.append('event % {prescale} == 0'.format(prescale = prescale))

        selection = ' && '.join(['(%s)' % c for c in cuts if c != ''])

        for repl in replacements:
            # replace the variable names given in repl = ('original', 'new')
            # enclose the original variable name with characters that would not be a part of the variable
            selection = re.sub(r'([^_a-zA-Z]?)' + repl[0] + r'([^_0-9a-zA-Z]?)', r'\1' + repl[1] + r'\2', selection)
    
        return selection

    def formExpression(self, replacements = []):
        if type(self.expr) is tuple:
            expr = ':'.join(self.expr)
        else:
            expr = self.expr

        for repl in replacements:
            # replace the variable names given in repl = ('original', 'new')
            # enclose the original variable name with characters that would not be a part of the variable
            expr = re.sub(r'([^_a-zA-Z]?)' + repl[0] + r'([^_0-9a-zA-Z]?)', r'\1' + repl[1] + r'\2', expr)

        return expr

class PlotConfig(object):
    def __init__(self, name, obsSamples):
        self.name = name # name serves as the default region selection (e.g. monoph)
        self.baseline = '1'
        self.fullSelection = ''
        self.obs = GroupSpec('data_obs', 'Observed', samples = obsSamples)
        self.sigGroups = []
        self.bkgGroups = []
        self.variables = []
        self.sensitiveVars = []
        self.treeMaker = ''

    def getVariable(self, name):
        return next(variable for variable in self.variables if variable.name == name)

    def countConfig(self):
        return VariableDef('count', '', '0.5', (1, 0., 1.), cut = self.fullSelection)

    def findGroup(self, name):
        return next(g for g in self.sigGroups + self.bkgGroups if g.name == name)

    def samples(self):
        snames = set(self.obs.samples)

        for group in self.bkgGroups:
            for s in group.samples:
                if type(s) is tuple:
                    snames.add(s[0])
                else:
                    snames.add(s)

        for group in self.sigGroups:
            snames.add(group.name)

        return list(snames)


class Variation(object):
    """
    Specifies alternative samples and cuts for systematic variation.
    Must specify either region or replacements or both as a two-component tuple corresponding to up and down variations.
    Alternatively reweight can be specified as a string or a value. See comments below.
    """

    def __init__(self, name, region = None, replacements = None, reweight = None):
        self.name = name
        self.region = region
        self.replacements = replacements
        # reweight:
        #  single float -> scale uniformly. Output suffix _{name}Var
        #  string -> use branches 'reweight_%sUp' & 'reweight_%sDown'. Output suffix _{name}Up & _{name}Down
        self.reweight = reweight

