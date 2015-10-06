#include <iostream>
#include "TF1.h"
#include "TH2D.h"
#include "TLegend.h"

#include "PlotResolution.h"

ClassImp(PlotResolution)

//--------------------------------------------------------------------
PlotResolution::PlotResolution() :
  fInExprX(""),
  fDumpingFits(false),
  fNumFitDumps(0)
{
  fParams.resize(0);
  fParamLows.resize(0);
  fParamHighs.resize(0);
  fInExprXs.resize(0);
}

//--------------------------------------------------------------------
PlotResolution::~PlotResolution()
{}

//--------------------------------------------------------------------
void
PlotResolution::SetParameterLimits(Int_t param, Double_t low, Double_t high)
{
  fParams.push_back(param);
  fParamLows.push_back(low);
  fParamHighs.push_back(high);
}


//--------------------------------------------------------------------
std::vector<TGraphErrors*>
PlotResolution::GetRatioToLines(std::vector<TGraphErrors*> InGraphs, std::vector<TGraphErrors*> RatioGraphs)
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
PlotResolution::GetRatioToLine(std::vector<TGraphErrors*> InGraphs, TGraphErrors *RatioGraph)
{
  std::vector<TGraphErrors*> tempRatioGraphs;
  for (UInt_t i0 = 0; i0 < InGraphs.size(); i0++)
    tempRatioGraphs.push_back(RatioGraph);
  return GetRatioToLines(InGraphs,tempRatioGraphs);
}

//--------------------------------------------------------------------
std::vector<TGraphErrors*>
PlotResolution::GetRatioToPoint(std::vector<TGraphErrors*> InGraphs, Double_t RatioPoint, Double_t PointError)
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
std::vector<TGraphErrors*>
PlotResolution::MakeFitGraphs(Int_t NumXBins, Double_t MinX, Double_t MaxX,
                              Int_t NumYBins, Double_t MinY, Double_t MaxY,
                              Int_t ParamNumber)
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

  TGraphErrors *tempGraph;
  std::vector<TGraphErrors*> theGraphs;

  TF1 *fitFunc = new TF1("func","[0]*TMath::Gaus(x,[1],[2])",MinY,MaxY);

  fitFunc->SetParLimits(0,0,1e8);
  fitFunc->SetParLimits(1,MinY,MaxY);
  fitFunc->SetParLimits(2,0,MaxY-MinY);

  for (UInt_t i0 = 0; i0 < fParams.size(); i0++)
    fitFunc->SetParLimits(fParams[i0],fParamLows[i0],fParamHighs[i0]);

  std::cout <<  NumPlots << " lines will be made." << std::endl;

  for (UInt_t i0 = 0; i0 < NumPlots; i0++) {
    std::cout << NumPlots - i0 << " more to go." << std::endl;

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
    tempHist = new TH2D(tempName,tempName,NumXBins,MinX,MaxX,NumYBins,MinY,MaxY);
    inTree->Draw(inExpr+":"+fInExprX+">>"+tempName,inCut);
    tempGraph = new TGraphErrors(NumXBins);

    for (Int_t i1 = 0; i1 < NumXBins; i1++) {
      TCanvas *tempCanvas = new TCanvas();
      fitFunc->SetParameters(1.,(MaxY + MinY)/2,(MaxY - MinY)/4);
      tempHist->ProjectionY(tempName+"_py",i1+1,i1+1)->Fit(fitFunc,"","",MinY,MaxY);
      if (fDumpingFits) {
        TString dumpName;
        dumpName.Form("DumpFit_%d",fNumFitDumps);
        tempCanvas->SaveAs(dumpName+".png");
        fNumFitDumps++;
      }
      tempGraph->SetPoint(i1,tempHist->GetXaxis()->GetBinCenter(i1+1),fitFunc->GetParameter(ParamNumber));
      if (fIncludeErrorBars)
        tempGraph->SetPointError(i1,0,fitFunc->GetParError(ParamNumber));
    }
    theGraphs.push_back(tempGraph);
    delete tempHist;
  }
  return theGraphs;
}

//--------------------------------------------------------------------
TCanvas*
PlotResolution::MakeCanvas(std::vector<TGraphErrors*> theGraphs,
                           TString CanvasTitle, TString XLabel, TString YLabel,
                           Double_t YMin, Double_t YMax, Bool_t logY)
{
  UInt_t NumPlots = theGraphs.size();
  TCanvas *theCanvas = new TCanvas(fCanvasName,fCanvasName);
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
PlotResolution::MakeCanvas(TString FileBase, std::vector<TGraphErrors*> theGraphs,
                           TString CanvasTitle, TString XLabel, TString YLabel,
                           Double_t YMin, Double_t YMax, Bool_t logY)
{
  TCanvas *theCanvas = MakeCanvas(theGraphs, CanvasTitle, XLabel, YLabel, YMin, YMax, logY);

  theCanvas->SaveAs(FileBase+".C");
  theCanvas->SaveAs(FileBase+".png");
  theCanvas->SaveAs(FileBase+".pdf");

  delete theCanvas;
}
