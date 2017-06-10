import os
import sys
import array
import ROOT
import time

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

if basedir not in sys.path:
    sys.path.append(basedir)

import config

### Getting cut values from simple tree ###

ROOT.gSystem.Load(config.libobjs)
e = ROOT.panda.Event

print 'bloop'

Eras = ['Spring15', 'Spring16', 'Ashim_ZG_CWIso']
Locations = [ 'barrel', 'endcap' ]
PhotonIds = [ 'none', 'loose', 'medium', 'tight', 'highpt' ]

AshimCuts = {'hOverE': 0.0263, 'sieie': 0.01002, 'chIso': 1.163, 'nhIso': 7.005, 'phIso': 3.271}

hOverECuts = {}
sieieCuts = {}
chIsoCuts = {}
nhIsoCuts = {}
phIsoCuts = {}

ROOT.gROOT.ProcessLine("double cut;")
for iEra, era in enumerate(Eras):
    hOverECuts[era] = {}
    sieieCuts[era] = {}
    chIsoCuts[era] = {}
    nhIsoCuts[era] = {}
    phIsoCuts[era] = {}

    for iLoc, loc in enumerate(Locations):
        hOverECuts[era][loc] = {}
        sieieCuts[era][loc] = {}
        chIsoCuts[era][loc] = {}
        nhIsoCuts[era][loc] = {}
        phIsoCuts[era][loc] = {}

        for cuts in [sieieCuts]:
            cuts[era][loc]['none'] = 1.

        if era == 'Ashim_ZG_CWIso':
            for pid in PhotonIds[1:]:
                hOverECuts[era][loc][pid] = AshimCuts['hOverE']
                sieieCuts[era][loc][pid] = AshimCuts['sieie']
                chIsoCuts[era][loc][pid] = AshimCuts['chIso']
                nhIsoCuts[era][loc][pid] = AshimCuts['nhIso']
                phIsoCuts[era][loc][pid] = AshimCuts['phIso']

        else:
            for iId, pid in enumerate(PhotonIds[1:]):
                ROOT.gROOT.ProcessLine("cut = panda::XPhoton::hOverECuts["+str(iEra)+"]["+str(iLoc)+"]["+str(iId)+"];")
                hOverECuts[era][loc][pid] = ROOT.cut
                ROOT.gROOT.ProcessLine("cut = panda::XPhoton::sieieCuts["+str(iEra)+"]["+str(iLoc)+"]["+str(iId)+"];")
                sieieCuts[era][loc][pid] = ROOT.cut
                ROOT.gROOT.ProcessLine("cut = panda::XPhoton::chIsoCuts["+str(iEra)+"]["+str(iLoc)+"]["+str(iId)+"];")
                chIsoCuts[era][loc][pid] = ROOT.cut
                ROOT.gROOT.ProcessLine("cut = panda::XPhoton::nhIsoCuts["+str(iEra)+"]["+str(iLoc)+"]["+str(iId)+"];")
                nhIsoCuts[era][loc][pid] = ROOT.cut
                ROOT.gROOT.ProcessLine("cut = panda::XPhoton::phIsoCuts["+str(iEra)+"]["+str(iLoc)+"]["+str(iId)+"];")
                phIsoCuts[era][loc][pid] = ROOT.cut

# plotter for template extraction
ROOT.gROOT.LoadMacro(basedir + '/../common/MultiDraw.cc+')

### Now start actual parameters that need to be changed ###

Version = 'Ashim'
# Version = 'MonojetSync'
versionDir =  '/scratch5/' + os.environ['USER'] + '/studies/purity/' + Version
if not os.path.isdir(versionDir):
    os.makedirs(versionDir)

from ROOT import *

ChIsoSbBins = range(20,111,5)

# Variables and associated properties
# {name: (expression, cuts, title, (EB binning, EE binning))}
Variables = {
    "sieie": ('photons.sieie[0]', sieieCuts, '#sigma_{i#etai#eta}', ((44, 0.004, 0.015), (48, 0.016, 0.040))),
    "chiso": ('TMath::Max(0., photons.chIso[0])', chIsoCuts, 'Ch Iso (GeV)', ([0., chIsoCuts["Spring15"]["barrel"]["medium"]] + [x * 0.1 for x in ChIsoSbBins], [0., chIsoCuts["Spring15"]["endcap"]["medium"]] + [x * 0.1 for x in ChIsoSbBins]))
}
               
