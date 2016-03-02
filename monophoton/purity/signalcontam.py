import os
import sys
from pprint import pprint
from subprocess import Popen, PIPE
from selections import Variables, Version, Measurement, Selections, SigmaIetaIetaSels, ChIsoSbSels, PhotonPtSels, MetSels, cutMatchedToReal, HistExtractor, HistToTemplate, PlotNames,FitTemplates
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
# plotDir = os.path.join(os.environ['CMSPLOTS'],'ST10','SignalContam',inputKey)
skimName = "Monophoton"

sbSkims = [ ('TempSidebandGJets','TempSignalGJets',kPhoton,r'Sideband Template from #gamma+jets MC')
            ,('TempSidebandGJetsScaled','TempSignalGJets',kPhoton,r'Scaled Sideband Template from #gamma+jets MC') ]

truthSel =  '( selPhotons.matchedGen == -22)'
sbSel = SigmaIetaIetaSels[loc][pid]+' && '+chIsoSel+' && '+truthSel+' && '+ptSel+' &&'+metSel

# fit, signal, contamination, background
skims = [ Measurement[skimName][1], Measurement[skimName][0], sbSkims[0], Measurement[skimName][5], sbSkims[1], Measurement[skimName][5] ]
sels = [ Selections[inputKey][1], Selections[inputKey][0], sbSel, Selections[inputKey][5], sbSel, Selections[inputKey][5] ]

nIter = 0
hists = []
templates = []
for skim, sel in zip(skims,sels):
    hist = HistExtractor(var[0],var[3][loc],skim,sel,skimDir,varBins)
    hists.append(hist)
    template = HistToTemplate(hist,var[3][loc],skim,"v"+str(nIter)+"_"+inputKey,plotDir)
    templates.append(template)

purities = [ (1,1,1) ]
sigContams = [ (1,1,1) ]
sigContamsPass = [ (1,1,1) ]

# labels = ["nominal", "low", "high"]
# labels = ["nominal", "scaled"]
while(True):
    tempPurity = []
    tempContams = []
    for iC, label in enumerate(labels):
        iContam = -4+2*iC
        iBack = -3+2*iC
        print iContam, iBack
        dataTitle = PlotNames[skimName][0]+" Iteration "+str(nIter)
        dataName = os.path.join(plotDir,"purity_"+label+"_"+"v"+str(nIter)+"_"+inputKey )
        dataPurity = FitTemplates(dataName, dataTitle,  var[3][loc][0], var[4][loc][pid], templates[0], templates[1], templates[iBack])
        tempPurity.append(dataPurity)
        
        sbTotal = templates[3].sumEntries()
        sbTrue = templates[iContam].sumEntries()
        trueContam = float(sbTrue) / float(sbTotal)

        sbTotalPass = templates[3].sumEntries(varName+' < '+str(var[4][loc][pid]))
        sbTruePass = templates[iContam].sumEntries(varName+' < '+str(var[4][loc][pid]))
        trueContamPass = float(sbTruePass) / float(sbTotalPass)

        tempContams.append( (trueContam, trueContamPass) )

    print "Signal contamination:", tempContams[0][0], tempContams[1][0] # , tempContams[2][0]
    sigContams.append( (tempContams[0][0], tempContams[1][0]) ) # , tempContams[2][0]) )

    print "Signal contamination pass:", tempContams[0][1], tempContams[1][1] # , tempContams[2][1]
    sigContamsPass.append( (tempContams[0][1], tempContams[1][1]) ) # , tempContams[2][1]) )

    print "Purity:", tempPurity[0][0], tempPurity[1][0] # , tempPurity[2][0]
    purities.append( (tempPurity[0][0], tempPurity[1][0]) ) # , tempPurity[2][0]) )
    diff = abs(purities[-1][0] - purities[-2][0] )
    print diff 
    if ( diff < 0.001):
        break
    nIter += 1
    if nIter > 5:
        break

    for iC, label in enumerate(labels):
        nSigTrue = tempPurity[iC][2]
        nSbTrue = float(isoHists[iC][1]) / float(isoHists[iC][2]) * nSigTrue
    
        print "Scaling sideband shape to", nSbTrue, "photons"
        
        iContam = 2+2*iC
        print iContam
        contamHist = hists[iContam].Clone()
        contamHist.Scale(float(nSbTrue) / float(contamHist.GetSumOfWeights()))
        hists.append(contamHist)

        contamTemp = HistToTemplate(contamHist,var[3][loc],skims[2],label+"_v"+str(nIter)+"_"+inputKey,plotDir)
        templates.append(contamTemp)
    
        backHist = hists[3].Clone()
        backHist.Add(contamHist, -1)
        hists.append(backHist)

        backTemp = HistToTemplate(backHist,var[3][loc],skims[3],label+"_v"+str(nIter)+"_"+inputKey,plotDir)
        templates.append(backTemp)

for version, (purity, contam)  in enumerate(zip(purities[1:],sigContams[1:])):
    print "Purity for iteration", version, "is:", purity
    print "Signal contamination for iteration", version, "is:", contam
