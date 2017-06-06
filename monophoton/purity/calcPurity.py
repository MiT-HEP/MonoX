#!/usr/bin/env python

import os
import sys
from pprint import pprint
from array import array
from subprocess import Popen, PIPE
import selections as s
import plotiso
from copy import deepcopy
import shutil
import time
import ROOT

ROOT.gErrorIgnoreLevel = ROOT.kWarning

from ROOT import *
gROOT.SetBatch(True)
gStyle.SetOptStat(0)
RooMsgService.instance().setGlobalKillBelow(RooFit.WARNING)

gROOT.LoadMacro('SignalSubtraction.cc+')

QUICKFIT = False # just run one main fit
FORCEHIST = True

### take inputs and make sure they match a selection
loc = sys.argv[1] # barrel, endcap
pid = sys.argv[2] # (loose|medium|tight)[-optional]
pt = sys.argv[3] # Inclusive, XtoY
met = sys.argv[4] # Inclusive, XtoY

try:
    era = sys.argv[5]
except:
    era = 'Spring15'

inputKey = era+'_'+loc+'_'+pid+'_PhotonPt'+pt+'_Met'+met

if loc == 'barrel':
    iloc = 0
elif loc == 'endcap':
    iloc = 1
 
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
versDir = s.versionDir
plotDir = os.path.join(versDir, inputKey)
histDir = os.path.join(versDir, inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)
if not os.path.exists(histDir):
    os.makedirs(histDir)

if not QUICKFIT:
    print ''
    print 'Generating chIso histograms for SR-CR extrapolation..'
    print ''

    ### Get ChIso Curve for true photons
    plotiso.plotiso(loc, pid, pt, met, era)
    
    isoFile = TFile(os.path.join(versDir, inputKey, 'chiso_'+inputKey+'.root'))
    
    isoHists = {}
    
    for chkey in s.ChIsoSbSels:
        isoHists[chkey] = []
        splits = chkey.strip('ChIso').split('to')
        minIso = float(splits[0])/10.0
        maxIso = float(splits[1])/10.0
    
        for label in ['rawmc', 'scaledmc']:
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

            # NOTE: Taking the first bin as the signal fraction
            sigFrac = isoHist.GetBinContent(1)

            isoHists[chkey].append( (isoHist, sbFrac, sigFrac) )


### Get Purity (first time)
varName = 'sieie'
var = s.Variables[varName]
roofitVar = s.MakeRooRealVar(varName, iloc)

pids = pid.split('-')
if len(pids) > 1:
    pid = pids[0]
    extras = pids[1:]
elif len(pids) == 1:
    pid = pids[0]
    extras = []

# high-pt jet + met + photon pt + photon hOverE/NHIso/PhIso
baseSel = 'jets.pt_[0] > 100. && ' + ptSel + ' && ' + metSel + ' && ' + s.SigmaIetaIetaSels[era][loc][pid]
if 'pixel' in extras:
    baseSel = baseSel+' && '+s.pixelVetoCut
if 'monoph' in extras:
    baseSel = baseSel+' && '+s.monophIdCut

ChIsoNear = 'ChIso35to50'
ChIsoNominal = 'ChIso50to75'
ChIsoFar = 'ChIso75to90'

sigSel = s.chIsoSels[era][loc][pid]
sbSel = s.ChIsoSbSels[ChIsoNominal]
sbSelNear = s.ChIsoSbSels[ChIsoNear]
sbSelFar  = s.ChIsoSbSels[ChIsoFar]
truthSel =  '(photons.matchedGenId[0] == -22)'

# fit, signal, contamination, background, contamination scaled, background
skims = s.Measurement['bambu']

# get initial templates
print '\n'
print '#####################################'
print '######## Doing initial skims ########'
print '#####################################'
print '\n'

