#!/usr/bin/env python

import os
import sys
import shutil
from pprint import pprint
from array import array
from subprocess import Popen, PIPE
import selections as s
from ROOT import *
gROOT.SetBatch(True)

### take inputs and make sure they match a selection
source = sys.argv[1]
loc = sys.argv[2]
pid = sys.argv[3]
chiso = sys.argv[4]
pt = sys.argv[5]
met = sys.argv[6]

inputKey = loc+'_'+pid+'_ChIso'+chiso+'_PhotonPt'+pt+'_Met'+met

chIsoSel = '(1)'
for chisosel in s.ChIsoSbSels:
    if 'ChIso'+chiso == chisosel[0]:
        chIsoSel = chisosel[1]
if chIsoSel == '(1)':
    print 'Inputted chIso range', chiso, 'not found!'
    print 'Not applying any chIso selection!'
 
ptSel = '(1)'
for ptsel in s.PhotonPtSels:
    if 'PhotonPt'+pt == ptsel[0]:
        ptSel = ptsel[1]
if ptSel == '(1)':
    print 'Inputted pt range', pt, 'not found!'
    print 'Not applying any pt selection!'

metSel = '(1)'
for metsel in s.MetSels:
    if 'Met'+met == metsel[0]:
        metSel = metsel[1]
if metSel == '(1)':
    print 'Inputted met range', met, 'not found!'
    print 'Not applying any met selection!'

### Directory stuff so that results are saved and such
varName = 'chiso'
versDir = os.path.join('/scratch5/ballen/hist/purity',s.Version,varName)
plotDir = os.path.join(versDir,'Plots','SignalContam',source,inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)
else:
    shutil.rmtree(plotDir)
    os.makedirs(plotDir)

### Get ChIso Curve for true photons
macroDir = os.environ['PURITY']
isoPath = os.path.join(macroDir,'plotiso.py')
plotiso = Popen( ['python',isoPath,source,loc,pid,chiso,pt,met],stdout=PIPE,stderr=PIPE,cwd=macroDir)
isoOut = plotiso.communicate()
if not isoOut[1] == "":
    print isoOut[1] 
isoFile = TFile(os.path.join(plotDir,'chiso_'+inputKey+'.root'))

splits = chiso.split("to")
minIso = float(splits[0])/10.0
maxIso = float(splits[1])/10.0

labels = [ 'rawmc', 'scaledmc' ] 
isoHists = []
for label in labels:
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

    sigFrac = isoHist.Integral(1,3)
    print "Fraction in signal:", sigFrac
    isoHists.append( (isoHist, sbFrac, sigFrac) )

