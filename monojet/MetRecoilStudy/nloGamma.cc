#include <iostream>
#include <vector>

#include "TString.h"
#include "TFile.h"
#include "TH1F.h"

#include "TTree.h"
#include "TLorentzVector.h"
#include "TClonesArray.h"

void nloGamma (TString filename, Float_t xsec) {

  TFile *histFile = new TFile("/afs/cern.ch/user/y/yiiyama/public/kfactor.root");
  TH1F *NLOhist   = (TH1F*) histFile->FindObjectAny("pho_pt");

  TFile *file = new TFile(filename,"UPDATE");
  TTree *tree = (TTree*) file->FindObjectAny("events");
  TH1F  *allHist = (TH1F*) file->FindObjectAny("htotal");

  Float_t photonPt = 1.;
  Float_t mcWeight = 1.;

  tree->SetBranchAddress("photonPt",&photonPt);
  tree->SetBranchAddress("mcWeight",&mcWeight);

  Float_t nloFactor = 1.;
  Float_t XSecWeight = 1.;

  file->cd();
  TTree *nloTree = new TTree("nloTree","nloTree");
  TBranch *nloFactorBr = nloTree->Branch("nloFactor",&nloFactor,"nloFactor/F");
  TBranch *XSecWeightBr = nloTree->Branch("XSecWeight",&XSecWeight,"XSecWeight/F");

  for (int entry = 0; entry < tree->GetEntriesFast(); entry++) {
    tree->GetEntry(entry);
    XSecWeight = xsec/allHist->GetBinContent(1) * 1000;
    if (photonPt > 175 && photonPt < 500)
      nloFactor = mcWeight * NLOhist->GetBinContent(NLOhist->FindBin(photonPt));
    else
      nloFactor = 1;
    nloTree->Fill();
  }
  nloTree->Write();
  tree->AddFriend(nloTree);
  file->Close();
  histFile->Close();
}
