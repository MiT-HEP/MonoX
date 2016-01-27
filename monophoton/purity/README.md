INSTRUCTIONS FOR HOW TO USE THE PURITY CODE


1. selections.py
   A big file containing things that are needed in multiple other files and/or are large and messy and would make the functional code look way worse.
   Most of the functional code has a big "from selections import <Variables>, <Functions>" at the top so you know what to look at in this file.
   There is some structure to this file, but it is probably easier to just search for the name of what you are looking for.

2. makeskims.py
   Takes simpletree files as input and then outputs skimmed trees to be used in the purity studies. 
   What input files, skims, cuts, regions, samples, etc are all specificed in selections.py

3. plotiso.py
   Used in bkgdstats.py, see below.

4. bkgdstats.py
   This is the file that runs the current signal subtraction method (shown in Monojet meeting on 16/01/22). Pulls a bunch of stuff from selections.py.
   Designed to take selection specifications from command line: i.e. bkgdstats.py barrel medium 50to80 250to300 0toInf
   Calls on plotiso.py to get the chIso distributions.
   Calculates purity using signal subtraction method and then does alternative calculations of purity for the uncertainty.
   Leaves a bunch of plots and text output behind. Text output is used in plotcontam.py

5. condor/contam/*
   The necessary scripts to use condor to run bkgdstats.py for lots of different selections at once. 
   Basic condor stuff, you probably only need to change the input and output directories in addition to the specific selections you want.

6. plotcontam.py
   Reads all the output from the condor jobs and then makes lots of pretty plots and tables.
   Commented out section was for fitting as a function of the chIso sideband choice.
   Should update to output a rootfile with the final purities and uncertainties.

7. Everything else
   Was used in the development of this code and for older versions of the studies. 
   You can play around if you want, but it won't give you as much information as the above procedure.