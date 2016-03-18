import re
import os

class SampleDef(object):
    def __init__(self, name, category = '', title = '', directory = '', crosssection = 0., nevents = 0, sumw = 0., lumi = 0., scale = 1., data = False, signal = False, custom = {}):
        self.name = name
        self.category = category
        self.title = title
        self.directory = directory
        self.crosssection = crosssection
        self.nevents = nevents
        if sumw == 0.:
            self.sumw = float(nevents)
        else:
            self.sumw = sumw
        self.lumi = lumi
        self.scale = scale
        self.data = data
        self.signal = signal
        self.custom = custom

    def clone(self):
        return SampleDef(self.name, category = self.category, title = self.title, directory = self.directory, crosssection = self.crosssection, nevents = self.nevents, sumw = self.sumw, lumi = self.lumi, data = self.data, signal = self.signal, custom = dict(self.custom.items()))

    def dump(self):
        print 'name =', self.name
        print 'category =', self.category
        print 'title =', self.title
        print 'directory =', self.directory
        print 'crosssection =', self.crosssection
        print 'nevents =', self.nevents
        print 'sumw =', self.sumw
        print 'lumi =', self.lumi
        print 'data =', self.data
        print 'signal =', self.signal

class SampleDefList(object):
    def __init__(self, samples = []):
        self.samples = samples

    def __iter__(self):
        return iter(self.samples)

    def __reversed__(self):
        return reversed(self.samples)

    def __getitem__(self, key):
        try:
            return self.get(key)
        except RuntimeError:
            raise KeyError(key + ' not defined')

    def names(self):
        return [s.name for s in self.samples]

    def get(self, name, category = ''):
        if category:
            try:
                return next(s for s in self.samples if s.name == name and s.category == category)
            except StopIteration:
                raise RuntimeError('Sample ' + name + ' category ' + category + ' not found')
        else:
            try:
                return next(s for s in self.samples if s.name == name)
            except StopIteration:
                raise RuntimeError('Sample ' + name + ' not found')

allsamples = SampleDefList()

with open(os.path.dirname(os.path.realpath(__file__)) + '/data/datasets.csv') as dsSource:
    for line in dsSource:
        # print line
        matches = re.match('([^ ]+) +"(.*)" +([^ ]+) +([0-9e.+-x]+) +([0-9]+) +([0-9e.+-]+)', line.strip())
        if not matches:
            continue
        # print matches.group(1), matches.group(2), matches.group(3), matches.group(4), matches.group(5), matches.group(6)

        if matches.group(6) == '-':
            sdef = SampleDef(matches.group(1), title = matches.group(2), directory = matches.group(3), lumi = float(matches.group(4)), nevents = int(matches.group(5)), data = True)
        else:
            xsec = matches.group(4)
            scale = 1.
            if 'x' in xsec:
                (xsec, scale) = xsec.split('x')
                xsec = float(xsec) # * float(scale)
                scale = float(scale)
            else:
                xsec = float(xsec)
            if xsec < 0.:
                signal = True
                xsec = -xsec
            else:
                signal = False

            # print signal, xsec, scale

            sdef = SampleDef(matches.group(1), title = matches.group(2), directory = matches.group(3), crosssection = xsec, scale = scale, nevents = int(matches.group(5)), sumw = float(matches.group(6)), signal = signal)

        allsamples.samples.append(sdef)

if __name__ == '__main__':
    import sys
    import os
    from argparse import ArgumentParser

    argParser = ArgumentParser(description = 'Dataset information management')
    argParser.add_argument('--list', '-L', action = 'store_true', dest = 'list', help = 'List datasets with nevents > 0')
    argParser.add_argument('--all', '-A', action = 'store_true', dest = 'all', help = '(With --list) Show all datasets.')
    argParser.add_argument('--print', '-p', metavar = 'DATASET', dest = 'showInfo', help = 'Print information of DATASET.')
    argParser.add_argument('--recalculate', '-r', metavar = 'DATASET', dest = 'recalculate', help = 'Recalculate nentries and sumw for DATASET.')
    argParser.add_argument('--source-dir', '-d', metavar = 'DIR', dest = 'sourceDir', help = 'Source directory where simpletree files are.')

    args = argParser.parse_args()
    sys.argv = []

    if args.list:
        if args.all:
            print ' '.join([sample.name for sample in allsamples])
        else:
            print ' '.join([sample.name for sample in allsamples if sample.nevents > 0.])

        sys.exit(0)

    if args.showInfo:
        try:
            allsamples[args.showInfo].dump()
        except:
            print 'No sample', args.showInfo
        
        sys.exit(0)

    if args.recalculate:
        name = args.recalculate

        import ROOT
        if args.sourceDir:
            sourceDir = args.sourceDir
        else:
            print 'Source dir?'
            sourceDir = sys.stdin.readline().strip()

        try:
            sample = allsamples[name]
            fNames = [f for f in os.listdir(sourceDir + '/' + sample.directory) if f.startswith('simpletree_')]

            counter = None
            for fName in fNames:
                source = ROOT.TFile.Open(sourceDir + '/' + sample.directory + '/' + fName)
                if counter is None:
                    counter = source.Get('counter')
                    counter.SetDirectory(ROOT.gROOT)
                else:
                    counter.Add(source.Get('counter'))
                source.Close()
        
            if sample.data:
                print name, '', '"' + sample.title + '"', '', sample.directory, '', sample.lumi, '', '%.0f' % counter.GetBinContent(1), '', '-'
            else:
                print name, '', '"' + sample.title + '"', '', sample.directory, '', sample.crosssection, '', '%.0f' % counter.GetBinContent(1), '', counter.GetBinContent(2)
    
        except:
            sys.stderr.write(name + '  NAN\n')

        sys.exit(0)
