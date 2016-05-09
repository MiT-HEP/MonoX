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
import config

parser = ArgumentParser()
parser.add_argument('-m', '--models', metavar = 'MODEL', action = 'store', default = [], nargs='+', help = 'Class of signal models: add, dmv, dma, dmewk')
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


    find = Popen(['egrep','Observed|Expected'],stdin=HiggsTool.stdout,stdout=PIPE,stderr=PIPE)
    """ for debugging, will cause next step to crash
    (fout, ferr) = find.communicate()
    print fout, '\n'
    print ferr, '\n'
    """

    lines = [line for line in find.stdout]
    # print lines

    obs = (-1., -1., -1.)
    exp = (-1., -1., -1.)

    for line in lines:
        # print line
        tmp = line.split()
        # print tmp
        if tmp:
            if 'Observed' in tmp[0]:
                obs = ( float(tmp[4]), float(tmp[4])/1.2, float(tmp[4])/0.8 )
            elif "50.0%" in tmp[0]:
                exp[0] = float(tmp[4])
            elif "16.0%" in tmp[0]:
                exp[1] = float(tmp[4])
            elif "84.0%" in tmp[0]:
                exp[2] = float(tmp[4])

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

modelList = []
if opts.models == []:
    for sample in allsamples:
        if sample.signal:
            modelList.append(sample.name)

if 'add' in opts.models:
    for sample in allsamples:
        if sample.signal and 'add' in sample.name:
            modelList.append(sample.name)
if 'dmv' in opts.models:
    for sample in allsamples:
        if sample.signal and 'dmv' in sample.name and not 'fs' in sample.name:
            modelList.append(sample.name)
if 'dmvfs' in opts.models:
    for sample in allsamples:
        if sample.signal and 'dmvfs' in sample.name:
            modelList.append(sample.name)
if 'dma' in opts.models:
    for sample in allsamples:
        if sample.signal and 'dma' in sample.name and not 'fs' in sample.name:
            modelList.append(sample.name)
if 'dmafs' in opts.models:
    for sample in allsamples:
        if sample.signal and 'dmafs' in sample.name:
            modelList.append(sample.name)
if 'dmewk' in opts.models:
    for sample in allsamples:
        if sample.signal and 'dmewk' in sample.name:
            modelList.append(sample.name)
if 'zgr' in opts.models:
    for sample in allsamples:
        if sample.signal and 'zgr' in sample.name:
            modelList.append(sample.name)

for model in list(opts.models):
    if model in ['add', 'dmv', 'dmvfs', 'dma', 'dmafs', 'dmewk', 'zgr']:
        continue
    try:
        if allsamples[model].signal:
            modelList.append(model)
            opts.models.remove(model)
    except KeyError:
        print model, 'not in datasets.csv. Skipping!'
        opts.models.remove(model)

LimitToolDir = os.path.join(os.environ['CMSSW_BASE'], 'src/HiggsAnalysis/CombinedLimit')
cardDir = os.path.join(LimitToolDir, 'data/monoph')
if not os.path.exists(cardDir):
    os.makedirs(cardDir)

rootFilePath = os.path.join(cardDir, opts.rootFile)
shutil.copy(opts.rootFile, rootFilePath)

print datetime.datetime.now(), '\n'

limits = {} # "dmv-500-150" : ( Obs, Exp )
print "%-16s %15s %15s %15s %15s" % ('model', 'Observed (r)', 'Expected (r)', 'Observed (1/fb)', 'Expected (1/fb)')
for iM, model in enumerate(modelList):
    try:
        allsamples[model]
    except:
        print 'Skipping', model
        continue

    '''./datacard.py dma-500-1 limitsfile.root -o test.txt -O -v phoPtHighMet'''
    cardPath = os.path.join(cardDir, model+'_'+opts.variable+'.txt')
    # print cardPath
    argList = ['./datacard.py', model, opts.rootFile, '-v', opts.variable, '-o', cardPath]
    if opts.shape:
        argList.append('-s')
    MakeDataCard = Popen(argList, stdout=PIPE, stderr=PIPE)
    
    (out, err) = MakeDataCard.communicate()
    # print out, '\n'
    # print err, '\n'
        
    (obs, exp) = RunHiggsTool(cardPath,LimitToolDir)
    # (obs, exp) = (1.0, 1.0)

    if allsamples[model].scale != 1.:
        obsNom =  obs[0] * allsamples[model].scale
        expNom = exp[0] * allsamples[model].scale
    else:
        obsNom = obs[0]
        expNom = exp[0]

    obsXsec = obsNom * allsamples[model].crosssection * 1000. # to 1/fb
    expXsec = expNom * allsamples[model].crosssection * 1000. # to 1/fb

    limits[model] = (obsNom, expNom, obsXsec, expXsec)

    limitString = "%-16s" % model
    
    if obsNom < 0.1 or expNom < 0.1:
        limitString += " %15.1E %15.1E" % (obsNom, expNom)
    else:
        limitString += " %15.2f %15.2f" % (obsNom, expNom)
    if obsXsec < 0.1 or expXsec < 0.1:
        limitString += " %15.1E %15.1E" % (obsXsec, expXsec)
    else:
        limitString += " %15.1f %15.1f" % (obsXsec, expXsec)

    print limitString

