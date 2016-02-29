#! /usr/bin/python

from Stack import *

gjetBRegion = ['gjets_noBVeto']
ReadExceptionConfig('gjets')

if __name__ == '__main__':
    RunPlots(gjetBRegion)
