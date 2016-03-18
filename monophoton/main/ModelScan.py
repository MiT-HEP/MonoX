#!/usr/bin/env python

from argparse import ArgumentParser
import os
import sys
from subprocess import Popen, PIPE
import shutil
from pprint import pprint
import datetime

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from plotstyle import *
from datasets import allsamples

parser = ArgumentParser()
parser.add_argument('-m', '--models', metavar = 'MODEL', action = 'store', default = [], nargs='+', help = 'Signal model(s) to compute limits for.')
parser.add_argument('-R', '--root-file', metavar = 'PATH', action = 'store', dest = 'rootFile', help = 'Histogram ROOT file.')
parser.add_argument('--variable', '-v', metavar = 'VARNAME', action = 'store', dest = 'variable', default = 'phoPtHighMet', help = 'Discriminating variable.')
parser.add_argument('--shape', '-s', action = 'store_true', dest = 'shape', default = False, help = 'Turn on shape analysis.')

opts = parser.parse_args()

mandatories = ['rootFile']
for m in mandatories:
    if not opts.__dict__[m]:
        print "\nMandatory option is missing\n"
        parser.print_help()
        exit(-1)

###======================================================================================
### Function to Run Higgs Tool and Get Expected Limit for a DataCard
###======================================================================================

def RunHiggsTool(DataCardPath,LimitToolDir):
    TextPath = DataCardPath
    HiggsTool = Popen(['combine','-M','Asymptotic',TextPath],
                      stdout=PIPE,stderr=PIPE,cwd=LimitToolDir)    
    """ For debugging, will cause grep step to crash
    (hout, herr) = HiggsTool.communicate()
    print hout, '\n'
    print herr, '\n'
    """


    find = Popen(['egrep','Observed|50.0%'],stdin=HiggsTool.stdout,stdout=PIPE,stderr=PIPE)
    """ for debugging, will cause next step to crash
    (fout, ferr) = find.communicate()
    print fout, '\n'
    print ferr, '\n'
    """

    lines = [line for line in find.stdout]
    # print lines

    obs = -1.
    exp = -1.

    for line in lines:
        # print line
        tmp = line.split()
        # print tmp
        if tmp:
            if 'Observed' in tmp[0]:
                obs = float(tmp[4])
            elif "Expected" in tmp[0]:
                exp = float(tmp[4])

    return (obs, exp)


###======================================================================================
### Make Datacards and compute limits
###======================================================================================

classes = {} # "dmv" : ( [mMed], [mDM] ) 
for model in sorted(allsamples): 
    if not model.signal:
        continue
    (name, xval, yval) = model.name.split('-')
    if not name in classes.keys():
        classes[name] = ( [], [] )
    if not xval in classes[name][0]:
        classes[name][0].append(xval)
    if not yval in classes[name][1]:
        classes[name][1].append(yval)

# pprint(classes)

modelList = opts.models
if modelList == []:
    for sample in allsamples:
        if sample.signal:
            modelList.append(sample.name)

LimitToolDir = os.path.join(os.environ['CMSSW_BASE'], 'src/HiggsAnalysis/CombinedLimit')
cardDir = os.path.join(LimitToolDir, 'data/monoph')
if not os.path.exists(cardDir):
    os.makedirs(cardDir)

rootFilePath = os.path.join(cardDir, opts.rootFile)
shutil.copy(opts.rootFile, rootFilePath)

print datetime.datetime.now(), '\n'

limits = {} # "dmv-500-150" : ( Obs, Exp )
print "%16s %15s %15s" % ('model', 'Observed (1/fb)', 'Expected (1/fb)')
for iM, model in enumerate(modelList):
    try:
        allsamples[model]
    except:
        print 'Skipping', model
        continue

    '''./datacard.py dma-500-1 limitsfile.root -o test.txt -O -v phoPtHighMet'''
    cardPath = os.path.join(cardDir, model+'_'+opts.variable+'.txt')
    argList = ['./datacard.py', model, opts.rootFile, '-v', opts.variable, '-o', cardPath]
    if opts.shape:
        argList.append('-s')
    MakeDataCard = Popen(argList, stdout=PIPE, stderr=PIPE)
    
    (out, err) = MakeDataCard.communicate()
    # print out, '\n'
    # print err, '\n'
        
    (obs, exp) = RunHiggsTool(cardPath,LimitToolDir)

    if allsamples[model].scale != 1.:
        obs = obs * allsamples[model].scale
        exp = exp * allsamples[model].scale

    obs = obs * allsamples[model].crosssection * 1000. # to 1/fb
    exp = exp * allsamples[model].crosssection * 1000. # to 1/fb

    limits[model] = (obs, exp)

    if obs < 0.1 or exp < 0.1:
        print "%16s %15.1E %15.1E" % (model, limits[model][0], limits[model][1])
    else:
        print "%16s %15.1f %15.1f" % (model, limits[model][0], limits[model][1])

print datetime.datetime.now()
