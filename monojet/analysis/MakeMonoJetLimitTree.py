#! /usr/bin/python

from MakeMonoJetIncLimitTree import *

ltm.SetOutFileName('MonoJetLimitsTrees.root')
SetCuts(ltm,'monoJet')
ltm.MakeTrees()
