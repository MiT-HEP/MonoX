import os
import sys
import subprocess
from ROOT import *
from selections import Regions, Variables, Version
gROOT.SetBatch(True)

# varName = 'chiso' 
varName = 'sieie'
# varName = 'sieieScaled'
var = Variables[varName]
# skims = Regions["ShapeChIso"]
skims = Regions["Monophoton"]

outDir = os.path.join('/scratch5/ballen/hist/purity/',Version,varName,'Skims/tmp')
if not os.path.exists(outDir):
    os.makedirs(outDir)
    

lumi = -1.0
try:
    print "Luminosity is: ", sys.argv[1]
except IndexError:
    print "Please provide a luminosity in 1/pb."
    print "Use the follow syntax:"
    print "python $PATH/makeskims.py LUMI"
    sys.exit()
else:
    lumi = float(sys.argv[1])

for skim in skims[:]:
    print 'Starting skim:', skim[0]
    
    filesToMerge = []
    for samp in skim[-1]:
        print 'Adding files from:', samp[-1]
        inputTree = TChain('events')
        
        for f in os.listdir(samp[-1]):
            if not 'simpletree' in str(f): 
                continue
            print 'Adding file: ', str(f)
            inputTree.Add(samp[-1] + '/' + f)
            # break
    
        outname = os.path.join(outDir,samp[0]+'.root')
        filesToMerge.append(outname)
        print 'Saving skim to:', outname
        generator = TemplateGenerator(skim[1], var[0], outname, True)
        generator.fillSkim(inputTree, var[1], var[2], samp[1], lumi)
        generator.writeSkim()
        generator.closeFile()

    mergedFileName = os.path.join(outDir,skim[0]+'.root')
    subprocess.call(['hadd','-f',mergedFileName]+filesToMerge)
    # break
