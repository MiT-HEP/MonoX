#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TF1.h"

void feetses(TString inFileName, TString ptName, TString paraName, TString funcName) {

  TFile *corrections = new TFile("fitTest_0.root");
  TF1 *ZmmFunc  = (TF1*) corrections->Get("mu_Zmm_Data");
  TF1 *corrFunc = (TF1*) corrections->Get(funcName);

  TFile *file = new TFile(inFileName,"UPDATE");
  TTree *inTree = (TTree*) file->Get("events");
  TTree *shiftTree = new TTree("footprints","footprints");

  Float_t bosonPt    = 0;
  Float_t u_paraBoso = 0.;
  Float_t u_paraFoot = 0.;

  TBranch *ptBranch  = inTree->GetBranch(ptName);
  ptBranch->SetAddress(&bosonPt);
  TBranch *inBranch  = inTree->GetBranch(paraName);
  inBranch->SetAddress(&u_paraBoso);
  TBranch *outBranch = shiftTree->Branch("u_paraFoot",&u_paraFoot);

  for (int iEntry = 0; iEntry < inBranch->GetEntries(); iEntry++) {
    inBranch->GetEntry(iEntry);
    ptBranch->GetEntry(iEntry);

    u_paraFoot = u_paraBoso + ZmmFunc->Eval(bosonPt) - corrFunc->Eval(bosonPt);
    
    shiftTree->Fill();
  }

  shiftTree->Write();

  file->Close();
  corrections->Close();

}
