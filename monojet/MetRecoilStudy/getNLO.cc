#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TH1D.h"
#include "TH1F.h"
#include "TProfile.h"

void getNLO() {

  TFile *nloFile = TFile::Open("root://eoscms//eos/cms/store/cmst3/user/pharris/mc/A_13TeV/A_13TeV_v2.root");
  TTree *nloTree = (TTree*) nloFile->Get("Events");

  float effWeight = 0.;
  TBranch *effBr = nloTree->GetBranch("effweight");
  effBr->SetAddress(&effWeight);

  TProfile *mcWeight = new TProfile("mcWeight","mcWeight",1,1000,1350);

  nloTree->Draw("mcweight:mcweight>>mcWeight");

  double xsec = mcWeight->GetBinContent(1);

  TH1F *numNLO = new TH1F("numNLO","numNLO",1,-1,1);
  for (int iEntry = 0; iEntry != nloTree->GetEntriesFast(); ++iEntry) {
    effBr->GetEntry(iEntry);
    if (effWeight < 0)
      numNLO->Fill(0.0,-1.0);
    else
      numNLO->Fill(0.0,1.0);
  }

  Int_t NBins = 27;
  Double_t Bins[28] = {40,60,80,100,120,140,160,180,200,220,240,260,280,300,340,380,420,460,500,540,580,640,700,760,820,880,940,1000};

  TFile *gjetsFile = TFile::Open("root://eoscms//eos/cms/store/user/zdemirag/MonoJet/Full/V003/monojet_GJets.root");
  TTree *gjetsTree = (TTree*) gjetsFile->Get("events");
  TH1D *gjetsHist = new TH1D("phoPt","phoPt",NBins,Bins);
  gjetsTree->Draw("genBos_pt>>phoPt","(genBos_PdgId == 22) * XSecWeight * (abs(genBos_eta) < 1.5)");

  TFile *outFile = new TFile("kfactor_aMCatNLO.root","RECREATE");
  TH1D *outHist = new TH1D("pho_pt","pho_pt",NBins,Bins);

  nloTree->Draw("dm_pt>>pho_pt","effweight/abs(effweight)*(abs(dm_eta) < 1.5)");
  outHist->Scale(xsec/numNLO->GetBinContent(1) * 1000);

  outHist->Divide(gjetsHist);

  outHist->Write();
  outFile->Close();

  gjetsFile->Close();
  nloFile->Close();

}
