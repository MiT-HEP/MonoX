#!/bin/bash

POINT=$(echo $1 | cut -d'/' -f 7)

POINT=$(echo $POINT | cut -d. -f 1)

MODEL=$(echo $POINT | cut -d- -f 1)
MMED=$(echo $POINT | cut -d- -f 2)
MDM=$(echo $POINT | cut -d- -f 3)

SCRIPTDIR=$(cd $(dirname $0); pwd)
CARDDIR=/scratch5/ballen/hist/monophoton/datacards
OUTDIR=/scratch5/ballen/hist/monophoton/limits

source /cvmfs/cms.cern.ch/cmsset_default.sh

export CMSSW_BASE=/home/ballen/cms/cmssw/042/CMSSW_7_4_6
cd $CMSSW_BASE
eval `scram runtime -sh`

cd -

DATACARD=$CARDDIR/$POINT.dat

combine -M Asymptotic --run blind $DATACARD
METHOD=Asymptotic
# combine -M ProfileLikelihood --significance $DATACARD -t -1 --expectSignal=1 # --toysFreq
# METHOD=ProfileLikelihood

# take care of r value scaling
python $SCRIPTDIR/fixLimit.py $DATACARD higgsCombineTest.$METHOD.mH120.root

mkdir -p $OUTDIR/$MODEL

mv higgsCombineTest.$METHOD.mH120.root $OUTDIR/$MODEL/$POINT-$METHOD.root
