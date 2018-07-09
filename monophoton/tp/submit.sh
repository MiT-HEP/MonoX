#!/bin/bash

rm -f syst_args.txt

binning=$1
seed=1001
for bin in $(python efake_conf.py $binning)
do
    for conf in ee eg # pass fail
    do
	for type in nominal altsig altbkg
	do
            while [ $(($seed%10)) -ne 0 ]
            do
		echo $bin $conf $type 100 $seed >> syst_args.txt
		seed=$(($seed+1))
            done
            seed=$(($seed+1))
	done
    done
done

~/bin/condor-run efake_tpsyst.py -e "data $binning" -a syst_args.txt
~/bin/condor-run efake_tpsyst.py -e "mc $binning" -a syst_args.txt