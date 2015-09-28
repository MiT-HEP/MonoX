import os
import sys
from ROOT import *
from selections import Regions, Variables, Version, ntupledir
#gROOT.SetBatch(True)

varName = 'sieie'
var = Variables[varName]

outDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName,'Skims')
if not os.path.exists(outDir):
    os.makedirs(outDir)
    
skims = Regions["Monophoton"]  #["Wgamma"]

for skim in skims:
    print 'Starting skim:', skim[0]
    inputTree = TChain('events')
    
    print 'Adding files from:', skim[-1]
    for f in os.listdir(skim[-1]):
        print 'Adding file: ', str(f)
        inputTree.Add(skim[-1] + '/' + f)
        # break
    
    outname = os.path.join(outdir,'Skim'+skim[0]+'.root')
    print 'Saving skim to:', outname
    generator = TemplateGenerator(skim[1], var[0], outname, True)
    generator.fillSkim(inputTree, var[1], var[2], skim[2])
    generator.writeSkim()
