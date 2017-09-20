#!/bin/bash

asimov=$1
signal=$2
outname=$3
datacard=$4

text2workspace.py ${datacard} -m 125 -o ${outname}.root

if [ ${asimov} == 1 ]
then
    echo "\n  Generating asimov data for impact study. \n"
    combineTool.py -M Impacts -d ${outname}.root -m 125 --robustFit 1 --setPhysicsModelParameterRanges r=-5.0,5.0 --expectSignal=${signal} -t -1 --doInitialFit
    combineTool.py -M Impacts -d ${outname}.root -m 125 --robustFit 1 --setPhysicsModelParameterRanges r=-5.0,5.0 --expectSignal=${signal} -t -1 --doFits --parallel 24
else
    echo "\n  Using provided data for impact study. \n"
    combineTool.py -M Impacts -d ${outname}.root -m 125 --robustFit 1 --setPhysicsModelParameterRanges r=-5.0,5.0 --expectSignal=${signal} --doInitialFit
    combineTool.py -M Impacts -d ${outname}.root -m 125 --robustFit 1 --setPhysicsModelParameterRanges r=-5.0,5.0 --expectSignal=${signal} --doFits --parallel 24
fi

combineTool.py -M Impacts -d ${outname}.root -m 125 -o impacts.json_${outname}
plotImpacts.py -i impacts.json_${outname} -o impacts_${outname}

echo "Done!"
