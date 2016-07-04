import re
import os
import math
import fnmatch

defaultList = os.path.dirname(os.path.realpath(__file__)) + '/data/datasets.csv'

class SampleDef(object):
    def __init__(self, name, title = '', book = '', fullname = '', crosssection = 0., nevents = 0, sumw = 0., lumi = 0., data = False, comments = '', custom = {}):
        self.name = name
        self.title = title
        self.book = book
        self.fullname = fullname
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
        return SampleDef(self.name, title = self.title, book = self.book, fullname = self.fullname, crosssection = self.crosssection, nevents = self.nevents, sumw = self.sumw, lumi = self.lumi, data = self.data, comments = self.comments, custom = dict(self.custom.items()))

    def dump(self, sourceDirs):
        print 'name =', self.name
        print 'title =', self.title
        print 'book =', self.book
        print 'fullname =', self.fullname
        print 'crosssection =', self.crosssection
        print 'nevents =', self.nevents
        if self.sumw >= 0.:
            print 'sumw =', self.sumw
        print 'lumi =', self.effectiveLumi(sourceDirs), 'pb'
        print 'data =', self.data
        print 'comments = "' + self.comments + '"'

    def linedump(self):
        title = '"%s"' % self.title

        if self.data:
            crosssection = self.lumi
            ndec = 1
            sumwstr = '-'
        else:
            crosssection = self.crosssection
            ndec = 0
            while crosssection < math.pow(10., 3 - ndec):
                ndec += 1

            if int(self.sumw) == self.nevents:
                sumwstr = '%.1f' % self.sumw
            else:
                sumwstr = '%.11e' % self.sumw

        if ndec >= 6:
            xsecstr = '%.{ndec}e'.format(ndec = 3) % crosssection
        else:
            xsecstr = '%.{ndec}f'.format(ndec = ndec) % crosssection

        if self.comments != '':
            comments = " # " + self.comments
        else:
            comments = ''
            
        lineTuple = (self.name, title, xsecstr, self.nevents, sumwstr, self.book, self.fullname, comments)
        return '%-16s %-35s %-20s %-10d %-20s %-20s %s%s' % lineTuple

    def _getCounter(self, dirs):
        for dName in dirs:
            fullPath = dName
            if os.path.exists(fullPath + '/' + self.name + '.root'):
                fNames = [self.name + '.root']
                break

            fullPath = dName + '/' + self.book + '/' + self.fullname
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
        if self.data:
            self.sumw = -1.
        else:
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
        self._commentLines = [] # to reproduce comment lines from the source

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
            name = ''
            for line in dsSource:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    self._commentLines.append((name, line)) # dataset from one line above, line
                    continue
        
                matches = re.match('([^ ]+)\s+"(.*)"\s+([0-9e.+-]+)\s+([0-9]+)\s+([0-9e.+-]+)\s+([^ ]+)\s+([^ ]+)(| +#.*)', line.strip())
                if not matches:
                    print 'Ill-formed line in ' + listpath
                    print line
                    continue
        
                name, title, crosssection, nevents, sumw, book, fullname, comments = [matches.group(i) for i in range(1, 9)]
        
                if sumw == '-':
                    sdef = SampleDef(name, title = title, book = book, fullname = fullname, lumi = float(crosssection), nevents = int(nevents), sumw = -1., data = True, comments = comments.lstrip(' #'))
                else:
                    sdef = SampleDef(name, title = title, book = book, fullname = fullname, crosssection = float(crosssection), nevents = int(nevents), sumw = float(sumw), comments = comments.lstrip(' #'))
        
                self.samples.append(sdef)

    def save(self, listpath):
        with open(listpath, 'w') as out:
            iC = 0
            while iC != len(self._commentLines) and self._commentLines[iC][0] == '':
                out.write(self._commentLines[iC][1] + '\n')
                iC += 1
            
            for sample in self.samples:
                out.write(sample.linedump() + '\n')
                
                while iC != len(self._commentLines) and self._commentLines[iC][0] == sample.name:
                    out.write(self._commentLines[iC][1] + '\n')
                    iC += 1

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
    commandHelp = '''list [DATASETS]: List datasets with nevents > 0 (no argument) or datasets with names matching to the argument.
print DATASET: Print information of DATASET.
dump DATASETS: Dump information of DATASETS in CSV form.
recalculate DATASETS: Recalculate nentries and sumw for DATASETS.
add INFO: Add a new dataset.'''
    argParser.add_argument('command', nargs = '+', help = commandHelp)
    argParser.add_argument('--list-path', '-s', metavar = 'PATH', dest = 'listPath', default = defaultList, help = 'CSV file to load data from.')
    argParser.add_argument('--save', '-o', metavar = 'PATH', dest = 'outPath', nargs = '?', const = '', help = 'Save updated content to CSV file (no argument: save to original CSV).')

    args = argParser.parse_args()
    sys.argv = []

    import ROOT

    samples = SampleDefList(listpath = args.listPath)

    command = args.command[0]
    arguments = args.command[1:]

    if command == 'list':
        if len(arguments) > 0:
            matches = samples.getmany(arguments)
        else:
            matches = samples.getmany(['*'])

        print ' '.join([sample.name for sample in matches])

    elif command == 'print':
        try:
            sample = samples[arguments[0]]
        except:
            print 'No sample', arguments[0]

        sample.dump([config.photonSkimDir, config.ntuplesDir])

    elif command == 'dump':
        if len(arguments) == 0:
            arguments = samples.names()

        for name in arguments:
            try:
                sample = samples[name]
            except:
                print 'No sample', name

            print sample.linedump()

    elif command == 'recalculate':
        for name in arguments:
            sample = samples[name]
            sample.recomputeWeight([config.photonSkimDir, config.ntuplesDir])
            print sample.linedump()

    elif command == 'add':
        name, title, crosssection, nevents, sumw, book, fullname = arguments[:7]
        try:
            comments = arguments[7]
        except IndexError:
            comments = ''
        
        if sumw == '-':
            sdef = SampleDef(name, title = title, book = book, fullname = fullname, lumi = float(crosssection), nevents = int(nevents), sumw = -1., data = True, comments = comments)
        else:
            sdef = SampleDef(name, title = title, book = book, fullname = fullname, crosssection = float(crosssection), nevents = int(nevents), sumw = float(sumw), comments = comments)
        
        samples.samples.append(sdef)

    else:
        print 'Unknown command', command
        sys.exit(1)
    
    if args.outPath is not None:
        if args.outPath == '':
            args.outPath = args.listPath

        samples.save(args.outPath)

else: # when importing from another python script
    allsamples = SampleDefList(listpath = defaultList)