# Skims for Purity Calculation
sphData = ['sph-16b-m', 'sph-16c-m', 'sph-16d-m', 'sph-16e-m', 'sph-16f-m', 'sph-16g-m', 'sph-16h-m']
#gjetsMc = ['gj04-100','gj04-200','gj04-400','gj04-600']
gjetsMc = ['gj-100', 'gj-200','gj-400','gj-600']
qcdMc = [ 'qcd-200', 'qcd-300', 'qcd-500', 'qcd-700', 'qcd-1000', 'qcd-1000', 'qcd-1500', 'qcd-2000']
sphDataNero = ['sph-16b2-d', 'sph-16c2-d', 'sph-16d2-d']
gjetsMcNero = ['gj-40-d','gj-100-d','gj-200-d','gj-400-d','gj-600-d']

Samples = {
    'sphData': sphData,
    'gjetsMc': gjetsMc,
    'qcdMc': qcdMc,
    'allMc': gjetsMc + qcdMc
}

Measurement = { "bambu" : [ ('FitSinglePhoton','sphData','Fit Template from SinglePhoton Data')
                            ,('TempSignalGJets','gjetsMc',r'Signal Template from #gamma+jets MC')
                            ,('TempSidebandGJets','gjetsMc',r'Sideband Template from #gamma+jets MC')
                            ,('TempBkgdSinglePhoton','sphData','Background Template from SinglePhoton Data')
                            ,('TempSidebandGJetsNear','gjetsMc',r'Near Sideband Template from #gamma+jets MC')
                            ,('TempBkgdSinglePhotonNear','sphData','Near Background Template from SinglePhoton Data')
                            ,('TempSidebandGJetsFar','gjetsMc',r'Far Sideband Template from #gamma+jets MC')
                            ,('TempBkgdSinglePhotonFar','sphData','Far Background Template from SinglePhoton Data')
                            ],
                "bambumc" : [ ('FitSinglePhoton','allMc','Fit Template from SinglePhoton Data')
                                 ,('TempSignalGJets','gjetsMc',r'Signal Template from #gamma+jets MC')
                                 ,('TempSidebandGJets','gjetsMc',r'Sideband Template from #gamma+jets MC')
                                 ,('TempBkgdSinglePhoton','allMc','Background Template from SinglePhoton Data')
                                 ,('TempSidebandGJetsScaled','gjetsMc',r'Scaled Sideband Template from #gamma+jets MC')
                                 ,('TempBkgdSinglePhoton','allMc','Background Template from SinglePhoton Data')
                                 ],
                }

# Selections for Purity Calculation
locationSels = {}
locationSels["barrel"] = '(TMath::Abs(photons.eta_[0]) < 1.5)'
locationSels["endcap"] = '((TMath::Abs(photons.eta_[0]) > 1.5) && (TMath::Abs(photons.eta_[0]) < 2.4))'

hOverESels = {} 
sieieSels = {} 
chIsoSels = {}
chWorstIsoSels = {}
chIsoMaxSels = {}
nhIsoSels = {}
phIsoSels = {}
SigmaIetaIetaSels = {}
PhotonIsolationSels = {}

