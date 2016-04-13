#! /usr/bin/python

import ROOT
import sys

theFile = ROOT.TFile(sys.argv[1])

triggerlist = str(theFile.triggerNames.GetTitle()).split(',')

print ''
trigNum = 0
for trigger in triggerlist:
    if trigger != '':
        print str(trigNum) + ' : ' + trigger
        trigNum += 1
print ''
