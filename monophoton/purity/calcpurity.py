import os
import sys
from ROOT import *
from selections import Measurement, Selections, Variables, Version, PlotNames, TemplateMaker, FitTemplates
#ROOT.gROOT.SetBatch(True)

# Make templates from skims
varName = 'sieie'
var = Variables[varName]

versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
skimDir  = os.path.join(versDir,'Skims')
plotDir = os.path.join(versDir,'Plots')
if not os.path.exists(plotDir):
    os.makedirs(plotDir)

skimName = "Monophoton"
skims = Measurement[skimName] 
#sels = ['medium_barrel_'+cut[0] for cut in cutPhotonPt]
selKeys = ['medium_barrel_PhotonPt180toInf'] 
# sels = ['medium_barrel_Wlike']
purities = [[],[],[],[]]

for selKey in selKeys:
    templates = []
    for skim,sel in zip(skims,Selections[selKey]):
        template = TemplateMaker(var,skim,sel,selKey,skimDir,plotDir)
        templates.append(template)

    # Fit for data
    dataTitle = PlotNames[skimName][0]
    dataName = os.path.join(plotDir,"purity_data_"+selKey)
    dataPurity = FitTemplates(dataName, dataTitle,  var[3], var[4], templates[3], templates[0], templates[1])
    
    # Fit for MC
    mcTitle = PlotNames[skimName][1]
    mcName = os.path.join(plotDir,"purity_mc_"+selKey)
    mcPurity = FitTemplates(mcName, mcTitle, var[3], var[4], templates[4], templates[0], templates[2])

    # Fit for MC truth
    truthTitle = PlotNames[skimName][2]
    truthName = os.path.join(plotDir,"purity_mcTruth_"+selKey)
    truthPurity = FitTemplates(truthName, truthTitle, var[3], var[4], templates[4], templates[5], templates[6])

    # Calculate purity and print results
    print "Purity of Photons in Data is:", dataPurity
    purities[0].append(dataPurity)

    print "Purity of Photons in MC is:", mcPurity
    purities[1].append(mcPurity)

    print "Purity of Photons in truthFit is:", truthPurity
    purities[2].append(truthPurity)
    
    truthReal = templates[5].sumEntries(varName+' < '+str(var[4]))
    truthTotal = templates[4].sumEntries(varName+' < '+str(var[4]))
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
