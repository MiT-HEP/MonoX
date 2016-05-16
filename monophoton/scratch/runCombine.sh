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

DATACARD=/scratch5/yiiyama/studies/monophoton/datacards/$POINT.dat

combine -M Asymptotic $DATACARD

# take care of r value scaling
fixLimit.py $DATACARD higgsCombineTest.Asymptotic.mH120.root

mv higgsCombineTest.Asymptotic.mH120.root /scratch5/yiiyama/studies/monophoton/limits/$MODEL/$POINT.root
