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
    if (fIncludeErrorBars)
      tempHist->Sumw2();
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
std::vector<TH1D*>
PlotHists::MakeHists(Int_t NumXBins, Double_t MinX, Double_t MaxX, Int_t DataNum)
{
  std::vector<TH1D*> theHists = MakeHists(NumXBins,MinX,MaxX);
  Float_t DataInt = theHists[DataNum]->Integral();
  for (UInt_t iHist = 0; iHist < theHists.size(); iHist++) {
    theHists[iHist]->Scale(DataInt/theHists[iHist]->Integral());
    std::cout << "chi2 test: " << fLegendEntries[iHist] << " " << theHists[DataNum]->Chi2Test(theHists[iHist],"UW") << std::endl;
  }

  theHists[DataNum]->SetMarkerStyle(8);
  theHists[DataNum]->Sumw2();
  return theHists;
}

//--------------------------------------------------------------------
TCanvas*
PlotHists::MakeCanvas(std::vector<TH1D*> theHists,
                      TString CanvasTitle, TString XLabel, TString YLabel,
                      Bool_t logY, Int_t ratPlot)
{
  gStyle->SetOptStat(0);

  Float_t fontSize  = 0.04;
  Float_t ratioFrac = 0.7;

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
    theLegend->AddEntry(theHists[i0],fLegendEntries[i0],"lp");

    std::cout << fLegendEntries[i0] << " -> Mean: " << theHists[i0]->GetMean() << "+-" << theHists[i0]->GetMeanError();
    std::cout                           << " RMS: " << theHists[i0]->GetRMS() << "+-" << theHists[i0]->GetRMSError() << std::endl;

    for (UInt_t i1 = 0; i1 < NumPlots; i1++) {
      if (i1 == i0)
        continue;
      std::cout << "Test with " << fLegendEntries[i1] << " KS: " << theHists[i0]->KolmogorovTest(theHists[i1]);
      std::cout << " AD: " << theHists[i0]->AndersonDarlingTest(theHists[i1]) << std::endl;
    }

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

  if (ratPlot != -1) {
    TPad *pad1 = new TPad("pad1", "pad1", 0, 1.0 - ratioFrac, 1, 1.0);
    pad1->SetBottomMargin(0.025);
    pad1->Draw();
    pad1->cd();
    for (UInt_t i0 = 0; i0 < NumPlots; i0++) {
      theHists[i0]->GetYaxis()->SetTitleSize(fontSize/ratioFrac);
      theHists[i0]->GetYaxis()->SetLabelSize(fontSize/ratioFrac);
      theHists[i0]->GetXaxis()->SetTitleSize(0);
      theHists[i0]->GetXaxis()->SetLabelSize(0);
    }
  }
  
  if (fNormalizedHists) {
    theHists[plotFirst]->DrawNormalized();
    for (UInt_t i0 = 0; i0 < NumPlots; i0++)
      theHists[i0]->DrawNormalized("same");
  }
  else {
    theHists[plotFirst]->Draw();
    for (UInt_t i0 = 0; i0 < NumPlots; i0++) {
      theHists[i0]->Draw("same");
    }
  }

  theLegend->Draw();
  if (logY)
    theCanvas->SetLogy();

  if (ratPlot != -1) {
    theCanvas->cd();
    TPad *pad2 = new TPad("pad2", "pad2", 0, 0, 1, 1 - ratioFrac);
    pad2->SetTopMargin(0.035);
    pad2->SetBottomMargin(0.4);
    pad2->Draw();
    pad2->cd();

    TH1D *tempHist = (TH1D*) theHists[ratPlot]->Clone("ValueHolder");
    for (Int_t iBin = 0; iBin < tempHist->GetXaxis()->GetNbins(); ++iBin)
      tempHist->SetBinError(iBin + 1, 0);

    TH1D *newHist  = (TH1D*) theHists[ratPlot]->Clone();
    newHist->Divide(tempHist);
    newHist->SetTitle(CanvasTitle+";"+XLabel+";Ratio");
    newHist->GetXaxis()->SetTitleSize(fontSize/(1 - ratioFrac));
    newHist->GetYaxis()->SetTitleSize(fontSize/(1 - ratioFrac));
    newHist->GetXaxis()->SetLabelSize(fontSize/(1 - ratioFrac));
    newHist->GetYaxis()->SetLabelSize(fontSize/(1 - ratioFrac));
    newHist->GetXaxis()->SetTitleOffset(1.1);
    newHist->GetYaxis()->SetTitleOffset((1 - ratioFrac)/ratioFrac);
    newHist->Draw();
    for (UInt_t iHists = 0; iHists < theHists.size(); iHists++) {
      if (int(iHists) == ratPlot)
        continue;
      newHist = (TH1D*) theHists[iHists]->Clone();
      newHist->SetTitle(CanvasTitle+";"+XLabel+";Ratio");
      newHist->GetXaxis()->SetTitleSize(fontSize/(1 - ratioFrac));
      newHist->GetYaxis()->SetTitleSize(fontSize/(1 - ratioFrac));
      newHist->GetXaxis()->SetLabelSize(fontSize/(1 - ratioFrac));
      newHist->GetYaxis()->SetLabelSize(fontSize/(1 - ratioFrac));
      newHist->GetXaxis()->SetTitleOffset(1.1);
      newHist->GetYaxis()->SetTitleOffset((1 - ratioFrac)/ratioFrac);
      newHist->Divide(tempHist);
      newHist->Draw("same,hist");
    }
  }
  
  return theCanvas;
}

