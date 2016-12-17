#!/usr/bin/env python

import os
import sys
from pprint import pprint
from array import array
from subprocess import Popen, PIPE
import selections as s
from copy import deepcopy
from ROOT import *
gROOT.SetBatch(True)

### take inputs and make sure they match a selection
loc = sys.argv[1]
pid = sys.argv[2]
pt = sys.argv[3]
met = sys.argv[4]

try:
    era = sys.argv[5]
except:
    era = 'Spring15'

inputKey = era+'_'+loc+'_'+pid+'_PhotonPt'+pt+'_Met'+met
 
try:
    ptSel = s.PhotonPtSels['PhotonPt'+pt]
except KeyError:
    print 'Inputted pt range', pt, 'not found!'
    print 'Not applying any pt selection!'
    ptSel = '(1)'

try:
    metSel = s.MetSels['Met'+met]
except KeyError:
    print 'Inputted met range', met, 'not found!'
    print 'Not applying any met selection!'
    metSel = '(1)'

### Directory stuff so that results are saved and such
versDir = os.path.join('/data/t3home000/ballen/hist/purity',s.Version)
plotDir = os.path.join(versDir,inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

### Get ChIso Curve for true photons
isoPath = os.path.join(s.thisdir,'plotiso.py')
plotiso = Popen( ['python',isoPath,loc,pid,pt,met,era],stdout=PIPE,stderr=PIPE,cwd=s.thisdir)
isoOut = plotiso.communicate()
if not isoOut[1] == "":
    print isoOut[1] 
isoFile = TFile(os.path.join(plotDir,'chiso_'+inputKey+'.root'))

labels = [ 'rawmc', 'scaledmc' ] 
isoHists = {}

for chkey in s.ChIsoSbSels:
    isoHists[chkey] = []
    splits = chkey.strip('ChIso').split('to')
    minIso = float(splits[0])/10.0
    maxIso = float(splits[1])/10.0

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
        isoHists[chkey].append( (isoHist, sbFrac, sigFrac) )

### Get Purity (first time)
varName = 'sieie'
var = s.Variables[varName]
varBins = False
skimDir  = s.config.skimDir

pids = pid.split('-')
if len(pids) > 1:
    pid = pids[0]
    extras = pids[1:]
elif len(pids) == 1:
    pid = pids[0]
    extras = []

baseSel = 'jets.pt[0] > 100. && ' + ptSel + ' && ' + metSel + ' && ' + s.SigmaIetaIetaSels[era][loc][pid]
if 'pixel' in extras:
    baseSel = baseSel+' && '+s.pixelVetoCut
if 'monoph' in extras:
    baseSel = baseSel+' && '+s.monophIdCut

ChIsoNear = 'ChIso35to50'
ChIsoNominal = 'ChIso50to75'
ChIsoFar = 'ChIso75to90'

sigSel = baseSel+' && '+s.chIsoSels[era][loc][pid]
sbSel = baseSel + ' && ' + s.ChIsoSbSels[ChIsoNominal]
sbSelNear = baseSel + ' && ' + s.ChIsoSbSels[ChIsoNear]
sbSelFar  = baseSel + ' && ' + s.ChIsoSbSels[ChIsoFar]
truthSel =  '(photons.matchedGen == -22)'

# fit, signal, contamination, background, contamination scaled, background
skims = s.Measurement['bambu']
sels = [  sigSel
         ,sigSel + ' && ' + truthSel
         ,sbSel + ' && ' + truthSel
         ,sbSel
         ,sbSelNear + ' && ' + truthSel
         ,sbSelNear
         ,sbSelFar + ' && ' + truthSel
         ,sbSelFar
         ]

if 'worst' in extras:
    sels[0] = sels[0] + ' && ' + s.chWorstIsoSels[era][loc][pid]
    sels[1] = sels[1] + ' && ' + s.chWorstIsoSels[era][loc][pid]


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
nominalHists = deepcopy(initialHists[:4])
nominalTemplates = deepcopy(initialTemplates[:4])
nominalSkims = skims[:4]
nominalRatio = float(isoHists[ChIsoNominal][0][1]) / float(isoHists[ChIsoNominal][0][2])
nominalDir = os.path.join(plotDir,'nominal')
if not os.path.exists(nominalDir):
    os.makedirs(nominalDir)

nominalPurity = s.SignalSubtraction(nominalSkims,nominalHists,nominalTemplates,nominalRatio,varName,var[2][loc],var[1][era][loc][pid],inputKey,nominalDir)

print "\n\n##############################\n######## Doing ch iso sideband uncertainty ########\n##############################\n\n"
### Get chiso sideband near uncertainty
nearHists = deepcopy(initialHists[:2] + initialHists[4:6])
nearTemplates = deepcopy(initialTemplates[:2] + initialTemplates[4:6])
nearSkims = skims[:4]
nearRatio = float(isoHists[ChIsoNear][0][1]) / float(isoHists[ChIsoNear][0][2])
nearDir = os.path.join(plotDir,'near')
if not os.path.exists(nearDir):
    os.makedirs(nearDir)

nearPurity = s.SignalSubtraction(nearSkims,nearHists,nearTemplates,nearRatio,varName,var[2][loc],var[1][era][loc][pid],inputKey,nearDir)

### Get chiso sideband far uncertainty
farHists = deepcopy(initialHists[:2] + initialHists[6:])
farTemplates = deepcopy(initialTemplates[:2] + initialTemplates[6:])
farSkims = skims[:4]
farRatio = float(isoHists[ChIsoFar][0][1]) / float(isoHists[ChIsoFar][0][2])
farDir = os.path.join(plotDir,'far')
if not os.path.exists(farDir):
    os.makedirs(farDir)

farPurity = s.SignalSubtraction(farSkims,farHists,farTemplates,farRatio,varName,var[2][loc],var[1][era][loc][pid],inputKey,farDir)
sidebandUncertainty = max( abs( nominalPurity[0] - nearPurity[0] ), abs( nominalPurity[0] - farPurity[0] ) )
sidebandUncYield = max( abs( nominalPurity[2] - nearPurity[2] ), abs( nominalPurity[2] - farPurity[2] ) )


print "\n\n##############################\n######## Doing ch iso dist uncertainty ########\n##############################\n\n"
### Get chiso dist uncertainty
scaledHists = deepcopy(initialHists[:4])
scaledTemplates = deepcopy(initialTemplates[:4])
scaledSkims = skims[:4]
scaledDir = os.path.join(plotDir,'scaled')
if not os.path.exists(scaledDir):
    os.makedirs(scaledDir)
scaledRatio = float(isoHists[ChIsoNominal][1][1]) / float(isoHists[ChIsoNominal][1][2])

scaledPurity = s.SignalSubtraction(scaledSkims,scaledHists,scaledTemplates,scaledRatio,varName,var[2][loc],var[1][era][loc][pid],inputKey,scaledDir)
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
    toyHists = deepcopy(initialHists[:3])
    toyTemplates = deepcopy(initialTemplates[:3])
    
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

    toyPurity = s.SignalSubtraction(toySkims,toyHists,toyTemplates,nominalRatio,varName,var[2][loc],var[1][era][loc][pid],inputKey,toyDir)
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

twobinPurity = s.SignalSubtraction(twobinSkims,twobinHists,twobinTemplates,nominalRatio,varName,var[2][loc],var[1][era][loc][pid],inputKey,twobinDir)
twobinUncertainty = abs( nominalPurity[0] - twobinPurity[0])
twobinUncYield = abs( nominalPurity[2] - twobinPurity[2])

print "\n\n##############################\n######## Showing results ########\n##############################\n\n"
print "Nominal purity is:", nominalPurity[0]
print "Sideband uncertainty is:", sidebandUncertainty
print "Method uncertainty is:", scaledUncertainty
print "Signal shape uncertainty is:", twobinUncertainty
print "Background stat uncertainty is:", bkgdUncertainty
totalUncertainty = ( (sidebandUncertainty**2) + (scaledUncertainty)**2 + (twobinUncertainty)**2 + (bkgdUncertainty)**2 )**(0.5)
totalUncYield = ( (sidebandUncYield)**2 + (scaledUncYield)**2 + (twobinUncYield)**2 + (bkgdUncYield)**2 )**(0.5)

print "Total uncertainty is:", totalUncertainty

outFile = file(plotDir + '/results.out', 'w')

for hist in initialHists[:]:
    outFile.write('%s has %f events \n' % (hist.GetName(), hist.Integral()))

outFile.write( "# of real photons is: "+str(nominalPurity[2])+'\n' )
outFile.write( "Sideband unc yield is: "+str(sidebandUncYield)+'\n' )
outFile.write( "Method unc yield is: "+str(scaledUncYield)+'\n' ) 
outFile.write( "Signal shape unc yield is: "+str(twobinUncYield)+'\n' ) 
outFile.write( "Background stat unc yield is: "+str(bkgdUncYield)+'\n' )
outFile.write( "Total unc yield is: "+str(totalUncYield)+'\n' )

outFile.write( "Nominal purity is: "+str(nominalPurity[0])+'\n' )
outFile.write( "Sideband uncertainty is: "+str(sidebandUncertainty)+'\n' )
outFile.write( "Method uncertainty is: "+str(scaledUncertainty)+'\n' ) 
outFile.write( "Signal shape uncertainty is: "+str(twobinUncertainty)+'\n' ) 
outFile.write( "Background stat uncertainty is: "+str(bkgdUncertainty)+'\n' )
outFile.write( "Total uncertainty is: "+str(totalUncertainty)+'\n' )

outFile.close()
