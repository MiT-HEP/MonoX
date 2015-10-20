import os
import sys
from pprint import pprint
from ROOT import *
from selections import Measurement, Selections, Variables, Version, PlotNames, HistExtractor, HistToTemplate, FitTemplates, Locations, PhotonIds, ChIsoSbSels, PhotonPtSels, MetSels
gROOT.SetBatch(True)

# Import selection from command line
loc = sys.argv[1]
pid = sys.argv[2]
chiso = sys.argv[3]
pt = sys.argv[4]
met = sys.argv[5]

selKeys = []
inputKey = loc+'_'+pid+'_ChIso'+chiso+'_PhotonPt'+pt+'_Met'+met
try: 
    Selections[inputKey]
except KeyError:
    print "Selection inputted from command line doesn't exist. Quitting!!!"
    sys.exit()
else:
    selKeys.append(inputKey)
# selKeys = ['barrel_medium_PhotonPt180toInf'] 
# selKeys = [loc+'_'+pid+'_'+chIsoCut[0]+'_'+ptCut[0]+'_'+metCut[0] for loc in Locations for pid in PhotonIds for chIsoCut in ChIsoSbSels for ptCut in PhotonPtSels[0] for metCut in MetSels]
# selKeys = [loc+'_'+pid+'_'+chIsoCut[0]+'_'+ptCut[0]+'_'+MetSels[0][0] for loc in Locations for pid in PhotonIds for chIsoCut in ChIsoSbSels for ptCut in PhotonPtSels[0]]

# Make templates from skims
varName = 'sieie'
var = Variables[varName]
varBins = False

versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
skimDir  = os.path.join(versDir,'Skims')
# plotDir = os.path.join(versDir,'Plots',inputKey)
plotDir = os.path.join('/home/ballen/public_html/cmsplots/PurityTemp',inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

skimName = "Monophoton"
skims = Measurement[skimName] 

purities = []
for i in xrange(0,3,1):
    purities.append([])

print len(selKeys), selKeys
for selKey in selKeys:
    templates = []
    for skim,sel in zip(skims,Selections[selKey]):
        hist = HistExtractor(var[0],var[3][loc],skim,sel,skimDir,varBins)
        template = HistToTemplate(hist,var[3][loc],skim,selKey,plotDir)
        templates.append(template)

    # Fit for data full sideband
    dataTitle = PlotNames[skimName][0]
    dataName = os.path.join(plotDir,"purity_data_"+selKey)
    dataPurity = FitTemplates(dataName, dataTitle,  var[3][loc][0], var[4][loc][pid], templates[1], templates[0], templates[5])
    
    # Fit for MC
    mcTitle = PlotNames[skimName][1]
    mcName = os.path.join(plotDir,"purity_mc_"+selKey)
    mcPurity = FitTemplates(mcName, mcTitle, var[3][loc][0], var[4][loc][pid], templates[2], templates[0], templates[6])

    # Calculate purity and print results
    print "Purity of Photons in data is:", dataPurity
    purities[0].append(dataPurity)
    
    print "Purity of Photons in mc is:", mcPurity
    purities[1].append(mcPurity)

    truthReal = templates[3].sumEntries(varName+' < '+str(var[4][loc][pid]))
    truthTotal = templates[2].sumEntries(varName+' < '+str(var[4][loc][pid]))
    print "Number of Real photons passing selection in truth:", truthReal
    print "Number of Total photons passing selection in truth:", truthTotal
    truthCenter = float(truthReal) / float(truthTotal)

    truthUpper = TEfficiency.ClopperPearson(int(truthTotal),int(truthReal),0.6827,True)
    truthLower = TEfficiency.ClopperPearson(int(truthTotal),int(truthReal),0.6827,False)

    truthUpSig = truthUpper - truthCenter;
    truthDownSig = truthCenter - truthLower;
    truthAveSig = float(truthUpSig + truthDownSig) / 2.0;

    truthPurity = (truthCenter, truthAveSig)
    
    print "Purity of Photons in truth is:", truthPurity
    purities[2].append(truthPurity)
    
# Plot purities
print "Purity of Photons in data is:", purities[0]

print "Purity of Photons in mc is:", purities[1]

print "Purity of Photons in truth is:", purities[2]
