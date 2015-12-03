#!/bin/bash

LOC=$1
SEL=$2
CHISO=$3
PT=$4
MET=$5

source /cvmfs/cms.cern.ch/cmsset_default.sh

cd /home/ballen/cms/cmssw/042/CMSSW_7_4_6
eval `scram runtime -sh`
cd -

python /home/ballen/cms/cmssw/042/CMSSW_7_4_6/src/MitMonoX/monophoton/purity/calcpurity.py $LOC $SEL $CHISO $PT $MET

#tar -zcvf out.tar *.pdf

#mv *.pdf /scratch5/ballen/hist/purity/simpletree5/sieie/Plots/${LOC}_${SEL}_${PT}_${MET}/.
