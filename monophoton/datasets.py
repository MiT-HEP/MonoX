import re
import os
import math
import fnmatch

class SampleDef(object):
    def __init__(self, name, title = '', book = '', directory = '', crosssection = 0., nevents = 0, sumw = 0., lumi = 0., data = False, comments = '', custom = {}):
        self.name = name
        self.title = title
        self.book = book
        self.directory = directory
        self.crosssection = crosssection
        self.nevents = nevents
        if sumw == 0.:
            self.sumw = float(nevents)
        else:
            self.sumw = sumw
        self.lumi = lumi
        self.data = data
        self.comments = comments
        self.custom = custom

    def clone(self):
        return SampleDef(self.name, title = self.title, book = self.book, directory = self.directory, crosssection = self.crosssection, nevents = self.nevents, sumw = self.sumw, lumi = self.lumi, data = self.data, comments = self.comments, custom = dict(self.custom.items()))

    def dump(self, sourceDirs):
        print 'name =', self.name
        print 'title =', self.title
        print 'book =', self.book
        print 'directory =', self.directory
        print 'crosssection =', self.crosssection
        print 'nevents =', self.nevents
        print 'sumw =', self.sumw
        print 'lumi =', self.effectiveLumi(sourceDirs), 'pb'
        print 'data =', self.data
        print 'comments = "' + self.comments + '"'

    def linedump(self):
        title = '"%s"' % self.title

        if self.data:
            xsec = self.lumi
            ndec = 1
            sumwstr = '-'
        else:
            xsec = self.crosssection
            ndec = 0
            while xsec < math.pow(10., 3 - ndec):
                ndec += 1

            if int(self.sumw) == self.nevents:
                sumwstr = '%.1f' % self.sumw
            else:
                sumwstr = '%.11e' % self.sumw

        if ndec >= 6:
            xsecstr = '%.{ndec}e'.format(ndec = 3) % xsec
        else:
            xsecstr = '%.{ndec}f'.format(ndec = ndec) % xsec

        if self.comments != '':
            self.comments = "# "+self.comments
            
        lineTuple = (self.name, title, xsecstr, self.nevents, sumwstr, self.book, self.directory, self.comments)
        return '%-16s %-35s %-20s %-10d %-20s %-20s %s %s' % lineTuple

    def _getCounter(self, dirs):
        for dName in dirs:
            fullPath = dName
            if os.path.exists(fullPath + '/' + self.name + '.root'):
                fNames = [self.name + '.root']
                break

            fullPath = dName + '/' + self.book + '/' + self.directory
            if os.path.isdir(fullPath):
                fNames = os.listdir(fullPath)
                break

        if len(fNames) == 0:
            print fullPath + ' has no files'
            return None

        counter = None
        for fName in fNames:
            source = ROOT.TFile.Open(fullPath + '/' + fName)
            if not source:
                continue
            
            try:
                if counter is None:
                    counter = source.Get('counter')
                    counter.SetDirectory(ROOT.gROOT)
                else:
                    counter.Add(source.Get('counter'))
            except:
                print path
                raise

            source.Close()

        return counter
    
    def recomputeWeight(self, sourceDirs):
        counter = self._getCounter(sourceDirs)

        if not counter:
            return

        self.nevents = int(counter.GetBinContent(1))
        if not self.data:
            self.sumw = counter.GetBinContent(2)

    def getSumw2(self, sourceDirs):
        counter = self._getCounter(sourceDirs)

        if not counter:
            return 0.

        return math.pow(counter.GetBinError(2), 2.)

    def effectiveLumi(self, sourceDirs):
        if self.lumi > 0.:
            return self.lumi
        else:
            sumw2 = self.getSumw2(sourceDirs)
            if sumw2 > 0.:
                return math.pow(self.sumw, 2.) / sumw2 / self.crosssection
            else:
                print 'sumw2 is zero'
                return 0.