for era in Eras:
    hOverESels[era] = {}
    sieieSels[era] = {}
    chIsoSels[era] = {}
    chWorstIsoSels[era] = {}
    chIsoMaxSels[era] = {}
    nhIsoSels[era] = {}
    phIsoSels[era] = {}
    SigmaIetaIetaSels[era] = {}
    PhotonIsolationSels[era] = {}

    for loc in Locations:
        hOverESels[era][loc] = {}
        sieieSels[era][loc] = {}
        chIsoSels[era][loc] = {}
        chWorstIsoSels[era][loc] = {}
        chIsoMaxSels[era][loc] = {}
        nhIsoSels[era][loc] = {}
        phIsoSels[era][loc] = {}
        SigmaIetaIetaSels[era][loc] = {}
        PhotonIsolationSels[era][loc] = {}

        for sel in [sieieSels, chIsoSels, chWorstIsoSels, nhIsoSels, phIsoSels]:
            sel[era][loc]['none'] = '(1)'

        hOverESels[era][loc]['none'] = '(photons.hOverE[0] < 0.06)'
        SigmaIetaIetaSels[era][loc]['none'] = '('+locationSels[loc]+' && '+hOverESels[era][loc]['none']+' && '+nhIsoSels[era][loc]['none']+' && '+phIsoSels[era][loc]['none']+')'
        PhotonIsolationSels[era][loc]['none'] = '('+locationSels[loc]+' && '+hOverESels[era][loc]['none']+' && '+chIsoSels[era][loc]['none']+' && '+nhIsoSels[era][loc]['none']+')'

        for pid in PhotonIds[1:]:
            hOverESel = '(photons.hOverE[0] < '+str(hOverECuts[era][loc][pid])+')'
            sieieSel = '(photons.sieie[0] < '+str(sieieCuts[era][loc][pid])+')'
            sieieSelWeighted = '( (0.891832 * photons.sieie[0] + 0.0009133) < '+str(sieieCuts[era][loc][pid])+')'

            chWorstIsoSel = '(photons.chWorstIso[0] < ' + str(chIsoCuts[era][loc][pid]) + ')'
            chIsoMaxSel = '(photons.chIsoMax[0] < ' + str(chIsoCuts[era][loc][pid]) + ')'

            if era == 'Spring15':
                chIsoSel = '(photons.chIsoS15[0] < '+str(chIsoCuts[era][loc][pid])+')'
            elif era == 'Spring16':
                chIsoSel = '(photons.chIso[0] < '+str(chIsoCuts[era][loc][pid])+')'
            elif era == 'Ashim_ZG_CWIso':
                chIsoSel = '(photons.chIso[0] < ' + str(chIsoCuts[era][loc][pid])+')'
#                chIsoSel = '(photons.chIsoZG[0] < 1.163)'

            if era == 'Spring15':
                nhIsoSel = '(photons.nhIsoS15[0] < '+str(nhIsoCuts[era][loc][pid])+')'
            elif era == 'Spring16':
                nhIsoSel = '(photons.nhIso[0] < '+str(nhIsoCuts[era][loc][pid])+')'
            elif era == 'Ashim_ZG_CWIso':
                nhIsoSel = '(photons.nhIso[0] + (0.0148 - 0.0112) * photons.scRawPt[0] + (0.000017 - 0.000028) * photons.scRawPt[0] * photons.scRawPt[0] < '+str(nhIsoCuts[era][loc][pid])+')'
#                nhIsoSel = '(photons.nhIsoZG[0] < 7.005)'

            if era == 'Spring15':
                if pid == 'highpt':
                    phIsoSel = '(photons.phIsoS15[0] + 0.0053*photons.scRawPt[0] < '+str(phIsoCuts[era][loc][pid])+')'
                else:
                    phIsoSel = '(photons.phIsoS15[0] < '+str(phIsoCuts[era][loc][pid])+')'
            elif era == 'Spring16':
                phIsoSel = '(photons.phIso[0] < '+str(phIsoCuts[era][loc][pid])+')'
            elif era == 'Ashim_ZG_CWIso':
                phIsoSel = '(photons.phIso[0] + (0.0047 - 0.0043) * photons.scRawPt[0] < '+str(phIsoCuts[era][loc][pid])+')'
#                phIsoSel = '(photons.phIsoZG[0] < 3.271)'

            hOverESels[era][loc][pid] = hOverESel 
            sieieSels[era][loc][pid] = sieieSel
            chIsoSels[era][loc][pid] = chIsoSel
            chWorstIsoSels[era][loc][pid] = chWorstIsoSel
            chIsoMaxSels[era][loc][pid] = chIsoMaxSel
            nhIsoSels[era][loc][pid] = nhIsoSel
            phIsoSels[era][loc][pid] = phIsoSel
            SigmaIetaIetaSel = '('+locationSels[loc]+' && '+hOverESel+' && '+nhIsoSel+' && '+phIsoSel+')'
            PhotonIsolationSel = '('+locationSels[loc]+' && '+hOverESel+' && '+chIsoSel+' && '+nhIsoSel+')'
            SigmaIetaIetaSels[era][loc][pid] = SigmaIetaIetaSel
            PhotonIsolationSels[era][loc][pid] = PhotonIsolationSel

cutIsLoose = '(photons.loose[0])'
cutIsMedium = '(photons.medium[0])'
cutIsTight = '(photons.tight[0])'

cutMatchedToPhoton = '(TMath::Abs(photons.matchedGenId[0]) == 22)'
cutMatchedToReal = '(photons.matchedGenId[0] == -22)'

