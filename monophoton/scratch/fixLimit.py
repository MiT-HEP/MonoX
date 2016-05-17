import sys
import os
import re
import shutil
import array
import ROOT

cardpath, sourcepath = sys.argv[1:3]

rscale = 1.

with open(cardpath) as datacard:
    lines = datacard.read().strip().split('\n')
    matches = re.match('# R x ([0-9.e+-]+)', lines[-1])
    if matches:
        rscale = float(matches.group(1))

if rscale == 1.:
    sys.exit(0)

shutil.copyfile(sourcepath, 'limittmp.root')

variables = {
    'limit': array.array('d', [0.]),
    'limitErr': array.array('d', [0.]),
    'mh': array.array('d', [0.]),
    'syst': array.array('i', [0]),
    'iToy': array.array('i', [0]),
    'iSeed': array.array('i', [0]),
    'iChannel': array.array('i', [0]),
    't_cpu': array.array('f', [0.]),
    't_real': array.array('f', [0.]),
    'quantileExpected': array.array('f', [0.])
}

source = ROOT.TFile.Open(sourcepath)

output = ROOT.TFile.Open('limittmp.root', 'update')

intree = source.Get('limit')

for vname, addr in variables.items():
    intree.SetBranchAddress(vname, addr)

output.cd()
outtree = intree.CloneTree(0)

iEntry = 0
while intree.GetEntry(iEntry) > 0:
    iEntry += 1
    
    variables['limit'][0] *= rscale
    variables['limitErr'][0] *= rscale

    outtree.Fill()

output.cd()
outtree.Write('limit', ROOT.TObject.kOverwrite)

source.Close()
output.Close()

os.rename('limittmp.root', sourcepath)
