import re
import os
import ROOT

class SampleDef(object):
    def __init__(self, name, category = '', title = '', directory = '', color = ROOT.kBlack, crosssection = 0., nevents = 0, sumw = 0., lumi = 0., data = False, group = '', custom = {}):
        self.name = name
        self.category = category
        self.title = title
        self.directory = directory
        self.color = color
        self.crosssection = crosssection
        self.nevents = nevents
        if sumw == 0.:
            self.sumw = float(nevents)
        else:
            self.sumw = sumw
        self.lumi = lumi
        self.data = data
        self.group = group
        self.custom = custom

    def clone(self):
        return SampleDef(self.name, category = self.category, title = self.title, directory = self.directory, color = self.color, crosssection = self.crosssection, nevents = self.nevents, sumw = self.sumw, lumi = self.lumi, data = self.data, group = self.group, custom = dict(self.custom.items()))


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

with open(os.path.dirname(__file__) + '/data/datasets.csv') as dsSource:
    for line in dsSource:
        matches = re.match('([^ ]+) +"(.*)" +([^ ]+) +([0-9e.+-]+) +([0-9]+) +([0-9e.+-]+)', line.strip())
        if not matches:
            continue

        if matches.group(6) == '-':
            sdef = SampleDef(matches.group(1), title = matches.group(2), directory = matches.group(3), lumi = float(matches.group(4)), nevents = int(matches.group(5)), data = True)
        else:
            sdef = SampleDef(matches.group(1), title = matches.group(2), directory = matches.group(3), crosssection = float(matches.group(4)), nevents = int(matches.group(5)), sumw = float(matches.group(6)))

        allsamples.samples.append(sdef)

if __name__ == '__main__':
    import sys

    if '-a' in sys.argv:
        print ' '.join([sample.name for sample in allsamples])
    else:
        print ' '.join([sample.name for sample in allsamples if sample.nevents > 0.])
