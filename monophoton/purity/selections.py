import os
import sys
import array
import collections
import time
import ROOT

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

if basedir not in sys.path:
    sys.path.append(basedir)

import config
import utils

### Configuration parameters ###

Version = 'GJetsTune'
# Version = 'MonojetSync'

# Skims for Purity Calculation
sphData = ['sph-16b-m', 'sph-16c-m', 'sph-16d-m', 'sph-16e-m', 'sph-16f-m', 'sph-16g-m', 'sph-16h-m']
gjetsMc = ['gj-100', 'gj-200','gj-400','gj-600']
qcdMc = ['qcd-200', 'qcd-300', 'qcd-500', 'qcd-700', 'qcd-1000', 'qcd-1000', 'qcd-1500', 'qcd-2000']
sphDataNero = ['sph-16b2-d', 'sph-16c2-d', 'sph-16d2-d']
gjetsMcNero = ['gj-40-d','gj-100-d','gj-200-d','gj-400-d','gj-600-d']

### Various load-time operations ###

versionDir =  config.histDir + '/purity/' + Version
if not os.path.isdir(versionDir):
    os.makedirs(versionDir)

ROOT.gSystem.Load(config.libobjs)
e = ROOT.panda.Event

ROOT.gROOT.ProcessLine("double cutvalue;")

ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')

### Statics ###

Tunes = ['Spring15', 'Spring16', 'GJetsCWIso', 'ZGCWIso']
Locations = ['barrel', 'endcap']
PhotonIds = ['none', 'loose', 'medium', 'tight', 'highpt']

Samples = {
    'sphData': sphData,
    'gjetsMc': gjetsMc,
    'qcdMc': qcdMc,
    'allMc': gjetsMc + qcdMc
}

Cuts = {
    'pixelVeto': 'photons.pixelVeto[0]',
    'mip': 'photons.mipEnergy[0] < 4.9',
    'time': 'std::abs(photons.time[0]) < 3.',
    'sieieNonzero': 'photons.sieie[0] > 0.001',
    'sipipNonzero': 'photons.sipip[0] > 0.001',
    'noisyRegion': '!(photons.eta_[0] > 0. && photons.eta_[0] < 0.15 && photons.phi_[0] > 0.527580 && photons.phi_[0] < 0.541795)'
}
Cuts['monophId'] = ' && '.join([
    Cuts['mip'],
    Cuts['time'],
    Cuts['sieieNonzero'],
    Cuts['sipipNonzero'],
    Cuts['noisyRegion']
])

photonPtBinning = [175,200,250,300,350,400,450,500]
PhotonPtSels = {
    'PhotonPtInclusive': 'photons.scRawPt[0] > %d' % photonPtBinning[0],
    'PhotonPt%dtoInf' % photonPtBinning[-1]: 'photons.scRawPt[0] > %d' % photonPtBinning[-1]
}
for low, high in zip(photonPtBinning, photonPtBinning[1:]):
    PhotonPtSels['PhotonPt%dto%d' % (low, high)] = '(photons.scRawPt[0] > %d && photons.scRawPt[0] < %d)' % (low, high)

metBinning = [0, 60, 120]
MetSels = {
    'MetInclusive': 't1Met.pt > %d' % metBinning[0],
    'Met%dtoInf' % metBinning[-1]: 't1Met.pt > %d' % metBinning[-1]
} 
for low, high in zip(metBinning, metBinning[1:]):
    MetSels['Met%dto%d' % (low, high)] = 't1Met.pt > %d && t1Met.pt < %d' % (low, high)

print 'bloop'

### Functions ###

# cut values for the ID tune
def getCuts(tune):
    variables = ['hovere', 'sieie', 'chiso', 'nhiso', 'phiso']

    cuts = dict((v, {}) for v in variables)

    tname = 'panda::XPhoton::k' + tune
    
    for iLoc, loc in enumerate(Locations):
        for cutdict in cuts.values():
            cutdict[loc] = {}

        for iId, pid in enumerate(PhotonIds[1:]):
            ROOT.gROOT.ProcessLine("cutvalue = panda::XPhoton::hOverECuts[%s][%d][%d];" % (tname, iLoc, iId))
            cuts['hovere'][loc][pid] = ROOT.cutvalue
            ROOT.gROOT.ProcessLine("cutvalue = panda::XPhoton::sieieCuts[%s][%d][%d];" % (tname, iLoc, iId))
            cuts['sieie'][loc][pid] = ROOT.cutvalue
            ROOT.gROOT.ProcessLine("cutvalue = panda::XPhoton::chIsoCuts[%s][%d][%d];" % (tname, iLoc, iId))
            cuts['chiso'][loc][pid] = ROOT.cutvalue
            ROOT.gROOT.ProcessLine("cutvalue = panda::XPhoton::nhIsoCuts[%s][%d][%d];" % (tname, iLoc, iId))
            cuts['nhiso'][loc][pid] = ROOT.cutvalue
            ROOT.gROOT.ProcessLine("cutvalue = panda::XPhoton::phIsoCuts[%s][%d][%d];" % (tname, iLoc, iId))
            cuts['phiso'][loc][pid] = ROOT.cutvalue

    return cuts

