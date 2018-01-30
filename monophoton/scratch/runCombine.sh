#!/bin/bash

POINT=$(echo $1 | cut -d'/' -f 7)

POINT=$(echo $POINT | cut -d. -f 1)

MODEL=$(echo $POINT | cut -d- -f 1)
MMED=$(echo $POINT | cut -d- -f 2)
MDM=$(echo $POINT | cut -d- -f 3)

SCRIPTDIR=$(cd $(dirname $0); pwd)
CARDDIR=/data/t3home000/ballen/monophoton/fit/datacards
OUTDIR=/data/t3home000/ballen/monophoton/fit/limits

source /cvmfs/cms.cern.ch/cmsset_default.sh

export CMSSW_BASE=/home/ballen/cms/cmssw/004/CMSSW_8_1_0
cd $CMSSW_BASE
eval `scram runtime -sh`

cd -

DATACARD=$CARDDIR/$POINT.dat

METHOD=AsymptoticLimits
combine -M $METHOD --run blind $DATACARD

# combine -M ProfileLikelihood --significance $DATACARD -t -1 --expectSignal=1 # --toysFreq
# METHOD=ProfileLikelihood

# take care of r value scaling
python $SCRIPTDIR/fixLimit.py $DATACARD higgsCombineTest.$METHOD.mH120.root

mkdir -p $OUTDIR/$MODEL

mv higgsCombineTest.$METHOD.mH120.root $OUTDIR/$MODEL/$POINT-$METHOD.root
