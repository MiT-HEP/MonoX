#! /usr/bin/python

from MakeMonoJetIncLimitTree import *

ltm.SetOutFileName('MonoJetLimitsTrees.root')
SetCuts(ltm,'monoJet')

if __name__ == '__main__':
    ltm.MakeTrees()
