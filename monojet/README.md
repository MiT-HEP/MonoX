# Monojet analysis 13TeV studies

This directory holds the skimmer & slimmer code (slimmer/monojet_TEMP.C) and the selection macro
(makePlots.py). Its usage is briefly explained below.

The skimmer input is a nero file (preferablly from bambu). This code will drop the unnecessary
branches, and add an other tree with some newly calculated information for the analysis.
This will also replace some of the branches in the events tree depending which control region
we would like to check such as met (it will become fakemet if you have 1 or 2 leptons).

In the future, this code can also be used to calculate shifted / smeared collection for systematic
uncertainty calculations.

Note that, if the input file format changes, the slimmer and skimmer will have to change (at least the .h file)
This is kind of annoying I agree.

At the current implementation monojet_TEMP.C is a TSelector. There is a small script written to interface the files to it
properly. This script is: new_simpleRunner.csh (great naming I know). The usage is:

```
./new_simpleRunner.csh sampleNAME
```

This script creates a tchain using the files specified in the sampleNAME. This sampleNAME is a txt file in the
/sourceFiles directory. It has list of all the files and their physical locations.
The runner script will chain "events" tree of these files and run the monojet.C on them. It also will merge the "all tree"
and write out at the same output file at the end. It further will save a histogram to be used in the plotting step
for the effective number of events.

Now we are the step of the selection macro. The selection macro is the makePlots.py At the end of this script you 
can specify the variable you would like to draw and also the channel (signal or the control regions or even all). 
"selection.py" script will hold the different selection to be called for each channel. This script relies on a simple TDraw. 
The weights (lumi, mc weight, etc) are applied on the fly. 

The input files to this plotter is given in LoadData.py There you can adjust the input file names, the colors, the xsec etc.
Here we also decalre the other trees (such as the one created with more info) as a friend to our main events tree.

To run the selector and plotter do:

```
./makePlots.py -b -q -l
```

Make sure you have a directory called /test where the output histograms will be written to.
This chain also produces the cut based data cards. There is a small annoyance to be fixed, which
is when there are multiple bins for a process (such as Zvv) it creates multiple entries. Easy to fix
will take care of it soon.

Once we have the signal samples we can test the sensitivity too.

The whole chain has been tested and the preliminary plots have been circulated. We are missing met filters
which effects the overall distributions.
