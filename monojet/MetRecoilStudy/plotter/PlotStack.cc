#include <iostream>

#include "TFile.h"
#include "TLegend.h"
#include "THStack.h"

#include "PlotStack.h"

ClassImp(PlotStack)

//--------------------------------------------------------------------
PlotStack::PlotStack() :
  fTreeName("Events"),
  fJSON(""),
  fAllHist("htotal"),
  fLuminosity(19700),
  fDebug(false)
{
  fFriends.resize(0);
  fDataFiles.resize(0);
  fMCFiles.resize(0);
  fDataFileHolder.resize(0);
  fMCFileHolder.resize(0);
}

//--------------------------------------------------------------------
PlotStack::~PlotStack()
{}

//--------------------------------------------------------------------
std::vector<TH1D*>
PlotStack::GetHistList(std::vector<TString> FileList, Int_t NumXBins, Double_t *XBins, Bool_t isMC)
{
  std::vector<TFile*> theFiles;
  std::vector<TTree*> theTrees;
  TFile *tempFile;
  TTree *tempTree;
  TTree *tempFriend;
  for (UInt_t iFile = 0; iFile < FileList.size(); iFile++) {
    tempFile = TFile::Open(FileList[iFile]);
    theFiles.push_back(tempFile);

    if (fTreeName.Contains("/"))
      tempTree = (TTree*) tempFile->Get(fTreeName);
    else
      tempTree = (TTree*) tempFile->FindObjectAny(fTreeName);

    for (UInt_t iFriend = 0; iFriend < fFriends.size(); iFriend++) {
      if (fFriends[iFriend].Contains("/"))
        tempFriend = (TTree*) tempFile->Get(fFriends[iFriend]);
      else
        tempFriend = (TTree*) tempFile->FindObjectAny(fFriends[iFriend]);
      tempTree->AddFriend(tempFriend);
    }
    theTrees.push_back(tempTree);
  }

  SetTreeList(theTrees);

  std::vector<TH1D*> theHists = MakeHists(NumXBins, XBins);

  for (UInt_t iFile = 0; iFile < theFiles.size(); iFile++) {
    if (isMC) {
      TH1D *allHist = (TH1D*) theFiles[iFile]->FindObjectAny(fAllHist);
      if (fDebug) {
        std::cout << "Integral before " << theHists[iFile]->Integral() << std::endl;
        std::cout << "Scale factor " << fLuminosity*fXSecs[iFile]/allHist->GetBinContent(1) << std::endl;
      }
      theHists[iFile]->Scale(fLuminosity*fXSecs[iFile]/allHist->GetBinContent(1));
      if (fDebug)
        std::cout << "Integral after " << theHists[iFile]->Integral() << std::endl;

      fMCFileHolder = theFiles;
    }
    else {
      fDataFileHolder = theFiles;
      if (fDebug)
        std::cout << "Data yield " << theHists[iFile]->Integral() << std::endl;
    }
  }

  return theHists;
}

//--------------------------------------------------------------------
void
PlotStack::Plot(Int_t NumXBins, Double_t *XBins, TString FileBase,
                TString CanvasTitle, TString XLabel, TString YLabel,
                Bool_t logY)
{
  TCanvas *theCanvas = new TCanvas(fCanvasName,fCanvasName);
  theCanvas->SetTitle(CanvasTitle+";"+XLabel+";"+YLabel);
  TLegend *theLegend = new TLegend(l1,l2,l3,l4);
  theLegend->SetBorderSize(fLegendBorderSize);

  std::vector<TH1D*> DataHists = GetHistList(fDataFiles,NumXBins,XBins,false);
  std::vector<TH1D*>   MCHists = GetHistList(fMCFiles,NumXBins,XBins,true);

  TH1D *DataHist = (TH1D*) DataHists[0]->Clone("DataHist");
  DataHist->Reset("M");
  DataHist->Sumw2();
  DataHist->SetTitle(CanvasTitle+";"+XLabel+";"+YLabel);
  DataHist->SetMarkerStyle(8);

  for (UInt_t iHist = 0; iHist < DataHists.size(); iHist++)
    DataHist->Add(DataHists[iHist]);

  theLegend->AddEntry(DataHist,"Data","p");

  THStack *histStack = new THStack();

  TString previousEntry = "";
  for (UInt_t iHist = 0; iHist < MCHists.size(); iHist++) {
    MCHists[iHist]->SetTitle(CanvasTitle+";"+XLabel+";"+YLabel);
    MCHists[iHist]->SetLineColor(fLineColors[iHist]);
    MCHists[iHist]->SetFillColor(fLineColors[iHist]);
    MCHists[iHist]->SetFillStyle(1001);

    if (fLegendEntries[iHist] != previousEntry) {
      theLegend->AddEntry(MCHists[iHist],fLegendEntries[iHist],"l");
      previousEntry = fLegendEntries[iHist];
    }

    histStack->Add(MCHists[iHist],"hist");
  }
  histStack->SetTitle(CanvasTitle+";"+XLabel+";"+YLabel);

  histStack->Draw("");
  DataHist->Draw("SAME");
  theLegend->Draw();
  if (logY)
    theCanvas->SetLogy();

  theCanvas->SaveAs(FileBase+".C");
  theCanvas->SaveAs(FileBase+".png");
  theCanvas->SaveAs(FileBase+".pdf");

  delete histStack;
  delete DataHist;
  delete theLegend;
  delete theCanvas;
  for (UInt_t iHist = 0; iHist < MCHists.size(); iHist++)
    delete MCHists[iHist];
  for (UInt_t iHist = 0; iHist < DataHists.size(); iHist++)
    delete DataHists[iHist];

  for (UInt_t iFile = 0; iFile < fDataFiles.size(); iFile++)
    fDataFileHolder[iFile]->Close();
  for (UInt_t iFile = 0; iFile < fMCFiles.size(); iFile++)
    fMCFileHolder[iFile]->Close();
}

//--------------------------------------------------------------------
void
PlotStack::Plot(Int_t NumXBins, Double_t MinX, Double_t MaxX, TString FileBase,
                TString CanvasTitle, TString XLabel, TString YLabel,
                Bool_t logY)
{
  Double_t binWidth = (MaxX - MinX)/NumXBins;
  Double_t XBins[NumXBins+1];
  for (Int_t i0 = 0; i0 < NumXBins + 1; i0++)
    XBins[i0] = MinX + i0 * binWidth;

  Plot(NumXBins,XBins,FileBase,CanvasTitle,XLabel,YLabel,logY);
}

