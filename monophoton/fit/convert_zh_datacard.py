import sys
sys.dont_write_bytecode = True
import os
import array

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)

import ROOT
ROOT.gSystem.Load('libRooFit.so')
ROOT.gSystem.Load('libRooFitCore.so')

outputFile = ROOT.TFile.Open(basedir + '/data/zh_results.root', 'recreate')

outputDir = outputFile.mkdir('imt')

with open(basedir + '/data/zh_datacard.dat') as source:
    while True:
        line = source.readline()
        if not line:
            break

        if not line.strip(' \n-') or line.startswith('kmax') or line.startswith('shapes'):
            continue

        elif line.startswith('imax'):
            nbins = int(line.split()[1])

            template = ROOT.TH1D('template', '', nbins, array.array('d', [0. + x for x in range(nbins + 1)]))

        elif line.startswith('jmax'):
            nprocs = int(line.split()[1])

        elif line.startswith('bin'):
            if not outputDir.Get('data_obs'):
                # first bin row
                line = source.readline() # observation
                outputDir.cd()
                obs = template.Clone('data_obs')
                for iw, word in enumerate(line.split()[1:]):
                    for _ in range(int(float(word))):
                        obs.Fill(float(iw))

                obs.Write()

            else:
                line = source.readline() # process
                proc_names = line.split()[1:nprocs + 2]

                outputDir.cd()
                nominals = []
                for iproc in range(len(proc_names)):
                    proc_name = proc_names[iproc]
                    nominals.append(template.Clone(proc_name))

                source.readline() # skip the process number line
                line = source.readline()
                iproc = 0
                ibin = 1
                for word in line.split()[1:]:
                    cont = float(word)
                    if proc_names[iproc] == 'dph-nlo-125':
                        cont *= 0.1 # gghg and vbfg uses 0.1*SM

                    nominals[iproc].SetBinContent(ibin, cont)
                    iproc += 1
                    if iproc % len(proc_names) == 0:
                        iproc = 0
                        ibin += 1

                for iproc, nominal in enumerate(nominals):
                    # signal will be written to outputDir
                    nominal.Write()

        else: # nuisance
            words = line.split()
            nuis_name = words[0]

            for iproc in range(nprocs + 1):
               
                proc_name = proc_names[iproc]

                outputDir.cd()
                nominal = outputDir.Get(proc_name)

                name = proc_name + '_' + nuis_name
                up = template.Clone(name + 'Up')
                down = template.Clone(name + 'Down')

                has_var = False

                for ix, word in enumerate(words[ix] for ix in range(2 + iproc, len(words), nprocs + 1)): # read every (nproc+1) word starting from 2 + iproc
                    if word == '-':
                        up.SetBinContent(ix + 1, nominal.GetBinContent(ix + 1))
                        down.SetBinContent(ix + 1, nominal.GetBinContent(ix + 1))
                        continue

                    elif '/' in word:
                        vup, vdown = map(float, word.split('/'))
                    else:
                        vup = float(word)
                        vdown = 2. - vup

                    has_var = True

                    up.SetBinContent(ix + 1, nominal.GetBinContent(ix + 1) * vup)
                    down.SetBinContent(ix + 1, nominal.GetBinContent(ix + 1) * vdown)

                if has_var:
                    up.Write()
                    down.Write()

                up.Delete()
                down.Delete()
