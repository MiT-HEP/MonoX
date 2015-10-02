import os
import sys
from ROOT import *
from selections import Measurement, Selections, Variables, Version, PlotNames, HistExtractor, HistToTemplate, FitTemplates
gROOT.SetBatch(True)

# Make templates from skims
varName = 'sieie'
var = Variables[varName]

versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
skimDir  = os.path.join(versDir,'Skims/tmp')
plotDir = os.path.join(versDir,'Plots/tmp')
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

skimName = "Monophoton"
skims = Measurement[skimName] 
#sels = ['medium_barrel_'+cut[0] for cut in cutPhotonPt]
selKeys = ['medium_barrel_PhotonPt180toInf'] 
# sels = ['medium_barrel_Wlike']
purities = [[]] * 10

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
    dataPurity = FitTemplates(dataName, dataTitle,  var[3], var[5], templates[3], templates[0], templates[1])

    # Fit for data low sideband
    lowTitle = PlotNames[skimName][3]
    lowName = os.path.join(plotDir,"purity_sblow_"+selKey)
    lowPurity = FitTemplates(lowName, lowTitle,  var[3], var[5], templates[3], templates[0], templates[7])
    
    # Fit for data med sideband
    medTitle = PlotNames[skimName][4]
    medName = os.path.join(plotDir,"purity_sbmed_"+selKey)
    medPurity = FitTemplates(medName, medTitle,  var[3], var[5], templates[3], templates[0], templates[8])

    # Fit for data high sideband
    highTitle = PlotNames[skimName][5]
    highName = os.path.join(plotDir,"purity_sbhigh_"+selKey)
    highPurity = FitTemplates(highName, highTitle,  var[3], var[5], templates[3], templates[0], templates[9])

    # Fit for MC
    mcTitle = PlotNames[skimName][1]
    mcName = os.path.join(plotDir,"purity_mc_"+selKey)
    mcPurity = FitTemplates(mcName, mcTitle, var[3], var[5], templates[4], templates[0], templates[2])

    # Fit for mc mclow sideband
    mclowTitle = PlotNames[skimName][3]
    mclowName = os.path.join(plotDir,"purity_sbmclow_"+selKey)
    mclowPurity = FitTemplates(mclowName, mclowTitle,  var[3], var[5], templates[4], templates[0], templates[10])
    
    # Fit for mcmed sideband
    mcmedTitle = PlotNames[skimName][3]
    mcmedName = os.path.join(plotDir,"purity_sbmcmed_"+selKey)
    mcmedPurity = FitTemplates(mcmedName, mcmedTitle,  var[3], var[5], templates[4], templates[0], templates[11])

    # Fit for mchigh sideband
    mchighTitle = PlotNames[skimName][4]
    mchighName = os.path.join(plotDir,"purity_sbmchigh_"+selKey)
    mchighPurity = FitTemplates(mchighName, mchighTitle,  var[3], var[5], templates[4], templates[0], templates[12])

    # Fit for MC truth
    truthTitle = PlotNames[skimName][2]
    truthName = os.path.join(plotDir,"purity_mcTruth_"+selKey)
    truthPurity = FitTemplates(truthName, truthTitle, var[3], var[5], templates[4], templates[5], templates[6])

    # Calculate purity and print results
    print "Purity of Photons in Data is:", dataPurity
    purities[0].append(dataPurity)

    print "Purity of Photons in Data with low Sideband is:", lowPurity
    purities[4].append(lowPurity)    

    print "Purity of Photons in Data with medium Sideband is:", medPurity
    purities[5].append(medPurity)    

    print "Purity of Photons in Data with high Sideband is:", highPurity
    purities[6].append(highPurity)

    print "Purity of Photons in MC is:", mcPurity
    purities[1].append(mcPurity)

    print "Purity of Photons in MC with low Sideband is:", mclowPurity
    purities[7].append(mclowPurity)    

    print "Purity of Photons in MC with medium Sideband is:", mcmedPurity
    purities[8].append(mcmedPurity)    

    print "Purity of Photons in MC with high Sideband is:", mchighPurity
    purities[9].append(mchighPurity)

    print "Purity of Photons in truthFit is:", truthPurity
    purities[2].append(truthPurity)
    
    truthReal = templates[5].sumEntries(varName+' < '+str(var[5]))
    truthTotal = templates[4].sumEntries(varName+' < '+str(var[5]))
    print "Number of Real photons passing selection in mcTruth:", truthReal
    print "Number of Total photons passing selection in mcTruth:", truthTotal
    truthPurity = float(truthReal) / float(truthTotal)
    print "Purity of Photons in mcTruth is:", truthPurity
    purities[3].append(truthPurity)

# Plot purities
print "Purity of Photons in Data is:", purities[0]
print "Purity of Photons in Data with low sideband is:", purities[4]
print "Purity of Photons in Data with medium sideband is:", purities[5]
print "Purity of Photons in Data with high sideband is:", purities[6]
print "Purity of Photons in MC is:", purities[1]
print "Purity of Photons in MC with low sideband is:", purities[7]
print "Purity of Photons in MC with medium sideband is:", purities[8]
print "Purity of Photons in MC with high sideband is:", purities[9]
print "Purity of Photons in truthFit is:", purities[2]
print "Purity of Photons in mcTruth is:", purities[3]
