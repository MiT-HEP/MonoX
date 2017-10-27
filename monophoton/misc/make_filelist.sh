#!/bin/bash

DIR=$1

i=0
ls $DIR/* | while read line
do
    URL=root:://t3serv006.mit.edu/$(echo $line | sed 's|/mnt/hadoop||')
    echo $URL
done