#! /usr/bin/python

from HistWriter import histWriter as writer

writer.SetFileName('files/JustZ.root')
writer.SetHistName('PostFits')

writer.MakeHist('files/JustZ.txt')
