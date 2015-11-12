#ifndef MITPLOTS_PLOT_PLOT2D_H
#define MITPLOTS_PLOT_PLOT2D_H

#include "TGraphErrors.h"
#include "TCanvas.h"

#include "PlotBase.h"

class Plot2D : public PlotBase
{
 public:
  Plot2D();
  virtual ~Plot2D();
  
  void                         SetExprX                ( TString expr )                                 { fInExprX = expr;             }
  void                         AddExprX                ( TString expr )                                 { fInExprXs.push_back(expr);   }
  void                         SetParameterLimits      ( Int_t param, Double_t low, Double_t high );

  void                         AddName                 ( TString name )                                 { fNames.push_back(name);      }

  // These were used to get response corrected plots
  // Can probably use them for ratio plots in the future
  // These tools should also be moved to a utils or something. They don't require an object.
  std::vector<TGraphErrors*>   GetRatioToPoint         ( std::vector<TGraphErrors*> InGraphs, Double_t RatioPoint, Double_t PointError = 0 );
  std::vector<TGraphErrors*>   GetRatioToLine          ( std::vector<TGraphErrors*> InGraphs, TGraphErrors *RatioGraph );
  std::vector<TGraphErrors*>   GetRatioToLines         ( std::vector<TGraphErrors*> InGraphs, std::vector<TGraphErrors*> RatioGraphs );

  void                         MakeFitGraphs           ( Int_t NumXBins, Double_t *XBins,               // This does the fitting
                                                         Int_t NumYBins, Double_t MinY, Double_t MaxY);

  void                         MakeFitGraphs           ( Int_t NumXBins, Double_t MinX, Double_t MaxX,
                                                         Int_t NumYBins, Double_t MinY, Double_t MaxY);
  
  // The defaults are set up for resolution, but response can be gotten too
  TCanvas*                     MakeCanvas              ( std::vector<TGraphErrors*> theGraphs,
                                                         TString CanvasTitle, TString XLabel, TString YLabel,
                                                         Double_t YMin, Double_t YMax, Bool_t logY = false);
  
  void                         MakeCanvas              ( TString FileBase, std::vector<TGraphErrors*> theGraphs,
                                                         TString CanvasTitle, TString XLabel, TString YLabel,
                                                         Double_t YMin, Double_t YMax, Bool_t logY = false);
  
 private:

  std::vector<TString>       fNames;

  std::vector<Int_t>         fParams;             // This is vector used for setting parameter limits for fits
  std::vector<Double_t>      fParamLows;          // Low values of these parameters
  std::vector<Double_t>      fParamHighs;         // High values of these parameters
  
  TString                    fInExprX;
  std::vector<TString>       fInExprXs;

  Int_t                      fResult;
  
  ClassDef(Plot2D,1)
};

#endif
