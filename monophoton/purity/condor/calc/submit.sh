#!/bin/bash

jdlpath=/home/ballen/cms/cmssw/042/CMSSW_7_4_6/src/MitMonoX/monophoton/purity
#scratch=/scratch5/ballen/hist/purity/simpletree5/sieie/Plots
scratch=/home/ballen/public_html/cmsplots/PurityTemp/

locations="barrel endcap"
photonids="loose medium tight"
chisosbcuts="3to5 5to7 7to9"
ptcuts="150to250 250to350 350toInf"
#ptcuts="150to200 200to250 250to300 300to500 500toInf"
#ptcuts="150to200 200to300 300to400 400toInf"
#ptcuts="150toInf 150to200 200to250 250to300 300to350 350to400 400to450 450to500 500toInf"
#metcuts="0toInf 0to100 100to250 250toInf"
metcuts="0toInf"

#locations="barrel"
#photonids="medium"
#ptcuts="180toInf 150toInf"
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