# selection expressions
def getSelections(tune, location, pid):
    itune = Tunes.index(tune)

    selections = {}
    cuts = getCuts(tune)

    selections['fiducial'] = 'photons.isEB' if location == 'barrel' else '!photons.isEB'
    selections['hovere'] = 'photons.hOverE[0] < %f' % cuts['hovere'][location][pid]
    selections['sieie'] = 'photons.sieie[0] < %f' % cuts['sieie'][location][pid]
    selections['chiso'] = 'photons.chIsoX[0][%d] < %f' % (itune, cuts['chiso'][location][pid])
    selections['chisomax'] = 'photons.chIsoMaxX[0][%d] < %f' % (itune, cuts['chiso'][location][pid])
    selections['nhiso'] = 'photons.nhIsoX[0][%d] < %f' % (itune, cuts['nhiso'][location][pid])
    selections['phiso'] = 'photons.phIsoX[0][%d] < %f' % (itune, cuts['phiso'][location][pid])

    return selections

# Variables and associated properties
Variable = collections.namedtuple('Variable', ['name', 'expression', 'cuts', 'title', 'binning'])

def getVariable(vname, tune, location):
    cuts = getCuts(tune)[vname]

    if vname == 'sieie':
        if location == 'barrel':
            binning = (44, 0.004, 0.015)
        else:
            binning = (48, 0.016, 0.040)

        return Variable(
            'sieie',
            'photons.sieie[0]',
            cuts[location],
            '#sigma_{i#etai#eta}',
            binning
        )
    elif vname == 'chiso':
        itune = Tunes.index(tune)
        if location == 'barrel':
            binning = [0., cuts["barrel"]["medium"]] + [x * 0.1 for x in range(20, 111, 5)]
        else:
            binning = [0., cuts["endcap"]["medium"]] + [x * 0.1 for x in range(20, 111, 5)]

        return Variable(
            'chiso',
            'TMath::Max(0., photons.chIsoX[0][%d])' % itune,
            cuts[location],
            'Ch Iso (GeV)',
            binning
        )
               

# Class for making templates
class HistExtractor(object):
    def __init__(self, name, snames, variable):
        self.name = name
        self.plotter = ROOT.MultiDraw()
        for sname in snames:
            self.plotter.addInputPath(utils.getSkimPath(sname, 'emjet'))

        self.variable = variable

        self.categories = [] # [(name, title, sel)]

    def extract(self, binning, outFile = None, mcsf = False):
        print 'Extracting ' + self.name + ' distributions'

        if type(binning) is tuple:
            template = ROOT.TH1D('template', '', *binning)
        else:
            template = ROOT.TH1D('template', '', len(binning) - 1, array.array('d', binning))

        template.Sumw2()

        if outFile is not None:
            outFile.cd()

        histograms = []
        for ic, (name, title, sel) in enumerate(self.categories):
            if mcsf and self.variable.name == 'sieie':
                name += '_raw'

            hist = template.Clone(name)
            hist.SetTitle(title)
            histograms.append(hist)

            print 'addPlot', self.variable.name, sel

            self.plotter.addPlot(hist, self.variable.expression, sel, True)

        self.plotter.fillPlots()

        if mcsf and self.variable.name == 'sieie':
            print 'Applying data/MC scale factor to the templates'

            source = ROOT.TFile(basedir + '/data/sieie_ratio.root')
            line = source.Get('fit')

            if outFile is not None:
                outFile.cd()

            corrected = []
            for hist in histograms:
                hcorr = hist.Clone(hist.GetName().replace('_raw', ''))
                corrected.append(hcorr)
                for iX in range(1, hist.GetNbinsX() + 1):
                    hcorr.SetBinContent(iX, hist.GetBinContent(iX) * line.Eval(hist.GetXaxis().GetBinCenter(iX)))

            source.Close()

            histograms.extend(corrected)

        if outFile is not None:
            outFile.cd()
            outFile.Write()

        return histograms


def StatUncert(nReal, nFake):
    # Calculate purity and print results
    print "Number of Real photons passing selection:", nReal
    print "Number of Fake photons passing selection:", nFake
    nTotal = nReal + nFake;
    purity = float(nReal) / float(nTotal)
    print "Purity of Photons is:", purity
    
    upper = ROOT.TEfficiency.ClopperPearson(int(nTotal),int(nReal),0.6827,True)
    lower = ROOT.TEfficiency.ClopperPearson(int(nTotal),int(nReal),0.6827,False)

    upSig = upper - purity;
    downSig = purity - lower;

    return float(upSig + downSig) / 2.0;

print 'blah'


