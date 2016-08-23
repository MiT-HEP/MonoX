import os
import sys
import array
import ROOT


thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

if basedir not in sys.path:
    sys.path.append(basedir)

import config

### Getting cut values from simple tree ###

# ROOT.gSystem.Load('libMitFlatDataFormats.so')
ROOT.gSystem.Load(os.environ['CMSSW_BASE'] + '/src/MitMonoX/monophoton/MitFlat/DataFormats/obj/libsimpletree.so')
ROOT.gSystem.AddIncludePath('-I' + '../MitFlat/DataFormats/interface')

Locations = [ 'barrel', 'endcap' ]
PhotonIds = [ 'none', 'loose', 'medium', 'tight' ]

hOverECuts = {}
sieieCuts = {}
chIsoCuts = {}
nhIsoCuts = {}
phIsoCuts = {}

ROOT.gROOT.ProcessLine("double cut;")
for iLoc, loc in enumerate(Locations):
    hOverECuts[loc] = {}
    sieieCuts[loc] = {}
    chIsoCuts[loc] = {}
    nhIsoCuts[loc] = {}
    phIsoCuts[loc] = {}

    for cuts in [sieieCuts]:
        cuts[loc]['none'] = 1.
    
    for iId, pid in enumerate(PhotonIds[1:]):
        ROOT.gROOT.ProcessLine("cut = simpletree::Photon::hOverECuts["+str(iLoc)+"]["+str(iId)+"];")
        # print "hOverE", loc, pid, ROOT.cut
        hOverECuts[loc][pid] = ROOT.cut
        ROOT.gROOT.ProcessLine("cut = simpletree::Photon::sieieCuts["+str(iLoc)+"]["+str(iId)+"];")
        # print "sieie", loc, pid, ROOT.cut
        sieieCuts[loc][pid] = ROOT.cut
        ROOT.gROOT.ProcessLine("cut = simpletree::Photon::chIsoCuts["+str(iLoc)+"]["+str(iId)+"];")
        # print "chIso", loc, pid, ROOT.cut
        chIsoCuts[loc][pid] = ROOT.cut
        ROOT.gROOT.ProcessLine("cut = simpletree::Photon::nhIsoCuts["+str(iLoc)+"]["+str(iId)+"];")
        # print "nhIso", loc, pid, ROOT.cut
        nhIsoCuts[loc][pid] = ROOT.cut
        ROOT.gROOT.ProcessLine("cut = simpletree::Photon::phIsoCuts["+str(iLoc)+"]["+str(iId)+"];")
        # print "phIso", loc, pid, ROOT.cut
        phIsoCuts[loc][pid] = ROOT.cut

### Now start actual parameters that need to be changed ###

# Version = config.simpletreeVersion
Version = 'nerogjets'

from ROOT import *

ChIsoSbBins = range(20,111,5)

# Variables and associated properties
# variable Enum, sideband Enum, selection Enum, roofit variable ( region : roofit variable, nbins, variable binning), cut dict for purity
Variables = { "sieie"  : ('photons.sieie', sieieCuts, { "barrel"  : (RooRealVar('sieie', '#sigma_{i#etai#eta}', 0.004, 0.015), 44, [0.004,0.011,0.015] )
                                                        ,"endcap" : (RooRealVar('sieie', '#sigma_{i#etai#eta}', 0.016, 0.040), 48, [0.016,0.030,0.040] ) } )
              ,"chiso" : ('photons.chIso', chIsoCuts, { "barrel"  : (RooRealVar('chiso', 'Ch Iso (GeV)', 0.0, 11.0), 22, [0.0,chIsoCuts["barrel"]["medium"]]+[float(x)/10.0 for x in ChIsoSbBins] )
                                                        ,"endcap" : (RooRealVar('chiso', 'Ch Iso (GeV)', 0.0, 11.0), 22, [0.0,chIsoCuts["endcap"]["medium"]]+[float(x)/10.0 for x in ChIsoSbBins] ) } ) 
              } 
               
# Skims for Purity Calculation
sphData = ['sph-16b2', 'sph-16b2s', 'sph-16c2', 'sph-16d2']
gjetsMc = ['gj-40','gj-100','gj-200','gj-400','gj-600']
qcdMc = [ 'qcd-200', 'qcd-300', 'qcd-500', 'qcd-700', 'qcd-1000', 'qcd-1000', 'qcd-1500', 'qcd-2000']
sphDataNero = ['sph-16b2-d', 'sph-16c2-d', 'sph-16d2-d']
gjetsMcNero = ['gj-40-d','gj-100-d','gj-200-d','gj-400-d','gj-600-d']

