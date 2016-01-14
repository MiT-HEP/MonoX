import os
import sys
from pprint import pprint
#from array import array
# from subprocess import Popen, PIPE
# from ROOT import *
import numpy as np
import matplotlib.pyplot as plot
import matplotlib.axes as axes
from scipy.optimize import leastsq
from selections import Version, Locations, PhotonIds, ChIsoSbSels, PhotonPtSels, MetSels
# gROOT.SetBatch(True)

varName = 'sieie'
versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
plotDirs = [ ('shape', os.path.join(versDir, 'Plots', 'SignalContam')) ] 
outDir = os.path.join(plotDirs[0][1], 'Fitting')
if not os.path.exists(outDir):
    os.makedirs(outDir)

purities = {}

for plotDir in plotDirs:
    fit = plotDir[0]
    purities[fit] = {}
    for loc in Locations[:1]:
        purities[fit][loc] = {}
        for pid in PhotonIds[:3]:
            purities[fit][loc][pid] = {}
            for ptCut in PhotonPtSels[0][:1]:
                purities[fit][loc][pid][ptCut[0]] = {}
                for metCut in MetSels[:1]:
                    purities[fit][loc][pid][ptCut[0]][metCut[0]] = {}
                    for chiso in ChIsoSbSels[:]:
                        purities[fit][loc][pid][ptCut[0]][metCut[0]][chiso[0]] = {}
                        
                        dirName = loc+'_'+pid+'_'+chiso[0]+'_'+ptCut[0]+'_'+metCut[0] 
                        condorFileName = os.path.join(plotDir[1],dirName,"condor.out") 
                        # print condorFileName
                        condorFile = open(condorFileName)
                    
                        match = False
                        purity = [1, 0, 0, 0, 0]
                        for line in condorFile:
                            if "Nominal purity is:" in line:
                                # print line
                                tmp = line.split()
                                if tmp:
                                    match = True
                                    # pprint(tmp)
                                    purity[0] = float(tmp[-1].strip("(),"))
                                    #print purity[0]
                            elif "Total uncertainty is:" in line:
                                # print line
                                tmp = line.split()
                                if tmp:
                                    match = True
                                    # pprint(tmp)
                                    purity[-1] = float(tmp[-1].strip("(),"))
                                    #print purity
                            elif "Method uncertainty is:" in line:
                                # print line
                                tmp = line.split()
                                if tmp:
                                    match = True
                                    # pprint(tmp)
                                    purity[1] = float(tmp[-1].strip("(),"))
                                    #print purity
                            elif "Signal shape uncertainty is:" in line: # need to add t back
                                # print line
                                tmp = line.split()
                                if tmp:
                                    match = True
                                    # pprint(tmp)
                                    purity[2] = float(tmp[-1].strip("(),"))
                                    #print purity
                            elif "Background stat uncertainty is:" in line:
                                # print line
                                tmp = line.split()
                                if tmp:
                                    match = True
                                    # pprint(tmp)
                                    purity[3] = float(tmp[-1].strip("(),"))
                                    #print purity
                        purities[fit][loc][pid][ptCut[0]][metCut[0]][chiso[0]] = purity 

                        if not match:
                            print "No purity found for skim:", dirName
                            purities[fit][loc][pid][ptCut[0]][metCut[0]][chiso[0]] = (1.025, 0.0)
                        condorFile.close()
pprint(purities)


for loc in Locations[:1]:
    for pid in PhotonIds[:3]:
        for ptCut in PhotonPtSels[0][:1]:
            for metCut in MetSels[:1]:
                for plotDir in plotDirs:
                    fit = plotDir[0] 
                    isoVals = np.asarray([ float(key.split('o')[1].strip('t'))/10.0 for key in sorted(purities[fit][loc][pid][ptCut[0]][metCut[0]]) ])
                    #isoVals = np.arange(2.0,8.5,0.5)
                    puritiesCalc = ( np.asarray(  [ (1 - value[0])*100 for key, value in sorted(purities[fit][loc][pid][ptCut[0]][metCut[0]].iteritems()) ])
                                     ,np.asarray( [ abs(value[-1])*100 for key, value in sorted(purities[fit][loc][pid][ptCut[0]][metCut[0]].iteritems()) ]) )
                    pprint(isoVals)
                    pprint(puritiesCalc)

                    params = [ 0.01, 10.0 ]
                    paramsInit = params

                    def purityFunc(_params, _iso):
                        purity_ = _params[0] # + _params[1] * _iso
                        return purity_
                    
                    def resFunc(_params, _iso, _purity):
                        err = ( _purity[0] - purityFunc(_params, _iso) ) / _purity[1]
                        return err

                    
                    paramsFit = leastsq(resFunc, paramsInit, args=(isoVals, puritiesCalc), full_output=1, warning=True )
                    pprint(paramsFit)

                    isosFit = np.arange(0.0,10.5,0.5)
                    puritiesFit = [ purityFunc(paramsFit[0], iso) for iso in  isosFit]
                    #pprint(isosFit)
                    #pprint(puritiesFit)
                    
                    
                    plot.figure()
                    plot.errorbar(isoVals, puritiesCalc[0], yerr=puritiesCalc[1], fmt='ko', markersize=8.0, capsize=8, solid_capstyle='projecting', elinewidth=2)
                    plot.plot(isosFit, puritiesFit, 'r-', linewidth=1.0)
                    # plot.legend(['Measured', 'Fit'])
                    plot.xlim(0.,10.)
                    plot.ylim(0.0,10.0)
                    # plot.ylim(2.5,7.5)
                    plot.tick_params(axis='both', which='major', labelsize=16)
                    plot.ylabel(r'Impurity (%)', fontsize=24)
                    plot.xlabel(r'Charged Hadron Isolation (GeV)', fontsize=24)
                    outName = os.path.join(outDir,'purityfit_'+loc+'_'+pid+'_'+ptCut[0]+'_'+metCut[0]+'_flat')
                    plot.savefig(outName+'.pdf', format='pdf')
                    plot.savefig(outName+'.png', format='png')
