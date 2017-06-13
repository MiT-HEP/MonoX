#!/usr/bin/env python

import os
import sys
import shutil

if sys.argv[1] == 'skim':
    task = 'skim'
    sname = sys.argv[2]
    fileset = sys.argv[3]
else:
    task = 'submit'
    snames = sys.argv[1:]

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

if task == 'submit':
    sys.path.append('/home/yiiyama/lib')
    from condor_run import CondorRun
    
    submitter = CondorRun(os.path.realpath(__file__))
    submitter.logdir = '/local/' + os.environ['USER']
    submitter.hold_on_fail = True
    submitter.min_memory = 1

    for sname in snames:
        submitter.pre_args = 'skim ' + sname
    
        filesets = set()
        with open(thisdir + '/catalog/' + sname + '.txt') as catalog:
            for line in catalog:
                filesets.add(line.split()[0])
    
        filesets = sorted(list(filesets))
    
        submitter.job_args = filesets
        submitter.job_names = ['%s_%s' % (sname, fileset) for fileset in filesets]
            
        submitter.submit(name = 'skimUncleaned')

elif task == 'skim':
    import ROOT
    
    ROOT.gSystem.Load(config.libobjs)
    try:
        e = ROOT.panda.Event
    except AttributeError:
        pass
    
    ROOT.gROOT.LoadMacro(thisdir + '/skimUncleaned.cc+')
    
    datadir = '/mnt/hadoop/scratch/yiiyama/ftpanda'

    tree = ROOT.TChain('events')

    with open(thisdir + '/catalog/' + sname + '.txt') as catalog:
        for line in catalog:
            if line.split()[0] == fileset:
                print line.split()[1]
                tree.Add(line.split()[1])
    
    fname = sname + '_' + fileset + '_offtime.root'
    tmpdir = '/local/' + os.environ['USER']
    if not os.path.exists(tmpdir):
        tmpdir = '/tmp/' + os.environ['USER']
    
    tmpname = tmpdir + '/skimUncleaned/' + sname + '/' + fname
    finalname = '/mnt/hadoop/scratch/' + os.environ['USER'] + '/monophoton/skim/' + sname + '/' + fname
    
    try:
        os.makedirs(os.path.dirname(tmpname))
    except:
        pass
    
    try:
        os.makedirs(os.path.dirname(finalname))
    except:
        pass
    
    outputFile = ROOT.TFile.Open(tmpname, 'recreate')
    
    ROOT.skimUncleaned(tree, outputFile)
    
    outputFile.Close()
 
    shutil.copy(tmpname, finalname)
    os.remove(tmpname)
