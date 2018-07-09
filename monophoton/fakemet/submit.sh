#!/bin/bash

# edit parameters_fakemet.py to point sourcename = injection.root and outname = 'workspace.root' cardname = 'datacard.dat'

THISDIR=$(cd $(dirname $0); pwd)

SOURCES="$1"
SIGS="$2"
FAKEN="$3"
IJOBS=$4


rm -f args.txt 

for SOURCE in $SOURCES
do
  for sigs in $SIGS
  do
    for faken in $FAKEN
    do
	i=0
	while [ $i -lt $IJOBS ]
	do
	    echo $SOURCE $sigs $faken $i >> args.txt
	    i=$(($i+1))
	done
    done
  done
done

~/bin/condor-run injection_test.sh -a args.txt