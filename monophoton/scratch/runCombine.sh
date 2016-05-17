#!/bin/bash

POINT=$1

MODEL=$(echo $POINT | cut -d- -f 1)
MMED=$(echo $POINT | cut -d- -f 2)
MDM=$(echo $POINT | cut -d- -f 3)

SCRIPTDIR=$(cd $(dirname $0); pwd)
CARDDIR=/scratch5/yiiyama/studies/monophoton/datacards
OUTDIR=/scratch5/yiiyama/studies/monophoton/limits

source /cvmfs/cms.cern.ch/cmsset_default.sh

export CMSSW_BASE=/scratch1/yiiyama/cmssw/combine/CMSSW_7_1_5
cd $CMSSW_BASE
eval `scram runtime -sh`

cd -

DATACARD=$CARDDIR/$POINT.dat

combine -M Asymptotic $DATACARD

# take care of r value scaling
python $SCRIPTDIR/fixLimit.py $DATACARD higgsCombineTest.Asymptotic.mH120.root

mv higgsCombineTest.Asymptotic.mH120.root $OUTDIR/$MODEL/$POINT.root
