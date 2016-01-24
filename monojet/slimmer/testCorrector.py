#! /usr/bin/python

import Corrector

Corrector.MakeApplicator('test',True,'events','test',1000000)
Corrector.AddCorrector(Corrector.MakeCorrector('test1','npv','','files/puWeights_13TeV_25ns.root','puWeights'))

Corrector.RunApplicator('/home/dabercro/GradSchool/Winter15/SkimV008',2)
