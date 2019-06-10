#!/usr/bin/env python

import os
import sys

if '/usr/local/lib/python2.7/site-packages' not in sys.path:
    sys.path.append('/usr/local/lib/python2.7/site-packages')

import time
import array
import shutil
import string
import random
import subprocess
import mysql.connector as mc
from argparse import ArgumentParser
    
argParser = ArgumentParser(description = 'Plot and count')
argParser.add_argument('indir', metavar = 'PATH', help = 'Input directory name.')
argParser.add_argument('outdir', metavar = 'PATH', help = 'Output directory name.')
argParser.add_argument('--search-subdir', '-S', action = 'store_true', dest = 'searchSubdir', help = 'Merge files in the subdirectories of input directory.')
argParser.add_argument('--post', '-t', metavar = 'PATH', dest = 'postdir', default = '', help = 'Post-process directory name.')
argParser.add_argument('--garbage', '-g', metavar = 'PATH', dest = 'garbagedir', default = '', help = 'Garbage directory name.')
argParser.add_argument('--num-merge', '-n', metavar = 'N', dest = 'nmerge', type = int, default = 50, help = 'Number of input files per output.')
argParser.add_argument('--num-out', '-o', metavar = 'N', dest = 'nout', type = int, default = 0, help = 'Number of output files to make. 0 = continue until all input are consumed.')
argParser.add_argument('--edm', '-E', action = 'store_true', dest = 'edm', help = 'Merge EDM input using cmsRun merge.py.')

args = argParser.parse_args()
sys.argv = []

import ROOT
ROOT.gSystem.Load('libPandaTreeObjects.so')
sys.path.append(os.getenv('CMSSW_BASE') + '/src/PandaTree/Utils/scripts')
from padd import padd

if args.edm:
    keynames = set(['MetaData', 'ParameterSets', 'Parentage', 'Events', 'LuminosityBlocks', 'Runs'])
else:
    # version <= 011
    #keynames = set(['ElectronTriggerObject', 'MuonTriggerObject', 'PhotonTriggerObject', 'RecoilCategory', 'events', 'runs', 'lumiSummary', 'hlt', 'hNPVReco', 'hNPVTrue', 'hSumW', 'eventcounter'])
    # version 012
    keynames = set(['RecoilCategory', 'events', 'runs', 'lumiSummary', 'hlt', 'hNPVReco', 'hNPVTrue', 'hSumW', 'eventcounter'])

def rm(infile, path = ''):
    if not path:
        path = infile.GetName()

    print 'Moving', path, 'to garbage'
    if infile:
        infile.Close()

    if args.garbagedir:
        fname = os.path.basename(path)
        while os.path.exists(args.garbagedir + '/' + fname):
            fname += '.1'
        os.rename(path, args.garbagedir + '/' + fname)
    else:
        os.unlink(path)

def opensanitize(path):
    infile = ROOT.TFile.Open(path)
    if not infile or infile.IsZombie():
        print path, 'is corrupt'
        rm(infile, path)
        return None

    if set(key.GetName() for key in infile.GetListOfKeys()) != keynames:
        print path, 'is incomplete'
        rm(infile)
        return None

    if args.edm:
        inevents = infile.Get('Events')
    else:
        inevents = infile.Get('events')

    if not inevents:
        print path, 'is incomplete'
        rm(infile)
        return None

    # nin = inevents.GetEntries()

    # if nin == 0:
    #     print path, 'is empty'
    #     rm(infile)
    #     return None

    return infile, inevents

def isdistinct(infile, inevents, postdir):
    fname = os.path.basename(infile.GetName())
    dname = postdir + '/' + fname.replace('.root', '')
    pnames = []
    if os.path.isdir(dname):
        for pname in os.listdir(dname):
            pnames.append(dname + '/' + pname)

    elif os.path.exists(postdir + '/' + fname):
        pnames.append(postdir + '/' + fname)

    for pname in pnames:
        pstuff = opensanitize(pname)
        if not pstuff:
            continue
    
        pfile, pevents = pstuff
    
        if inevents.GetEntries() != pevents.GetEntries():
            continue
    
        if args.edm:
            inevents.Draw('recoGenParticles_prunedGenParticles__PAT.product().pdgId()', '', 'goff')
            pevents.Draw('recoGenParticles_prunedGenParticles__PAT.product().pdgId()', '', 'goff')
    
            result = inevents.GetV1()[3] != pevents.GetV1()[3] or inevents.GetV1()[10] != pevents.GetV1()[10] or inevents.GetV1()[15] != pevents.GetV1()[15]
    
        else:
            inevents.Draw('genParticles.size', '', 'goff')
            pevents.Draw('genParticles.size', '', 'goff')
    
            result = inevents.GetV1()[0] != pevents.GetV1()[0]

        pfile.Close()
    
        if not result:
            print inevents.GetCurrentFile().GetName(), 'and', pevents.GetCurrentFile().GetName(), 'may be identical'
            return False

    return True

def writepanda(inpaths, outfname):
    padd(outfname, inpaths, 'TMath::Finite(weight)')

    source = ROOT.TFile.Open(outfname)
    if not source:
        return False

    tree = source.Get('events')
    if not tree or tree.GetEntries() == 0:
        return False

    source.Close()

    return True

