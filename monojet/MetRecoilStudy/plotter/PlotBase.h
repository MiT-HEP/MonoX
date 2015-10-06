#ifndef MITPLOTS_PLOT_PLOTBASE_H
#define MITPLOTS_PLOT_PLOTBASE_H

#include <vector>

#include "TTree.h"
#include "TString.h"

class PlotBase
{
 public:
  PlotBase();
  virtual ~PlotBase();
  
  void                   SetCanvasName            ( TString name )                                { fCanvasName = name;          }
  
  void                   AddLine                  ( TTree *tree, TString cut, TString expr );  // Each line has a potentially different
  //   tree, weight, and expression.
  void                   SetDefaultTree           ( TTree *tree )                                 { fDefaultTree = tree;         }
  void                   SetDefaultWeight         ( TString cut )                                 { fDefaultCut = cut;           }
  void                   SetDefaultExpr           ( TString expr )                                { fDefaultExpr = expr;         }
  
  void                   SetTreeList              ( std::vector<TTree*> treelist )                { fInTrees = treelist;         }
  void                   AddTree                  ( TTree *tree )                                 { fInTrees.push_back(tree);    }
  void                   AddWeight                ( TString cut )                                 { fInCuts.push_back(cut);      }
  void                   AddExpr                  ( TString expr )                                { fInExpr.push_back(expr);     }
  void                   ResetExpr                ()                                              { fInExpr.resize(0);           }
  void                   AddTreeWeight            ( TTree *tree, TString cut );           // These are used to set multiple values at
  void                   AddTreeExpr              ( TTree *tree, TString expr );          //  the same time. It may be simpler to
  void                   AddWeightExpr            ( TString cut, TString expr );          //  just set single variables for most users.
  
  void                   SetDefaultLineWidth      ( Int_t width )                                 { fDefaultLineWidth = width;   }
  void                   SetDefaultLineStyle      ( Int_t style )                                 { fDefaultLineStyle = style;   }
  void                   SetIncludeErrorBars      ( Bool_t include )                              { fIncludeErrorBars = include; }
  void                   SetLegendLimits          ( Double_t lim1, Double_t lim2, Double_t lim3, Double_t lim4 );
  void                   AddLegendEntry           ( TString LegendEntry, Color_t ColorEntry );    // Uses default line width and style
  void                   AddLegendEntry           ( TString LegendEntry, Color_t ColorEntry, Int_t LineWidth, Int_t LineStyle );
  void                   SetLegendBorderSize      ( Int_t size )                                  { fLegendBorderSize = size;    }
  
 protected:
  
  UInt_t                     fPlotCounter;        // This is used so that making scratch plots does not overlap
  
  TString                    fCanvasName;         // The name of the output canvas
  Int_t                      fDefaultLineWidth;   // Line width to make all plots
  Int_t                      fDefaultLineStyle;   // Line style to use on all plots
  Bool_t                     fIncludeErrorBars;   // Option to include error bars
  
  TTree*                     fDefaultTree;        // Default Tree if needed
  TString                    fDefaultCut;         // Default cut if needed
  TString                    fDefaultExpr;        // Default resolution expression if needed
  
  Double_t                   l1;                  // First X value of legend location
  Double_t                   l2;                  // First Y value of legend location
  Double_t                   l3;                  // Second X value of legend location
  Double_t                   l4;                  // Second Y value of legend location
  Int_t                      fLegendBorderSize;   // Border size of legend
  
  std::vector<TTree*>        fInTrees;            // Holds all the trees for each line if needed
  std::vector<TString>       fInCuts;             // Holds the cuts for the trees if needed
  std::vector<TString>       fInExpr;             // Holds multiple resolution expressions if needed
  
  std::vector<TString>       fLegendEntries;      // Number of legend entries should match number of lines
  std::vector<Color_t>       fLineColors;         // Number of colors should match number of lines
  std::vector<Int_t>         fLineWidths;         // Will be filled with defaults unless
  std::vector<Int_t>         fLineStyles;         //   set explicitly with overloaded function
  
  ClassDef(PlotBase,1)
};

#endif
