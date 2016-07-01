#!/bin/bash

LOC=$1
SEL=$2
CHISO=$3
PT=$4
MET=$5

source /cvmfs/cms.cern.ch/cmsset_default.sh

cd /home/ballen/cms/cmssw/044/CMSSW_8_0_7_patch3
eval `scram runtime -sh`
cd -

# python ${CMSSW_BASE}/src/MitMonoX/monophoton/purity/signalcontam.py $LOC $SEL $CHISO $PT $MET
python ${CMSSW_BASE}/src/MitMonoX/monophoton/purity/bkgdstats.py $LOC $SEL $CHISO $PT $MET