//--------------------------------------------------------------------
void
PlotHists::MakeCanvas(Int_t NumXBins, Double_t *XBins, TString FileBase,
                      TString CanvasTitle, TString XLabel, TString YLabel,
                      Bool_t logY, Int_t ratPlot)
{
  std::vector<TH1D*> hists = MakeHists(NumXBins,XBins);
  TCanvas *theCanvas = MakeCanvas(hists,CanvasTitle,
                                  XLabel,YLabel,logY,ratPlot);

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
                      Int_t DataNum, Bool_t logY, Int_t ratPlot)
{
  std::vector<TH1D*> hists = MakeHists(NumXBins,MinX,MaxX,DataNum);
  TCanvas *theCanvas = MakeCanvas(hists,CanvasTitle,
                                  XLabel,YLabel,logY,ratPlot);

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
                      Bool_t logY, Int_t ratPlot)
{
  Double_t binWidth = (MaxX - MinX)/NumXBins;
  Double_t XBins[NumXBins+1];
  for (Int_t i0 = 0; i0 < NumXBins + 1; i0++)
    XBins[i0] = MinX + i0 * binWidth;


  MakeCanvas(NumXBins,XBins,FileBase,CanvasTitle,XLabel,YLabel,logY,ratPlot);
}
//--------------------------------------------------------------------
void
PlotHists::MakeRatio(Int_t NumXBins, Double_t MinX, Double_t MaxX, TString FileBase,
                     TString CanvasTitle, TString XLabel, TString YLabel,
                     Int_t DataNum)
{
  std::vector<TH1D*> hists = MakeHists(NumXBins,MinX,MaxX,DataNum);
  TH1D *tempHist = (TH1D*) hists[DataNum]->Clone("ValueHolder");
  for (UInt_t iHists = 0; iHists < hists.size(); iHists++) {
    hists[iHists]->Divide(tempHist);
  }

  TCanvas *theCanvas = MakeCanvas(hists,CanvasTitle,
                                  XLabel,YLabel,false);

  theCanvas->SaveAs(FileBase+".C");
  theCanvas->SaveAs(FileBase+".png");
  theCanvas->SaveAs(FileBase+".pdf");

  delete theCanvas;
  for (UInt_t i0 = 0; i0 < hists.size(); i0++)
    delete hists[i0];

  delete tempHist;
}
