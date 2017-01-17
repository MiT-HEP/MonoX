import os
import sys
from pprint import pprint
from array import array
from subprocess import Popen, PIPE
import ROOT as r

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if basedir not in sys.path:
    sys.path.append(basedir)
import config
from plotstyle import SimpleCanvas
from datasets import allsamples
import selections as s

versDir = os.path.join('/data/t3home000/ballen/hist/purity',s.Version)
outDir = os.path.join(versDir, 'Fitting')
if not os.path.exists(outDir):
    os.makedirs(outDir)

outFile = r.TFile("../data/impurity.root", "RECREATE")

bases = ['loose', 'medium', 'tight', 'highpt']
mods = ['', '-pixel', '-pixel-monoph', '-pixel-monoph-max'] # , '-pixel-monoph-worst']
PhotonIds = [base+mod for base in bases for mod in mods]
PhotonPtSels = sorted(s.PhotonPtSels.keys())[:-1]
MetSels = sorted(s.MetSels.keys())[:1]

era = 'Spring16'

purities = {}
for loc in s.Locations[:1]:
    purities[loc] = {}
    for pid in PhotonIds:
        purities[loc][pid] = {}
        for ptCut in PhotonPtSels:
            purities[loc][pid][ptCut] = {}
            for metCut in MetSels:
                purities[loc][pid][ptCut][metCut] = {}
                
                dirName = era + '_' + loc+'_'+pid+'_'+ptCut+'_'+metCut 
                condorFileName = os.path.join(versDir,dirName,"results.out")
                # print condorFileName
                try:
                    condorFile = open(condorFileName)

                    match = False
                    purity = [1, 0, 0, 0, 0, 0]
                    for line in condorFile:
                        if "Nominal purity is:" in line:
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[0] = (1.0 - float(tmp[-1].strip("(),"))) * 100
                                # print purity[0]
                        elif "Total uncertainty is:" in line:
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[1] = float(tmp[-1].strip("(),")) * 100
                                #print purity
                        elif "Sideband uncertainty is:" in line:
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[2] = float(tmp[-1].strip("(),")) * 100
                                #print purity
                        elif "Method uncertainty is:" in line:
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[3] = float(tmp[-1].strip("(),")) * 100
                                #print purity
                        elif "Signal shape uncertainty is:" in line: # need to add t back
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[4] = float(tmp[-1].strip("(),")) * 100
                                #print purity
                        elif "Background stat uncertainty is:" in line:
                            # print line
                            tmp = line.split()
                            if tmp:
                                match = True
                                # pprint(tmp)
                                purity[5] = float(tmp[-1].strip("(),")) * 100
                                #print purity
                    purities[loc][pid][ptCut][metCut] = tuple(purity)

                    if not match:
                        print "No purity found for skim:", dirName
                        purities[loc][pid][ptCut][metCut] = (102.5, 0.0)

                    condorFile.close()
                except:
                    print "No purity file found for skim:", dirName
                    purities[loc][pid][ptCut][metCut] = (102.5, 0.0)
                       
pprint(purities)

sphLumi = sum(allsamples[s].lumi for s in ['sph-16b-r', 'sph-16c-r', 'sph-16d-r', 'sph-16e-r', 'sph-16f-r', 'sph-16g-r', 'sph-16h'])
canvas = SimpleCanvas(lumi = sphLumi)

for loc in s.Locations[:1]:
    for base in bases:
        for metCut in MetSels:
            canvas.cd()
            canvas.Clear()
            canvas.legend.Clear()
            canvas.legend.setPosition(0.45, 0.7, 0.8, 0.9)

            for iMod, mod in enumerate(mods):
                
                pGraph = r.TGraphAsymmErrors()
                pGraph.SetName(loc+'-'+base+mod+'-'+metCut)

                for iB, ptCut in enumerate(PhotonPtSels):
                    if 'Inclusive' in ptCut:
                        lowEdge = 175.
                        highEdge = 500.
                    else:
                        lowEdge = float(ptCut.split('t')[2])
                        highEdge = ptCut.split('to')[-1]
                        if highEdge == 'Inf':
                            highEdge = 500.
                        highEdge = float(highEdge)

                    center = (lowEdge + highEdge) / 2.
                    exl = center - lowEdge
                    exh = highEdge - center

                    purity = purities[loc][base+mod][ptCut][metCut]

                    pGraph.SetPoint(iB, center, purity[0])
                    pGraph.SetPointError(iB, exl, exh, purity[1], purity[1])

               #  if not 'max' in mod:
                canvas.legend.add(base+mod, title = base+mod, mcolor = r.kBlue+iMod, lcolor = r.kBlue+iMod, lwidth = 2)
                canvas.legend.apply(base+mod, pGraph)
                canvas.addHistogram(pGraph, drawOpt = 'EP')

                outFile.cd()
                pGraph.Write()
                
            canvas.ylimits = (0.0, 15.0)
            canvas.ytitle = 'Photon Impurity'
            canvas.xtitle = 'E_{T}^{#gamma} (GeV)'
            canvas.SetGridy(True)

            plotName = "impurity_"+str(loc)+"_"+str(base)
            canvas.printWeb('purity/'+s.Version+'/Fitting', era+'_'+plotName, logy = False)
