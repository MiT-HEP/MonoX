#include <iostream>
#include "fitFunctions.h"
#include "TFile.h"
#include "TF2.h"
#include "TF1.h"
#include "TH2D.h"
#include "TH1D.h"
#include "TProfile.h"
#include "TLegend.h"
#include "TFitResultPtr.h"
#include "TFitResult.h"
#include "TMatrixDSym.h"

#include "Plot2D.h"

ClassImp(Plot2D)

//--------------------------------------------------------------------
Plot2D::Plot2D() :
  fInExprX(""),
  fResult(0)
{
  fNames.resize(0);
  fParams.resize(0);
  fParamLows.resize(0);
  fParamHighs.resize(0);
  fInExprXs.resize(0);
}

//--------------------------------------------------------------------
Plot2D::~Plot2D()
{}

//--------------------------------------------------------------------
void
Plot2D::SetParameterLimits(Int_t param, Double_t low, Double_t high)
{
  fParams.push_back(param);
  fParamLows.push_back(low);
  fParamHighs.push_back(high);
}

//--------------------------------------------------------------------
std::vector<TGraphErrors*>
Plot2D::GetRatioToLines(std::vector<TGraphErrors*> InGraphs, std::vector<TGraphErrors*> RatioGraphs)
{
  TGraphErrors *tempGraph;
  std::vector<TGraphErrors*> outGraphs;
  for (UInt_t i0 = 0; i0 < InGraphs.size(); i0++) {
    Double_t *GraphX = InGraphs[i0]->GetX();
    Double_t *GraphY = InGraphs[i0]->GetY();
    Double_t *GraphYErrors = InGraphs[i0]->GetEY();
    Int_t NumPoints = RatioGraphs[i0]->GetN();
    Double_t *RatioY = RatioGraphs[i0]->GetY();
    Double_t *RatioYErrors = RatioGraphs[i0]->GetEY();
    tempGraph = new TGraphErrors(NumPoints);
    for (Int_t i1 = 0; i1 < NumPoints; i1++) {
      if (InGraphs[i0]->GetN() != NumPoints) {
        std::cout << "Messed up graph size... Check that out" << std::endl;
        exit(1);
      }

      tempGraph->SetPoint(i1,GraphX[i1],GraphY[i1]/RatioY[i1]);
      if (fIncludeErrorBars)
        tempGraph->SetPointError(i1,0,sqrt(pow(GraphYErrors[i1]/RatioY[i1],2) + pow((GraphY[i1])*(RatioYErrors[i1])/pow(RatioY[i1],2),2)));
    }
    outGraphs.push_back(tempGraph);
  }
  return outGraphs;
}

//--------------------------------------------------------------------
std::vector<TGraphErrors*>
Plot2D::GetRatioToLine(std::vector<TGraphErrors*> InGraphs, TGraphErrors *RatioGraph)
{
  std::vector<TGraphErrors*> tempRatioGraphs;
  for (UInt_t i0 = 0; i0 < InGraphs.size(); i0++)
    tempRatioGraphs.push_back(RatioGraph);
  return GetRatioToLines(InGraphs,tempRatioGraphs);
}

//--------------------------------------------------------------------
std::vector<TGraphErrors*>
Plot2D::GetRatioToPoint(std::vector<TGraphErrors*> InGraphs, Double_t RatioPoint, Double_t PointError)
{
  Int_t NumPoints = InGraphs[0]->GetN();
  Double_t *GraphX = InGraphs[0]->GetX();
  TGraphErrors *tempRatioGraph = new TGraphErrors(NumPoints);
  for (Int_t i0 = 0; i0 < NumPoints; i0++) {
    tempRatioGraph->SetPoint(i0,GraphX[i0],RatioPoint);
    if (fIncludeErrorBars)
      tempRatioGraph->SetPointError(i0,0,PointError);
  }
  return GetRatioToLine(InGraphs,tempRatioGraph);
}

