#!/bin/bash

jdlpath=${PURITY}/condor/
scratch=/scratch5/ballen/hist/purity/simpletree18/sieie/Plots/SignalContam
# scratch=${CMSPLOTS}/SignalContamTemp
mkdir -p $scratch

locations="barrel"
#locations="barrel endcap"
photonids="medium"
#photonids="loose medium tight"
chisosbcuts="20to50 50to80 80to110"
ptcuts="175to200 200to250 250to300 300to350 350toInf"
metcuts="0toInf 0to60" # 60to120 120toInf"
# metcuts="60to120 120toInf"

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