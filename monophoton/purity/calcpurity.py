import os
import sys
from ROOT import *
from selections import Measurement, Selections, Variables, Version, PlotNames, HistExtractor, HistToTemplate, FitTemplates, Locations, PhotonIds, ChIsoSbSels, PhotonPtSels, MetSels
gROOT.SetBatch(True)

# Import selection from command line
loc = sys.argv[1]
sel = sys.argv[2]
chiso = sys.argv[3]
pt = sys.argv[4]
met = sys.argv[5]

selKeys = []
inputKey = loc+'_'+sel+'_ChIso'+chiso+'_PhotonPt'+pt+'_Met'+met
try: 
    Selections[inputKey]
except KeyError:
    print "Selection inputted from command line doesn't exist. Quitting!!!"
    sys.exit()
else:
    selKeys.append(inputKey)
# selKeys = ['barrel_medium_PhotonPt180toInf'] 
# selKeys = [loc+'_'+pid+'_'+chIsoCut[0]+'_'+ptCut[0]+'_'+metCut[0] for loc in Locations for pid in PhotonIds for chIsoCut in ChIsoSbSels for ptCut in PhotonPtSels[0] for metCut in MetSels]

# Make templates from skims
varName = 'sieie'
var = Variables[varName]

versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
skimDir  = os.path.join(versDir,'Skims')
# plotDir = os.path.join(versDir,'Plots',inputKey)
plotDir = os.path.join('/home/ballen/public_html/cmsplots/PurityTemp',inputKey)
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

skimName = "Monophoton"
skims = Measurement[skimName] 

purities = [ ] # [[]]*10
for i in xrange(1,15,1):
    purities.append([])