//--------------------------------------------------------------------
void
Plot2D::MakeFitGraphs(Int_t NumXBins, Double_t *XBins,
		      Int_t NumYBins, Double_t MinY, Double_t MaxY)
{
  UInt_t NumPlots = 0;

  if (fInExprX == "" && fInExprXs.size() == 0) {
    std::cout << "You haven't initialized an x expression yet!" << std::endl;
    exit(1);
  }

  if (fInTrees.size() > 0)
    NumPlots = fInTrees.size();
  else if (fInCuts.size() > 0)
    NumPlots = fInCuts.size();
  else
    NumPlots = fInExpr.size();

  if(NumPlots == 0){
    std::cout << "Nothing has been initialized in resolution plot." << std::endl;
    exit(1);
  }

  TTree *inTree = fDefaultTree;
  TString inCut = fDefaultCut;
  TString inExpr = fDefaultExpr;

  TH2D *tempHist;
  // TH2D *shitHist;
  // TH1D *ptHist;

  Double_t params[5] = {0,0,30,0,0};

  // TF2 *fitFunc = new TF2("fit",singleFunc,XBins[0],XBins[NumXBins],MinY,MaxY,4);
  TF1 *fitFunc = new TF1("fit","[0] + [1] * x",XBins[0],XBins[NumXBins]);

  for (UInt_t i0 = 0; i0 < fParams.size(); i0++)
    fitFunc->SetParLimits(fParams[i0],fParamLows[i0],fParamHighs[i0]);

  TF1 *aFunc = new TF1("muFits",quad,XBins[0],XBins[NumXBins],3);
  // TF1 *bFunc = new TF1("sigFits",quad,XBins[0],XBins[NumXBins],3);

  TString fileName;
  fileName.Form("fitTest_%d.root",fResult);
  TFile *results = new TFile(fileName,"RECREATE");
  fResult++;

  std::cout << "File: " << results << std::endl;

  for (UInt_t i0 = 0; i0 < NumPlots; i0++) {

    if (fInTrees.size() != 0)
      inTree = fInTrees[i0];
    if (fInCuts.size()  != 0)
      inCut  = fInCuts[i0];
    if (fInExpr.size() != 0)
      inExpr = fInExpr[i0];
    if (fInExprXs.size() != 0)
      fInExprX = fInExprXs[i0];

    TString tempName;
    tempName.Form("Hist_%d",fPlotCounter);
    fPlotCounter++;
    tempHist = new TH2D(tempName,tempName,NumXBins,XBins,NumYBins,MinY,MaxY);
    tempHist->Sumw2();
    TCanvas *tempCanvas = new TCanvas();
    inTree->Draw(inExpr+":"+fInExprX+">>"+tempName,inCut,"COLZ");
    // ptHist = tempHist->ProjectionX(tempName+"_fuck");
    // shitHist = new TH2D(tempName+"_shit",tempName+"_shit",NumXBins,XBins,NumYBins,MinY,MaxY);
    // for (Int_t iXBin = 0; iXBin < NumXBins; iXBin++){
    //   for (Int_t iYBin = 0; iYBin < NumYBins; iYBin++){
    //     shitHist->SetBinContent(iXBin+1,iYBin+1,ptHist->GetBinContent(iXBin+1));
    //   }      
    // }

    // tempHist->Divide(shitHist);

    fitFunc->SetParameters(params);
    TFitResultPtr fitResult = tempHist->Fit(fitFunc,"MLES");

    TMatrixDSym cov = fitResult->GetCovarianceMatrix();

    std::cout << "Finished fit!" << std::endl;

    results->WriteTObject(tempCanvas->Clone(TString("canv_") + fNames[i0]),TString("canv_") + fNames[i0]);
    results->WriteTObject(tempHist->Clone(TString("hist_") + fNames[i0]),TString("hist_") + fNames[i0]);
    results->WriteTObject(fitFunc->Clone(TString("func_") + fNames[i0]),TString("func_") + fNames[i0]);

    std::cout << "Wrote raw stuff." << std::endl;

    aFunc->SetParameter(0,fitFunc->GetParameter(0));
    aFunc->SetParameter(1,fitFunc->GetParameter(1));
    aFunc->SetParameter(2,0);
    results->WriteTObject(aFunc->Clone(TString("mu_") + fNames[i0]),TString("mu_") + fNames[i0]);

    std::cout << "Wrote mu." << std::endl;

    // bFunc->SetParameter(0,fitFunc->GetParameter(2));
    // bFunc->SetParameter(1,fitFunc->GetParameter(3));
    // // bFunc->SetParameter(2,fitFunc->GetParameter(4));
    // results->WriteTObject(bFunc->Clone(TString("sig_") + fNames[i0]),TString("sig_") + fNames[i0]);

    // std::cout << "Wrote sig." << std::endl;

    aFunc->SetParameter(0,fitFunc->GetParameter(0) + cov(0,0)); // fitFunc->GetParError(0));
    aFunc->SetParameter(1,fitFunc->GetParameter(1) + abs(cov(0,1))); // fitFunc->GetParError(1));
    aFunc->SetParameter(2,cov(1,1));
    results->WriteTObject(aFunc->Clone(TString("mu_up_") + fNames[i0]),TString("mu_up_") + fNames[i0]);

    std::cout << "Wrote mu_up." << std::endl;

    // bFunc->SetParameter(0,fitFunc->GetParameter(2) + cov(2,2)); // fitFunc->GetParError(2));
    // bFunc->SetParameter(1,fitFunc->GetParameter(3) + cov(3,3)); // fitFunc->GetParError(3));
    // // bFunc->SetParameter(2,fitFunc->GetParameter(4) + cov(4,4)); // fitFunc->GetParError(4));
    // results->WriteTObject(bFunc->Clone(TString("sig_up_") + fNames[i0]),TString("sig_up_") + fNames[i0]);

    // std::cout << "Wrote sig_up." << std::endl;

    aFunc->SetParameter(0,fitFunc->GetParameter(0) - cov(0,0)); // fitFunc->GetParError(0));
    aFunc->SetParameter(1,fitFunc->GetParameter(1) - abs(cov(0,1))); // fitFunc->GetParError(1));
    aFunc->SetParameter(2,-1 * cov(1,1));
    results->WriteTObject(aFunc->Clone(TString("mu_down_") + fNames[i0]),TString("mu_down_") + fNames[i0]);

    std::cout << "Wrote mu_down." << std::endl;

    // bFunc->SetParameter(0,fitFunc->GetParameter(2) - cov(2,2)); // fitFunc->GetParError(2));
    // bFunc->SetParameter(1,fitFunc->GetParameter(3) - cov(3,3)); // fitFunc->GetParError(3));
    // // bFunc->SetParameter(2,fitFunc->GetParameter(4) - cov(4,4)); // fitFunc->GetParError(4));
    // results->WriteTObject(bFunc->Clone(TString("sig_down_") + fNames[i0]),TString("sig_down_") + fNames[i0]);

    // std::cout << "Wrote sig_down." << std::endl;
  }

  results->Close();
}

