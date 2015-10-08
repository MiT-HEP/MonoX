# MonoX
Common repository for mono-X searches

# Met Studies Tool

Located in `MonoX/monojet/MetRecoilStudy` is a set of tools that can be used to generate very flat trees from Nero, make plots, and do fits.

## Generating flat trees

### Configuring Trees

The variables that you want to include in a flat tree can be specified in `MonoJetTree.txt`.
The format of the configuration file is `<branchName>/<type>=<default>`.
`<branchName>` should be easy to understand.
Valid entries for `<type>` include `F`, `I`, or `O` for float, integer, and boolean, respectively.
You can also use `VF`, `VI`, or `VO` for (pointers of) vectors of these types.
After writing a tree configuration file with name `MonoJetTree.txt`, just run
```
./makeTree.sh
```
This makes a class that contains your tree.
You can call each branch of the tree via a public member with the same name of the `<branchName>` and fill it with function `Fill()` at the end of each event.
You can then write the tree to a file via `WriteToFile(*TFile,"<WhatYouWantToCallTree>")`.
If you do not set a value for a particular event, the branch will be filled with `<default>`.
See `NeroSlimmer.cc` for an example of how to write a flat tree writer using this class.

To actually run `NeroSlimmer.cc`, you need to run
```
./runSlimmer.py <NeroFileLocation> <OutputFileLocation>
```
This loads the `MonoJetTree` class as well as the `NeroTree` class, generated from a Nero file.
Simply running
```
./runSlimmer.py test
```
also runs over one Nero file.
Use this to debug.

### Making Trees

Assuming everything in this repository works, you can start turning Nero files into MonoJetTrees right away.
Configure `submit.sh` to submit batch jobs on LXPLUS.
`FilesPerJob` determines the maximum number of files on a single job.
Don't change the number of files per job unless you are starting a fresh run over Nero.
Otherwise, the script can't keep track of which files are finished.
`numProc` determines the number of processers you want to use if you really need to speed up your jobs.
`outDir` specifies your eventual output (with hadded files).
`lfsOut` is the directory files will be stored in the meanwhile.
Make sure this is empty before a fresh run, or corresponding jobs won't be submitted.
`eosDir` is the directory all of your Nero samples are in.
`skimmedDir` is the directory you might want your skimmed files eventually.
I'll get to that later.
Once these are set, run
```
./submit.sh
```
Once these jobs finish, run the same script again.
If any jobs failed, they will be resubmitted.
If all files are successfully completed, the files in `lfsOut` will be hadded into `outDir`.

### Slimming Trees

To slim trees, configure `FlatSlimmer.py`.
`inDir` is where the unslimmed root files are.
`outDir` is where they will be placed.
Make sure `outDir` exists.
Set a `GoodRunsFile` that will be used to apply a filter on data, and `cut` to make any additional cut on the slimmed trees.
Then just run
```
./FlatSlimmer.py <NumProc>
```
Your slimmed files will appear soon.

If you set `inDir` and `outDir` to match the `lfsOut` and `lfsOut/skimmed` from `submit.sh`, then you can do the following from `MonoX/monojet/MetRecoilStudy`
```
cat <lfsOut>/skimmed/myHadd.txt | xargs -n2 -P<NumProc> ./haddArgs.sh
```
I use `localSlimmer.sh` to do that, actually.
This will hadd skimmed files into the `skimmedDir` set in `submit.sh`.

If you just want to apply the good runs filter without slimming other trees, set `inDir`, `outDir`, and `GoodRunsFile` in `goodRunSlimmer.py` and run
```
./goodRunSlimmer.py <NumProc>
```

### NLO Corrections to GJets

In order to apply NLO corrections to your GJets files, set the directory where your samples are located in `runNLOGamma.sh`.
Make sure you have the `kfactor.root` file in your directory.
I'll try to keep a copy at `/afs/cern.ch/work/d/dabercro/public/Winter15/MonoX/monojet/MetRecoilStudy/kfactor.root`.
Or you can edit `nloGamma.cc` to just load this file directly.
Anyway
```
./runNLOGamma.sh
```
will also put an hadded sample `monojet_GJets.root` into your sample directory.
This file has `XSecWeight` and `nloFactor` branches in the friendly treey `nloTree`.
`XSecWeight` is just a relative weight for plotting all of GJets on the same histogram.

## Plotter

This describes some of the packages in `MonoX/monojet/MetRecoilStudy/plotter`

### Plotting resolution

The configuration is mostly done in `recoilPlots.py`.
The most important object for recoil studies is the PlotResolution object.
It operates by pushing back legend entries, trees, cuts (called weights in the functions), and plotting expressions into parallel vectors.
Alternatively, you can set default values for these.
I've just found it's never good to assume you have a default.
`PlotBase.h` has most of the functions you can use to push back or set a default.
In the case of PlotResolution, the variable you are fitting should be pushed via the `AddExpr`, etc. functions in PlotBase.
The variable you are doing the fits as a function of (such as Z pt or something) should be set using `SetExprX` (setting a default) or `AddExprX` in shown in `PlotResolution.h`.

If you want to dump your fits, make sure to call `SetDumpingFits(True)` first.
This will dump out fits.
In the plots, green is a single Gaussian, blue is a double, and the red lines are the double Gaussian's components.

Once all of these are set, call MakeFitGraphs.
There are two implementations in `PlotResolution.h`, depending on how you want to define binning for the variable you are fitting as a function of.
In the example of `recoilPlots.py`, `xArray` defines your binning in the final plot.
You can also do non-variable binning and just use NumXBins, XMin, and XMax for the first three arguments.
The last three arguments must be NumYBins,YMin, and YMax.
Make sure these are reasonable because that's the region the double Gaussian will be fit over.
To help with the fitting, you can use `SetParameterLimits(ParamNum,Low,High)` to constrain your parameters before fitting.
The function you are constraining with this is `"[3]*TMath::Gaus(x,[0],[1]) + [4]*TMath::Gaus(x,[0],[2])"`.
(See PlotResolution.cc for `fitFunc`.)
So if you want to constrain the mean, use `ParamNum = 0`, or `1` and `2` to constrain the width.

Once you can called the fitting function, the fit results are stored in the plotter.
You can get a vector of TGraphErrors using `FitGraph(num)`.
The numbers correspond to the following fit parameters.
```
0 = Mean of Double Gaussian
1 = Smaller Sigma of Two Gaussians
2 = Larger Sigma of Two Gaussians
3 = Weighted Average of Sigmas
4 = Mean of a Single Gaussian Fit
5 = Sigma of a Single Gaussian Fit
```

There are some things in `recoilPlots.py` that then fit these TGraphErrors for the eventual recoil corrections.
I'll skip that for now.

The final step you're probably interested in is `MakeCanvas(fileBase,vector<TGraphErrors*>,PlotTitle,XLabel,YLabel,MinY,MaxY)`.
The Graphs determine MinX and MaxX.
There's also an optional argument at the end to make log plots.
See the `PlotResolution.h` for more help maybe.
This function will save files `<fileBase>.png(.pdf){.C}`.
If you leave out `fileBase`, you will call a function that actually returns a TCanvas*.

### Plotting histograms

PlotHists is probably really easy to use if you get used to using PlotResolution.
In this case, you only need to make sure to use `SetExpr` for the X values (because `SetExprX` is only a PlotResolution member).
Otherwise, it is also derived from PlotBase.
It only has a couple options and does not even require for you to call `MakeHists` in order to save a filled canvas.
(I just have that there because it's really handy in other codes, such as my ROC curve stuff that isn't here.)
