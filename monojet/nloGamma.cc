#include <iostream>
#include <vector>

#include "TString.h"
#include "TFile.h"
#include "TH1F.h"

#include "TTree.h"
#include "TLorentzVector.h"
#include "TClonesArray.h"

void nloGamma (TString filename) {

  TFile *histFile = new TFile("/afs/cern.ch/user/y/yiiyama/public/kfactor.root");
  TH1F *NLOhist   = (TH1F*) histFile->FindObjectAny("pho_pt");

  TFile *file = new TFile(filename,"UPDATE");
  TTree *tree = (TTree*) file->FindObjectAny("events");

  TClonesArray *photons = new TClonesArray("TLorentzVector",20);
  Float_t mcWeight = 1.;

  tree->SetBranchAddress("photonP4",&photons);
  tree->SetBranchAddress("mcWeight",&mcWeight);

  Float_t nloFactor = 1.;

  file->cd();
  TTree *nloTree = new TTree("nloTree","nloTree");
  TBranch *nloFactorBr = nloTree->Branch("nloFactor",&nloFactor,"nloFactor/F");

  for (int entry = 0; entry < tree->GetEntriesFast(); entry++) {
    tree->GetEntry(entry);
    if (photons->GetEntries() != 0) {
      TLorentzVector *tempPhoton = (TLorentzVector*) photons->At(0);
      nloFactor = mcWeight * NLOhist->GetBinContent(NLOhist->FindBin(tempPhoton->Pt()));
      if (tempPhoton->Pt() > 500)
        nloFactor = 1;
    }
    else
      nloFactor = 1;
    nloTree->Fill();
  }
  nloTree->Write();
  tree->AddFriend(nloTree);
  file->Close();
  histFile->Close();
}