Measurement = { "bambu" : [ ('FitSinglePhoton',sphData,'Fit Template from SinglePhoton Data')
                                 ,('TempSignalGJets',gjetsMc,r'Signal Template from #gamma+jets MC')
                                 ,('TempSidebandGJets',gjetsMc,r'Sideband Template from #gamma+jets MC')
                                 ,('TempBkgdSinglePhoton',sphData,'Background Template from SinglePhoton Data')
                                 ,('TempSidebandGJetsScaled',gjetsMc,r'Scaled Sideband Template from #gamma+jets MC')
                                 ,('TempBkgdSinglePhoton',sphData,'Background Template from SinglePhoton Data')
                                 ],
                "bambumc" : [ ('FitSinglePhoton',gjetsMc+qcdMc,'Fit Template from SinglePhoton Data')
                                 ,('TempSignalGJets',gjetsMc,r'Signal Template from #gamma+jets MC')
                                 ,('TempSidebandGJets',gjetsMc,r'Sideband Template from #gamma+jets MC')
                                 ,('TempBkgdSinglePhoton',gjetsMc+qcdMc,'Background Template from SinglePhoton Data')
                                 ,('TempSidebandGJetsScaled',gjetsMc,r'Scaled Sideband Template from #gamma+jets MC')
                                 ,('TempBkgdSinglePhoton',gjetsMc+qcdMc,'Background Template from SinglePhoton Data')
                                 ],
                "nero" : [ ('FitSinglePhoton',sphDataNero,'Fit Template from SinglePhoton Data')
                                 ,('TempSignalGJets',gjetsMcNero,r'Signal Template from #gamma+jets MC')
                                 ,('TempSidebandGJets',gjetsMcNero,r'Sideband Template from #gamma+jets MC')
                                 ,('TempBkgdSinglePhoton',sphDataNero,'Background Template from SinglePhoton Data')
                                 ,('TempSidebandGJetsScaled',gjetsMcNero,r'Scaled Sideband Template from #gamma+jets MC')
                                 ,('TempBkgdSinglePhoton',sphDataNero,'Background Template from SinglePhoton Data')
                                 ],
                "neromc" : [ ('FitSinglePhoton',gjetsMcNero+qcdMc,'Fit Template from SinglePhoton Data')
                                 ,('TempSignalGJets',gjetsMcNero,r'Signal Template from #gamma+jets MC')
                                 ,('TempSidebandGJets',gjetsMcNero,r'Sideband Template from #gamma+jets MC')
                                 ,('TempBkgdSinglePhoton',gjetsMcNero+qcdMc,'Background Template from SinglePhoton Data')
                                 ,('TempSidebandGJetsScaled',gjetsMcNero,r'Scaled Sideband Template from #gamma+jets MC')
                                 ,('TempBkgdSinglePhoton',gjetsMcNero+qcdMc,'Background Template from SinglePhoton Data')
                                 ]
                }

# Selections for Purity Calculation
locationSels = {}
locationSels["barrel"] = '(TMath::Abs(photons.eta) < 1.5)'
locationSels["endcap"] = '((TMath::Abs(photons.eta) > 1.5) && (TMath::Abs(photons.eta) < 2.4))'

hOverESels = {} 
sieieSels = {} 
chIsoSels = {}
nhIsoSels = {}
phIsoSels = {}
SigmaIetaIetaSels = {}
PhotonIsolationSels = {}

