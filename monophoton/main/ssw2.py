#!/usr/bin/env python

import sys
import os
import subprocess

from batch import BatchManager

## load condor-run
sys.path.append('/home/yiiyama/lib')
from condor_run import CondorRun

logger = None

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
            self.tmpDir = '/local/' + os.environ['USER'] + '/ssw2'
        else:
            self.tmpDir = '/tmp/' + os.environ['USER'] + '/ssw2'

        if self.manual or len(sample.filesets()) == 1:
            self.outDir = SkimSlimWeight.config['skimDir']
        else:
            self.outDir = SkimSlimWeight.config['skimDir'] + '/' + sample.name

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
        
        tmpOutDir = self.tmpDir + '/' + self.sample.name
        if not os.path.exists(tmpOutDir):
            try:
                os.makedirs(tmpOutDir)
            except OSError:
                # did someone running on this machine beat this job and made the directory?
                if not os.path.exists(tmpOutDir):
                    raise
    
        if not os.path.exists(self.outDir):
            try:
                os.makedirs(self.outDir)
            except OSError:
                if not os.path.exists(self.outDir):
                    raise
    
        logger.debug('getting all input files')

        if not SkimSlimWeight.config['readRemote'] and not self.manual:
            # check for missing local copies and issue a smartcache download request
            self.sample.download()

        if SkimSlimWeight.config['skipExisting']:
            logger.info('Checking for existing files.')
        else:
            logger.info('Removing existing files.')
    
        # abort if any one of the selector output exists
        for fileset in list(self.filesets):
            outNameBase = self.getOutNameBase(fileset)

            for rname in self.selectors:
                outName = outNameBase + '_' + rname + '.root'
                outPath = self.outDir + '/' + outName
                logger.debug(outPath)
    
                if SkimSlimWeight.config['skipExisting']:
                    if os.path.exists(outPath) and os.stat(outPath).st_size != 0:
                        logger.info('Output files for %s already exist. Skipping skim.', outNameBase)
                        self.filesets.remove(fileset)
                        break

                elif not SkimSlimWeight.config['testRun']:
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
        if not SkimSlimWeight.config['noPhotonSkim']:
            skimmer.setCommonSelection('superClusters.rawPt > 165. && TMath::Abs(superClusters.eta) < 1.4442')

        # temporary - backward compatibility issue 004 -> 005/006/007
        if self.sample.book != 'pandaf/004':
            skimmer.setCompatibilityMode(True)

        for rname, selgen in self.selectors.items():
            if type(selgen) is tuple: # has modifiers
                selector = selgen[0](self.sample, rname)
                for mod in selgen[1:]:
                    mod(self.sample, selector)
            else:
                selector = selgen(self.sample, rname)

            selector.setUseTimers(SkimSlimWeight.config['timer'])
            skimmer.addSelector(selector)
    
        if self.sample.data and SkimSlimWeight.config['json']:
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
                for path in self.sample.files([fileset]):
                    if SkimSlimWeight.config['readRemote']:
                        if not os.path.exists(path) or os.stat(path).st_size == 0:
                            path = path.replace('/mnt/hadoop/cms', 'root://xrootd.cmsaf.mit.edu/')
        
                    logger.debug('Add input: %s %s', fileset, path)
                    paths[fileset].append(path)

        tmpOutDir = self.tmpDir + '/' + self.sample.name
    
        for fileset, fnames in paths.items():
            skimmer.clearPaths()
            for fname in fnames:
                skimmer.addPath(fname)

            outNameBase = self.getOutNameBase(fileset)
            nentries = SkimSlimWeight.config['nentries']
            firstEntry = SkimSlimWeight.config['firstEntry']
    
            logger.debug('Skimmer.run(%s, %s, %s, %d, %d)', tmpOutDir, outNameBase, self.sample.data, nentries, firstEntry)
            skimmer.run(tmpOutDir, outNameBase, self.sample.data, nentries, firstEntry)
    
            for rname in self.selectors:
                outName = outNameBase + '_' + rname + '.root'
        
                if SkimSlimWeight.config['testRun']:
                    logger.info('Output at %s/%s', tmpOutDir, outName)
                else:
                    logger.info('Copying output to %s/%s', self.outDir, outName)
                    shutil.copy(tmpOutDir + '/' + outName, self.outDir)
                    logger.info('Removing %s/%s', tmpOutDir, outName)
                    os.remove(tmpOutDir + '/' + outName)

    def setupMerge(self):
        if not os.path.exists(self.tmpDir):
            try:
                os.makedirs(self.tmpDir)
            except OSError:
                # did someone beat this job and made the directory?
                if not os.path.exists(self.tmpDir):
                    raise

        for rname in list(self.selectors):
            outNameBase = self.sample.name + '_' + rname
            outName = outNameBase + '.root'
            outPath = SkimSlimWeight.config['skimDir'] + '/' + outName
        
            if SkimSlimWeight.config['skipExisting']:
                if os.path.exists(outPath) and os.stat(outPath).st_size != 0:
                    logger.info('Output files for %s already exist. Skipping merge.', outNameBase)
                    self.selectors.pop(rname)

            elif not SkimSlimWeight.config['testRun']:
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
        
            mergePath = self.tmpDir + '/' + outName
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


