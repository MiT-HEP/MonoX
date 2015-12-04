#!/bin/bash

jdlpath=${PURITY}/condor/contam
scratch=/scratch5/ballen/hist/purity/simpletree10/sieie/Plots/SignalContam
# scratch=${CMSPLOTS}/SignalContamTemp
mkdir -p $scratch

#locations="barrel endcap"
#photonids="loose medium tight"
#chisosbcuts="3.0to5.0 5.0to7.0 7.0to9.0"
chisosbcuts="20to40 25to45 30to50 35to55 40to60 45to65 50to70 55to75 60to80 65to85 70to90 75to95 80to100"
#ptcuts="150to250 250to350 350toInf"
#ptcuts="150to200 200to250 250to300 300to500 500toInf"
#ptcuts="150to200 200to300 300to400 400toInf"
#ptcuts="150toInf 150to200 200to250 250to300 300to350 350to400 400to450 450to500 500toInf"
#metcuts="0toInf 0to100 100to250 250toInf"
metcuts="0toInf"

locations="barrel"
photonids="medium"
ptcuts="175toInf"
#metcuts="0toInf"

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