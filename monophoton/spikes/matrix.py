import os
import sys
import math
import ROOT as r

basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(basedir)
from plotstyle import SimpleCanvas
from datasets import allsamples
import config

candTree = r.TChain('events')
candTree.Add(config.skimDir + '/sph-16b2-d_monoph.root')
candTree.Add(config.skimDir + '/sph-16c2-d_monoph.root')
candTree.Add(config.skimDir + '/sph-16d2-d_monoph.root')

promptTree = r.TChain('events')
promptTree.Add(config.skimDir + '/sph-16b2-d_efake.root')
promptTree.Add(config.skimDir + '/sph-16c2-d_efake.root')
promptTree.Add(config.skimDir + '/sph-16d2-d_efake.root')

spikeTree = r.TChain('events')
spikeTree.Add(config.skimDir + '/sph-16b2-d_spikeSieie.root')
spikeTree.Add(config.skimDir + '/sph-16c2-d_spikeSieie.root')
spikeTree.Add(config.skimDir + '/sph-16d2-d_spikeSieie.root')

selection = 'photons.scRawPt[0] > 175. && t1Met.photonDPhi > 2. && t1Met.minJetDPhi > 0.5 && t1Met.met > 170.'
variable = '((photons.emax[0] + photons.e2nd[0]) / photons.e33[0])'

hbase = r.TH1F('hbase', ';E2/E9', 50, 0.2, 1.2)

cuts = [ ('Total', ''), ('Pass', ' && '+variable+' < 0.95'), ('Fail', ' && '+variable+' > 0.95')]

cands = [] 
prompts = []
spikes = []

for title, cut in cuts:
    hcand = hbase.Clone('hcand'+title)
    candTree.Draw(variable+'>>hcand'+title, selection+cut)
    print title+" candidates", hcand.Integral()
    cands.append(hcand.Integral())
    
    hprompt = hbase.Clone('hprompt'+title)
    promptTree.Draw(variable+'>>hprompt'+title, selection+cut)
    print title+" prompt sample", hprompt.Integral()
    prompts.append(hprompt.Integral())
    
    hspike = hbase.Clone('hspike'+title)
    spikeTree.Draw(variable+'>>hspike'+title, selection+cut)
    print title+" spike sample", hspike.Integral()
    spikes.append(hspike.Integral())

promptEff = prompts[1] / prompts[0]
promptEffErr = promptEff * math.sqrt( 1. / prompts[1] + 1. / prompts[0] )
spikeEff = spikes[1] / spikes[0]
spikeEffErr = spikeEff * math.sqrt( 1. / spikes[1] + 1. / prompts[0] )
print "Prompt efficiency", promptEff, 'pm', promptEffErr
print "Spike efficiency", spikeEff, 'pm', spikeEffErr

effDiff = spikeEff - promptEff
effDiffErr = math.sqrt( spikeEffErr**2 + promptEffErr**2)
print "Efficiency difference", effDiff, 'pm', effDiffErr

candPromptEff = promptEff * cands[0]
candPromptEffErr = candPromptEff * math.sqrt( (promptEffErr / promptEff)**2 + 1. / cands[0] )
print "PromptEff * Candidates", candPromptEff, 'pm', candPromptEffErr

candPassDiff = cands[1] - candPromptEff
candPassDiffErr = math.sqrt( cands[1] + candPromptEffErr**2)
print "Candidate Pass Difference", candPassDiff, 'pm', candPassDiffErr

spikeEst = candPassDiff / effDiff
spikeEstErr = spikeEst * math.sqrt( candPassDiffErr**2 + effDiffErr**2)
print "Spike estimate is", spikeEst, 'pm', spikeEstErr
    