class SampleDefList(object):
    def __init__(self, samples = [], listpath = ''):
        self.samples = list(samples)

        if listpath:
            self._load(listpath)

    def __iter__(self):
        return iter(self.samples)

    def __reversed__(self):
        return reversed(self.samples)

    def __getitem__(self, key):
        try:
            return self.get(key)
        except RuntimeError:
            raise KeyError(key + ' not defined')

    def _load(self, listpath):
        with open(listpath) as dsSource:
            for line in dsSource:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
        
                matches = re.match('([^ ]+)\s+"(.*)"\s+([0-9e.+-]+)\s+([0-9]+)\s+([0-9e.+-]+)\s+([^ ]+)\s+([^ ]+)(| +#.*)', line.strip())
                if not matches:
                    print 'Ill-formed line in datasets.csv'
                    print line
                    continue
        
                name, title, xsec, nevents, sumw, book, directory, comments = [matches.group(i) for i in range(1, 9)]
        
                if sumw == '-':
                    sdef = SampleDef(name, title = title, book = book, directory = directory, lumi = float(xsec), nevents = int(nevents), data = True, comments = comments.lstrip(' #'))
                else:
                    sdef = SampleDef(name, title = title, book = book, directory = directory, crosssection = float(xsec), nevents = int(nevents), sumw = float(sumw), comments = comments.lstrip(' #'))
        
                self.samples.append(sdef)

    def names(self):
        return [s.name for s in self.samples]

    def get(self, name):
        try:
            return next(s for s in self.samples if s.name == name)
        except StopIteration:
            raise RuntimeError('Sample ' + name + ' not found')

    def getmany(self, names):
        samples = []
        for name in names:
            match = True
            if name.startswith('!'):
                name = name[1:]
                match = False

            if '*' in name:
                matching = [s for s in self.samples if fnmatch.fnmatch(s.name, name)]
            else:
                matching = [self.get(name)]

            if match:
                samples += matching
            else:
                samples += [s for s in self.samples if s not in matching]

        return sorted(list(set(samples)), key = lambda s: s.name)


if __name__ == '__main__':
    import sys
    from argparse import ArgumentParser
    import config

    argParser = ArgumentParser(description = 'Dataset information management')
    argParser.add_argument('--list', '-L', metavar = 'SAMPLES', dest = 'list', nargs = '*', help = 'List datasets with nevents > 0 (no argument) or datasets with names matching to the argument')
    argParser.add_argument('--print', '-p', metavar = 'DATASET', dest = 'showInfo', help = 'Print information of DATASET.')
    argParser.add_argument('--recalculate', '-r', metavar = 'DATASET', dest = 'recalculate', nargs = '+', help = 'Recalculate nentries and sumw for DATASET.')
    argParser.add_argument('--list-path', '-s', metavar = 'PATH', dest = 'listPath', default = os.path.dirname(os.path.realpath(__file__)) + '/data/datasets.csv', help = 'List CSV file to load data from.')

    args = argParser.parse_args()
    sys.argv = []

    import ROOT

    samples = SampleDefList(listpath = args.listPath)

    if args.list is not None:
        if len(args.list) != 0:
            matches = samples.getmany(args.list)
        else:
            matches = samples.getmany(['*'])

        print ' '.join([sample.name for sample in matches])

        sys.exit(0)

    if args.showInfo:
        try:
            sample = samples[args.showInfo]
        except:
            print 'No sample', args.showInfo

        sample.dump([config.photonSkimDir, config.ntuplesDir])
        
        sys.exit(0)

    if args.recalculate:
        for name in args.recalculate:
            sample = samples[name]
            sample.recomputeWeight([config.photonSkimDir, config.ntuplesDir])
            print sample.linedump()

        sys.exit(0)

else: # when importing from another python script
    allsamples = SampleDefList(listpath = os.path.dirname(os.path.realpath(__file__)) + '/data/datasets.csv')