# chWorstIsoCut 
pixelVetoCut = 'photons.pixelVeto[0]'
mipCut = 'photons.mipEnergy[0] < 4.9'
timeCut = 'std::abs(photons.time[0]) < 3.'
sieieNonzeroCut = 'photons.sieie[0] > 0.001'
sipipNonzeroCut = 'photons.sipip[0] > 0.001'
noisyRegionCut = '!(photons.eta_[0] > 0. && photons.eta_[0] < 0.15 && photons.phi_[0] > 0.527580 && photons.phi_[0] < 0.541795)'

monophIdCut = ' && '.join([mipCut, timeCut, sieieNonzeroCut, sipipNonzeroCut, noisyRegionCut])

cutPhotonPtHigh = [175,200,250,300,350,400,450,500]#,550,600] 
# cutPhotonPtHigh = [175, 200, 225, 250, 280, 320, 375, 425]
PhotonPtSels = { 'PhotonPtInclusive' : '((photons.scRawPt[0] > '+str(cutPhotonPtHigh[0])+'))' }
for low, high in zip(cutPhotonPtHigh, cutPhotonPtHigh[1:]):
    PhotonPtSels['PhotonPt'+str(low)+'to'+str(high)] = '((photons.scRawPt[0] > '+str(low)+') && (photons.scRawPt[0] < '+str(high)+'))' 
PhotonPtSels['PhotonPt'+str(cutPhotonPtHigh[-1])+'toInf'] =  '((photons.scRawPt[0] > '+str(cutPhotonPtHigh[-1])+'))'

cutMet = [0,60,120]
MetSels = { 'MetInclusive' : '((t1Met.pt > '+str(cutMet[0])+'))' } 
for low, high in zip(cutMet,cutMet[1:]):
    MetSels['Met'+str(low)+'to'+str(high)] = '((t1Met.pt > '+str(low)+') && (t1Met.pt < '+str(high)+'))'
MetSels['Met'+str(cutMet[-1])+'toInf'] =  '((t1Met.pt > '+str(cutMet[-1])+'))' 

ChIsoSbSels = { 'ChIso50to80'  : '(photons.chIso[0] > 5.0 && photons.chIso[0] < 8.0)',
                'ChIso20to50'  : '(photons.chIso[0] > 2.0 && photons.chIso[0] < 5.0)',
                'ChIso80to110' : '(photons.chIso[0] > 8.0 && photons.chIso[0] < 11.0)',
                'ChIso35to50'  : '(photons.chIso[0] > 3.5 && photons.chIso[0] < 5.0)', 
                'ChIso50to75'  : '(photons.chIso[0] > 5.0 && photons.chIso[0] < 7.5)',
                'ChIso75to90'  : '(photons.chIso[0] > 7.5 && photons.chIso[0] < 9.0)',
                'ChIso40to60'  : '(photons.chIso[0] > 4.0 && photons.chIso[0] < 6.0)', 
                'ChIso60to80'  : '(photons.chIso[0] > 6.0 && photons.chIso[0] < 8.0)',
                'ChIso80to100'  : '(photons.chIso[0] > 8.0 && photons.chIso[0] < 10.0)'
                }

# Function for making templates!
class HistExtractor(object):
    def __init__(self, name, snames, variable):
        self.name = name
        self.plotter = ROOT.MultiDraw()
        for sname in snames:
            inName = os.path.join(config.skimDir, sname+'_emjet.root')
            localName = os.path.join(config.localSkimDir, sname+'_emjet.root')
            if os.path.exists(localName) and os.stat(localName).st_mtime > os.stat(inName).st_mtime:
                self.plotter.addInputPath(localName)
            else:
                self.plotter.addInputPath(inName)

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
            if not mcsf:
                name += '_raw'

            hist = template.Clone(name)
            hist.SetTitle(title)
            histograms.append(hist)

            print 'addPlot', self.variable, sel

            self.plotter.addPlot(hist, self.variable, sel, True)

        self.plotter.fillPlots()

        if mcsf and 'sieie' in self.variable:
            print 'Applying data/MC scale factor to the templates'

            source = ROOT.TFile(basedir + '/data/sieie_ratio.root')
            line = source.Get('fit')

            for hist in histograms:
                for iX in range(1, hist.GetNbinsX() + 1):
                    hist.SetBinContent(iX, hist.GetBinContent(iX) * line.Eval(hist.GetXaxis().GetBinCenter(iX)))

            source.Close()

        if outFile is not None:
            outFile.cd()
            outFile.Write()

        return histograms