for loc in Locations:
    hOverESels[loc] = {}
    sieieSels[loc] = {}
    chIsoSels[loc] = {}
    nhIsoSels[loc] = {}
    phIsoSels[loc] = {}
    SigmaIetaIetaSels[loc] = {}
    PhotonIsolationSels[loc] = {}

    for sel in [hOverESels, sieieSels, chIsoSels, nhIsoSels, phIsoSels, SigmaIetaIetaSels, PhotonIsolationSels]:
        sel[loc]['none'] = '(1)'
    
    for pid in PhotonIds[1:]:
        hOverESel = '(photons.hOverE < '+str(hOverECuts[loc][pid])+')'
        sieieSel = '(photons.sieie < '+str(sieieCuts[loc][pid])+')'
        sieieSelWeighted = '( (0.891832 * photons.sieie + 0.0009133) < '+str(sieieCuts[loc][pid])+')'
        chIsoSel = '(photons.chIso < '+str(chIsoCuts[loc][pid])+')'
        nhIsoSel = '(photons.nhIso < '+str(nhIsoCuts[loc][pid])+')'
        phIsoSel = '(photons.phIso < '+str(phIsoCuts[loc][pid])+')'
        hOverESels[loc][pid] = hOverESel 
        sieieSels[loc][pid] = sieieSel
        chIsoSels[loc][pid] = chIsoSel
        nhIsoSels[loc][pid] = nhIsoSel
        phIsoSels[loc][pid] = phIsoSel
        SigmaIetaIetaSel = '('+locationSels[loc]+' && '+hOverESel+' && '+nhIsoSel+' && '+phIsoSel+')'
        PhotonIsolationSel = '('+locationSels[loc]+' && '+hOverESel+' && '+chIsoSel+' && '+nhIsoSel+')'
        # print loc, pid, SigmaIetaIetaSel, chIsoSel
        SigmaIetaIetaSels[loc][pid] = SigmaIetaIetaSel
        PhotonIsolationSels[loc][pid] = PhotonIsolationSel
        


cutIsLoose = '(photons.loose)'
cutIsMedium = '(photons.medium)'
cutIsTight = '(photons.tight)'

cutMatchedToPhoton = '(TMath::Abs(photons.matchedGen) == 22)'
cutMatchedToReal = '(photons.matchedGen == -22)'

# chWorstIsoCut 
pixelVetoCut = 'photons.pixelVeto'
mipCut = 'photons.mipEnergy < 4.9'
timeCut = 'std::abs(photons.time) < 3.'
sieieNonzeroCut = 'photons.sieie > 0.001'
sipipNonzeroCut = 'photons.sipip > 0.001'
noisyRegionCut = '!(photons.eta > 0. && photons.eta < 0.15 && photons.phi > 0.527580 && photons.phi < 0.541795)'

monophIdCut = ' && '.join([mipCut, timeCut, sieieNonzeroCut, sipipNonzeroCut, noisyRegionCut])

cutPhotonPtHigh = [175,200,250,300,350] 
PhotonPtSels = [ ('PhotonPt'+str(cutPhotonPtHigh[0])+'toInf', '((photons.scRawPt > '+str(cutPhotonPtHigh[0])+'))') ]
PhotonPtSels = PhotonPtSels + [ ('PhotonPt'+str(low)+'to'+str(high), '((photons.scRawPt > '+str(low)+') && (photons.scRawPt < '+str(high)+'))') for low, high in zip(cutPhotonPtHigh, cutPhotonPtHigh[1:]) ] 
PhotonPtSels = PhotonPtSels + [ ('PhotonPt'+str(cutPhotonPtHigh[-1])+'toInf', '((photons.scRawPt > '+str(cutPhotonPtHigh[-1])+'))') ]

cutMet = [000,60,120]
MetSels = [ ('Met'+str(cutMet[0])+'toInf', '((t1Met.met > '+str(cutMet[0])+'))') ] 
MetSels = MetSels + [ ('Met'+str(low)+'to'+str(high),'((t1Met.met  >'+str(low)+') && (t1Met.met < '+str(high)+'))') for low, high in zip(cutMet,cutMet[1:]) ]
MetSels = MetSels + [ ('Met'+str(cutMet[-1])+'toInf', '((t1Met.met > '+str(cutMet[-1])+'))') ]

"""
ChIsoSbBins = range(20,105,5)
ChIsoSbSels = [ ('ChIso'+str(low)+'to'+str(high), '((photons.chIso > '+str(float(low)/10.0)+') && (photons.chIso < '+str(float(high)/10.0)+'))') for low, high in zip(ChIsoSbBins[:-4], ChIsoSbBins[4:]) ]
"""
ChIsoSbBins = range(20,111,30)
ChIsoSbSels = [ ('ChIso'+str(low)+'to'+str(high), '((photons.chIso > '+str(float(low)/10.0)+') && (photons.chIso < '+str(float(high)/10.0)+'))') for low, high in zip(ChIsoSbBins[:-1], ChIsoSbBins[1:]) ]

