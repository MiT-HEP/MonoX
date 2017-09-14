#!/bin/bash

signal=$1
outname=$2
datacard=$3

text2workspace.py ${datacard} -m 125 -o ${outname}.root
combineTool.py -M Impacts -d ${outname}.root -m 125 --robustFit 1 --freezeNuisances lumiscale --setPhysicsModelParameterRanges r=-5.0,5.0 --expectSignal=${signal} -t -1 --doInitialFit
combineTool.py -M Impacts -d ${outname}.root -m 125 --robustFit 1 --freezeNuisances lumiscale --setPhysicsModelParameterRanges r=-5.0,5.0 --expectSignal=${signal} -t -1 --doFits
combineTool.py -M Impacts -d ${outname}.root -m 125 -o impacts.json_${outname}
plotImpacts.py -i impacts.json_${outname} -o impacts_${outname}

echo "Done!"