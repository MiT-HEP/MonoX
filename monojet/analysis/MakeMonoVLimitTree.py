#! /usr/bin/python

from MakeMonoJetIncLimitTree import *

ltm.SetOutFileName('MonoVLimitsTrees.root')
SetCuts(ltm,'monoV')

if __name__ == '__main__':
    ltm.MakeTrees()
