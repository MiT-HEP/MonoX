# Met Studies Tool

Located in `MonoX/monojet/MetRecoilStudy` is a set of tools that can be used to make plots, and do fits.

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