if not os.path.exists(os.path.join(histDir, 'initialHists.root')) or FORCEHIST:
    extractors = {
        'sphData': s.HistExtractor('sphData', s.sphData, var[0]),
        'gjetsMc': s.HistExtractor('gjetsMc', s.gjetsMc, var[0])
    }
    
    start = time.time()
    extractors['sphData'].baseSel = baseSel
    
    start = time.time()
    extractors['gjetsMc'].baseSel = baseSel + ' && ' + truthSel
    
    extractors['sphData'].categories.append((skims[0][0], skims[0][2], sigSel))
    extractors['gjetsMc'].categories.append((skims[1][0], skims[1][2], sigSel))
    extractors['gjetsMc'].categories.append((skims[2][0], skims[2][2], sbSel))
    extractors['sphData'].categories.append((skims[3][0], skims[3][2], sbSel))
    extractors['gjetsMc'].categories.append((skims[4][0], skims[4][2], sbSelNear))
    extractors['sphData'].categories.append((skims[5][0], skims[5][2], sbSelNear))
    extractors['gjetsMc'].categories.append((skims[6][0], skims[6][2], sbSelFar))
    extractors['sphData'].categories.append((skims[7][0], skims[7][2], sbSelFar))
    
    #if 'worst' in extras:
    #    sels[0] = sels[0] + ' && ' + s.chWorstIsoSels[era][loc][pid]
    #    sels[1] = sels[1] + ' && ' + s.chWorstIsoSels[era][loc][pid]
    #elif 'max' in extras:
    #    sels[0] = sels[0] + ' && ' + s.chIsoMaxSels[era][loc][pid]
    #    sels[1] = sels[1] + ' && ' + s.chIsoMaxSels[era][loc][pid]

    histFile = TFile.Open(os.path.join(histDir, 'initialHists.root'), 'recreate')
    
    start = time.time()
    dataTemplates = extractors['sphData'].extract(var[3][iloc], histFile)
    print 'Took', (time.time() - start), 'seconds to extract data templates'
    
    start = time.time()
    mcTemplates = extractors['gjetsMc'].extract(var[3][iloc], histFile)
    print 'Took', (time.time() - start), 'seconds to extract MC templates'
    
    initialHists = [
        dataTemplates[0],
        mcTemplates[0],
        mcTemplates[1],
        dataTemplates[1],
        mcTemplates[2],
        dataTemplates[2],
        mcTemplates[3],
        dataTemplates[3]
    ]
    
    for hist in initialHists:
        hist.SetDirectory(histFile)
        
    histFile.Write()

else:
    histFile = TFile.Open(os.path.join(histDir, 'initialHists.root'))

    initialHists = [
        histFile.Get(skims[0][0]),
        histFile.Get(skims[1][0]),
        histFile.Get(skims[2][0]),
        histFile.Get(skims[3][0]),
        histFile.Get(skims[4][0]),
        histFile.Get(skims[5][0]),
        histFile.Get(skims[6][0]),
        histFile.Get(skims[7][0])
    ]

initialTemplates = []
for hist in initialHists:
    template = s.HistToTemplate(hist,roofitVar,"v0_"+inputKey,plotDir)
    initialTemplates.append(template)

canvas = TCanvas()

ssfitter = SSFitter.singleton()
# allowing the bin edge to be lower than the actual cut (makes the purity higher!)
cutBin = initialHists[0].FindBin(var[1][era][loc][pid])

def runSSFit(datasb, mcsb, sbRatio, name = '', pdir = plotDir):
    ssfitter.initialize(initialHists[0], initialHists[1], datasb, mcsb, sbRatio)
    ssfitter.fit()

    purity = ssfitter.getPurity(cutBin)
    nReal = ssfitter.getNsig(cutBin)
    nFake = ssfitter.getNbkg(cutBin)
    aveSig = s.StatUncert(nReal, nFake)

    if name:
        ssfitter.plotOn(canvas)
        text = TLatex()
        text.DrawLatexNDC(0.525,0.8,"Purity: "+str(round(purity,3))+'#pm'+str(round(aveSig,3))) 

        canvas.SetLogy(False)
        canvas.Print(pdir + '/ssfit_' + name + '.png')
        canvas.Print(pdir + '/ssfit_' + name + '.pdf')
        canvas.SetLogy(True)
        canvas.Print(pdir + '/ssfit_' + name + '_log.png')
        canvas.Print(pdir + '/ssfit_' + name + '_log.pdf')

    return (purity, aveSig, nReal, nFake)


print '\n'
print '##################################################'
print '######## Doing initial purity calculation ########'
print '##################################################'
print '\n'

### Get nominal value
#nominalTemplates = deepcopy(initialTemplates[:4])
#nominalDir = os.path.join(plotDir,'nominal')
#if not os.path.exists(nominalDir):
#    os.makedirs(nominalDir)

#nominalHists = deepcopy(initialHists[:4])
#nominalSkims = skims[:4]
# nominal sideband, nominal (MC raw) iso distribution, SB bin / SR bin

