#! /usr/bin/python

from MakeMonoJetIncLimitTree import *

ltm.SetOutFileName('MonoVLimitsTrees.root')
SetupFromEnv(ltm,'monoV')
ltm.MakeTrees()
