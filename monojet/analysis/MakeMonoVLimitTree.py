#! /usr/bin/python

from MakeMonoJetIncLimitTree import *

ltm.SetOutFileName('MonoVLimitsTrees.root')
SetCuts(ltm,'monoV')
ltm.MakeTrees()
