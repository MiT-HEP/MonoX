#! /usr/bin/python

from MakeMonoJetIncLimitTree import *

ltm.SetOutFileName('MonoJetLimitsTrees.root')
SetupFromEnv(ltm,'monoJet')
ltm.MakeTrees()
