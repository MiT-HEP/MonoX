#! /usr/bin/python

import Corrector
import os,sys

directory = sys.argv[1]

applicator = Corrector.MakeApplicator('',True,'events','events',100000)

def addCorr(name,expr,cut,fileName,histName):
    applicator.AddCorrector(Corrector.MakeCorrector(name,expr,cut,fileName,histName))
##

addCorr('METTrigger','met','1','files/triggerEffs.root','MET_trigger')

for fileName in os.listdir(directory):
    if not '.root' in fileName:
        continue
    ##

    applicator.ApplyCorrections(directory + "/" + fileName)
##
