#!/bin/bash

binning=ptalt
seed=1001
for bin in $(python efake_conf.py $binning)
do
    for conf in ee eg pass fail
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