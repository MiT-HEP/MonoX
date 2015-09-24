import os
import sys
from ROOT import *
from selections import *
#ROOT.gROOT.SetBatch(True)

gSystem.Load('libMitFlatDataFormats.so')
gSystem.AddIncludePath('-I' + os.environ['CMSSW_BASE'] + '/src/MitFlat/DataFormats/interface')
TemplateGeneratorPath = os.path.join(os.environ['CMSSW_BASE'],'src/MitMonoX/monophoton/purity','TemplateGenerator.cc+')
gROOT.LoadMacro(TemplateGeneratorPath)


# Fitting function
def FitTemplates(name,title,var,cut,datahist,sigtemp,bkgtemp):
    nEvents = datahist.sumEntries()
    sigpdf = RooHistPdf('sig', 'sig', RooArgSet(var), sigtemp) #, 2)
    bkgpdf = RooHistPdf('bkg', 'bkg', RooArgSet(var), bkgtemp) #, 2)
    nsig = RooRealVar('nsig', 'nsig', nEvents/2, 0., nEvents*1.5)
    nbkg = RooRealVar('nbkg', 'nbkg', nEvents/2, 0., nEvents*1.5)
    model = RooAddPdf("model", "model", RooArgList(sigpdf, bkgpdf), RooArgList(nsig, nbkg))
    model.fitTo(datahist) # , Extended(True), Minimizer("Minuit2", "migrad"))
    
    canvas = TCanvas()

    frame = var.frame()
    frame.SetTitle(title)

    datahist.plotOn(frame, RooFit.Name("data"))
    model.plotOn(frame, RooFit.Name("Fit"))
    # model.paramOn(frame)
    model.plotOn(frame, RooFit.Components('bkg'),RooFit.Name("fake"),RooFit.LineStyle(kDashed),RooFit.LineColor(kGreen))
    model.plotOn(frame, RooFit.Components('sig'),RooFit.Name("real"),RooFit.LineStyle(kDashed),RooFit.LineColor(kRed))
    #sigpdf.plotOn(frame, RooFit.Name("signal"))
    #bkgpdf.plotOn(frame, RooFit.Name("fake"))
    
    frame.Draw("goff")
    
    var.setRange("selection",0.0,cut)
    
    fReal = float(sigpdf.createIntegral(RooArgSet(var), "selection").getVal()) / float(sigpdf.createIntegral(RooArgSet(var)).getVal())
    fFake = float(bkgpdf.createIntegral(RooArgSet(var), "selection").getVal()) / float(bkgpdf.createIntegral(RooArgSet(var)).getVal())
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

    text = TLatex() #0.8,0.7,"Purity: "+str(round(purity,4)))
    text.DrawLatexNDC(0.525,0.8,"Purity: "+str(round(purity,4))+'#pm'+str(round(aveSig,4))) # '+'+str(round(upSig,4))+'-'+str(round(downSig,4)))

    leg = TLegend(0.6,0.6,0.85,0.75 );
    leg.SetFillColor(kWhite);
    leg.SetTextSize(0.03);
    # leg.SetHeader("templates LOWER<p_{T}<UPPER");
    leg.AddEntry(frame.findObject("data"), "data", "P");
    leg.AddEntry(frame.findObject("Fit"), "real+fake fit to data", "L");
    leg.AddEntry(frame.findObject("real"), "real", "L"); # model_Norm[sieie]_Comp[sig]
    leg.AddEntry(frame.findObject("fake"), "fake", "L"); # model_Norm[sieie]_Comp[bkg]
    leg.Draw();

    canvas.SaveAs(name+'.pdf')
    canvas.SetLogy()
    canvas.SaveAs(name+'_Logy.pdf')

    return purity

    # purity = float(nReal) / float(nReal + nFake)
    # purity = nsig / nEvents
    # return (nReal,nFake)

# Template info
Measurement = { "Wlike_sieie" : [ ('TempSignal','TempSignal',kPhoton,'Signal Template from MC') # (selection name, skim file to read from, template type, template title)
                                  ,('TempBkgdData','TempBkgdData',kBackground,'Background Template from Data')
                                  ,('TempBkgdMc','TempBkgdMc',kBackground,'Background Template from MC')
                                  ,('FitData','FitData',kPhoton,'Fit Template from Data')
                                  ,('FitMc','FitMc',kPhoton,'Fit Template from MC')
                                  ,('McTruthSignal','FitMc',kPhoton,'Signal Template from MC Truth')
                                  ,('McTruthBkgd','FitMc',kBackground,'Background Template from MC Truth') ]
                ,"Monophoton_sieie" : [ ( 'TempSignalGJets','TempSignalGJets',kPhoton)
                                        ,('TempBkgdSinglePhoton','TempBkgdSinglePhoton',kBackground)
                                        ,('TempBkgdGJets','TempBkgdGJets',kBackground)
                                        ,('FitSinglePhoton','FitSinglePhoton',kPhoton)
                                        ,('FitGJets','TempSignalGJets',kPhoton)
                                        ,('GJetsTruthSignal','TempSignalGJets',kPhoton)
                                        ,('GJetsTruthBkgd','TempSignalGJets',kBackground) ] 
                ,"CompGammaE_phIso" : [ ( 'TempSignalWgPhotons','TempSignalWgPhotons',kPhoton)
                                     ,('TempSignalWgElectrons','TempSignalWgElectrons',kElectron) ] }