def MakeRooRealVar(_name, _iloc):
    var = Variables[_name]

    if type(var[3][_iloc]) is tuple:
        n, low, high = var[3][_iloc]
        binning = RooUniformBinning(low, high, n)
    else:
        arr = var[3][_iloc]
        binning = RooBinning(len(arr) - 1, array.array('d', arr))

    v = RooRealVar(_name, var[2], binning.lowBound(), binning.highBound())
    v.setBinning(binning)

    return v

        
def HistToTemplate(_hist,_rfvar,_selName,_plotDir):
    # remove negative weights
    for bin in range(_hist.GetNbinsX()+1):
        binContent = _hist.GetBinContent(bin)
        if ( binContent < 0.):
            _hist.SetBinContent(bin, 0.)
            _hist.SetBinError(bin, 0.)
        binErrorLow = _hist.GetBinErrorLow(bin)
        if ( (binContent - binErrorLow) < 0.):
            _hist.SetBinError(bin, binContent)


    print 'Making RooFit template from ' + _hist.GetName()
    tempname = 'template_' + _hist.GetName() + '_' + _selName
    temp = RooDataHist(tempname, tempname, RooArgList(_rfvar), _hist)
    
    canvas = TCanvas()
    frame = _rfvar.frame()
    temp.plotOn(frame)
        
    frame.SetTitle(_hist.GetTitle())
        
    frame.Draw()
        
    outName = os.path.join(_plotDir,tempname)
    canvas.SaveAs(outName+'.pdf')
    canvas.SaveAs(outName+'.png')
    canvas.SaveAs(outName+'.C')

    """
    canvas.SetLogy()
    canvas.SaveAs(outName+'_Logy.pdf')
    canvas.SaveAs(outName+'_Logy.png')
    canvas.SaveAs(outName+'_Logy.C')
    """
    
    return temp

def StatUncert(nReal, nFake):
    # Calculate purity and print results
    print "Number of Real photons passing selection:", nReal
    print "Number of Fake photons passing selection:", nFake
    nTotal = nReal + nFake;
    purity = float(nReal) / float(nTotal)
    print "Purity of Photons is:", purity
    
    upper = TEfficiency.ClopperPearson(int(nTotal),int(nReal),0.6827,True)
    lower = TEfficiency.ClopperPearson(int(nTotal),int(nReal),0.6827,False)

    upSig = upper - purity;
    downSig = purity - lower;

    return float(upSig + downSig) / 2.0;

# Fitting function
def FitTemplates(_name,_title,_var,_cut,_datahist,_sigtemp,_bkgtemp):
    nEvents = _datahist.sumEntries()
    sigpdf = RooHistPdf('sig', 'sig', RooArgSet(_var), _sigtemp) #, 2)
    bkgpdf = RooHistPdf('bkg', 'bkg', RooArgSet(_var), _bkgtemp) #, 2)
    nsig = RooRealVar('nsig', 'nsig', nEvents/2, nEvents*0.01, nEvents*1.5)
    nbkg = RooRealVar('nbkg', 'nbkg', nEvents/2, 0., nEvents*1.5)
    model = RooAddPdf("model", "model", RooArgList(sigpdf, bkgpdf), RooArgList(nsig, nbkg))
    model.fitTo(_datahist, ROOT.RooFit.PrintLevel(1)) # , Extended(True), Minimizer("Minuit2", "migrad"))
    
    canvas = TCanvas()

    frame = _var.frame()
    frame.SetTitle(_title)
    # frame.SetMinimum(0.001)
    # frame.SetMaximum(10000)

    _datahist.plotOn(frame, RooFit.Name("data"))
    model.plotOn(frame, RooFit.Name("Fit"))
    model.plotOn(frame, RooFit.Components('bkg'),RooFit.Name("fake"),RooFit.LineStyle(kDashed),RooFit.LineColor(kGreen))
    model.plotOn(frame, RooFit.Components('sig'),RooFit.Name("real"),RooFit.LineStyle(kDashed),RooFit.LineColor(kRed))

    
    frame.Draw("goff")
    
    _var.setRange("selection",0.0,_cut)
    
    fReal = float(sigpdf.createIntegral(RooArgSet(_var), "selection").getVal()) / float(sigpdf.createIntegral(RooArgSet(_var)).getVal())
    fFake = float(bkgpdf.createIntegral(RooArgSet(_var), "selection").getVal()) / float(bkgpdf.createIntegral(RooArgSet(_var)).getVal())
    nReal = fReal * nsig.getVal()
    nFake = fFake * nbkg.getVal()
    nTotal = nReal + nFake

    purity = float(nReal) / float(nTotal)

    aveSig = StatUncert(nReal, nFake)

    text = TLatex()
    text.DrawLatexNDC(0.525,0.8,"Purity: "+str(round(purity,3))+'#pm'+str(round(aveSig,3))) 

    leg = TLegend(0.6,0.6,0.85,0.75 );
    leg.SetFillColor(kWhite);
    leg.SetTextSize(0.03);
    # leg.SetHeader("templates LOWER<p_{T}<UPPER");
    leg.AddEntry(frame.findObject("data"), "data", "P");
    leg.AddEntry(frame.findObject("Fit"), "real+fake fit to data", "L");
    leg.AddEntry(frame.findObject("real"), "real", "L");
    leg.AddEntry(frame.findObject("fake"), "fake", "L");
    leg.Draw();

    canvas.SaveAs(_name+'.pdf')
    canvas.SaveAs(_name+'.png')
    canvas.SaveAs(_name+'.C')
    canvas.SaveAs(_name+'.root')

    canvas.SetLogy()
    canvas.SaveAs(_name+'_Logy.pdf')
    canvas.SaveAs(_name+'_Logy.png')
    canvas.SaveAs(_name+'_Logy.C')

    return (purity, aveSig, nReal, nFake)

