#!/usr/bin/env python

import os
import subprocess

logger = None

DEFAULT_NTUPLES_DIR = '/mnt/hadoop/cms/store/user/paus'
padd = os.environ['CMSSW_BASE'] + '/bin/' + os.environ['SCRAM_ARCH'] + '/padd'

class SkimSlimWeight(object):

    config = {}

    def __init__(self, sample, selectors, flist, files = False):
        self.sample = sample
        self.selectors = selectors
        if files:
            self.manual = True
            self.filesets = ['manual']
            self.files = flist
        else:
            self.manual = False
            self.filesets = flist
            self.files = []

        if os.path.isdir('/local/' + os.environ['USER']):
            self.tmpDir = '/local/' + os.environ['USER'] + '/' + sample.name
        else:
            self.tmpDir = '/tmp/' + os.environ['USER'] + '/' + sample.name

        if self.manual or sample.filesets() == 1:
            self.outDir = SkimSlimWeight.config['skimDir']
        else:
            self.outDir = SkimSlimWeight.config['skimDir'] + '/' + sample.name

        if os.path.isdir('/local/' + os.environ['USER']):
            self.mergeDir = '/local/' + os.environ['USER'] + '/ssw2/merge'
        else:
            self.mergeDir = '/tmp/' + os.environ['USER'] + '/ssw2/merge'

        # batch-mode attributes
        self.jobClusters = []
        self.argTemplate = ''

    def getOutNameBase(self, fileset):
        if self.manual:
            return self.sample.name + '_manual'
        elif SkimSlimWeight.config['outSuffix']:
            return self.sample.name + '_' + SkimSlimWeight.config['outSuffix']
        else:
            if len(self.sample.filesets()) > 1:
                return self.sample.name + '_' + fileset
            else:
                return self.sample.name

    def setupSkim(self):
        """
        Set up the skimmer, clean up the destination, request T2->T3 downloads if necessary.
        """
    
        if not os.path.exists(self.tmpDir):
            try:
                os.makedirs(self.tmpDir)
            except OSError:
                # did someone beat this job and made the directory?
                if not os.path.exists(self.tmpDir):
                    raise
    
        if not os.path.exists(self.outDir):
            try:
                os.makedirs(self.outDir)
            except OSError:
                if not os.path.exists(self.outDir):
                    raise
    
        logger.debug('getting all input files')

        if not self.manual and SkimSlimWeight.config['ntuplesDir'] == DEFAULT_NTUPLES_DIR:
            for path in self.sample.files(self.filesets):
                if not os.path.exists(path):
                    fname = os.path.basename(path)
                    dataset = os.path.basename(os.path.dirname(path))
                    proc = subprocess.Popen(['/usr/local/DynamicData/SmartCache/Client/addDownloadRequest.py', '--file', fname, '--dataset', dataset, '--book', self.sample.book], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    print proc.communicate()[0].strip()

        if SkimSlimWeight.config['skipExisting']:
            logger.info('Checking for existing files.')
        else:
            logger.info('Removing existing files.')
    
        # abort if any one of the selector output exists
        for fileset in self.filesets:
            outNameBase = self.getOutNameBase(fileset)

            for rname in self.selectors:
                outName = outNameBase + '_' + rname + '.root'
                outPath = self.outDir + '/' + outName
                logger.debug(outPath)
    
                if args.skipExisting:
                    if os.path.exists(outPath) and os.stat(outPath).st_size != 0:
                        logger.info('Output files for %s already exist. Skipping skim.', outNameBase)
                        return False
                else:
                    try:
                        os.remove(outPath)
                    except:
                        pass
    
        return True

    def executeSkim(self):
        """
        Execute the skim.
        """

        skimmer = ROOT.Skimmer()
    
        skimmer.setPrintEvery(SkimSlimWeight.config['printEvery'])
        skimmer.setPrintLevel(SkimSlimWeight.config['printLevel'])
        skimmer.setSkipMissingFiles(SkimSlimWeight.config['skipMissing'])
    
        for rname, gen in self.selectors.items():
            selector = gen(self.sample, rname)
            selector.setUseTimers(SkimSlimWeight.config['timer'])
            skimmer.addSelector(selector)
    
        if self.sample.data and SkimslimWeight.config['json']:
            logger.info('Good lumi filter: %s', SkimSlimWeight.config['json'])
            skimmer.setGoodLumiFilter(makeGoodLumiFilter(SkimSlimWeight.config['json']))

        paths = {} # {filset: list of paths}
    
        if self.manual:
            paths['manual'] = []
            for path in self.files:
                paths['manual'].append(path)

        else:
            for fileset in self.filesets:
                paths[fileset] = []
                for path in sample.files([fileset]):
                    if SkimSlimWeight.config['ntuplesDir'] != DEFAULT_NTUPLES_DIR:
                        path = path.replace(DEFAULT_NTUPLES_DIR, SkimSlimWeight.config['ntuplesDir'])
        
                    logger.debug('Add input: %s %s', fileset, path)
                    paths[fileset].append(path)
    
        for fileset, fnames in paths.items():
            skimmer.clearPaths()
            for fname in fnames:
                skimmer.addPath(fname)

            outNameBase = self.getOutNameBase(fileset)
            nentries = SkimSlimWeight.config['nentries']
    
            logger.debug('Skimmer.run(%s, %s, %s, %d)', self.tmpDir, outNameBase, self.sample.data, nentries)
            skimmer.run(self.tmpDir, outNameBase, self.sample.data, nentries)
    
            for rname in self.selectors:
                outName = outNameBase + '_' + rname + '.root'
        
                if SkimSlimWeight.config['testRun']:
                    logger.info('Output at %s/%s', self.tmpDir, outName)
                else:
                    logger.info('Copying output to %s/%s', self.outDir, outName)
                    shutil.copy(self.tmpDir + '/' + outName, self.outDir)
                    logger.info('Removing %s/%s', self.tmpDir, outName)
                    os.remove(self.tmpDir + '/' + outName)

    def setupMerge(self):
        if not os.path.exists(self.mergeDir):
            try:
                os.makedirs(self.mergeDir)
            except OSError:
                # did someone beat this job and made the directory?
                if not os.path.exists(self.mergeDir):
                    raise

        for rname in self.selectors:
            outNameBase = self.sample.name + '_' + rname
            outName = outNameBase + '.root'
            outPath = SkimSlimWeight.config['skimDir'] + '/' + outName
        
            if SkimSlimWeight.config['skipExisting']:
                if os.path.exists(outPath) and os.stat(outPath).st_size != 0:
                    logger.info('Output files for %s already exist. Skipping merge.', outNameBase)
                    return False
            else:
                try:
                    os.remove(outPath)
                except:
                    pass
    
        return True

    def executeMerge(self):
        inDir = SkimSlimWeight.config['skimDir'] + '/' + self.sample.name

        for rname in self.selectors:
            for fileset in self.filesets:
                fname = inDir + '/' + self.sample.name + '_' + fileset + '_' + rname + '.root'
                if not os.path.exists(fname) or os.stat(fname).st_size == 0:
                    raise RuntimeError('Missing input file', fname)
        
            outNameBase = self.sample.name + '_' + rname
            outName = outNameBase + '.root'
        
            mergePath = self.mergeDir + '/' + outName
            outPath = SkimSlimWeight.config['skimDir'] + '/' + outName
        
            logger.debug('%s %s %s', padd, mergePath, ' '.join(inDir + '/' + self.sample.name + '_' + fileset + '_' + rname + '.root' for fileset in self.filesets))
            proc = subprocess.Popen([padd, mergePath] + [inDir + '/' + self.sample.name + '_' + fileset + '_' + rname + '.root' for fileset in self.filesets], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            out, err = proc.communicate()
            print out.strip()
            print err.strip()
        
            if SkimSlimWeight.config['testRun']:
                logger.info('Output at %s', mergePath)
            else:
                logger.info('Copying output to %s', outPath)
                shutil.copy(mergePath, SkimSlimWeight.config['skimDir'])
                logger.info('Removing %s', mergePath)
                os.remove(mergePath)

    def submitMerge(self, submitter):
        arguments = []
    
        # Collect arguments and remove output
        for rname in self.selectors:

            arguments.append((self.sample.name, rname))

            # clean up old .log files
            path = '/local/' + os.environ['USER'] + '/ssw2/' + self.sample.name + '_' + rname + '.0.log'
            logger.debug('Removing %s', path)
            try:
                os.remove(path)
            except:
                pass
    
        self.argTemplate = '-M %s -s %s'
        submitter.job_args = [self.argTemplate % arg for arg in arguments]
        submitter.job_names = ['%s_%s' % arg for arg in arguments]
    
        self.jobClusters = submitter.submit(name = 'ssw2')

    def submitSkim(self, submitter, skipMissing):
        arguments = []

        for fileset in self.filesets:
            arguments.append((self.sample.name, fileset))

            # clean up old .log files
            logpath = '/local/' + os.environ['USER'] + '/ssw2/' + self.sample.name + '_' + fileset + '.0.log'
            logger.debug('Removing %s', logpath)
            try:
                os.remove(logpath)
            except:
                pass
    
        self.argTemplate = '%s -f %s'
    
        if skipMissing:
            self.argTemplate += ' -K'
    
        self.argTemplate += ' -s ' + ' '.join(self.selectors.keys())
    
        submitter.job_args = []
        submitter.job_names = []
        for arg in arguments:
            submitter.job_args.append(self.argTemplate % arg)
            submitter.job_names.append('%s_%s' % arg)
    
        self.jobClusters = submitter.submit(name = 'ssw2')

    def waitForCompletion(self):
        heldJobs = []
    
        argsToExtract = []
        for ia, a in enumerate(self.argTemplate.split()):
            if a == '%s':
                argsToExtract.append(ia)
    
        while True:
            proc = subprocess.Popen(['condor_q'] + self.jobClusters + ['-af', 'ClusterId', 'JobStatus', 'Arguments'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
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


if __name__ == '__main__':

    import sys
    import socket
    import time
    import shutil
    import collections
    import logging
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
    argParser.add_argument('--printlevel', '-p', metavar = 'LEVEL', dest = 'printLevel', default = '', help = 'Override config.printLevel.')
    argParser.add_argument('--print-every', '-e', metavar = 'NEVENTS', dest = 'printEvery', type = int, default = 10000, help = 'Print frequency.')
    argParser.add_argument('--no-wait', '-W', action = 'store_true', dest = 'noWait', help = '(With batch option) Don\'t wait for job completion.')
    argParser.add_argument('--skip-missing', '-K', action = 'store_true', dest = 'skipMissing', help = 'Skip missing files in skim.')
    argParser.add_argument('--test-run', '-E', action = 'store_true', dest = 'testRun', help = 'Don\'t copy the output files to the production area.')
    
    args = argParser.parse_args()
    sys.argv = []

    ## option conflicts
    if len(args.files) != 0:
        if len(args.filesets) != 0:
            logger.error('Cannot set filesets and files simultaneously.')
            sys.exit(1)

        if args.batch:
            logger.error('Cannot use batch mode with individual files.')
            sys.exit(1)

    ## directories to include
    thisdir = os.path.dirname(os.path.realpath(__file__))
    basedir = os.path.dirname(thisdir)
    monoxdir = os.path.dirname(basedir)
    
    ## import the monophoton config
    sys.path.append(basedir)
    import config

    ## set up logger
    try:
        printLevel = getattr(logging, args.printLevel.upper())
    except AttributeError:
        printLevel = config.printLevel
    
    logging.basicConfig(level = printLevel)
    logger = logging.getLogger(__name__)

    logger.debug('Running at %s', socket.gethostname())

    ## set up global configurations with args and config
    for key in dir(args):
        if not key.startswith('_'):
            SkimSlimWeight.config[key] = getattr(args, key)

    for key in dir(config):
        if not key.startswith('_'):
            SkimSlimWeight.config[key] = getattr(config, key)

    ## set up samples and selectors
    from datasets import allsamples
    from main.skimconfig import selectors as allSelectors

    # construct {sname: {selector name: generator}}
    selectors = {}
    for sname, sels in allSelectors.items():
        for rname, gen in sels:
            if len(args.selnames) == 0 or rname in args.selnames:
                try:
                    selectors[sname][rname] = gen
                except KeyError:
                    selectors[sname] = {rname: gen}
    
    ## get the list of sample objects according to args.snames
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

    ## compile and load the Skimmer
    import ROOT
    logger.debug('dataformats: %s', config.dataformats)
    
    ROOT.gSystem.AddIncludePath('-I' + os.path.dirname(basedir) + '/common')
    ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')
    
    try:
        s = ROOT.Skimmer
    except:
        logger.error("Couldn't compile Skimmer.cc. Quitting.")
        sys.exit(1)
    
    if args.compileOnly:
        sys.exit(0)

    ## load good lumi filter
    sys.path.append(monoxdir + '/common')
    from goodlumi import makeGoodLumiFilter

    ## flist argument for SkimSlimWeight
    if len(args.files) != 0:
        flist = args.files
        files = True
    else:
        flist = args.filesets
        files = False

    if args.batch:
        ## load condor-run
        sys.path.append('/home/yiiyama/lib')
        from condor_run import CondorRun

        submitter = CondorRun(os.path.realpath(__file__))
        submitter.logdir = '/local/' + os.environ['USER']
        submitter.hold_on_fail = True
        submitter.group = 'group_t3mit.urgent'

    ## construct and run SkimSlimWeight objects
    for sample in samples:
        if len(flist) == 0:
            flist = sample.filesets()

        ssw = SkimSlimWeight(sample, selectors[sample.name], flist, files)

        if args.batch:
            ## job submission only
            if args.merge:
                jobtype = 'merge'
                setup = lambda: ssw.setupMerge()
                sub = lambda: ssw.submitMerge(submitter)
            else:
                jobtype = 'skim'
                setup = lambda: ssw.setupSkim()
                sub = lambda: ssw.submitSkim(submitter, args.skipMissing)
    
            print 'Submitting ' + jobtype + ' jobs for ' + sample.name + '.'
    
            if not setup():
                logger.warning('Failed to set up %s job for %s', jobtype, sample.name)
                continue
    
            sub()
    
            if args.noWait:
                print 'Jobs have been submitted.'
            else:
                print 'Waiting for individual ' + jobtype + ' jobs to complete.'
                ssw.waitForCompletion()
                print 'All merge jobs finished.'

        else:
            if args.merge:
                print 'Merging.'
                if not ssw.setupMerge():
                    logger.warning('Failed to set up merge job for %s', sample.name)
                    continue

                ssw.executeMerge()

            else:
                print 'Skimming.'
                if not ssw.setupSkim():
                    logger.warning('Failed to set up skim job for %s', sample.name)
                    continue
                
                ssw.executeSkim()