Variables = { "sieie"  : (RooRealVar('sieie', '#sigma_{i#etai#eta}', 0., 0.02),0.0100,kSigmaIetaIeta)
              ,"phIso" : (RooRealVar('phIso', 'Ph Iso (GeV)', 0., 0.02),1.33,kPhotonIsolation) } # cut is actually a function of pT

# Make templates from skims
varName = 'sieie'
var = Variables[varName]
skims = Measurement["Wlike_sieie"]
#sels = ['medium_barrel_'+cut[0] for cut in cutPhotonPt]
sels = ['medium_barrel_Wlike'] #PhotonPt180toInf']
purities = [[],[],[],[]]
for sel in sels:
    templates = []
    for skim in xrange(0,len(skims)):
        print '\nStarting template:', skims[skim][0]
        
        inname = '/scratch5/ballen/hist/purity/simpletree3/Skim'+skims[skim][1]+'_Wlike.root'
        print 'Making template from:', inname
        generator = TemplateGenerator(skims[skim][2], var[2], inname)
        generator.setTemplateBinning(40, 0., 0.02)
        
        print 'Applying selection:', sel
        print selections[sel][skim], '\n'
        tempH = generator.makeTemplate(sel, selections[sel][skim])
        
        tempname = 'template_'+skims[skim][0]+'_'+sel
        temp = RooDataHist(tempname, tempname, RooArgList(var[0]), tempH)
        
        # temp.Write()
        templates.append(temp)
        
        canvas = TCanvas()
        frame = var[0].frame()
        temp.plotOn(frame)
        
        frame.SetTitle(skims[skim][3])

        frame.Draw()
        
        canvas.SaveAs(tempname+'.pdf')


    # Fit for data
    dataTitle = "Photon Purity in SingleMuon DataSet"
    # (dataReal,dataFake) = FitTemplates("purity_data_"+sel, var[0], var[1], templates[3], templates[0], templates[1])
    dataPurity = FitTemplates("purity_data_"+sel, dataTitle,  var[0], var[1], templates[3], templates[0], templates[1])
    
    # Fit for MC
    mcTitle = "Photon Purity in WJets Monte Carlo"
    # (mcReal, mcFake) = FitTemplates("purity_mc_"+sel, var[0], var[1], templates[4], templates[0], templates[2])
    mcPurity = FitTemplates("purity_mc_"+sel, mcTitle, var[0], var[1], templates[4], templates[0], templates[2])

    # Fit for MC truth
    truthTitle = "Photon Purity in WJets MC Truth"
    # (truthReal, truthFake) = FitTemplates("purity_mcTruth_"+sel, var[0], var[1], templates[4], templates[5], templates[6])
    truthPurity = FitTemplates("purity_mcTruth_"+sel, truthTitle, var[0], var[1], templates[4], templates[5], templates[6])

    # Calculate purity and print results
    '''
    print "Number of Real photons passing selection in data:", dataReal
    print "Number of Fake photons passing selection in data:", dataFake
    dataPurity = float(dataReal) / float(dataReal + dataFake)
    '''
    print "Purity of Photons in Data is:", dataPurity
    purities[0].append(dataPurity)

    '''
    print "Number of Real photons passing selection in mc:", mcReal
    print "Number of Fake photons passing selection in mc:", mcFake
    mcPurity = float(mcReal) / float(mcReal + mcFake)
    '''
    print "Purity of Photons in MC is:", mcPurity
    purities[1].append(mcPurity)

    '''
    print "Number of Real photons passing selection in mcTruth:", truthReal
    print "Number of Fake photons passing selection in mcTruth:", truthFake
    truthPurity = float(truthReal) / float(truthReal + truthFake)
    '''
    print "Purity of Photons in truthFit is:", truthPurity
    purities[2].append(truthPurity)
    
    truthReal = templates[5].sumEntries(varName+' < '+str(var[1]))
    truthTotal = templates[4].sumEntries(varName+' < '+str(var[1]))
    print "Number of Real photons passing selection in mcTruth:", truthReal
    print "Number of Total photons passing selection in mcTruth:", truthTotal
    truthPurity = float(truthReal) / float(truthTotal)
    print "Purity of Photons in mcTruth is:", truthPurity
    purities[3].append(truthPurity)

# Plot purities
print "Purity of Photons in Data is:", purities[0]
print "Purity of Photons in MC is:", purities[1]
print "Purity of Photons in truthFit is:", purities[2]
print "Purity of Photons in mcTruth is:", purities[3]

