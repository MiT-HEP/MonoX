#include <iostream>
#include "TGraph.h"
#include "TF1.h"
#include "TH2D.h"
#include "TLegend.h"

#include "PlotBase.h"

ClassImp(PlotBase)

//--------------------------------------------------------------------
PlotBase::PlotBase() :
  fPlotCounter(0),
  fCanvasName("canvas"),
  fDefaultLineWidth(2),
  fDefaultLineStyle(1),
  fIncludeErrorBars(false),
  fDefaultTree(0),
  fDefaultCut(""),
  fDefaultExpr(""),
  l1(0.6),
  l2(0.7),
  l3(0.9),
  l4(0.9),
  fLegendBorderSize(0)
{
  fInTrees.resize(0);
  fInCuts.resize(0);
  fInExpr.resize(0);
  fLegendEntries.resize(0);
  fLineColors.resize(0);
  fLineWidths.resize(0);
  fLineStyles.resize(0);
}

//--------------------------------------------------------------------
PlotBase::~PlotBase()
{}

//--------------------------------------------------------------------
void
PlotBase::AddLine(TTree *tree, TString cut, TString expr)
{
  // Check for defaults. If none, set the values for each line.
  if (fDefaultTree != NULL) {
    std::cout << "Default tree already set! Check configuration..." << std::endl;
    exit(1);
  }
  if (fDefaultCut != "") {
    std::cout << "Default cut already set! Check configuration..." << std::endl;
    exit(1);
  }
  if (fDefaultExpr != "") {
    std::cout << "Default resolution expression already set! Check configuration..." << std::endl;
    exit(1);
  }
  fInTrees.push_back(tree);
  fInCuts.push_back(cut);
  fInExpr.push_back(expr);
}

//--------------------------------------------------------------------
void
PlotBase::AddTreeWeight(TTree *tree, TString cut)
{
  // Check for defaults. If none, set the values for each line.
  if (fDefaultTree != NULL) {
    std::cout << "Default tree already set! Check configuration..." << std::endl;
    exit(1);
  }
  if (fDefaultCut != "") {
    std::cout << "Default cut already set! Check configuration..." << std::endl;
    exit(1);
  }
  if (fDefaultExpr == "") {
    std::cout << "Please set default resolution expression first!" << std::endl;
    exit(1);
  }
  fInTrees.push_back(tree);
  fInCuts.push_back(cut);
}

//--------------------------------------------------------------------
void
PlotBase::AddTreeExpr(TTree *tree, TString expr)
{
  // Check for defaults. If none, set the values for each line.
  if (fDefaultTree != NULL) {
    std::cout << "Default tree already set! Check configuration..." << std::endl;
    exit(1);
  }
  if (fDefaultCut == "") {
    std::cout << "Please set default cut first!" << std::endl;
    exit(1);
  }
  if (fDefaultExpr != "") {
    std::cout << "Default resolution expression already set! Check configuration..." << std::endl;
    exit(1);
  }
  fInTrees.push_back(tree);
  fInExpr.push_back(expr);
}

//--------------------------------------------------------------------
void
PlotBase::AddWeightExpr(TString cut, TString expr)
{
  // Check for defaults. If none, set the values for each line.
  if (fDefaultTree == NULL) {
    std::cout << "Please set default tree first!" << std::endl;
    exit(1);
  }
  if (fDefaultCut != "") {
    std::cout << "Default cut already set! Check configuration..." << std::endl;
    exit(1);
  }
  if (fDefaultExpr != "") {
    std::cout << "Default resolution expression already set! Check configuration..." << std::endl;
    exit(1);
  }
  fInCuts.push_back(cut);
  fInExpr.push_back(expr);
}

//--------------------------------------------------------------------
void
PlotBase::SetLegendLimits(Double_t lim1, Double_t lim2, Double_t lim3, Double_t lim4)
{
  l1 = lim1;
  l2 = lim2;
  l3 = lim3;
  l4 = lim4;
}

//--------------------------------------------------------------------
void
PlotBase::AddLegendEntry(TString LegendEntry, Color_t ColorEntry )
{
  // Uses default line width and style.
  fLegendEntries.push_back(LegendEntry);
  fLineColors.push_back(ColorEntry);
  fLineWidths.push_back(fDefaultLineWidth);
  fLineStyles.push_back(fDefaultLineStyle);
}

//--------------------------------------------------------------------
void
PlotBase::AddLegendEntry(TString LegendEntry, Color_t ColorEntry, Int_t LineWidth, Int_t LineStyle)
{
  fLegendEntries.push_back(LegendEntry);
  fLineColors.push_back(ColorEntry);
  fLineWidths.push_back(LineWidth);
  fLineStyles.push_back(LineStyle);
}
