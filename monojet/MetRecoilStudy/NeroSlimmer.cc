#include <iostream>
#include <vector>

#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TH1F.h"

#include "functions.h"
#include "MonoJetTree.h"
#include "NeroTree.h"

void NeroSlimmer(TString inFileName, TString outFileName) {

  TFile *inFile           = TFile::Open(inFileName);
  TTree *inTreeFetch      = (TTree*) inFile->Get("nero/events");
  NeroTree *inTree        = new NeroTree(inTreeFetch);
  TTree *allTree          = (TTree*) inFile->Get("nero/all");
  Float_t mcWeight        = 0.;
  TBranch *mcWeightBranch = allTree->GetBranch("mcWeight");
  mcWeightBranch->SetAddress(&mcWeight);

  TFile *outFile = new TFile(outFileName,"RECREATE");
  MonoJetTree *outTree = new MonoJetTree("events");
  TH1F *allHist = new TH1F("htotal","htotal",1,-1,1);

  TLorentzVector vec1;
  TLorentzVector vec2;
  TLorentzVector vec3;

  for (Int_t iEntry = 0; iEntry < allTree->GetEntriesFast(); iEntry++) {
    mcWeightBranch->GetEntry(iEntry);
    if (mcWeight > 0)
      allHist->Fill(0.0,1.0);
    else if (mcWeight < 0)
      allHist->Fill(0.0,-1.0);
  }
  outFile->WriteTObject(allHist,allHist->GetName());

  Int_t nentries = inTreeFetch->GetEntriesFast();

  std::vector<TLorentzVector*> cleaningVecs;

  for (Int_t iEntry = 0; iEntry < nentries; iEntry++) {

    cleaningVecs.resize(0);

    if (iEntry % 10000 == 0)
      std::cout << "Processing events: ... " << float(iEntry)/float(nentries)*100 << "%" << std::endl;

    inTree->GetEntry(iEntry);

    outTree->runNum   = inTree->runNum;
    outTree->lumiNum  = inTree->lumiNum;
    outTree->eventNum = inTree->eventNum;

    if (inTree->mcWeight < 0)
      outTree->mcWeight = -1;
    else
      outTree->mcWeight = 1;

    outTree->met    = ((TLorentzVector*)((*(inTree->metP4))[0]))->Pt();
    outTree->metPhi = ((TLorentzVector*)((*(inTree->metP4))[0]))->Phi();

    for (Int_t iLepton = 0; iLepton < inTree->lepP4->GetEntries(); iLepton++) {
      TLorentzVector* tempLepton = (TLorentzVector*) inTree->lepP4->At(iLepton);

      if (tempLepton->Pt() > 10. && ((*(inTree->lepSelBits))[iLepton] & 8) == 8) {
        cleaningVecs.push_back(tempLepton);
        outTree->n_looselep++;
        if (outTree->n_looselep == 1) {
          outTree->lep1Pt    = tempLepton->Pt();
          outTree->lep1Eta   = tempLepton->Eta();
          outTree->lep1Phi   = tempLepton->Phi();
          outTree->lep1PdgId = (*(inTree->lepPdgId))[iLepton];
        }          
        else if (outTree->n_looselep == 2) {
          outTree->lep2Pt    = tempLepton->Pt();
          outTree->lep2Eta   = tempLepton->Eta();
          outTree->lep2Phi   = tempLepton->Phi();
          outTree->lep2PdgId = (*(inTree->lepPdgId))[iLepton];
        }          
        if (tempLepton->Pt() > 20. && ((*(inTree->lepSelBits))[iLepton] & 32) == 32) {
          outTree->n_tightlep +=1;
          if (outTree->n_looselep == 1)
            outTree->lep1isTight = 1;
          else if (outTree->n_looselep == 2)
            outTree->lep2isTight = 2;
        }
      }
    }

    if (outTree->n_looselep > 1) {
      vec1.SetPtEtaPhiM(outTree->lep1Pt,outTree->lep1Eta,outTree->lep1Phi,0);
      vec2.SetPtEtaPhiM(outTree->lep2Pt,outTree->lep2Eta,outTree->lep2Phi,0);
      vec3 = vec1 + vec2;
      outTree->dilep_pt  = vec3.Pt();
      outTree->dilep_eta = vec3.Eta();
      outTree->dilep_phi = vec3.Phi();
      outTree->dilep_m   = vec3.M();

      vec2.SetPtEtaPhiM(outTree->met,0,outTree->metPhi,0);
      vec1 = vec2 + vec3;

      outTree->u_magZ  = vec1.Pt();
      outTree->u_phiZ  = vec1.Phi();
      outTree->u_perpZ = uPerp(outTree->u_magZ,outTree->u_phiZ,outTree->dilep_phi);
      outTree->u_paraZ = uPara(outTree->u_magZ,outTree->u_phiZ,outTree->dilep_phi);
    }
    if (outTree->n_looselep > 0)
      outTree->mt = transverseMass(outTree->lep1Pt,outTree->lep1Phi,outTree->met,outTree->metPhi);

    for (Int_t iPhoton = 0; iPhoton < inTree->photonP4->GetEntries(); iPhoton++) {
      TLorentzVector* tempPhoton = (TLorentzVector*) inTree->lepP4->At(iPhoton);

      if (tempPhoton->Pt() > 10. && ((*(inTree->lepSelBits))[iPhoton] & 8) == 8) {
        cleaningVecs.push_back(tempPhoton);
        outTree->n_looselep++;
        if (outTree->n_looselep == 1) {
          outTree->lep1Pt    = tempLepton->Pt();
          outTree->lep1Eta   = tempLepton->Eta();
          outTree->lep1Phi   = tempLepton->Phi();
          outTree->lep1PdgId = (*(inTree->lepPdgId))[iLepton];
        }          
        else if (outTree->n_looselep == 2) {
          outTree->lep2Pt    = tempLepton->Pt();
          outTree->lep2Eta   = tempLepton->Eta();
          outTree->lep2Phi   = tempLepton->Phi();
          outTree->lep2PdgId = (*(inTree->lepPdgId))[iLepton];
        }          
        if (tempLepton->Pt() > 20. && ((*(inTree->lepSelBits))[iLepton] & 32) == 32) {
          outTree->n_tightlep +=1;
          if (outTree->n_looselep == 1)
            outTree->lep1isTight = 1;
          else if (outTree->n_looselep == 2)
            outTree->lep2isTight = 2;
        }
      }
    }
  // float photonPt;
  // float photonEta;
  // float photonPhi;
  // int   photonIsTight;
  // int   n_tightpho;
  // int   n_loosepho;

  // float u_perpPho;
  // float u_paraPho;
  // float u_magPho;
  // float u_phiPho;

  // float jet1Pt;
  // float jet1Eta;
  // float jet1Phi;
  // float jet1dRmet;
  // int   n_jets;

    outTree->triggerFired = inTree->triggerFired;

    outTree->Fill();
  }

  outTree->WriteToFile(outFile);

  outFile->Close();
  inFile->Close();

}
