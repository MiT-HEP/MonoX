#!/usr/bin/env python

import sys
import os
import socket
import time
import shutil
import collections
import logging
from subprocess import Popen, PIPE
from argparse import ArgumentParser

argParser = ArgumentParser(description = 'Plot and count')
argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '*', help = 'Sample names to skim.')
argParser.add_argument('--list', '-L', action = 'store_true', dest = 'list', help = 'List of samples.')
argParser.add_argument('--nentries', '-N', metavar = 'N', dest = 'nentries', type = int, default = -1, help = 'Maximum number of entries.')
argParser.add_argument('--timer', '-T', action = 'store_true', dest = 'timer', help = 'Turn on timers on Selectors.')
argParser.add_argument('--compile-only', '-C', action = 'store_true', dest = 'compileOnly', help = 'Compile and exit.')
argParser.add_argument('--json', '-j', metavar = 'PATH', dest = 'json', default = '/cvmfs/cvmfs.cmsaf.mit.edu/hidsk0001/cmsprod/cms/json/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt', help = 'Good lumi list to apply.')
argParser.add_argument('--catalog', '-c', metavar = 'PATH', dest = 'catalog', default = '/home/cmsprod/catalog/t2mit', help = 'Source file catalog.')
argParser.add_argument('--filesets', '-f', metavar = 'ID', dest = 'filesets', nargs = '+', default = [], help = 'Fileset id to run on.')
argParser.add_argument('--files', '-i', metavar = 'PATH', dest = 'files', nargs = '+', default = [], help = 'Directly run on files.')
argParser.add_argument('--suffix', '-x', metavar = 'SUFFIX', dest = 'outSuffix', default = '', help = 'Output file suffix.')
argParser.add_argument('--batch', '-B', action = 'store_true', dest = 'batch', help = 'Use condor-run to run.')
argParser.add_argument('--skip-existing', '-X', action = 'store_true', dest = 'skipExisting', help = 'Do not run skims on files that already exist.')
argParser.add_argument('--merge', '-M', action = 'store_true', dest = 'merge', help = 'Merge the fragments without running any skim jobs.')
argParser.add_argument('--selectors', '-s', metavar = 'SELNAME', dest = 'selnames', nargs = '+', default = [], help = 'Selectors to process.')
argParser.add_argument('--printlevel', '-p', metavar = 'LEVEL', dest = 'printLevel', default = '', help = 'Override config.printLevel')
argParser.add_argument('--no-wait', '-W', action = 'store_true', dest = 'noWait', help = '(With batch option) Don\'t wait for job completion.')
argParser.add_argument('--test-run', '-E', action = 'store_true', dest = 'testRun', help = 'Don\'t copy the output files to the production area.')

DEFAULT_NTUPLES_DIR = '/mnt/hadoop/cms/store/user/paus'

args = argParser.parse_args()
sys.argv = []

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
monoxdir = os.path.dirname(basedir)

sys.path.append(basedir)
import config

try:
    printLevel = getattr(logging, args.printLevel.upper())
except AttributeError:
    printLevel = config.printLevel

logging.basicConfig(level = printLevel)
logger = logging.getLogger(__name__)

logger.debug('Running at %s', socket.gethostname())

from datasets import allsamples
from main.skimconfig import selectors as allSelectors

import ROOT

ROOT.gSystem.AddIncludePath('-I' + os.path.dirname(basedir) + '/common')

logger.debug('dataformats: %s', config.dataformats)

ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')

try:
    s = ROOT.Skimmer
except:
    logger.error("Couldn't compile Skimmer.cc. Quitting.")
    sys.exit(1)

if args.compileOnly:
    print 'hello'
    sys.exit(0)

sys.path.append(monoxdir + '/common')
from goodlumi import makeGoodLumiFilter

sys.path.append('/home/yiiyama/lib')
from condor_run import CondorRun

if len(args.files) != 0 and len(args.filesets) != 0:
    logger.error('Cannot set filesets and files simultaneously.')
    sys.exit(1)

if len(args.selnames) != 0:
    selectors = {}
    for sname, sels in allSelectors.items():
        selectors[sname] = []
        for rname, gen in sels:
            if rname in args.selnames:
                selectors[sname].append((rname, gen))

else:
    selectors = allSelectors

if 'all' in args.snames:
    spatterns = selectors.keys()
elif 'bkgd' in args.snames:
    spatterns = selectors.keys() + ['!add*', '!dm*']
else:
    spatterns = list(args.snames)

samples = allsamples.getmany(spatterns)

if args.list:
    print ' '.join(sorted(s.name for s in samples))
    sys.exit(0)

if args.merge:
    padd = os.environ['CMSSW_BASE'] + '/bin/' + os.environ['SCRAM_ARCH'] + '/padd'

if len(args.files) != 0:
    # make a dummy fileset
    args.filesets = ['manual']


