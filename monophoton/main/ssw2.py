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
#argParser.add_argument('--eos-input', '-e', action = 'store_true', dest = 'eosInput', help = 'Specify that input needs to be read from eos.')
argParser.add_argument('--nentries', '-N', metavar = 'N', dest = 'nentries', type = int, default = -1, help = 'Maximum number of entries.')
argParser.add_argument('--timer', '-T', action = 'store_true', dest = 'timer', help = 'Turn on timers on Selectors.')
argParser.add_argument('--compile-only', '-C', action = 'store_true', dest = 'compileOnly', help = 'Compile and exit.')
argParser.add_argument('--json', '-j', metavar = 'PATH', dest = 'json', default = '/cvmfs/cvmfs.cmsaf.mit.edu/hidsk0001/cmsprod/cms/json/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt', help = 'Good lumi list to apply.')
argParser.add_argument('--catalog', '-c', metavar = 'PATH', dest = 'catalog', default = '/home/cmsprod/catalog/t2mit', help = 'Source file catalog.')
argParser.add_argument('--filesets', '-f', metavar = 'ID', dest = 'filesets', nargs = '+', default = [], help = 'Fileset id to run on.')
argParser.add_argument('--suffix', '-x', metavar = 'SUFFIX', dest = 'outSuffix', default = '', help = 'Output file suffix.')
argParser.add_argument('--split', '-B', action = 'store_true', dest = 'split', help = 'Use condor-run to run one instance per fileset. Output is merged at the end.')
argParser.add_argument('--skip-existing', '-X', action = 'store_true', dest = 'skipExisting', help = 'Do not run skims on files that already exist.')
argParser.add_argument('--merge', '-M', action = 'store_true', dest = 'merge', help = 'Merge the fragments without running any skim jobs.')
argParser.add_argument('--interactive', '-I', action = 'store_true', dest = 'interactive', help = 'Force interactive execution with split or merge.')
argParser.add_argument('--skip-photonSkim', '-S', action = 'store_true', dest = 'skipPhotonSkim', help = 'Skip photon skim step.')
argParser.add_argument('--selectors', '-s', metavar = 'SELNAME', dest = 'selnames', nargs = '+', default = [], help = 'Selectors to merge.')

# eosInput:
# Case for running on LXPLUS (used for ICHEP 2016 with simpletree from MINIAOD)
# not maintained any more - use github to recover

args = argParser.parse_args()
sys.argv = []

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
monoxdir = os.path.dirname(basedir)

sys.path.append(basedir)
import config

logging.basicConfig(level = config.printLevel)
logger = logging.getLogger(__name__)

logger.debug('Running at %s', socket.gethostname())

from datasets import allsamples
from main.skimconfig import selectors

sys.path.append(monoxdir + '/common')
from goodlumi import makeGoodLumiFilter

sys.path.append('/home/yiiyama/lib')
from condor_run import CondorRun

batch = (args.split or args.merge) and not args.interactive

if args.merge and batch and len(args.selnames) != 0:
    logger.error('Batch merge mode must be inclusive in selectors.')
    sys.exit(1)

if args.split and len(args.filesets) != 0:
    logger.error('Split mode must be inclusive in filesets.')
    sys.exit(1)

import ROOT

ROOT.gSystem.Load(config.libobjs)
ROOT.gSystem.AddIncludePath('-I' + config.dataformats)
ROOT.gSystem.AddIncludePath('-I' + os.path.dirname(basedir) + '/common')

logger.debug('dataformats: %s', config.dataformats)

ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')
try:
    s = ROOT.Skimmer
except:
    logger.error("Couldn't compile Skimmer.cc. Quitting.")
    sys.exit(1)

if args.compileOnly:
    sys.exit(0)

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


def executeSkim(sample, filesets, outDir):
    """
    Set up the skimmer, clean up the destination, request T2->T3 downloads if necessary, and execute the skim.
    """

    skimmer = ROOT.Skimmer()
    if args.skipPhotonSkim:
        skimmer.skipPhotonSkim()
    else:
        skimmer.setCommonSelection('superClusters.rawPt > 175. && TMath::Abs(superClusters.eta) < 1.4442')

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

    for path in sample.files(filesets):
        if not os.path.exists(path):
            fname = os.path.basename(path)
            dataset = os.path.basename(os.path.dirname(path))
            proc = Popen(['/usr/local/DynamicData/SmartCache/Client/addDownloadRequest.py', '--file', fname, '--dataset', dataset, '--book', sample.book], stdout = PIPE, stderr = PIPE)
            print proc.communicate()[0].strip()

        logger.debug('Add input: %s', path)
        skimmer.addPath(path)
   
    outNameBase = sample.name

    outSuffix = None
    if args.outSuffix:
        outSuffix = args.outSuffix
    elif len(filesets) == 1 and len(sample.filesets()) > 1:
        outSuffix = filesets[0]

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

    for rname, gen in selectors[sample.name]:
        outName = outNameBase + '_' + rname + '.root'

        logger.info('Copying output to %s/%s', outDir, outName)
        shutil.copy(tmpDir + '/' + outName, outDir)
        logger.info('Removing %s/%s', tmpDir, outName)
        os.remove(tmpDir + '/' + outName)