if QUICKFIT:
    # no signal subtraction
    nominalPurity = runSSFit(initialHists[3], initialHists[2], 0., 'nominal')
    print "Purity: %f +- %f" % nominalPurity[0]
    sys.exit(0)

nominalRatio = float(isoHists[ChIsoNominal][0][1]) / float(isoHists[ChIsoNominal][0][2])

nominalPurity = runSSFit(initialHists[3], initialHists[2], nominalRatio, 'nominal')

#nominalPurity = s.SignalSubtraction(nominalSkims,nominalHists,nominalTemplates,nominalRatio,roofitVar,var[1][era][loc][pid],inputKey,nominalDir)

print '\n'
print '###################################################'
print '######## Doing ch iso sideband uncertainty ########'
print '###################################################'
print '\n'

### Get chiso sideband near uncertainty
#nearHists = deepcopy(initialHists[:2] + initialHists[4:6])
#nearTemplates = deepcopy(initialTemplates[:2] + initialTemplates[4:6])
#nearSkims = skims[:4]
#nearDir = os.path.join(plotDir,'near')
#if not os.path.exists(nearDir):
#    os.makedirs(nearDir)

nearRatio = float(isoHists[ChIsoNear][0][1]) / float(isoHists[ChIsoNear][0][2])

nearPurity = runSSFit(initialHists[5], initialHists[4], nearRatio, 'near')

#nearPurity = s.SignalSubtraction(nearSkims,nearHists,nearTemplates,nearRatio,roofitVar,var[1][era][loc][pid],inputKey,nearDir)

### Get chiso sideband far uncertainty
#farHists = deepcopy(initialHists[:2] + initialHists[6:])
#farTemplates = deepcopy(initialTemplates[:2] + initialTemplates[6:])
#farSkims = skims[:4]
#farDir = os.path.join(plotDir,'far')
#if not os.path.exists(farDir):
#    os.makedirs(farDir)

farRatio = float(isoHists[ChIsoFar][0][1]) / float(isoHists[ChIsoFar][0][2])

farPurity = runSSFit(initialHists[7], initialHists[6], farRatio, 'far')

#farPurity = s.SignalSubtraction(farSkims,farHists,farTemplates,farRatio,roofitVar,var[1][era][loc][pid],inputKey,farDir)

sidebandUncertainty = max( abs( nominalPurity[0] - nearPurity[0] ), abs( nominalPurity[0] - farPurity[0] ) )
sidebandUncYield = max( abs( nominalPurity[2] - nearPurity[2] ), abs( nominalPurity[2] - farPurity[2] ) )

print sidebandUncertainty, sidebandUncYield

print '\n'
print '###############################################'
print '######## Doing ch iso dist uncertainty ########'
print '###############################################'
print '\n'

### Get chiso dist uncertainty
#scaledHists = deepcopy(initialHists[:4])
#scaledTemplates = deepcopy(initialTemplates[:4])
#scaledSkims = skims[:4]
#scaledDir = os.path.join(plotDir,'scaled')
#if not os.path.exists(scaledDir):
#    os.makedirs(scaledDir)

scaledRatio = float(isoHists[ChIsoNominal][1][1]) / float(isoHists[ChIsoNominal][1][2])

scaledPurity = runSSFit(initialHists[3], initialHists[2], scaledRatio, 'scaled')

scaledUncertainty = abs( nominalPurity[0] - scaledPurity[0] )
scaledUncYield = abs( nominalPurity[2] - scaledPurity[2] )

print '\n'
print '###################################################'
print '######## Doing background stat uncertainty ########'
print '###################################################'
print '\n'

#NTOYS = 100
NTOYS = 10

### Get background stat uncertainty
toyPlot = TH1F("toyplot","Impurity Difference from Background Template Toys", 100, -5, 5)
toyPlotYield = TH1F("toyplotyield","True Photon Yield Difference from Background Template Toys", 100, -5000, 5000)
#toySkims = skims[:4]
toysDir = os.path.join(plotDir,'toys')
if not os.path.exists(toysDir):
    os.makedirs(toysDir)

eventsToGenerate = initialTemplates[3].sumEntries()
toyGenerator = RooHistPdf('bkg', 'bkg', RooArgSet(roofitVar), initialTemplates[3])
#print "Expect events to generate:", toyGenerator.expectedEvents(roofitVar)
#toyGenSpec = toyGenerator.prepareMultiGen(roofitVar) #,eventsToGenerate)

