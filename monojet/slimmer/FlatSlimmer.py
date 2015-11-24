#! /usr/bin/python

import sys
from multiprocessing import Process, Queue
import os
import goodlumi
import ROOT

#### These are all the variables the user should have to configure ####

numMaxProcesses = int(sys.argv[1])

#inDir  = "/tmp/zdemirag/flat_Nov11/"
inDir  = "/tmp/zdemirag/nov19_flat"

#"/tmp/zdemirag/hadd/"#"/afs/cern.ch/work/d/dabercro/public/Winter15/flatTreesV6/" #"/afs/cern.ch/work/z/zdemirag/work/frozen_monojet/monojet/slimmer"
#outDir = "/tmp/zdemirag/slim_Nov11/"
outDir = "/tmp/zdemirag/nov19_slim/"

#"/afs/cern.ch/work/z/zdemirag/public/slim_Nov9_new/" #"/afs/cern.ch/work/z/zdemirag/work/frozen_monojet/monojet/slimmer/slim"

#GoodRunsFile="/afs/cern.ch/work/z/zdemirag/work/frozen_monojet/monojet/MetRecoilStudy/latest_Json_Nov4.txt"

GoodRunsFile="/afs/cern.ch/work/z/zdemirag/work/frozen_monojet/monojet/slimmer/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON.txt"

cut = "(met > 200)"

#######################################################################

def skim(inQueue):
    running = True
    while running:
        try:
            inFileName = inQueue.get(True,2)
            print "About to process " + inFileName
            inFile  = ROOT.TFile(inDir + "/" + inFileName)
            if not os.path.isfile(outDir + "/" + inFileName):
                outFile = ROOT.TFile(outDir + "/" + inFileName,"RECREATE")
                if "Run201" in inFileName:
                    goodRunFilter = goodlumi.makeGoodLumiFilter(GoodRunsFile)
                    tempInTree = inFile.events
                    inTree = tempInTree.CloneTree(0)
                    for entry in range(tempInTree.GetEntriesFast()):
                        tempInTree.GetEntry(entry)
                        if goodRunFilter.isGoodLumi(tempInTree.runNum,tempInTree.lumiNum):
                            inTree.Fill()
                    ##
                ##
                else:
                    inTree = inFile.Get("events")
                ##
                outTree = inTree.CopyTree(cut)
                outFile.WriteTObject(outTree,"events")
                outFile.WriteTObject(inFile.htotal.Clone())
                outFile.Close()
                inFile.Close()
                print "Finished " + inFileName
            ##
            else:
                print inFileName + " already processed!"
        except:
            print "Worker finished..."
            running = False
##

theQueue     = Queue()
theProcesses = []

for inFileName in os.listdir(inDir):
    if inFileName.endswith(".root") and not "OLD" in inFileName:
        theQueue.put(inFileName)
##

for worker in range(numMaxProcesses):
    aProcess = Process(target=skim, args=(theQueue,))
    aProcess.start()
    theProcesses.append(aProcess)
##

for aProccess in theProcesses:
    aProccess.join()
##

print "All done!"