# Function for making templates!
""" arguments = ( variable, RooRealVar, skim, selection, location, variablebinning ) """
def HistExtractor(_temp,_var,_skim,_sel,_skimDir,_varBins):
    print '\nStarting template:', _skim[0]

    tree = ROOT.TChain('events')
    for skim in _skim[1]:
        inName = os.path.join(_skimDir,skim+'_purity.root')
        print 'Adding', inName, "to chain"
        tree.Add(inName)

    if _varBins:
        tempH = TH1D(_skim[0], "", (len(_var[2])-1), array.array('d', _var[2]))
    else:
        tempH = TH1D(_skim[0], "", _var[1], _var[0].getMin(), _var[0].getMax())
    tempH.Sumw2();

    print 'Applying selection:'
    if _sel:
        _sel = _sel + ' && !(run > %s)' % config.runCutOff
        _sel = 'weight * (%s)' % _sel
    else:
        _sel = 'weight * (%s)' % ('!(run > %s)' % config.runCutOff)
    print _sel, '\n'
    
    tree.Draw(_temp+">>"+_skim[0], _sel, "goff")

    if not 'Fit' in _skim[0]:
        for iBin in range(1, tempH.GetNbinsX()+1):
            if not tempH.GetBinContent(iBin) > 0:
                tempH.SetBinContent(iBin, 0.0000001)

    print tempH.Integral()

    return tempH
        
def HistToTemplate(_hist,_var,_skim,_selName,_plotDir):
    # remove negative weights
    for bin in range(_hist.GetNbinsX()+1):
        binContent = _hist.GetBinContent(bin)
        if ( binContent< 0.):
            _hist.SetBinContent(bin, 0.)
            _hist.SetBinError(bin, 0.)
        binErrorLow = _hist.GetBinErrorLow(bin)
        if ( (binContent - binErrorLow) < 0.):
            _hist.SetBinError(bin, binContent)


    print _selName
    tempname = 'template_'+_skim[0]+'_'+_selName
    temp = RooDataHist(tempname, tempname, RooArgList(_var[0]), _hist)
    
    canvas = TCanvas()
    frame = _var[0].frame()
    temp.plotOn(frame)
        
    print _skim[2]
    frame.SetTitle(_skim[2])
        
    frame.Draw()
        
    outName = os.path.join(_plotDir,tempname)
    canvas.SaveAs(outName+'.pdf')
    canvas.SaveAs(outName+'.png')
    canvas.SaveAs(outName+'.C')

    canvas.SetLogy()
    canvas.SaveAs(outName+'_Logy.pdf')
    canvas.SaveAs(outName+'_Logy.png')
    canvas.SaveAs(outName+'_Logy.C')

    return temp

# Fitting function
def FitTemplates(_name,_title,_var,_cut,_datahist,_sigtemp,_bkgtemp):
    nEvents = _datahist.sumEntries()
    sigpdf = RooHistPdf('sig', 'sig', RooArgSet(_var), _sigtemp) #, 2)
    bkgpdf = RooHistPdf('bkg', 'bkg', RooArgSet(_var), _bkgtemp) #, 2)
    nsig = RooRealVar('nsig', 'nsig', nEvents/2, 0., nEvents*1.5)
    nbkg = RooRealVar('nbkg', 'nbkg', nEvents/2, 0., nEvents*1.5)
    model = RooAddPdf("model", "model", RooArgList(sigpdf, bkgpdf), RooArgList(nsig, nbkg))
    model.fitTo(_datahist) # , Extended(True), Minimizer("Minuit2", "migrad"))
    
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
    aveSig = float(upSig + downSig) / 2.0;

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

def SignalSubtraction(_skims,_initialHists,_initialTemplates,_isoRatio,_varName,_var,_cut,_inputKey,_plotDir):
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
        
        print _var[0]
        dataPurity = FitTemplates(dataName, dataTitle, _var[0], _cut, templates[0], templates[1], templates[-1])
       
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

        print _var
        contamTemp = HistToTemplate(contamHist,_var,_skims[2],"v"+str(nIter)+"_"+_inputKey,_plotDir)
        templates.append(contamTemp)
    
        backHist = hists[3].Clone()
        backHist.Add(contamHist, -1)
        hists.append(backHist)

        backTemp = HistToTemplate(backHist,_var,_skims[3],"v"+str(nIter)+"_"+_inputKey,_plotDir)
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

