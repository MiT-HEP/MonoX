import os
import sys
import shutil

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config
import utils
from datasets import allsamples

import ROOT

for sample in allsamples.getmany('sph-16*'):
    source = ROOT.TFile.Open(utils.getSkimPath(sample.name, 'offtime'))

    tree = source.Get('events')
    tmpname = '/tmp/' + os.environ['USER'] + '/' + sample.name + '_offtimeIso.root'
    outputFile = ROOT.TFile.Open(tmpname, 'recreate')

    newtree = tree.CopyTree('TMath::Abs(photons.scEta) < 1.4442 && photons.scRawPt > 175 && photons.mipEnergy < 4.9 && photons.time > -15. && photons.time < -10. && (photons.mediumX[][2] || (photons.type == 2 && photons.trackIso < 40.)) && photons.sieie < 0.0104 && photons.hOverE < 0.026 && t1Met.pt > 170. && t1Met.photonDPhi > 0.5 && t1Met.minJetDPhi > 0.5')
    newtree.Write()
    source.Close()
    outputFile.Close()

    shutil.copy(tmpname, config.skimDir + '/' + sample.name + '_offtimeIso.root')
    os.remove(tmpname)
