import os
import sys
from pprint import pprint
#from array import array
# from subprocess import Popen, PIPE
# from ROOT import *
import numpy as np
import matplotlib.pyplot as plot
from scipy.optimize import leastsq
from selections import Version, Locations, PhotonIds, ChIsoSbSels, PhotonPtSels, MetSels
# gROOT.SetBatch(True)

varName = 'sieie'
versDir = os.path.join('/scratch5/ballen/hist/purity',Version,varName)
plotDirs = [ ('shape', '/home/ballen/public_html/cmsplots/SignalContamTemp/') ] # , ('twobin', '/home/ballen/public_html/cmsplots/SignalContamTemp/') ]
outDir = '/home/ballen/public_html/cmsplots/SignalContamTemp/Fitting'
if not os.path.exists(outDir):
    os.makedirs(outDir)

# sources = [ "data" ] 

purities = {}

for plotDir in plotDirs:
    fit = plotDir[0]
    purities[fit] = {}
    for loc in Locations[:1]:
        purities[fit][loc] = {}
        for pid in PhotonIds[1:2]:
            purities[fit][loc][pid] = {}
            for ptCut in PhotonPtSels[0][:1]:
                purities[fit][loc][pid][ptCut[0]] = {}
                for metCut in MetSels[:1]:
                    purities[fit][loc][pid][ptCut[0]][metCut[0]] = {}
                    for chiso in ChIsoSbSels[:-1]:
                        purities[fit][loc][pid][ptCut[0]][metCut[0]][chiso[0]] = {}
                        
                        dirName = loc+'_'+pid+'_'+chiso[0]+'_'+ptCut[0]+'_'+metCut[0] 
                        condorFileName = os.path.join(plotDir[1],dirName,"condor.out") 
                        # print condorFileName
                        condorFile = open(condorFileName)
                    
                        match = False
                        for line in condorFile:
                            if "Purity for iteration" in line:
                                # print line
                                tmp = line.split()
                                if tmp:
                                    match = True
                                    # pprint(tmp)
                                    purity = float(tmp[-1].strip("(),"))
                                    # uncertainty = float(tmp[-1].strip("(),"))
                                    # print purity # , uncertainty
                                    purities[fit][loc][pid][ptCut[0]][metCut[0]][chiso[0]] = (purity) # (purity, uncertainty)
                        if not match:
                            print "No purity found for skim:", dirName
                            purities[fit][loc][pid][ptCut[0]][metCut[0]][chiso[0]] = (1.025, 0.0)
                        condorFile.close()
pprint(purities)


for loc in Locations[:1]:
    for pid in PhotonIds[1:2]:
        for ptCut in PhotonPtSels[0][:1]:
            for metCut in MetSels[:1]:
                for plotDir in plotDirs:
                    fit = plotDir[0] 
                    isoVals = np.array([ float(key.split('o')[1].strip('t'))/10.0 for key in sorted(purities[fit][loc][pid][ptCut[0]][metCut[0]]) ])
                    #isoVals = np.arange(2.0,8.5,0.5)
                    puritiesCalc = np.array([ 1 - value for key, value in sorted(purities[fit][loc][pid][ptCut[0]][metCut[0]].iteritems()) ])
                    #pprint(isoVals)
                    #pprint(puritiesCalc)

                    params = [ 0.01, 10.0 ]
                    paramsInit = params

                    def purityFunc(_params, _iso):
                        purity_ = _params[0] + _params[1] * _iso
                        return purity_
                    
                    def resFunc(_params, _iso, _purity):
                        err = _purity - purityFunc(_params, _iso)
                        return err

                    paramsFit = leastsq(resFunc, paramsInit, args=(isoVals, puritiesCalc), full_output=1, warning=True )
                    pprint(paramsFit)

                    isosFit = np.arange(0.0,10.5,0.5)
                    puritiesFit = [ purityFunc(paramsFit[0], iso) for iso in  isosFit]
                    #pprint(isosFit)
                    #pprint(puritiesFit)
                    
                    plot.plot(isoVals, puritiesCalc, 'k.', isosFit, puritiesFit, 'r-')
                    plot.legend(['Measured', 'Fit'])
                    plot.xlim(0.,10.)
                    plot.ylim(0.00,0.10)
                    plot.ylabel(r'Impurity')
                    plot.xlabel(r'Charged Hadron Isolation (GeV)')
                    outName = os.path.join(outDir,'purityfit_'+loc+'_'+pid+'_'+ptCut[0]+'_'+metCut[0])
                    plot.savefig(outName+'.pdf', format='pdf')
                    plot.savefig(outName+'.png', format='png')