def executeSkim(sample, fileset, outDir):
    """
    Set up the skimmer, clean up the destination, request T2->T3 downloads if necessary, and execute the skim.
    """

    skimmer = ROOT.Skimmer()

    skimmer.setPrintLevel(printLevel)

    for rname, gen in selectors[sample.name]:
        selector = gen(sample, rname)
        selector.setUseTimers(args.timer)
        skimmer.addSelector(selector)

    tmpDir = '/local/' + os.environ['USER'] + '/' + sample.name
    try:
        os.makedirs(tmpDir)
    except OSError:
        pass

    if not os.path.isdir(tmpDir):
        tmpDir = '/tmp/' + os.environ['USER'] + '/' + sample.name
        try:
            os.makedirs(tmpDir)
        except OSError:
            pass

    logger.debug('getting all input files')

    if fileset == 'manual':
        for path in args.files:
            skimmer.addPath(path)
    else:
        for path in sample.files([fileset]):
            if config.ntuplesDir == DEFAULT_NTUPLES_DIR:
                if not os.path.exists(path):
                    fname = os.path.basename(path)
                    dataset = os.path.basename(os.path.dirname(path))
                    proc = Popen(['/usr/local/DynamicData/SmartCache/Client/addDownloadRequest.py', '--file', fname, '--dataset', dataset, '--book', sample.book], stdout = PIPE, stderr = PIPE)
                    print proc.communicate()[0].strip()

            else:
                path = path.replace(DEFAULT_NTUPLES_DIR, config.ntuplesDir)
    
            logger.debug('Add input: %s', path)
            skimmer.addPath(path)

    outNameBase = sample.name

    outSuffix = None
    if args.outSuffix:
        outSuffix = args.outSuffix
    elif fileset == 'manual':
        outSuffix = 'manual'
    elif len(sample.filesets()) > 1:
        outSuffix = fileset

    if outSuffix is not None:
        outNameBase += '_' + outSuffix

    if args.skipExisting:
        logger.info('Checking for existing files.')
    else:
        logger.info('Removing existing files.')

    for selname in [rname for rname, gen in selectors[sample.name]]:
        outName = outDir + '/' + outNameBase + '_' + selname + '.root'
        logger.debug(outName)

        if args.skipExisting:
            if not os.path.exists(outName) or os.stat(outName).st_size == 0:
                break
            logger.debug('%s exists.', outName)
        else:
            try:
                os.remove(outName)
            except:
                pass

    else:
        if args.skipExisting:
            logger.info('Output files for %s already exist. Skipping skim.', outNameBase)
            return

    if sample.data and args.json:
        logger.info('Good lumi filter: %s', args.json)
        skimmer.setGoodLumiFilter(makeGoodLumiFilter(args.json))

    logger.debug('Skimmer.run(%s, %s, %s, %d)', tmpDir, outNameBase, sample.data, args.nentries)
    skimmer.run(tmpDir, outNameBase, sample.data, args.nentries)

    del skimmer

    for rname, gen in selectors[sample.name]:
        outName = outNameBase + '_' + rname + '.root'

        if args.testRun:
            logger.info('Output at %s/%s', tmpDir, outName)
        else:
            logger.info('Copying output to %s/%s', outDir, outName)
            shutil.copy(tmpDir + '/' + outName, outDir)
            logger.info('Removing %s/%s', tmpDir, outName)
            os.remove(tmpDir + '/' + outName)

#def executeSkim

def executeMerge(sample, selname, fslist):
    mergeDir = '/local/' + os.environ['USER'] + '/ssw2/merge'
    try:
        os.makedirs(mergeDir)
    except OSError:
        pass

    if not os.path.isdir(mergeDir):
        mergeDir = '/tmp/' + os.environ['USER'] + '/ssw2/merge'
        try:
            os.makedirs(mergeDir)
        except OSError:
            pass

    inDir = config.skimDir + '/' + sample.name

    for fileset in fslist:
        fname = inDir + '/' + sample.name + '_' + fileset + '_' + selname + '.root'
        if not os.path.exists(fname) or os.stat(fname).st_size == 0:
            raise RuntimeError('Missing input file', fname)

    outName = sample.name + '_' + selname + '.root'

    mergePath = mergeDir + '/' + outName

    logger.debug('%s %s %s', padd, mergePath, ' '.join(inDir + '/' + sample.name + '_' + fileset + '_' + selname + '.root' for fileset in fslist))
    proc = Popen([padd, mergePath] + [inDir + '/' + sample.name + '_' + fileset + '_' + selname + '.root' for fileset in fslist], stdout = PIPE, stderr = PIPE)
    out, err = proc.communicate()
    print out.strip()
    print err.strip()

    if args.testRun:
        logger.info('Output at %s', mergePath)
    else:
        logger.info('Copying output to %s/%s', config.skimDir, outName)
        shutil.copy(mergePath, config.skimDir)
        logger.info('Removing %s', mergePath)
        os.remove(mergePath)