for sample in samples:
    print 'Starting sample %s (%d/%d)' % (sample.name, samples.index(sample) + 1, len(samples))

    splitOutDir = config.skimDir + '/' + sample.name

    if len(args.filesets) != 0 and len(sample.filesets()) > 1:
        outDir = splitOutDir
        fslist = args.filesets
    else:
        outDir = config.skimDir
        fslist = sorted(sample.filesets())

    try:
        os.makedirs(outDir)
    except OSError:
        pass

    if batch:
        # Batch mode - only need to collect the input names
        # Will spawn condor jobs below
        continue

    # Will do the actual merging
    if args.merge:
        print 'Merging.'

        selnames = args.selnames
        if selnames == []:
            selnames = [rname for rname, gen in selectors[sample.name]]

        for selname in selnames:
            for fileset in fslist:
                fname = splitOutDir + '/' + sample.name + '_' + fileset + '_' + selname + '.root'
                if not os.path.exists(fname) or os.stat(fname).st_size == 0:
                    raise RuntimeError('Missing input file', fname)

            outName = sample.name + '_' + selname + '.root'

            mergePath = mergeDir + '/' + outName

            logger.debug('%s %s %s', padd, mergePath, ' '.join(splitOutDir + '/' + sample.name + '_' + fileset + '_' + selname + '.root' for fileset in fslist))
            proc = Popen([padd, mergePath] + [splitOutDir + '/' + sample.name + '_' + fileset + '_' + selname + '.root' for fileset in fslist], stdout = PIPE, stderr = PIPE)
            out, err = proc.communicate()
            print out.strip()
            print err.strip()
    
            logger.info('Copying output to %s/%s', config.skimDir, outName)
            shutil.copy(mergePath, config.skimDir)
            logger.info('Removing %s', mergePath)
            os.remove(mergePath)

    else:
        # Will do the actual skimming
        print 'Skimming.'
        if args.split:
            # Interactive + split -> not very useful. For debugging
            for fileset in fslist:
                executeSkim(sample, [fileset], outDir)
        else:
            executeSkim(sample, fslist, outDir)

# Remainder of the script relates to condor submission
if not batch:
    sys.exit(0)


def waitForCompletion(jobClusters):
    heldJobs = []

    while True:
        proc = Popen(['condor_q'] + jobClusters + ['-af', 'ClusterId', 'JobStatus', 'Arguments'], stdout = PIPE, stderr = PIPE)
        out, err = proc.communicate()
        lines = out.split('\n')
        completed = True
        for line in lines:
            if line.strip() == '':
                continue

            clusterId, jobStatus = line.split()[:2]
            if jobStatus == '5':
                sname, _, fileset = line.split()[3:6] # [2] is the executable
                if (sname, fileset) in heldJobs:
                    continue

                print 'Job %s %s is held' % (sname, fileset)
                heldJobs.append((sname, fileset))
                continue
            
            completed = False

        if completed:
            break

        time.sleep(10)


submitter = CondorRun(os.path.realpath(__file__))
submitter.logdir = '/local/' + os.environ['USER']
submitter.hold_on_fail = True
submitter.group = 'group_t3mit.urgent'

if args.split:
    print 'Submitting skim jobs.'

    # Spawn condor jobs
    arguments = []

    # Collect arguments and remove output
    for sample in samples:
        if len(args.filesets) == 0:
            fslist = sorted(sample.filesets())
        else:
            fslist = args.filesets

        splitOutDir = config.skimDir + '/' + sample.name

        for fileset in fslist:
            if len(sample.filesets()) == 1:
                arguments.append(sample.name)
            else:
                arguments.append((sample.name, fileset))

            # clean up old .log files
            logpath = '/local/' + os.environ['USER'] + '/ssw2/' + sample.name + '_' + fileset + '.0.log'
            logger.debug('Removing %s', logpath)
            try:
                os.remove(logpath)
            except:
                pass

    submitter.job_args = []
    submitter.job_names = []
    for arg in arguments:
        if type(arg) is tuple:
            job_arg = '{0} -f {1}'.format(*arg)
            job_name = '{0}_{1}'.format(*arg)
        else:
            job_arg = arg
            job_name = '%s_0000' % arg

        if args.skipExisting:
            job_arg += ' -X'

        submitter.job_args.append(job_arg)
        submitter.job_names.append(job_name)

    jobClusters = submitter.submit(name = 'ssw2')

    print 'Waiting for individual skim jobs to complete.'

    waitForCompletion(jobClusters)

    print 'All skim jobs finished.'

if args.merge:
    print 'Submitting merge jobs.'

    # Spawn condor jobs
    arguments = []

    # Collect arguments and remove output
    for sample in samples:
        splitOutDir = config.skimDir + '/' + sample.name

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

    submitter.job_args = ['-M -I %s -s %s' % arg for arg in arguments]
    submitter.job_names = ['%s_%s' % arg for arg in arguments]

    jobClusters = submitter.submit(name = 'ssw2')

    print 'Waiting for individual merge jobs to complete.'

    waitForCompletion(jobClusters)

    print 'All merge jobs finished.'
