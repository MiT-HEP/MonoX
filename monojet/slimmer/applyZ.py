#! /usr/bin/python

from CrombieTools.SkimmingTools import Corrector
import os,sys

directory = sys.argv[1]

applicator = Corrector.MakeApplicator('',True,'events','postfit',100000)

acorrector = Corrector.MakeCorrector('postfit','met','0 == 1','files/JustZ.root','PostFits')

applicator.AddCorrector(acorrector)

z_ = { 'cut'   : '1',
       'list'  : ['DYJets','ZJets'] }

for fileName in os.listdir(directory):
    if not '.root' in fileName:
        continue

    acorrector.SetInCut('0 == 1')

    for testName in z_['list']:
        if testName in fileName:
            print '##################'
            print fileName, ' is getting special treatments!!!!'
            print '##################'
            acorrector.SetInCut(z_['cut'])

    applicator.ApplyCorrections(directory + "/" + fileName)
