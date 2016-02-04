#! /usr/bin/python

from HistWriter import histWriter as writer

writer.SetFileName('files/triggerEffs.root')
writer.SetHistName('MET_trigger')

writer.MakeHist('files/METTrigger.txt')
