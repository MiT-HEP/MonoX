import os
import sys
from pprint import pprint
from subprocess import Popen, PIPE
from selections import Variables, Version, Measurement, Selections, SigmaIetaIetaSels, ChIsoSbSels, cutMatchedToReal, HistExtractor, HistToTemplate, PlotNames,FitTemplates
from ROOT import *

### take inputs and make sure they match a selection
loc = sys.argv[1]
pid = sys.argv[2]
chiso = sys.argv[3]
pt = sys.argv[4]
met = sys.argv[5]

inputKey = loc+'_'+pid+'_ChIso'+chiso+'_PhotonPt'+pt+'_Met'+met

try: 
    Selections[inputKey]
except KeyError:
    print "Selection inputted from command line doesn't exist. Quitting!!!"
    sys.exit()

chIsoSel = '(1)'
for chisosel in ChIsoSbSels:
    if 'ChIso'+chiso == chisosel[0]:
        chIsoSel = chisosel[1]
if chIsoSel == '(1)':
    print 'Inputted chIso range', chiso, 'not found!'
    print 'Not applying any chIso selection!'
 
### Directory stuff so that results are saved and such
plotDir = os.path.join(os.environ['CMSPLOTS'],'SignalContamTemp',inputKey)
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
isoHist = isoFile.Get("ShapeChIso_dR5")

### Get Sig and Sideband fractions
splits = chiso.split("to")
minIso = float(splits[0])/10.0
maxIso = float(splits[1])/10.0
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

sigFrac = isoHist.GetBinContent(1)
print "Fraction in signal:", sigFrac

### Get Purity (first time)
varName = 'sieie'
var = Variables[varName]
varBins = False
versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
skimDir  = os.path.join(versDir,'Skims')
skimName = "Monophoton"

sbSkim = ('TempSidebandGJets','TempSignalGJets',kPhoton,r'Sideband Template from #gamma+jets MC')
sbSel = SigmaIetaIetaSels[loc][pid]+' && '+chIsoSel+' && '+cutMatchedToReal
print sbSel

# fit, signal, contamination, background
skims = [ Measurement[skimName][1], Measurement[skimName][0], sbSkim, Measurement[skimName][5] ] 
sels = [ Selections[inputKey][1], Selections[inputKey][0], sbSel, Selections[inputKey][5] ] 

nIter = 0
hists = []
templates = []
for skim, sel in zip(skims,sels):
    hist = HistExtractor(var[0],var[3][loc],skim,sel,skimDir,varBins)
    hists.append(hist)
    template = HistToTemplate(hist,var[3][loc],skim,"v"+str(nIter)+"_"+inputKey,plotDir)
    templates.append(template)

purities = [ (1,0,1,0) ]
sigContams = [ (1,1) ]

while(True):
    dataTitle = PlotNames[skimName][0]+" Iteration "+str(nIter)
    dataName = os.path.join(plotDir,"purity_data_"+"v"+str(nIter)+"_"+inputKey )
    dataPurity = FitTemplates(dataName, dataTitle,  var[3][loc][0], var[4][loc][pid], templates[0], templates[1], templates[-1])

    sbTotal = templates[3].sumEntries()
    sbTrue = templates[-2].sumEntries()
    trueContam = float(sbTrue) / float(sbTotal)

    sbTotalPass = templates[3].sumEntries(varName+' < '+str(var[4][loc][pid]))
    sbTruePass = templates[-2].sumEntries(varName+' < '+str(var[4][loc][pid]))
    trueContamPass = float(sbTruePass) / float(sbTotalPass)

    print "Signal contamination:", trueContam, trueContamPass
    sigContams.append( (trueContam, trueContamPass) )

    print "Purity:", dataPurity[0]
    purities.append(dataPurity)
    diff = abs(dataPurity[0] - purities[-2][0] )
    print diff 
    if ( diff < 0.001):
        break
    nIter += 1
    if nIter > 5:
        break

    nSigTrue = dataPurity[2]
    nSbTrue = float(sbFrac) / float(sigFrac) * nSigTrue
    
    print "Scaling sideband shape to", nSbTrue, "photons"

    contamHist = hists[2].Clone()
    contamHist.Scale(float(nSbTrue) / float(contamHist.GetSumOfWeights()))
    hists.append(contamHist)

    contamTemp = HistToTemplate(contamHist,var[3][loc],skims[2],"v"+str(nIter)+"_"+inputKey,plotDir)
    templates.append(contamTemp)
    
    backHist = hists[3].Clone()
    backHist.Add(contamHist, -1)
    hists.append(backHist)

    backTemp = HistToTemplate(backHist,var[3][loc],skims[3],"v"+str(nIter)+"_"+inputKey,plotDir)
    templates.append(backTemp)

for version, (purity, contam)  in enumerate(zip(purities[1:],sigContams[1:])):
    print "Purity for iteration", version, "is:", purity[0]
    print "Signal contamination for iteration", version, "is:", contam
