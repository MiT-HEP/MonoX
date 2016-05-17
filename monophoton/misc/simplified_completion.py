import os
import re
import collections
import subprocess

server = 'root://xrootd.cmsaf.mit.edu/'
directory = '/store/user/paus/fastsm/043/'
command = 'source /cvmfs/cms.cern.ch/cmsset_default.sh; cd ' + os.environ['CMSSW_BASE'] + '; eval `scram runtime -sh`; xrdfs %s ls %s/monophoton_{point} | sort | uniq' % (server, directory)

output = open('simplified_fastsim.txt', 'w')

with open('../data/fastsim_list.txt') as source:
    for line in source:
        matches = re.match('(med-([0-9]+)_dm-([0-9]+)_cv-([01]\.0)_ca-[01]\.0)_nev-50000', line)
        if not matches:
            continue

        point = matches.group(1)
        med = int(matches.group(2))
        dm = int(matches.group(3))
        cv = float(matches.group(4))

        print point

        proc = subprocess.Popen(command.format(point = point), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, err = proc.communicate()

        fnames = filter(lambda f: 'miniaodsim' in f, out.split('\n'))

        flist = collections.defaultdict(list)
        for fname in fnames:
            matches = re.match('/.*/monophoton_med-[0-9]+_dm-[0-9]+_cv-.+_ca-.+_nev-([0-9]+)_seed-([0-9]+)_miniaodsim.root', fname)
            if not matches:
                print fname
                continue

            flist[int(matches.group(2))].append((int(matches.group(1)), fname))

        total = 0
        block = ''
        for seed in sorted(flist.keys()):
            best = ''
            bestn = 0
            for nev, fname in flist[seed]:
                if nev > bestn:
                    best = fname
                    bestn = nev

            total += bestn
            flist[seed].remove((bestn, best))

            block += server + best.replace('//', '/') + '\n'

            for nev, fname in flist[seed]:
                block += '#' + server + fname.replace('//', '/') + '\n'
            
        output.write('[med-%d_dm-%d %s] %d events\n' % (med, dm, 'V' if cv == 1. else 'AV', total))
        output.write(block)
        output.write('\n')
