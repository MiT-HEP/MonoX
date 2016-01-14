import os
import sys
from pprint import pprint
from array import array
from subprocess import Popen, PIPE
from selections import Variables, Version, Measurement, Selections, SigmaIetaIetaSels, ChIsoSbSels, PhotonPtSels, MetSels, cutMatchedToReal, HistExtractor, HistToTemplate, PlotNames,FitTemplates, SignalSubtraction
from ROOT import *
gROOT.SetBatch(True)

### take inputs and make sure they match a selection
loc = sys.argv[1]
pid = sys.argv[2]
chiso = sys.argv[3]
pt = sys.argv[4]
met = sys.argv[5]

inputKey = loc+'_'+pid+'_ChIso'+chiso+'_PhotonPt'+pt+'_Met'+met

try: 
    print Selections[inputKey]
except KeyError:
    print "Selection inputted from command line doesn't exist. Quitting!!!"
    print inputKey
    print "Available selections are: "
    for sel in Selections: print sel
    sys.exit()

chIsoSel = '(1)'
for chisosel in ChIsoSbSels:
    if 'ChIso'+chiso == chisosel[0]:
        chIsoSel = chisosel[1]
if chIsoSel == '(1)':
    print 'Inputted chIso range', chiso, 'not found!'
    print 'Not applying any chIso selection!'
 
ptSel = '(1)'
for ptsel in PhotonPtSels[0]:
    if 'PhotonPt'+pt == ptsel[0]:
        ptSel = ptsel[1]
if ptSel == '(1)':
    print 'Inputted pt range', pt, 'not found!'
    print 'Not applying any pt selection!'

metSel = '(1)'
for metsel in MetSels:
    if 'Met'+met == metsel[0]:
        metSel = metsel[1]
if metSel == '(1)':
    print 'Inputted met range', met, 'not found!'
    print 'Not applying any met selection!'

### Directory stuff so that results are saved and such
varName = 'chiso'
versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
# skimDir  = os.path.join(versDir,'Skims')
plotDir = os.path.join(versDir,'Plots','SignalContam',inputKey)
# plotDir = os.path.join(os.environ['CMSPLOTS'],'ST10','SignalContam',inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

### Get ChIso Curve for true photons
macroDir = os.environ['PURITY']
isoPath = os.path.join(macroDir,'plotiso.py')
plotiso = Popen( ['python',isoPath,loc,pid,chiso,pt,met],stdout=PIPE,stderr=PIPE,cwd=macroDir)
isoOut = plotiso.communicate()
if not isoOut[1] == "":
    print isoOut[1] 
isoFile = TFile(os.path.join(plotDir,'chiso_'+inputKey+'.root'))

splits = chiso.split("to")
minIso = float(splits[0])/10.0
maxIso = float(splits[1])/10.0

# dRcuts = [0.5,0.4,0.8]
labels = [ 'rawmc', 'scaledmc' ] 
isoHists = []
for label in labels:
    # isoHist = isoFile.Get("ShapeChIso_dR"+str(int(dR*10)))
    isoHist = isoFile.Get(label)
    
    ### Get Sig and Sideband fractions
    minIsoBin = 1
    maxIsoBin = isoHist.GetNbinsX()
    for bin in range(isoHist.GetNbinsX()+1):
        binLowEdge = isoHist.GetXaxis().GetBinLowEdge(bin)
        if (binLowEdge == minIso):
            minIsoBin = bin
        binUpEdge = isoHist.GetXaxis().GetBinUpEdge(bin)
        if (binUpEdge == maxIso):
            maxIsoBin = bin
    sbFrac = isoHist.Integral(minIsoBin,maxIsoBin)
    print "Fraction in sideband:", sbFrac

    # sigFrac = isoHist.GetBinContent(1)
    sigFrac = isoHist.Integral(1,3)
    print "Fraction in signal:", sigFrac
    isoHists.append( (isoHist, sbFrac, sigFrac) )

### Get Purity (first time)
varName = 'sieie'
var = Variables[varName]
varBins = False
versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
skimDir  = os.path.join(versDir,'Skims')
plotDir = os.path.join(versDir,'Plots','SignalContam',inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)
# plotDir = os.path.join(os.environ['CMSPLOTS'],'ST10','SignalContam',inputKey)
skimName = "Monophoton"

sbSkims = [ ('TempSidebandGJets','TempSignalGJets',kPhoton,r'Sideband Template from #gamma+jets MC')
            ,('TempSidebandGJetsScaled','TempSignalGJets',kPhoton,r'Scaled Sideband Template from #gamma+jets MC') ]

truthSel =  '( selPhotons.matchedGen == -22)'
sbSel = SigmaIetaIetaSels[loc][pid]+' && '+chIsoSel+' && '+truthSel+' && '+ptSel+' &&'+metSel

# fit, signal, contamination, background
skims = [ Measurement[skimName][1], Measurement[skimName][0], sbSkims[0], Measurement[skimName][5], sbSkims[1], Measurement[skimName][5] ]
sels = [ Selections[inputKey][1], Selections[inputKey][0], sbSel, Selections[inputKey][5], sbSel, Selections[inputKey][5] ]

# get initial templates

