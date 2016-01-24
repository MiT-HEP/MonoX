#! /usr/bin/python

import Corrector
import os

directory = '/afs/cern.ch/work/d/dabercro/public/Winter15/SkimTest'

applicator = Corrector.MakeApplicator('test',True,'events','test',1000000)
applicator.AddCorrector(Corrector.MakeCorrector('test1','npv','1','files/puWeights_13TeV_25ns.root','puWeights'))

for fileName in os.listdir(directory):
    applicator.ApplyCorrections(directory + "/" + fileName)
##
