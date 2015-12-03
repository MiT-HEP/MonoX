#!/bin/bash

jdlpath=/home/ballen/cms/cmssw/042/CMSSW_7_4_6/src/MitMonoX/monophoton/purity/condor/calc
scratch=/scratch5/ballen/hist/purity/simpletree10/sieie/Plots
# scratch=/home/ballen/public_html/cmsplots/PurityTemp/

# shape="Shape"
shape="TwoBin"
locations="barrel endcap"
photonids="loose medium tight"
chisosbcuts="30to50 50to70 70to90"
ptcuts="175to200 200to250 250to300 300to350 350toInf"
#metcuts="0toInf 0to100 100to250 250toInf"
metcuts="0toInf"

#locations="barrel"
#photonids="medium"
#ptcuts="175toInf"


for loc in $locations
do
    # echo $loc
    for sel in $photonids
    do
	# echo $sel
	for chiso in $chisosbcuts
	do
	    # echo chiso
	    for pt in $ptcuts
	    do
		# echo pt
		for met in $metcuts
		do
		    echo ${scratch}/${shape}/${loc}_${sel}_ChIso${chiso}_PhotonPt${pt}_Met${met}
		    mkdir -p ${scratch}/${shape}/${loc}_${sel}_ChIso${chiso}_PhotonPt${pt}_Met${met}
		    sed 's#LOC#'$loc'#' ${jdlpath}/condor.jdl | sed 's#SEL#'$sel'#' | sed 's#CHISO#'$chiso'#' | sed 's#PT#'$pt'#' | sed 's#MET#'$met'#' | sed 's#SHAPE#'$shape'#' | condor_submit
		done
	    done
	done
    done
done