class SSWBatchManager(BatchManager):
    def __init__(self, ssws):
        BatchManager.__init__(self, 'ssw2')

        self.ssws = ssws # list of SlimSkimWeight objects to manage
        self.catalogDir = ''

    def submitMerge(self, noWait, autoResubmit = False):
        submitter = CondorRun(os.path.realpath(__file__))

        arguments = []

        for ssw in self.ssws:
            # Collect arguments and remove output
            for rname in ssw.selectors:
                arguments.append((ssw.sample.name, rname))
    
                # clean up old .log files
                path = '/local/' + os.environ['USER'] + '/ssw2/' + ssw.sample.name + '_' + rname + '.0.log'
                logger.debug('Removing %s', path)
                try:
                    os.remove(path)
                except:
                    pass
    
        argTemplate = '-M %s -s %s'
        if self.catalogDir:
            argTemplate += ' -c ' + self.catalogDir

        submitter.job_args = [argTemplate % arg for arg in arguments]
        submitter.job_names = ['%s_%s' % arg for arg in arguments]

        self._submit(submitter, 'merge', argTemplate, noWait, autoResubmit)

    def submitSkim(self, noWait, skipMissing, readRemote, autoResubmit = False):
        submitter = CondorRun(os.path.realpath(__file__))

        argTemplate = '%s -f %s'
    
        if skipMissing:
            argTemplate += ' -K'

        if readRemote:
            argTemplate += ' -R'

        if self.catalogDir:
            argTemplate += ' -c ' + self.catalogDir

        for ssw in self.ssws:
            for fileset in ssw.filesets:
                submitter.job_args.append(argTemplate % (ssw.sample.name, fileset) + ' -s ' + ' '.join(ssw.selectors.keys()))
                submitter.job_names.append('%s_%s' % (ssw.sample.name, fileset))
    
                # clean up old .log files
                logpath = '/local/' + os.environ['USER'] + '/ssw2/' + ssw.sample.name + '_' + fileset + '.0.log'
                logger.debug('Removing %s', logpath)
                try:
                    os.remove(logpath)
                except:
                    pass

        self._submit(submitter, 'skim', argTemplate, noWait, autoResubmit)
    

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
    argParser.add_argument('--catalog', '-c', metavar = 'PATH', dest = 'catalog', default = '', help = 'Source file catalog.')
    argParser.add_argument('--filesets', '-f', metavar = 'ID', dest = 'filesets', nargs = '+', default = [], help = 'Fileset id to run on.')
    argParser.add_argument('--files', '-i', metavar = 'PATH', dest = 'files', nargs = '+', default = [], help = 'Directly run on files.')
    argParser.add_argument('--first-entry', '-t', metavar = 'ENTRY', dest = 'firstEntry', type = int, default = 0, help = 'First entry number to process.')
    argParser.add_argument('--suffix', '-x', metavar = 'SUFFIX', dest = 'outSuffix', default = '', help = 'Output file suffix.')
    argParser.add_argument('--batch', '-B', action = 'store_true', dest = 'batch', help = 'Use condor-run to run.')
    argParser.add_argument('--no-photonskim', '-P', action = 'store_true', dest = 'noPhotonSkim', help = 'Force skim on all events.')
    argParser.add_argument('--skip-existing', '-X', action = 'store_true', dest = 'skipExisting', help = 'Do not run skims on files that already exist.')
    argParser.add_argument('--merge', '-M', action = 'store_true', dest = 'merge', help = 'Merge the fragments without running any skim jobs.')
    argParser.add_argument('--selectors', '-s', metavar = 'SELNAME', dest = 'selnames', nargs = '*', default = None, help = 'Selectors to process. With --list, print the selectors configured with the samples.')
    argParser.add_argument('--printlevel', '-p', metavar = 'LEVEL', dest = 'printLevel', default = 'WARNING', help = 'Override config.printLevel.')
    argParser.add_argument('--print-every', '-e', metavar = 'NEVENTS', dest = 'printEvery', type = int, default = 10000, help = 'Print frequency.')
    argParser.add_argument('--no-wait', '-W', action = 'store_true', dest = 'noWait', help = '(With batch option) Don\'t wait for job completion.')
    argParser.add_argument('--read-remote', '-R', action = 'store_true', dest = 'readRemote', help = 'Read from root://xrootd.cmsaf.mit.edu if a local copy of the file does not exist.')
    argParser.add_argument('--resubmit', '-S', action = 'store_true', dest = 'autoResubmit', help = '(Without no-wait option) Automatically release held jobs.')
    argParser.add_argument('--skip-missing', '-K', action = 'store_true', dest = 'skipMissing', help = 'Skip missing files in skim.')
    argParser.add_argument('--test-run', '-E', action = 'store_true', dest = 'testRun', help = 'Don\'t copy the output files to the production area. Sets --filesets to 0000 by default.')
    
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
    printLevel = getattr(logging, args.printLevel.upper())
    args.printLevel = printLevel # gets passed to SkimSlimWeight.config

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
    import datasets
    if args.catalog:
        datasets.catalogDir = args.catalog

    from main.skimconfig import allSelectors

    # list of (sample, {rname: selgen})
    sampleList = []
    
    ## get the list of sample objects according to args.snames
    if 'all' in args.snames:
        spatterns = allSelectors.keys()
        samples = datasets.allsamples.getmany(spatterns)
        sampleList = [(sample, dict()) for sample in samples]
    elif 'bkgd' in args.snames:
        spatterns = allSelectors.keys() + ['!add*', '!dm*', '!dph*']
        samples = datasets.allsamples.getmany(spatterns)
        sampleList = [(sample, dict()) for sample in samples]
    else:
        for ss in args.snames:
            # ss can be given in format sname=selector1,selector2,.. or sname_region
            if '=' in ss:
                spattern, rn = ss.split('=')
                rnames = rn.split(',')
            elif '_' in ss:
                spattern = ss.split('_')[0]
                rnames = [ss.split('_')[1]]
            else:
                spattern = ss
                rnames = []

            samples = datasets.allsamples.getmany(spattern)
            for sample in samples:
                selectors = {}

                if len(rnames) == 0:
                    # fill in the selectors for samples with no selector specification
                    if args.selnames is not None and len(args.selnames) != 0:
                        for sel in args.selnames:
                            selectors[sel] = allSelectors[sample][sel]
                    else:
                        selectors.update(allSelectors[sample])

                else:
                    for rname in rnames:
                        try:
                            selectors[rname] = allSelectors[sample][rname]
                        except KeyError:
                            print 'Selector', sample.name, rname, 'not defined'
                            raise

                sampleList.append((sample, selectors))

    if args.list:
        if args.selnames is not None:
            for sample, selectors in sampleList:
                print sample.name + ' (' + ' '.join(selectors.keys()) + ')'
        else:
            print ' '.join(sorted(s.name for s, r in sampleList))

        sys.exit(0)

    ## compile and load the Skimmer
    import ROOT
    
    ROOT.gSystem.AddIncludePath('-I' + monoxdir + '/common')
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

    ## construct and run SkimSlimWeight objects
    ssws = []
    for sample, selectors in sampleList:
        if len(args.files) != 0:
            files = True
            flist = args.files
        else:
            files = False
            if len(args.filesets) == 0 and args.testRun:
                flist = ['0000']
            else:
                flist = args.filesets

        if len(flist) == 0:
            flist = sample.filesets()

        ssw = SkimSlimWeight(sample, selectors, flist, files)

        if args.merge:
            if not ssw.setupMerge():
                logger.warning('Failed to set up merge job for %s', sample.name)
                continue
        else:
            if not ssw.setupSkim():
                logger.warning('Failed to set up skim job for %s', sample.name)
                continue

        ssws.append(ssw)

    if args.batch:
        ## job submission only
        print 'Submitting jobs.'
       
        batchManager = SSWBatchManager(ssws)
        if args.catalog:
            batchManager.catalogDir = args.catalog

        if args.merge:
            batchManager.submitMerge(args.noWait, args.autoResubmit)
        else:
            batchManager.submitSkim(args.noWait, args.skipMissing, args.readRemote, args.autoResubmit)

        if args.noWait:
            print 'Jobs have been submitted.'
        else:
            print 'All jobs finished.'

    else:
        if args.merge:
            print 'Merging.'
            for ssw in ssws:
                ssw.executeMerge()

        else:
            print 'Skimming.'
            for ssw in ssws:
                ssw.executeSkim()
