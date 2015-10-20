#! /bin/bash

root -q -l -b xsecWeights.cc+                      # This is to just make sure the macro is compiled

cat xsecArgs.txt | xargs -n2 -P6 ./xsecRunner.sh
