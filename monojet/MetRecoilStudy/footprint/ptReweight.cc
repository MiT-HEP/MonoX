#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TF1.h"
#include "TH1D.h"

void ptReweight(TString inFileName, TString ptName, TString theCut) {

  TFile *corrections = new TFile("monojet_SingleMuon+Run2015D.root");
  TTree *zPtTree = (TTree*) corrections->Get("events");

  Int_t numBins = 120;
  Float_t lower = 0.;
  Float_t upper = 600.;

  TH1D *zHist = new TH1D("Z","Z",numBins,lower,upper);

  TString lepCut = "(n_looselep == 2 && n_tightlep > 0 && n_loosepho == 0 && n_tau == 0 && lep2Pt > 20) && abs(dilep_m - 91) < 15 && (jet1isMonoJetId == 1) && (lep1PdgId*lep2PdgId == -169)";

  zPtTree->Draw("dilep_pt>>Z",lepCut);

  TFile *file = new TFile(inFileName,"UPDATE");
  TTree *inTree = (TTree*) file->Get("events");
  TTree *weightTree = new TTree("ptweights","ptweights");

  TH1D *bosHist = new TH1D("Bos","Bos",numBins,lower,upper);

  inTree->Draw(ptName + ">>Bos",theCut);

  zHist->Divide(bosHist);

  Float_t bosonPt  = 0;
  Float_t ptWeight = 1.;

  TBranch *ptBranch  = inTree->GetBranch(ptName);
  ptBranch->SetAddress(&bosonPt);
  TBranch *outBranch = weightTree->Branch("ptWeight",&ptWeight);

  for (int iEntry = 0; iEntry < ptBranch->GetEntries(); iEntry++) {
    ptBranch->GetEntry(iEntry);

    if (bosonPt < lower || bosonPt > upper)
      ptWeight = 1;
    else 
      ptWeight = zHist->GetBinContent(zHist->FindBin(bosonPt));

    weightTree->Fill();
  }

  weightTree->Write();

  file->Close();
  corrections->Close();

}