print datetime.datetime.now()

# "dmv" : ( [mMed], [mDM] ) 
for name in opts.models:
    params = classes[name]
    xvals = sorted([int(param) for param in params[0]])
    yvals = sorted([int(param) for param in params[1]])

    fileName = "ModelScan_"+name+".tex"
    limitDir = os.path.join(config.webDir, "limits")
    filePath = os.path.join(limitDir, fileName)
    limitsFile = open(filePath, "w")
    
    limitsFile.write(r"\documentclass{article}")
    limitsFile.write("\n")
    limitsFile.write(r"\usepackage[paperheight=2in, paperwidth=16in]{geometry}")
    limitsFile.write("\n")
    limitsFile.write(r"\begin{document}")
    limitsFile.write("\n")
    limitsFile.write(r"\pagenumbering{gobble}")
    limitsFile.write("\n")


    tableString = r"\begin{tabular}{ |r|"
    ylabelString = ""
    for xval in xvals:
        tableString += r"c "
        ylabelString += r" & "+str(xval)
    tableString += r"| }"
    ylabelString += r" \\ "

    limitsFile.write(tableString)
    limitsFile.write("\n")
    limitsFile.write(r"\hline")
    limitsFile.write("\n")

    limitsFile.write(r"$m_\mathrm{DM}$ (GeV) & \multicolumn{"+str(len(params[0]))+r"}{|c|}{$m_\mathrm{MED}$ (GeV)} \\")
    limitsFile.write("\n")
    limitsFile.write(r"\hline")
    limitsFile.write("\n")
    
    limitsFile.write(ylabelString)
    limitsFile.write("\n")
    limitsFile.write(r"\hline")
    limitsFile.write("\n")
    
    rowStrings = []
    for yval in yvals:
        rowString = str(yval)
        for xval in xvals:
            model = name+"-"+str(xval)+"-"+str(yval)
            if model in limits.keys():
                (obs, exp, obsXsec, expXsec) = limits[model]
                if obs < 0. or exp < 0.:
                    rowString += " & "    
                elif obs > 999.9 or exp > 999.9:
                    rowString += " & $>1000$ "
                elif obs < 0.1 or exp < 0.1:
                    rowString += " & %.1E (%.1E)" % (obs, exp)
                else:
                    rowString += " & %.2f (%.2f)" % (obs, exp)
            else:
                rowString += " & "
        rowString += r" \\ "
        limitsFile.write(rowString)
        limitsFile.write("\n")
        
    limitsFile.write(r"\hline")
    limitsFile.write("\n")

    limitsFile.write(r"\end{tabular}")
    limitsFile.write("\n")
    limitsFile.write(r"\end{document}")
    limitsFile.write("\n")
    limitsFile.close()

    pdflatex = Popen( ["pdflatex",filePath,"-interaction nonstopmode"]
                      ,stdout=PIPE,stderr=PIPE,cwd=limitDir)
    pdfout = pdflatex.communicate()
    if not pdfout[1] == "":
        print pdfout[1]
            
    convert = Popen( ["convert",filePath.replace(".tex",".pdf")
                      ,filePath.replace(".tex",".png") ]
                     ,stdout=PIPE,stderr=PIPE,cwd=limitDir)
    conout = convert.communicate()
    if not conout[1] == "":
        print conout[1]
