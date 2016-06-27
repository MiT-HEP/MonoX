import re
import os
import math
import fnmatch
import sqlite3

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
            self.comments = "# "+self.comments
            
        lineTuple = (self.name, title, xsecstr, self.nevents, sumwstr, self.book, self.fullname, self.comments)
        return '%-16s %-35s %-20s %-10d %-20s %-20s %s %s' % lineTuple

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
    def __init__(self, samples = [], dbpath = '', listpath = ''):
        self.samples = list(samples)

        if dbpath:
            self._load(dbpath)

        elif listpath:
            self._loadCSV(listpath)

    def __iter__(self):
        return iter(self.samples)

    def __reversed__(self):
        return reversed(self.samples)

    def __getitem__(self, key):
        try:
            return self.get(key)
        except RuntimeError:
            raise KeyError(key + ' not defined')

    def _loadCSV(self, listpath):
        with open(listpath) as dsSource:
            for line in dsSource:
                line = line.strip()
                
                if not line or line.startswith('#'):
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

    def _load(self, dbpath):
        conn = sqlite3.connect(dbpath)
        db = conn.cursor()

        db.execute('SELECT `name`, `title`, `crosssection`, `nevents`, `sumw`, `book`, `fullname`, `comments` FROM `datasets`')
        for name, title, crosssection, nevents, sumw, book, fullname, comments in db.fetchall():
            # cast strings to str from unicode
            if sumw < 0.:
                sdef = SampleDef(str(name), title = str(title), book = str(book), fullname = str(fullname), lumi = crosssection, nevents = nevents, sumw = sumw, data = True, comments = str(comments))
            else:
                sdef = SampleDef(str(name), title = str(title), book = str(book), fullname = str(fullname), crosssection = crosssection, nevents = nevents, sumw = sumw, comments = str(comments))
        
            self.samples.append(sdef)

        conn.close()

    def save(self, dbpath):
        conn = sqlite3.connect(dbpath)
        db = conn.cursor()

        values = []
        for s in self.samples:
            if s.data:
                values.append((s.name, s.title, s.lumi, s.nevents, -1., s.book, s.fullname, s.comments))
            else:
                values.append((s.name, s.title, s.crosssection, s.nevents, s.sumw, s.book, s.fullname, s.comments))

        db.executemany('INSERT OR REPLACE INTO `datasets` (`name`, `title`, `crosssection`, `nevents`, `sumw`, `book`, `fullname`, `comments`) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', values)
        conn.commit()

        conn.close()

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
    argParser.add_argument('--list-path', '-s', metavar = 'PATH', dest = 'listPath', help = 'CSV file to load data from.')
    argParser.add_argument('--db-path', '-d', metavar = 'PATH', dest = 'dbPath', default = os.path.dirname(os.path.realpath(__file__)) + '/data/datasets.db', help = 'SQLite3 file to load data from.')
    argParser.add_argument('--save', '-O', action = 'store_true', dest = 'saveDB', help = 'Save updated content to DB.')

    args = argParser.parse_args()
    sys.argv = []

    import ROOT

    if args.listPath:
        samples = SampleDefList(listpath = args.listPath)
    else:
        samples = SampleDefList(dbpath = args.dbPath)

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
    
    if args.saveDB and args.dbPath:
        samples.save(args.dbPath)

else: # when importing from another python script
    allsamples = SampleDefList(dbpath = os.path.dirname(os.path.realpath(__file__)) + '/data/datasets.db')