### Get Purity (first time)
varName = 'sieie'
var = s.Variables[varName]
varBins = False
versDir = os.path.join('/scratch5/ballen/hist/purity',s.Version,varName)
skimDir  = s.config.skimDir
plotDir = os.path.join(versDir,'Plots','SignalContam',source,inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

pids = pid.split('_')
if len(pids) > 1:
    pid = pids[0]
    extras = pids[2:]
elif len(pids) == 1:
    pid = pids[0]
    extras = []

baseSel = s.SigmaIetaIetaSels[loc][pid]+' && '+ptSel+' && '+metSel
if 'pixel' in extras:
    baseSel = baseSel+' && '+s.pixelVetoCut
if 'monoph' in extras:
    baseSel = baseSel+' && '+s.monophIdCut

sigSel = baseSel+' && '+s.chIsoSels[loc][pid]
sbSel = baseSel+' && '+chIsoSel
truthSel =  '(photons.matchedGen == -22)'

# fit, signal, contamination, background, contamination scaled, background
skims = s.Measurement[source]
sels = [ sigSel
         ,sigSel+' && '+truthSel
         ,sbSel+' && '+truthSel
         ,sbSel
         ,sbSel+' && '+truthSel
         ,sbSel
         ]

# get initial templates
print "\n\n##############################\n######## Doing initial skims ########\n##############################\n\n"
initialHists = []
initialTemplates = []
for skim, sel in zip(skims,sels):
    hist = s.HistExtractor(var[0],var[2][loc],skim,sel,skimDir,varBins)
    initialHists.append(hist)
    template = s.HistToTemplate(hist,var[2][loc],skim,"v0_"+inputKey,plotDir)
    initialTemplates.append(template)

print "\n\n##############################\n######## Doing initial purity calculation ########\n##############################\n\n"
### Get nominal value
nominalHists = initialHists[:4]
nominalTemplates = initialTemplates[:4]
nominalSkims = skims[:4]
nominalRatio = float(isoHists[0][1]) / float(isoHists[0][2])
nominalDir = os.path.join(plotDir,'nominal')
if not os.path.exists(nominalDir):
    os.makedirs(nominalDir)

nominalPurity = s.SignalSubtraction(nominalSkims,nominalHists,nominalTemplates,nominalRatio,varName,var[2][loc],var[1][loc][pid],inputKey,nominalDir)

print "\n\n##############################\n######## Doing ch iso dist uncertainty ########\n##############################\n\n"
### Get chiso dist uncertainty
scaledHists = initialHists[:2] + initialHists[4:]
scaledTemplates = initialTemplates[:2] + initialTemplates[4:]
scaledSkims = skims[:2] + skims[4:]
scaledDir = os.path.join(plotDir,'scaled')
if not os.path.exists(scaledDir):
    os.makedirs(scaledDir)
scaledRatio = float(isoHists[1][1]) / float(isoHists[1][2])

scaledPurity = s.SignalSubtraction(scaledSkims,scaledHists,scaledTemplates,scaledRatio,varName,var[2][loc],var[1][loc][pid],inputKey,scaledDir)
# scaledUncertainty = abs( nominalPurity[0][0] - scaledPurity[0][0] )
scaledUncertainty = abs( nominalPurity[0] - scaledPurity[0] )
scaledUncYield = abs( nominalPurity[2] - scaledPurity[2] )

print "\n\n##############################\n######## Doing background stat uncertainty ########\n##############################\n\n"
### Get background stat uncertainty
toyPlot = TH1F("toyplot","Impurity Difference from Background Template Toys", 100, -5, 5)
toyPlotYield = TH1F("toyplotyield","True Photon Yield Difference from Background Template Toys", 100, -5000, 5000)
toySkims = skims[:4]
toysDir = os.path.join(plotDir,'toys')
if not os.path.exists(toysDir):
    os.makedirs(toysDir)
eventsToGenerate = initialTemplates[3].sumEntries()
varToGen = RooArgSet(var[2][loc][0])
toyGenerator = RooHistPdf('bkg', 'bkg', varToGen, initialTemplates[3])
#print "Expect events to generate:", toyGenerator.expectedEvents(varToGen)
#toyGenSpec = toyGenerator.prepareMultiGen(varToGen) #,eventsToGenerate)

tempCanvas = TCanvas()
tempFrame = var[2][loc][0].frame()
toyGenerator.plotOn(tempFrame)
tempFrame.Draw()
tempName = os.path.join(toysDir, 'GenDist')
tempCanvas.SaveAs(tempName+'.pdf')
tempCanvas.SaveAs(tempName+'.png')
tempCanvas.SaveAs(tempName+'.C')
 
for iToy in range(1,101):
    print "\n###############\n#### Toy "+str(iToy)+" ####\n###############\n"
    toyHists = initialHists[:3]
    toyTemplates = initialTemplates[:3]
    
    toyDir = os.path.join(toysDir, 'toy'+str(iToy))
    if not os.path.exists(toyDir):
        os.makedirs(toyDir)

    tempTemplate = toyGenerator.generateBinned(varToGen,eventsToGenerate)
    tempCanvas = TCanvas()
    tempFrame = var[2][loc][0].frame()
    tempTemplate.plotOn(tempFrame)
    tempFrame.Draw()
    tempName = os.path.join(toyDir, 'toydist')
    tempCanvas.SaveAs(tempName+'.pdf')
    tempCanvas.SaveAs(tempName+'.png')
    tempCanvas.SaveAs(tempName+'.C')

    toyData = RooDataSet.Class().DynamicCast(RooAbsData.Class(), tempTemplate)
    toyHist = toyData.createHistogram("toyhist", var[2][loc][0], RooFit.Binning(var[2][loc][1], var[2][loc][0].getMin(), var[2][loc][0].getMax() ) )
    toyHists.append(toyHist)

    toyTemplate = s.HistToTemplate(toyHist,var[2][loc],toySkims[3],"v0_"+inputKey,toyDir)
    toyTemplates.append(toyTemplate)

    toyPurity = s.SignalSubtraction(toySkims,toyHists,toyTemplates,nominalRatio,varName,var[2][loc],var[1][loc][pid],inputKey,toyDir)
    # purityDiff = toyPurity[0][0] - nominalPurity[0][0]
    purityDiff = toyPurity[0] - nominalPurity[0]
    print "Purity diff is:", purityDiff
    toyPlot.Fill(purityDiff)

    yieldDiff = toyPurity[2] - nominalPurity[2]
    print "Yield diff is:", yieldDiff
    toyPlotYield.Fill(yieldDiff)

bkgdUncertainty = toyPlot.GetStdDev()
bkgdUncYield = toyPlotYield.GetStdDev()
toyPlot.GetXaxis().SetTitle("Impurity Difference")
toyPlot.GetYaxis().SetTitle("# of Toys")

toyPlot.SetLineWidth(3)
                    
toyPlot.GetXaxis().SetLabelSize(0.045)
toyPlot.GetXaxis().SetTitleSize(0.045)
toyPlot.GetYaxis().SetLabelSize(0.045)
toyPlot.GetYaxis().SetTitleSize(0.045)


toyPlotName = os.path.join(toysDir, 'toyplot_'+inputKey)
toyCanvas = TCanvas()
toyPlot.Draw()
toyCanvas.SaveAs(toyPlotName+'.pdf')
toyCanvas.SaveAs(toyPlotName+'.png')
toyCanvas.SaveAs(toyPlotName+'.C')

print "\n\n##############################\n######## Doing signal shape uncertainty ########\n##############################\n\n"
### Get signal shape uncertainty
twobinDir = os.path.join(plotDir,'twobin')
if not os.path.exists(twobinDir):
    os.makedirs(twobinDir)
twobinSkims = skims[:4]
twobinHists = []
twobinTemplates = []
nbins = len(var[2][loc][2])-1
for iH, hist in enumerate(initialHists[:4]):
    newHist = hist.Clone("newhist"+str(iH))
    twobinHist = newHist.Rebin(nbins, "twobinhist"+str(iH), array('d', var[2][loc][2]))
    twobinHists.append(twobinHist)
    template = s.HistToTemplate(twobinHist,var[2][loc],twobinSkims[iH],"v0_"+inputKey,twobinDir)
    twobinTemplates.append(template)

twobinPurity = s.SignalSubtraction(twobinSkims,twobinHists,twobinTemplates,nominalRatio,varName,var[2][loc],var[1][loc][pid],inputKey,twobinDir)
# twobinUncertainty = abs( nominalPurity[0][0] - twobinPurity[0][0])
twobinUncertainty = abs( nominalPurity[0] - twobinPurity[0])
twobinUncYield = abs( nominalPurity[2] - twobinPurity[2])


print "\n\n##############################\n######## Showing results ########\n##############################\n\n"
print "Nominal purity is:", nominalPurity[0]
print "Method uncertainty is:", scaledUncertainty
print "Signal shape uncertainty is:", twobinUncertainty
print "Background stat uncertainty is:", bkgdUncertainty
totalUncertainty = ( (scaledUncertainty)**2 + (twobinUncertainty)**2 + (bkgdUncertainty)**2 )**(0.5)
totalUncYield = ( (scaledUncYield)**2 + (twobinUncYield)**2 + (bkgdUncYield)**2 )**(0.5)

print "Total uncertainty is:", totalUncertainty

outFile = file(plotDir + '/results.out', 'w')

outFile.write( "# of real photons is: "+str(nominalPurity[2])+'\n' )
outFile.write( "Method unc yield is: "+str(scaledUncYield)+'\n' ) 
outFile.write( "Signal shape unc yield is: "+str(twobinUncYield)+'\n' ) 
outFile.write( "Background stat unc yield is: "+str(bkgdUncYield)+'\n' )
outFile.write( "Total unc yield is: "+str(totalUncYield)+'\n' )

outFile.write( "Nominal purity is: "+str(nominalPurity[0])+'\n' )
outFile.write( "Method uncertainty is: "+str(scaledUncertainty)+'\n' ) 
outFile.write( "Signal shape uncertainty is: "+str(twobinUncertainty)+'\n' ) 
outFile.write( "Background stat uncertainty is: "+str(bkgdUncertainty)+'\n' )
outFile.write( "Total uncertainty is: "+str(totalUncertainty)+'\n' )

outFile.close()
