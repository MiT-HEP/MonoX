#! /usr/bin/python

import sys
from multiprocessing import Process, Queue
import goodlumi
import ROOT

import os
import subprocess

#### These are all the variables the user should have to configure ####

# Now I have them configured in the config.sh script
command = ['bash', '-c', 'source config.sh && env']

proc = subprocess.Popen(command, stdout = subprocess.PIPE)

for line in proc.stdout:
  (key, _, value) = line.partition("=")
  os.environ[key] = value.rstrip('\n')
##

proc.communicate()

numMaxProcesses = int(os.environ['MonoJetCoresPerLocalJob'])

inDir  = os.environ['MonoJetFullOutDir']
outDir = os.environ['MonoJetSkimOutDir']

GoodRunsFile = os.environ['MonoJetGoodRunsFile']
cut = os.environ['MonoJetSkimmingCut']

#######################################################################

if not os.path.exists(outDir):
  os.mkdir(outDir)
##

def skim(inQueue):
    running = True
    while running:
        try:
            inFileName = inQueue.get(True,2)
            print "About to process " + inFileName
            inFile  = ROOT.TFile(inDir + "/" + inFileName)
            if not os.path.isfile(outDir + "/" + inFileName):
                outFile = ROOT.TFile(outDir + "/" + inFileName,"RECREATE")
                tempInTree = inFile.events
                tempInTree.GetEntry(0)
                if tempInTree.runNum != 1:           # If runNum !=, then this is data
                    goodRunFilter = goodlumi.makeGoodLumiFilter(GoodRunsFile)
                    inTree = tempInTree.CloneTree(0)
                    for entry in range(tempInTree.GetEntriesFast()):
                        if entry % 100000 == 0:
                            print "Processing events: " + inFileName + " ... " + str(entry*100.0/tempInTree.GetEntriesFast()) + "%"
                        ##
                        tempInTree.GetEntry(entry)
                        if goodRunFilter.isGoodLumi(tempInTree.runNum,tempInTree.lumiNum):
                            inTree.Fill()
                        ##
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
    if inFileName.endswith(".root"):
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
