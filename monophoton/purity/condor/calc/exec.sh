#!/bin/bash

LOC=$1
SEL=$2
CHISO=$3
PT=$4
MET=$5
SHAPE=$6

source /cvmfs/cms.cern.ch/cmsset_default.sh

cd /home/ballen/cms/cmssw/042/CMSSW_7_4_6
eval `scram runtime -sh`
cd -

python /home/ballen/cms/cmssw/042/CMSSW_7_4_6/src/MitMonoX/monophoton/purity/calcpurity.py $LOC $SEL $CHISO $PT $MET $SHAPE

mkdir -p /home/ballen/public_html/cmsplots/ST10/Plots/${SHAPE}
cp -r /scratch5/ballen/hist/purity/simpletree10/sieie/Plots/${SHAPE}/${LOC}_${SEL}_ChIso${CHISO}_PhotonPt${PT}_Met${MET} /home/ballen/public_html/cmsplots/ST10/Plots/${SHAPE}/.
