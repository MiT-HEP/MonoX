#include <iostream>
#include "TStyle.h"
#include "TLegend.h"

#include "PlotHists.h"

ClassImp(PlotHists)

//--------------------------------------------------------------------
PlotHists::PlotHists() :
  fNormalizedHists(kFALSE)
{}

//--------------------------------------------------------------------
PlotHists::~PlotHists()
{}

//--------------------------------------------------------------------
std::vector<TH1D*>
PlotHists::MakeHists(Int_t NumXBins, Double_t *XBins)
{
  UInt_t NumPlots = 0;

  if (fInTrees.size() > 0)
    NumPlots = fInTrees.size();
  else if (fInCuts.size() > 0)
    NumPlots = fInCuts.size();
  else
    NumPlots = fInExpr.size();

  if(NumPlots == 0){
    std::cout << "Nothing has been initialized in hists plot." << std::endl;
    exit(1);
  }

  TTree *inTree = fDefaultTree;
  TString inCut = fDefaultCut;
  TString inExpr = fDefaultExpr;

  TH1D *tempHist;
  std::vector<TH1D*> theHists;

  for (UInt_t i0 = 0; i0 < NumPlots; i0++) {

    if (fInTrees.size() != 0)
      inTree = fInTrees[i0];
    if (fInCuts.size()  != 0)
      inCut  = fInCuts[i0];
    if (fInExpr.size() != 0)
      inExpr = fInExpr[i0];

    TString tempName;
    tempName.Form("Hist_%d",fPlotCounter);
    fPlotCounter++;
    tempHist = new TH1D(tempName,tempName,NumXBins,XBins);
    inTree->Draw(inExpr+">>"+tempName,inCut);

    theHists.push_back(tempHist);
  }
  return theHists;
}

//--------------------------------------------------------------------
std::vector<TH1D*>
PlotHists::MakeHists(Int_t NumXBins, Double_t MinX, Double_t MaxX)
{
  Double_t binWidth = (MaxX - MinX)/NumXBins;
  Double_t XBins[NumXBins+1];
  for (Int_t i0 = 0; i0 < NumXBins + 1; i0++)
    XBins[i0] = MinX + i0 * binWidth;

  return MakeHists(NumXBins,XBins);
}

//--------------------------------------------------------------------
TCanvas*
PlotHists::MakeCanvas(std::vector<TH1D*> theHists,
                      TString CanvasTitle, TString XLabel, TString YLabel,
                      Bool_t logY)
{
  gStyle->SetOptStat(0);
  UInt_t NumPlots = theHists.size();
  TCanvas *theCanvas = new TCanvas(fCanvasName,fCanvasName);
  theCanvas->SetTitle(CanvasTitle+";"+XLabel+";"+YLabel);
  TLegend *theLegend = new TLegend(l1,l2,l3,l4);
  theLegend->SetBorderSize(fLegendBorderSize);
  float maxValue = 0.;
  UInt_t plotFirst = 0;
  for (UInt_t i0 = 0; i0 < NumPlots; i0++) {
    theHists[i0]->SetTitle(CanvasTitle+";"+XLabel+";"+YLabel);
    theHists[i0]->SetLineWidth(fLineWidths[i0]);
    theHists[i0]->SetLineStyle(fLineStyles[i0]);
    theHists[i0]->SetLineColor(fLineColors[i0]);
    theLegend->AddEntry(theHists[i0],fLegendEntries[i0],"l");

    Double_t checkMax = 0;
    if (fNormalizedHists)
      checkMax = theHists[i0]->GetMaximum()/theHists[i0]->Integral("width");
    else
      checkMax = theHists[i0]->GetMaximum();
      
    if (checkMax > maxValue) {
      maxValue = checkMax;
      plotFirst = i0;
    }
  }
  
  if (fNormalizedHists) {
    theHists[plotFirst]->DrawNormalized();
    for (UInt_t i0 = 0; i0 < NumPlots; i0++)
      theHists[i0]->DrawNormalized("same");
  }
  else {
    theHists[plotFirst]->Draw();
    for (UInt_t i0 = 0; i0 < NumPlots; i0++)
      theHists[i0]->Draw("same");
  }

  theLegend->Draw();
  if (logY)
    theCanvas->SetLogy();

  return theCanvas;
}

//--------------------------------------------------------------------
void
PlotHists::MakeCanvas(Int_t NumXBins, Double_t *XBins, TString FileBase,
                      TString CanvasTitle, TString XLabel, TString YLabel,
                      Bool_t logY)
{
  std::vector<TH1D*> hists = MakeHists(NumXBins,XBins);
  TCanvas *theCanvas = MakeCanvas(hists,CanvasTitle,
                                  XLabel,YLabel,logY);

  theCanvas->SaveAs(FileBase+".C");
  theCanvas->SaveAs(FileBase+".png");
  theCanvas->SaveAs(FileBase+".pdf");

  delete theCanvas;
  for (UInt_t i0 = 0; i0 < hists.size(); i0++)
    delete hists[i0];

}

//--------------------------------------------------------------------
void
PlotHists::MakeCanvas(Int_t NumXBins, Double_t MinX, Double_t MaxX, TString FileBase,
                      TString CanvasTitle, TString XLabel, TString YLabel,
                      Bool_t logY)
{
  Double_t binWidth = (MaxX - MinX)/NumXBins;
  Double_t XBins[NumXBins+1];
  for (Int_t i0 = 0; i0 < NumXBins + 1; i0++)
    XBins[i0] = MinX + i0 * binWidth;

  MakeCanvas(NumXBins,XBins,FileBase,CanvasTitle,XLabel,YLabel,logY);
}