#def executeMerge


for sample in samples:
    print 'Starting sample %s (%d/%d)' % (sample.name, samples.index(sample) + 1, len(samples))

    if len(args.filesets) != 0 and args.filesets[0] == 'manual':
        outDir = config.skimDir
    elif len(sample.filesets()) > 1:
        outDir = config.skimDir + '/' + sample.name
    else:
        outDir = config.skimDir

    try:
        os.makedirs(outDir)
    except OSError:
        pass

    if args.batch:
        # Batch mode - only need to collect the input names
        # Will spawn condor jobs below
        continue

    if len(args.filesets) != 0:
        fslist = sorted(args.filesets)
    else:
        fslist = sorted(sample.filesets())

    # Will do the actual merging
    if args.merge:
        print 'Merging.'
        # Merge outputs for each sample-selector combination
        selnames = [rname for rname, gen in selectors[sample.name]]
        for selname in selnames:
            executeMerge(sample, selname, fslist)
    else:
        # Will do the actual skimming
        print 'Skimming.'
        # Create an output for each fileset separately
        for fileset in fslist:
            executeSkim(sample, fileset, outDir)

# Remainder of the script relates to condor submission
if not args.batch:
    sys.exit(0)


def waitForCompletion(jobClusters, argTemplate):
    heldJobs = []

    argsToExtract = []
    for ia, a in enumerate(argTemplate.split()):
        if a == '%s':
            argsToExtract.append(ia)

    while True:
        proc = Popen(['condor_q'] + jobClusters + ['-af', 'ClusterId', 'JobStatus', 'Arguments'], stdout = PIPE, stderr = PIPE)
        out, err = proc.communicate()
        lines = out.split('\n')
        completed = True
        for line in lines:
            if line.strip() == '':
                continue

            words = line.split()

            clusterId, jobStatus = words[:2]
            if jobStatus == '5':
                args = tuple(words[3 + i] for i in argsToExtract)
                if args in heldJobs:
                    continue

                print 'Job %s is held' % str(args)
                heldJobs.append(args)
                continue
            
            completed = False

        if completed:
            break

        time.sleep(10)


submitter = CondorRun(os.path.realpath(__file__))
submitter.logdir = '/local/' + os.environ['USER']
submitter.hold_on_fail = True
submitter.group = 'group_t3mit.urgent'

if args.merge:
    print 'Submitting merge jobs.'

    # Spawn condor jobs
    arguments = []

    # Collect arguments and remove output
    for sample in samples:
        for selname in [rname for rname, gen in selectors[sample.name]]:
            arguments.append((sample.name, selname))

            # clean up old .log files
            path = '/local/' + os.environ['USER'] + '/ssw2/' + sample.name + '_' + selname + '.0.log'
            logger.debug('Removing %s', path)
            try:
                os.remove(path)
            except:
                pass

            # not sure if I want to delete old file immediately
            path = config.skimDir + '/' + sample.name + '_' + selname + '.root'
            logger.debug('Removing %s', path)
            try:
                os.remove(path)
            except:
                pass

    argTemplate = '-M %s -s %s'
    submitter.job_args = [argTemplate % arg for arg in arguments]
    submitter.job_names = ['%s_%s' % arg for arg in arguments]

    jobClusters = submitter.submit(name = 'ssw2')

    if args.noWait:
        print 'Jobs have been submitted.'
    else:
        print 'Waiting for individual merge jobs to complete.'
        waitForCompletion(jobClusters, argTemplate)
        print 'All merge jobs finished.'

else:
    print 'Submitting skim jobs.'

    # Spawn condor jobs
    arguments = []

    # Collect arguments and remove output
    for sample in samples:
        if len(args.filesets) == 0:
            fslist = sorted(sample.filesets())
        else:
            fslist = args.filesets

        for fileset in fslist:
            arguments.append((sample.name, fileset))

            # clean up old .log files
            logpath = '/local/' + os.environ['USER'] + '/ssw2/' + sample.name + '_' + fileset + '.0.log'
            logger.debug('Removing %s', logpath)
            try:
                os.remove(logpath)
            except:
                pass

    argTemplate = '%s -f %s'
    if args.skipExisting:
        argTemplate += ' -X'

    if len(args.selnames) != 0:
        argTemplate += ' -s ' + ' '.join(args.selnames)

    submitter.job_args = []
    submitter.job_names = []
    for arg in arguments:
        submitter.job_args.append(argTemplate % arg)
        submitter.job_names.append('%s_%s' % arg)

    jobClusters = submitter.submit(name = 'ssw2')

    if args.noWait:
        print 'Jobs have been submitted.'
    else:
        print 'Waiting for individual skim jobs to complete.'
        waitForCompletion(jobClusters, argTemplate)
        print 'All skim jobs finished.'
