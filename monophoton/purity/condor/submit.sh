#!/bin/bash

jdlpath=${PURITY}/condor/
scratch=/scratch5/ballen/hist/purity/simpletree13c/sieie/Plots/SignalContam
# scratch=${CMSPLOTS}/SignalContamTemp
mkdir -p $scratch

locations="barrel"
#locations="barrel endcap"
photonids="medium"
#photonids="loose medium tight"
#chisosbcuts="20to40 25to45 30to50 35to55 40to60 45to65 50to70 55to75 60to80 65to85 70to90 75to95 80to100"
chisosbcuts="20to50 50to80 80to110"
#chisosbcuts="50to70"
# ptcuts="250to350"
ptcuts="100to140 140to175 175to200 200to250 250to300 300to350 350toInf"
#ptcuts="175to200 200to250 250to300 300to350 350to400 400to500 500to600 600toInf"
#metcuts="0toInf 0to100 100to250 250toInf"
metcuts="0toInf 0to60 60to120 120to180 180toInf"

for loc in $locations
do
    for sel in $photonids
    do
	for chiso in $chisosbcuts
	do
	    for pt in $ptcuts
	    do
		for met in $metcuts
		do
		    mkdir -p ${scratch}/${loc}_${sel}_ChIso${chiso}_PhotonPt${pt}_Met${met}
		    sed 's#LOC#'$loc'#' ${jdlpath}/condor.jdl | sed 's#SEL#'$sel'#' | sed 's#CHISO#'$chiso'#' | sed 's#PT#'$pt'#' | sed 's#MET#'$met'#' | condor_submit
		done
	    done
	done
    done
done

# cp -r $scratch ${CMSPLOTS}/ST10/Plots/.