print len(selKeys), selKeys
for selKey in selKeys:
    templates = []
    for skim,sel in zip(skims,Selections[selKey]):
        hist = HistExtractor(var,skim,sel,skimDir)
        template = HistToTemplate(hist,var,skim,selKey,plotDir)
        templates.append(template)

    # Fit for data full sideband
    dataTitle = PlotNames[skimName][0]
    dataName = os.path.join(plotDir,"purity_data_"+selKey)
    dataPurity = FitTemplates(dataName, dataTitle,  var[3], var[5], templates[1], templates[0], templates[5])

    '''
    # Fit for data in low sideband
    checkTitle = PlotNames[skimName][6]
    checkName = os.path.join(plotDir,"purity_check_"+selKey)
    checkPurity = FitTemplates(checkName, checkTitle,  var[3], var[5], templates[6], templates[0], templates[5])

    # Fit for data low sideband
    lowTitle = PlotNames[skimName][3]
    lowName = os.path.join(plotDir,"purity_sblow_"+selKey)
    lowPurity = FitTemplates(lowName, lowTitle,  var[3], var[5], templates[1], templates[0], templates[6])

    # Fit for data med sideband
    medTitle = PlotNames[skimName][4]
    medName = os.path.join(plotDir,"purity_sbmed_"+selKey)
    medPurity = FitTemplates(medName, medTitle,  var[3], var[5], templates[1], templates[0], templates[7])

    # Fit for data high sideband
    highTitle = PlotNames[skimName][5]
    highName = os.path.join(plotDir,"purity_sbhigh_"+selKey)
    highPurity = FitTemplates(highName, highTitle,  var[3], var[5], templates[1], templates[0], templates[8])
    '''
    
    # Fit for MC
    mcTitle = PlotNames[skimName][1]
    mcName = os.path.join(plotDir,"purity_mc_"+selKey)
    mcPurity = FitTemplates(mcName, mcTitle, var[3], var[5], templates[2], templates[0], templates[6])
    
    '''
    # Fit for MC in low sideband
    checkMcTitle = PlotNames[skimName][6]
    checkMcName = os.path.join(plotDir,"purity_checkmc_"+selKey)
    checkMcPurity = FitTemplates(checkMcName, checkMcTitle,  var[3], var[5], templates[10], templates[0], templates[9])

    # Fit for mc mclow sideband
    mclowTitle = PlotNames[skimName][3]
    mclowName = os.path.join(plotDir,"purity_sbmclow_"+selKey)
    mclowPurity = FitTemplates(mclowName, mclowTitle,  var[3], var[5], templates[2], templates[0], templates[10])
    
    # Fit for mcmed sideband
    mcmedTitle = PlotNames[skimName][4]
    mcmedName = os.path.join(plotDir,"purity_sbmcmed_"+selKey)
    mcmedPurity = FitTemplates(mcmedName, mcmedTitle,  var[3], var[5], templates[2], templates[0], templates[11])

    # Fit for mchigh sideband
    mchighTitle = PlotNames[skimName][5]
    mchighName = os.path.join(plotDir,"purity_sbmchigh_"+selKey)
    mchighPurity = FitTemplates(mchighName, mchighTitle,  var[3], var[5], templates[2], templates[0], templates[12])

    # Fit for MC truth
    truthTitle = PlotNames[skimName][2]
    truthName = os.path.join(plotDir,"purity_mcTruth_"+selKey)
    truthPurity = FitTemplates(truthName, truthTitle, var[3], var[5], templates[4], templates[5], templates[6])
    '''

    # Calculate purity and print results
    # print purities[0]
    print "Purity of Photons in Data is:", dataPurity
    purities[0].append(dataPurity)
    # print purities[0]

    '''
    print "Purity of Photons in low Sideband Region in Data is:", checkPurity
    purities[9].append(checkPurity)

    # print purities[1]
    print "Purity of Photons in Data with low Sideband is:", lowPurity
    purities[1].append(lowPurity)    
    # print purities[1]

    # print purities[2]
    print "Purity of Photons in Data with medium Sideband is:", medPurity
    purities[2].append(medPurity)    
    # print purities[2]

    # print purities[3]
    print "Purity of Photons in Data with high Sideband is:", highPurity
    purities[3].append(highPurity)
    # print purities[3]
    '''
    
    # print purities[4]
    print "Purity of Photons in MC is:", mcPurity
    purities[4].append(mcPurity)
    # print purities[4]

    '''
    print "Purity of Photons in low Sideband Region in MC is:", checkPurity
    purities[10].append(checkPurity)

    # print purities[5]
    print "Purity of Photons in MC with low Sideband is:", mclowPurity
    purities[5].append(mclowPurity)    
    # print purities[5]

    # print purities[6]
    print "Purity of Photons in MC with medium Sideband is:", mcmedPurity
    purities[6].append(mcmedPurity)    
    # print purities[6]

    # print purities[7]
    print "Purity of Photons in MC with high Sideband is:", mchighPurity
    purities[7].append(mchighPurity)
    # print purities[7]

    print "Purity of Photons in truthFit is:", truthPurity
    purities[2].append(truthPurity)
    '''    

    # print purities[8]
    truthReal = templates[3].sumEntries(varName+' < '+str(var[5]))
    truthTotal = templates[2].sumEntries(varName+' < '+str(var[5]))
    print "Number of Real photons passing selection in mcTruth:", truthReal
    print "Number of Total photons passing selection in mcTruth:", truthTotal
    truthCenter = float(truthReal) / float(truthTotal)

    truthUpper = TEfficiency.ClopperPearson(int(truthTotal),int(truthReal),0.6827,True)
    truthLower = TEfficiency.ClopperPearson(int(truthTotal),int(truthReal),0.6827,False)

    truthUpSig = truthUpper - truthCenter;
    truthDownSig = truthCenter - truthLower;
    truthAveSig = float(truthUpSig + truthDownSig) / 2.0;

    truthPurity = (truthCenter, truthAveSig)
    
    print "Purity of Photons in mcTruth is:", truthPurity
    purities[8].append(truthPurity)
    # print purities[8]

    
# Plot purities
print "Purity of Photons in Data is:", purities[0]
'''
print "Purity of Phtons in low sideband in Data is:", purities[9]
print "Purity of Photons in Data with low sideband is:", purities[1]
print "Purity of Photons in Data with medium sideband is:", purities[2]
print "Purity of Photons in Data with high sideband is:", purities[3]
'''
print "Purity of Photons in MC is:", purities[4]
'''
print "Purity of Phtons in low sideband in MC is:", purities[10]
print "Purity of Photons in MC with low sideband is:", purities[5]
print "Purity of Photons in MC with medium sideband is:", purities[6]
print "Purity of Photons in MC with high sideband is:", purities[7]
# print "Purity of Photons in truthFit is:", purities[2]
'''
print "Purity of Photons in mcTruth is:", purities[8]

