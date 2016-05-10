#!/bin/bash

POINT=$1

MODEL=$(echo $POINT | cut -d- -f 1)
MMED=$(echo $POINT | cut -d- -f 2)
MDM=$(echo $POINT | cut -d- -f 3)

source /cvmfs/cms.cern.ch/cmsset_default.sh

export CMSSW_BASE=/scratch1/yiiyama/cmssw/combine/CMSSW_7_1_5
cd $CMSSW_BASE
eval `scram runtime -sh`

cd -

combine -M Asymptotic -m $(printf %d%04d $MMED $MDM) /scratch5/yiiyama/studies/monophoton/datacards/$POINT.dat
cp *.root /scratch5/yiiyama/studies/monophoton/limits/$MODEL/$POINT.root