def writeedm(inpaths, outfname):
    command = ['cmsRun', '/home/yiiyama/cms/cmssw/cfg/merge.py', 'outputFile=' + outfname]
    command += ['inputFiles=file:' + inpath for inpath in inpaths]

    proc = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    out, err = proc.communicate()

    outlines = out.split('\n')
    errlines = err.split('\n')

    print '[STDOUT]'
    print '\n'.join(outlines[:2])
    print '\n'.join(outlines[-2:])
    print '[STDERR]'
    print '\n'.join(errlines[:2])
    print '\n'.join(errlines[-2:])

    return proc.returncode == 0


class SynchDB(object):
    def __init__(self):
        self.dbconn = None
        self.cursor = None

    def connect(self):
        while True:
            try:
                self.dbconn = mc.connect(host = 't3desk007.mit.edu', user = 'merge', password = 'merge', database = 'merging')
                break
            except mc.errors.OperationalError:
                pass
            except mc.errors.DatabaseError:
                pass
    
            time.sleep(1)
        
        self.cursor = self.dbconn.cursor()
        self.cursor.execute('LOCK TABLES `inputs` WRITE, `logs` WRITE')

    def execute(self, query, *args):
        self.cursor.execute(query, args)

    def close(self):
        if self.cursor:
            self.cursor.execute('UNLOCK TABLES')
            self.cursor.close()
            self.cursor = None

        if self.dbconn:
            self.dbconn.close()
            self.dbconn = None


def find_recursive(path, maxn=0):
    fulllist = []

    for fname in os.listdir(path):
        inpath = path + '/' + fname
        if fname.endswith('.root'):
            fulllist.append(inpath)
        elif os.path.isdir(inpath):
            fulllist.extend(find_recursive(inpath))

        if maxn > 0 and len(fulllist) >= maxn:
            return fulllist, False

    if maxn > 0:
        return fulllist, True
    else:
        return fulllist


iout = 0

while True:
    while True:
        outbase = ''.join(random.sample(string.hexdigits, 16)) + '.root'
        outname = args.outdir + '/' + outbase
        if not os.path.exists(outname):
            break

    db = SynchDB()

    try:
        allin, exhausted = find_recursive(args.indir, args.nmerge + 10)

        inpaths = []
        unused = []
        for inpath in allin:
            do_open = False
    
            db.connect()
    
            if os.path.exists(inpath) and os.stat(inpath).st_mtime < time.time() - 300:
                db.execute('SELECT COUNT(*) FROM `logs` WHERE `path` = %s', inpath)
                if db.cursor.fetchall()[0][0] != 0:
                    print inpath, 'appears in the log table.'
                    rm(None, inpath)
                else:
                    db.execute('SELECT COUNT(*) FROM `inputs` WHERE `path` = %s', inpath)
                    if db.cursor.fetchall()[0][0] == 0:
                        db.execute('INSERT INTO `inputs` VALUES (%s, %s)', inpath, outname)
                        do_open = True
   
            db.close()
    
            if not do_open:
                continue

            instuff = opensanitize(inpath)
            if not instuff:
                unused.append(inpath)
                continue

            infile, inevents = instuff
    
            if args.postdir and not isdistinct(infile, inevents, args.postdir):
                rm(infile)
                unused.append(inpath)
                continue

            infile.Close()
    
            print '-->', inpath
            inpaths.append(inpath)
    
            if len(inpaths) == args.nmerge:
                break

        for path in unused:
            db.execute('DELETE FROM `inputs` WHERE `path` = %s', path)
    
        if len(inpaths) == 0:
            break

        elif len(inpaths) < args.nmerge:
            if not exhausted:
                # too many files went into unused
                continue
                
            print 'Too few files to merge. Sleeping for 5 minutes.'
            time.sleep(300)
            iout += 1
            continue
    
        if args.edm:
            success = writeedm(inpaths, '/tmp/' + outbase)
        else:
            success = writepanda(inpaths, '/tmp/' + outbase)

        if success:
            print outname
            shutil.copy('/tmp/' + outbase, outname)

            db.connect()
    
            for inpath in inpaths:
                if args.postdir:
                    fname = os.path.basename(inpath)
                    pdirname = args.postdir + '/' + fname.replace('.root', '')
                    pname = args.postdir + '/' + fname
                    if os.path.isdir(pdirname):
                        idx = len(os.listdir(pdirname))
                        os.rename(inpath, pdirname + ('/%d_%s' % (idx, fname)))
                    elif os.path.exists(pname):
                        os.mkdir(pdirname)
                        os.rename(pname, pdirname + '/0_' + fname)
                        os.rename(inpath, pdirname + '/1_' + fname)
                    else:
                        os.rename(inpath, pname)
    
                else:
                    os.unlink(inpath)

   
            db.execute('INSERT INTO `logs` SELECT * FROM `inputs` WHERE `outpath` = %s', outname)
            db.close()

    finally:
        db.close()
        db.connect()
        db.execute('DELETE FROM `inputs` WHERE `outpath` = %s', outname)
        db.close()

        if os.path.exists('/tmp/' + outbase):
            os.unlink('/tmp/' + outbase)

    iout += 1

    if iout == args.nout:
        break