def SignalSubtraction(_skims,_initialHists,_initialTemplates,_isoRatio,_rfvar,_cut,_inputKey,_plotDir):
    ''' initialHists = [ fit template, signal template, subtraction template, background template ]'''
    nIter = 0
    purities = [ (1,1,1,1) ]
    # sigContams = [ (1,1) ]
    hists = list(_initialHists)
    templates = list(_initialTemplates)

    while(True):
        print "Starting on iteration:", nIter

        dataTitle = "Photon Purity in SinglePhoton DataSet Iteration "+str(nIter)
        dataName = os.path.join(_plotDir,"purity_"+"v"+str(nIter)+"_"+_inputKey )

        dataPurity = FitTemplates(dataName, dataTitle, _rfvar, _cut, templates[0], templates[1], templates[-1])
       
        """
        sbTotal = templates[3].sumEntries()
        sbTrue = templates[-2].sumEntries()
        trueContam = float(sbTrue) / float(sbTotal)

        sbTotalPass = templates[3].sumEntries(_varName+' < '+str(_cut))
        sbTruePass = templates[-2].sumEntries(_varName+' < '+str(_cut))
        trueContamPass = float(sbTruePass) / float(sbTotalPass)

        print "Signal contamination:", trueContam, trueContamPass
        sigContams.append( (trueContam, trueContamPass) ) 
        """
                
        print "Purity:", dataPurity[0]
        purities.append( dataPurity )
        diff = abs(purities[-1][0] - purities[-2][0] )
        print diff 
        if ( diff < 0.001):
            break
        nIter += 1
        if nIter > 10:
            break
        
        nSigTrue = purities[-1][2]
        nSbTrue = _isoRatio * nSigTrue
            
        print "Scaling sideband shape to", nSbTrue, "photons"
            
        contamHist = hists[2].Clone()
        contamHist.Scale(float(nSbTrue) / float(contamHist.GetSumOfWeights()))
        hists.append(contamHist)

        contamTemp = HistToTemplate(contamHist,_rfvar,"v"+str(nIter)+"_"+_inputKey,_plotDir)
        templates.append(contamTemp)
    
        backHist = hists[3].Clone()
        backHist.Add(contamHist, -1)
        hists.append(backHist)

        backTemp = HistToTemplate(backHist,_rfvar,"v"+str(nIter)+"_"+_inputKey,_plotDir)
        templates.append(backTemp)

    """
    for version, (purity, contam)  in enumerate(zip(purities[1:],sigContams[1:])):
        print "Purity for iteration", version, "is:", purity
        print "Signal contamination for iteration", version, "is:", contam
    
    return (purities[-1], sigContams[-1])
    """

    for version, purity  in enumerate(purities[1:]):
        print "Purity for iteration", version, "is:", purity
    return purities[-1]

print 'blah'