tempCanvas = TCanvas()
tempFrame = roofitVar.frame()
toyGenerator.plotOn(tempFrame)
tempFrame.Draw()
tempName = os.path.join(toysDir, 'GenDist')
tempCanvas.SaveAs(tempName+'.pdf')
tempCanvas.SaveAs(tempName+'.png')
tempCanvas.SaveAs(tempName+'.C')
 
for iToy in range(1, NTOYS + 1):
    print "\n###############\n#### Toy "+str(iToy)+" ####\n###############\n"
#    toyHists = deepcopy(initialHists[:3])
#    toyTemplates = deepcopy(initialTemplates[:3])
    
#    toyDir = os.path.join(toysDir, 'toy'+str(iToy))
#    if not os.path.exists(toyDir):
#        os.makedirs(toyDir)

    tempTemplate = toyGenerator.generateBinned(RooArgSet(roofitVar),eventsToGenerate)
    tempCanvas = TCanvas()
    tempFrame = roofitVar.frame()
    tempTemplate.plotOn(tempFrame)
    tempFrame.Draw()
    tempName = os.path.join(toysDir, 'toy%d' % iToy)
    tempCanvas.SaveAs(tempName+'.pdf')
    tempCanvas.SaveAs(tempName+'.png')
    tempCanvas.SaveAs(tempName+'.C')

    toyData = RooDataSet.Class().DynamicCast(RooAbsData.Class(), tempTemplate)
    toyHist = toyData.createHistogram("toyhist", roofitVar)
#    toyHists.append(toyHist)

#    toyTemplate = s.HistToTemplate(toyHist,roofitVar,"v0_"+inputKey,toyDir)
#    toyTemplates.append(toyTemplate)

    toyPurity = runSSFit(toyHist, initialHists[2], nominalRatio, 'fit%d' % iToy, pdir = toysDir)

#    toyPurity = s.SignalSubtraction(toySkims,toyHists,toyTemplates,nominalRatio,roofitVar,var[1][era][loc][pid],inputKey,toyDir)

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

print '\n'
print '################################################'
print '######## Doing signal shape uncertainty ########'
print '################################################'
print '\n'

### Get signal shape uncertainty
#twobinDir = os.path.join(plotDir,'twobin')
#if not os.path.exists(twobinDir):
#    os.makedirs(twobinDir)
#twobinSkims = skims[:4]
#twobinHists = []
#twobinTemplates = []
#nbins = len(var[2][loc][2])-1
#for iH, hist in enumerate(initialHists[:4]):
#    newHist = hist.Clone("newhist"+str(iH))
#    twobinHist = newHist.Rebin(nbins, "twobinhist"+str(iH), array('d', var[2][loc][2]))
#    twobinHists.append(twobinHist)
#    template = s.HistToTemplate(twobinHist,var[2][loc],twobinSkims[iH],"v0_"+inputKey,twobinDir)
#    twobinTemplates.append(template)
#
#twobinPurity = s.SignalSubtraction(twobinSkims,twobinHists,twobinTemplates,nominalRatio,roofitVar,var[1][era][loc][pid],inputKey,twobinDir)
#twobinUncertainty = abs( nominalPurity[0] - twobinPurity[0])
#twobinUncYield = abs( nominalPurity[2] - twobinPurity[2])
twobinUncertainty = 0.
twobinUncYield = 0.

print '\n'
print '#################################'
print '######## Showing results ########'
print '#################################'
print '\n'

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

outFile.write( "\n\n# of real photons is: "+str(nominalPurity[2])+'\n' )
outFile.write( "Sideband unc yield is: "+str(sidebandUncYield)+'\n' )
outFile.write( "Method unc yield is: "+str(scaledUncYield)+'\n' ) 
outFile.write( "Signal shape unc yield is: "+str(twobinUncYield)+'\n' ) 
outFile.write( "Background stat unc yield is: "+str(bkgdUncYield)+'\n' )
outFile.write( "Total unc yield is: "+str(totalUncYield)+'\n\n\n' )

outFile.write( "Nominal purity is: "+str(nominalPurity[0])+'\n' )
outFile.write( "Sideband uncertainty is: "+str(sidebandUncertainty)+'\n' )
outFile.write( "Method uncertainty is: "+str(scaledUncertainty)+'\n' ) 
outFile.write( "Signal shape uncertainty is: "+str(twobinUncertainty)+'\n' ) 
outFile.write( "Background stat uncertainty is: "+str(bkgdUncertainty)+'\n' )
outFile.write( "Total uncertainty is: "+str(totalUncertainty)+'\n' )

outFile.close()