//--------------------------------------------------------------------
void
Plot2D::MakeFitGraphs(Int_t NumXBins, Double_t MinX, Double_t MaxX,
                              Int_t NumYBins, Double_t MinY, Double_t MaxY)
{
  Double_t binWidth = (MaxX - MinX)/NumXBins;
  Double_t XBins[NumXBins+1];
  for (Int_t i0 = 0; i0 < NumXBins + 1; i0++)
    XBins[i0] = MinX + i0 * binWidth;

  MakeFitGraphs(NumXBins,XBins,NumYBins,MinY,MaxY);
}

//--------------------------------------------------------------------
TCanvas*
Plot2D::MakeCanvas(std::vector<TGraphErrors*> theGraphs,
                           TString CanvasTitle, TString XLabel, TString YLabel,
                           Double_t YMin, Double_t YMax, Bool_t logY)
{
  UInt_t NumPlots = theGraphs.size();
  TCanvas *theCanvas = new TCanvas("temp","temp");
  theCanvas->SetTitle(CanvasTitle+";"+XLabel+";"+YLabel);
  TLegend *theLegend = new TLegend(l1,l2,l3,l4);
  theLegend->SetBorderSize(fLegendBorderSize);
  for (UInt_t i0 = 0; i0 < NumPlots; i0++) {
    theGraphs[i0]->SetTitle(CanvasTitle+";"+XLabel+";"+YLabel);
    theGraphs[i0]->SetLineWidth(fLineWidths[i0]);
    theGraphs[i0]->SetLineStyle(fLineStyles[i0]);
    theGraphs[i0]->SetLineColor(fLineColors[i0]);
    theLegend->AddEntry(theGraphs[i0],fLegendEntries[i0],"l");
  }
  theGraphs[0]->GetYaxis()->SetRangeUser(YMin,YMax);
  theGraphs[0]->Draw();
  for (UInt_t i0 = 1; i0 < NumPlots; i0++)
    theGraphs[i0]->Draw("same");

  theLegend->Draw();
  if (logY)
    theCanvas->SetLogy();

  return theCanvas;
}

//--------------------------------------------------------------------
void
Plot2D::MakeCanvas(TString FileBase, std::vector<TGraphErrors*> theGraphs,
                           TString CanvasTitle, TString XLabel, TString YLabel,
                           Double_t YMin, Double_t YMax, Bool_t logY)
{
  TCanvas *theCanvas = MakeCanvas(theGraphs, CanvasTitle, XLabel, YLabel, YMin, YMax, logY);

  theCanvas->SaveAs(FileBase+".C");
  theCanvas->SaveAs(FileBase+".png");
  theCanvas->SaveAs(FileBase+".pdf");

  delete theCanvas;
}