initialHists = []
initialTemplates = []
for skim, sel in zip(skims,sels):
    hist = HistExtractor(var[0],var[3][loc],skim,sel,skimDir,varBins)
    initialHists.append(hist)
    template = HistToTemplate(hist,var[3][loc],skim,"v0_"+inputKey,plotDir)
    initialTemplates.append(template)


### Get nominal value
nominalHists = initialHists[:4]
nominalTemplates = initialTemplates[:4]
nominalSkims = skims[:4]
nominalRatio = float(isoHists[0][1]) / float(isoHists[0][2])
nominalDir = os.path.join(plotDir,'nominal')
if not os.path.exists(nominalDir):
    os.makedirs(nominalDir)

nominalPurity = SignalSubtraction(nominalSkims,nominalHists,nominalTemplates,nominalRatio,varName,var[3][loc],var[4][loc][pid],inputKey,nominalDir)


### Get chiso dist uncertainty
scaledHists = initialHists[:2] + initialHists[4:]
scaledTemplates = initialTemplates[:2] + initialTemplates[4:]
scaledSkims = skims[:2] + skims[4:]
scaledDir = os.path.join(plotDir,'scaled')
if not os.path.exists(scaledDir):
    os.makedirs(scaledDir)
scaledRatio = float(isoHists[1][1]) / float(isoHists[1][2])

scaledPurity = SignalSubtraction(scaledSkims,scaledHists,scaledTemplates,scaledRatio,varName,var[3][loc],var[4][loc][pid],inputKey,scaledDir)
scaledUncertainty = abs( nominalPurity[0][0] - scaledPurity[0][0] )


### Get signal shape uncertainty
twobinDir = os.path.join(plotDir,'twobin')
if not os.path.exists(twobinDir):
    os.makedirs(twobinDir)
twobinSkims = skims[:4]
twobinHists = []
twobinTemplates = []
nbins = len(var[3][loc][2])-1
for iH, hist in enumerate(initialHists[:4]):
    newHist = hist.Clone("newhist"+str(iH))
    twobinHist = newHist.Rebin(nbins, "twobinhist"+str(iH), array('d', var[3][loc][2]))
    twobinHists.append(twobinHist)
    template = HistToTemplate(twobinHist,var[3][loc],twobinSkims[iH],"v0_"+inputKey,twobinDir)
    twobinTemplates.append(template)

twobinPurity = SignalSubtraction(twobinSkims,twobinHists,twobinTemplates,nominalRatio,varName,var[3][loc],var[4][loc][pid],inputKey,twobinDir)
twobinUncertainty = abs( nominalPurity[0][0] - twobinPurity[0][0])


### Get background stat uncertainty
toyPlot = TH1F("toyplot","Purity Difference from Background Template Toys", 200, -10.0, 10.0)
toySkims = skims[:4]
toysDir = os.path.join(plotDir,'toys')
if not os.path.exists(toysDir):
    os.makedirs(toysDir)
eventsToGenerate = initialTemplates[3].sumEntries()
varToGen = RooArgSet(var[3][loc][0])
toyGenerator = RooHistPdf('bkg', 'bkg', varToGen, initialTemplates[3])
for iToy in range(1,1001):
    toyHists = initialHists[:3]
    toyTemplates = initialTemplates[:3]
    
    toyDir = os.path.join(toysDir, 'toy'+str(iToy))
    if not os.path.exists(toyDir):
        os.makedirs(toyDir)

    tempTemplate = toyGenerator.generate(varToGen,eventsToGenerate)
    toyData = RooDataSet.Class().DynamicCast(RooAbsData.Class(), tempTemplate)
    toyHist = toyData.createHistogram("toyhist", var[3][loc][0], RooFit.Binning(var[3][loc][1], var[3][loc][0].getMin(), var[3][loc][0].getMax() ) )
    toyHists.append(toyHist)

    toyTemplate = HistToTemplate(toyHist,var[3][loc],toySkims[3],"v0_"+inputKey,toyDir)
    toyTemplates.append(toyTemplate)

    toyPurity = SignalSubtraction(toySkims,toyHists,toyTemplates,nominalRatio,varName,var[3][loc],var[4][loc][pid],inputKey,toyDir)
    purityDiff = toyPurity[0][0] - nominalPurity[0][0]
    toyPlot.Fill(purityDiff)

bkgdUncertainty = toyPlot.GetStdDev()
toyPlot.GetXaxis().SetTitle("Purity Difference")
toyPlot.GetYaxis().SetTitle("# of Toys")
toyPlotName = os.path.join(toysDir, 'toyplot_'+inputKey)
toyPlot.SaveAs(toyPlotName+'.pdf')
toyPlot.SaveAs(toyPlotName+'.png')
toyPlot.SaveAs(toyPlotName+'.C')


print "\n\n\n"
print "Nominal purity is:", nominalPurity[0][0]
print "Method uncertainty is:", scaledUncertainty
print "Signal shape uncertainty is:", twobinUncertainty
print "Background stat uncertainty is:", bkgdUncertainty
totalUncertainty = ( (scaledUncertainty)**2 + (twobinUncertainty)**2 + (bkgdUncertainty)**2 )**(0.5)
print "Total uncertainty is:", totalUncertainty
