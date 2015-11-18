# Monojet analysis 13TeV studies

This directory holds the skimmer & slimmer code and the selection macro
(makePlots.py). Its usage is briefly explained below and in the respective directories.

To learn about the usage of the slimmer please look at the read me file under /slimmer directory

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
