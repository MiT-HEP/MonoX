#include <iostream>
#include "TF1.h"
#include "TH2D.h"
#include "TProfile.h"
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
void
PlotResolution::MakeFitGraphs(Int_t NumXBins, Double_t *XBins,
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
  TProfile *tempProfile;

  TGraphErrors *tempGraph[6];
  for (Int_t init = 0; init < 6; init++)
    fFits[init].resize(0);

  TF1 *fitLoose = new TF1("loose","[0]*TMath::Gaus(x,[1],[2])",MinY,MaxY);
  TF1 *fitFunc  = new TF1("func","[3]*TMath::Gaus(x,[0],[1]) + [4]*TMath::Gaus(x,[0],[2])",MinY,MaxY);
  TF1 *subFit1  = new TF1("fit1","[0]*TMath::Gaus(x,[1],[2])",MinY,MaxY);
  TF1 *subFit2  = new TF1("fit2","[0]*TMath::Gaus(x,[1],[2])",MinY,MaxY);

  fitLoose->SetLineColor(kGreen);
  fitFunc->SetLineColor(kBlue);

  fitLoose->SetParLimits(0,0,1e8);
  fitLoose->SetParLimits(1,MinY,MaxY);
  fitLoose->SetParLimits(2,0,MaxY-MinY);

  fitFunc->SetParLimits(0,MinY,MaxY);
  fitFunc->SetParLimits(1,0,MaxY-MinY);
  fitFunc->SetParLimits(2,0,MaxY-MinY);
  fitFunc->SetParLimits(3,0,1e8);
  fitFunc->SetParLimits(4,0,1e8);

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
    tempHist    = new TH2D(tempName,tempName,NumXBins,XBins,NumYBins,MinY,MaxY);
    tempProfile = new TProfile(tempName+"prof",tempName+"prof",NumXBins,XBins);
    inTree->Draw(inExpr+":"+fInExprX+">>"+tempName,inCut);
    inTree->Draw(fInExprX+":"+fInExprX+">>"+tempName+"prof",inCut);
    for (Int_t init = 0; init < 6; init++)
      tempGraph[init] = new TGraphErrors(NumXBins);

    for (Int_t i1 = 0; i1 < NumXBins; i1++) {
      TCanvas *tempCanvas = new TCanvas();
      fitLoose->SetParameter(0,10);
      fitLoose->SetParameter(1,0);
      fitLoose->SetParameter(2,30);
      tempHist->ProjectionY(tempName+"_py_loose",i1+1,i1+1)->Fit(fitLoose,"","",MinY,MaxY);
      fitFunc->SetParameter(0,fitLoose->GetParameter(1));
      fitFunc->SetParameter(1,fitLoose->GetParameter(2));
      fitFunc->SetParameter(2,fitLoose->GetParameter(2) * 0.4);
      fitFunc->SetParameter(3,fitLoose->GetParameter(0) * 0.9);
      fitFunc->SetParameter(4,fitLoose->GetParameter(0) * 0.2);
      tempHist->ProjectionY(tempName+"_py",i1+1,i1+1)->Fit(fitFunc,"","",MinY,MaxY);
      if (fDumpingFits) {
        TString dumpName;
        Int_t lower = XBins[i1];
        Int_t upper = XBins[i1 + 1];
        dumpName.Form("DumpFit_%04d_%dTo%d",fNumFitDumps,lower,upper);
        fitLoose->Draw("SAME");
	subFit1->SetParameter(0,fitFunc->GetParameter(3));
	subFit1->SetParameter(1,fitFunc->GetParameter(0));
	subFit1->SetParameter(2,fitFunc->GetParameter(1));
	subFit1->Draw("SAME");
	subFit2->SetParameter(0,fitFunc->GetParameter(4));
	subFit2->SetParameter(1,fitFunc->GetParameter(0));
	subFit2->SetParameter(2,fitFunc->GetParameter(2));
	subFit2->Draw("SAME");
        tempCanvas->SaveAs(dumpName+".png");
        tempCanvas->SaveAs(dumpName+".pdf");
        tempCanvas->SaveAs(dumpName+".C");
        fNumFitDumps++;
      }

      Double_t xValue = tempProfile->GetBinContent(i1+1);
      Double_t xError = tempProfile->GetBinError(i1+1);

      tempGraph[0]->SetPoint(i1,xValue,fitFunc->GetParameter(0));
      if (fIncludeErrorBars)
	tempGraph[0]->SetPointError(i1,xError,fitFunc->GetParError(0));

      Int_t sigWanted = 0;
      if (fitFunc->GetParameter(1) < fitFunc->GetParameter(2))
	sigWanted = 1;
      else
	sigWanted = 2;
      tempGraph[1]->SetPoint(i1,xValue,fitFunc->GetParameter(sigWanted));
      if (fIncludeErrorBars)
	tempGraph[1]->SetPointError(i1,xError,fitFunc->GetParError(sigWanted));

      if (fitFunc->GetParameter(1) > fitFunc->GetParameter(2))
	sigWanted = 1;
      else
	sigWanted = 2;
      tempGraph[2]->SetPoint(i1,xValue,fitFunc->GetParameter(sigWanted));
      if (fIncludeErrorBars)
	tempGraph[2]->SetPointError(i1,xError,fitFunc->GetParError(sigWanted));

      Float_t weight1 = 0.;
      Float_t weight2 = 0.;
      
      weight1 = fitFunc->GetParameter(3)/sqrt(fitFunc->GetParameter(1));
      weight2 = fitFunc->GetParameter(4)/sqrt(fitFunc->GetParameter(2));
      
      tempGraph[3]->SetPoint(i1,xValue,(weight1 * fitFunc->GetParameter(1) + weight2 * fitFunc->GetParameter(2))/(weight1 + weight2));
      if (fIncludeErrorBars)
	tempGraph[3]->SetPointError(i1,xError,sqrt(pow(weight1 * fitFunc->GetParError(1),2) + pow(weight2 * fitFunc->GetParError(2),2))/(weight1 + weight2));
      
      tempGraph[4]->SetPoint(i1,xValue,fitLoose->GetParameter(1));
      if (fIncludeErrorBars)
	tempGraph[4]->SetPointError(i1,xError,fitLoose->GetParError(1));
      
      tempGraph[5]->SetPoint(i1,xValue,fitLoose->GetParameter(2));
      if (fIncludeErrorBars)
	tempGraph[5]->SetPointError(i1,xError,fitLoose->GetParError(2));
      
      delete tempCanvas;
    }
    for (Int_t iPlot = 0; iPlot < 6; iPlot++)
      fFits[iPlot].push_back(tempGraph[iPlot]);
    delete tempHist;
  }
}

//--------------------------------------------------------------------
void
PlotResolution::MakeFitGraphs(Int_t NumXBins, Double_t MinX, Double_t MaxX,
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
PlotResolution::MakeCanvas(std::vector<TGraphErrors*> theGraphs,
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
