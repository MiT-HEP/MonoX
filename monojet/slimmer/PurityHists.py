#! /usr/bin/python

from HistWriter import histWriter as writer

writer.SetFileName('files/Purity.root')
writer.SetHistName('purity')

writer.MakeHist('files/Purity.txt')
