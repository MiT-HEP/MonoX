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

  std::vector<TLorentzVector*> leptonVecs;
  std::vector<TLorentzVector*> photonVecs;

  for (Int_t iEntry = 0; iEntry < nentries; iEntry++) {

    leptonVecs.resize(0);
    photonVecs.resize(0);

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

      if (tempLepton->Pt() > 10. && ((*(inTree->lepSelBits))[iLepton] & 16) == 16) {
        leptonVecs.push_back(tempLepton);
        outTree->n_looselep++;
        if (outTree->n_looselep == 1) {
          outTree->lep1Pt    = tempLepton->Pt();
          outTree->lep1Eta   = tempLepton->Eta();
          outTree->lep1Phi   = tempLepton->Phi();
          outTree->lep1PdgId = (*(inTree->lepPdgId))[iLepton];
          outTree->lep1IsMedium = 0;
          outTree->lep1IsTight  = 0;
        }          
        else if (outTree->n_looselep == 2) {
          outTree->lep2Pt    = tempLepton->Pt();
          outTree->lep2Eta   = tempLepton->Eta();
          outTree->lep2Phi   = tempLepton->Phi();
          outTree->lep2PdgId = (*(inTree->lepPdgId))[iLepton];
          outTree->lep2IsMedium = 0;
          outTree->lep2IsTight  = 0;
        }          
        if (tempLepton->Pt() > 20. && ((*(inTree->lepSelBits))[iLepton] & 32) == 32) {
          outTree->n_mediumlep +=1;
          if (outTree->n_looselep == 1)
            outTree->lep1IsMedium = 1;
          else if (outTree->n_looselep == 2)
            outTree->lep2IsMedium = 1;
        }
        if (tempLepton->Pt() > 20. && ((*(inTree->lepSelBits))[iLepton] & 64) == 64) {
          outTree->n_tightlep +=1;
          if (outTree->n_looselep == 1)
            outTree->lep1IsTight = 1;
          else if (outTree->n_looselep == 2)
            outTree->lep2IsTight = 1;
        }
      }
    }
    
    if (outTree->n_looselep > 0) {
      vec1.SetPtEtaPhiM(outTree->lep1Pt,0.,outTree->lep1Phi,0);
      vec2.SetPtEtaPhiM(outTree->met,0,outTree->metPhi,0);
      vec3 = vec1 + vec2;

      outTree->mt     = vec3.M();
      outTree->u_magW = vec3.Pt();
      outTree->u_phiW = vec3.Phi();
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

    for (Int_t iPhoton = 0; iPhoton < inTree->photonP4->GetEntries(); iPhoton++) {
      TLorentzVector* tempPhoton = (TLorentzVector*) inTree->photonP4->At(iPhoton);

      Bool_t match = false;

      for (UInt_t iLepton = 0; iLepton < leptonVecs.size(); iLepton++) {
        if (deltaR(leptonVecs[iLepton]->Phi(),leptonVecs[iLepton]->Eta(),tempPhoton->Phi(),tempPhoton->Eta()) < 0.1)
          match = true;
      }
      
      if (match)
        continue;

      outTree->n_loosepho++;
      photonVecs.push_back(tempPhoton);

      if (tempPhoton->Pt() > 175 && (*(inTree->photonTightId))[iPhoton] == 1)
        outTree->n_tightpho++;

      if (outTree->n_loosepho == 1) {
        outTree->photonPt  = tempPhoton->Pt();
        outTree->photonEta = tempPhoton->Eta();
        outTree->photonPhi = tempPhoton->Phi();
        if (outTree->n_tightpho == 1)
          outTree->photonIsTight = 1;

        vec1.SetPtEtaPhiM(outTree->photonPt,0,outTree->photonPhi,0);
        vec2.SetPtEtaPhiM(outTree->met,0,outTree->metPhi,0);
        vec3 = vec1 + vec2;
        
        outTree->u_magPho  = vec3.Pt();
        outTree->u_phiPho  = vec3.Phi();
        outTree->u_perpPho = uPerp(outTree->u_magPho,outTree->u_phiPho,outTree->photonPhi);
        outTree->u_paraPho = uPara(outTree->u_magPho,outTree->u_phiPho,outTree->photonPhi);
      }
    }
    
    for (Int_t iJet = 0; iJet < inTree->jetP4->GetEntries(); iJet++) {
      TLorentzVector* tempJet = (TLorentzVector*) inTree->jetP4->At(iJet);

      Bool_t match = false;

      for (UInt_t iLepton = 0; iLepton < leptonVecs.size(); iLepton++) {
        if (deltaR(leptonVecs[iLepton]->Phi(),leptonVecs[iLepton]->Eta(),tempJet->Phi(),tempJet->Eta()) < 0.1)
          match = true;
      }

      if (match)
        continue;

      for (UInt_t iPhoton = 0; iPhoton < photonVecs.size(); iPhoton++) {
        if (deltaR(photonVecs[iPhoton]->Phi(),photonVecs[iPhoton]->Eta(),tempJet->Phi(),tempJet->Eta()) < 0.1)
          match = true;
      }

      if (match)
        continue;

      outTree->n_jets++;

      if (outTree->n_jets == 1) {
        outTree->jet1Pt  = tempJet->Pt();
        outTree->jet1Eta = tempJet->Eta();
        outTree->jet1Phi = tempJet->Phi();
        outTree->jet1M   = tempJet->M();

        outTree->jet1PuId             = (*(inTree->jetPuId))[iJet];
        outTree->jet1isMonoJetId      = (*(inTree->jetMonojetId))[iJet];
        outTree->jet1isLooseMonoJetId = (*(inTree->jetMonojetIdLoose))[iJet];

        outTree->jet1DPhiMet  = deltaPhi(outTree->jet1Phi,outTree->metPhi);
        outTree->jet1DPhiUZ   = deltaPhi(outTree->jet1Phi,outTree->u_phiZ);
        outTree->jet1DPhiUPho = deltaPhi(outTree->jet1Phi,outTree->u_phiPho);
      }

      else if (outTree->n_jets == 2) {
        outTree->jet2Pt  = tempJet->Pt();
        outTree->jet2Eta = tempJet->Eta();
        outTree->jet2Phi = tempJet->Phi();
        outTree->jet2M   = tempJet->M();

        outTree->jet2PuId             = (*(inTree->jetPuId))[iJet];
        outTree->jet2isMonoJetId      = (*(inTree->jetMonojetId))[iJet];
        outTree->jet2isLooseMonoJetId = (*(inTree->jetMonojetIdLoose))[iJet];

        outTree->jet2DPhiMet  = deltaPhi(outTree->jet2Phi,outTree->metPhi);
        outTree->jet2DPhiUZ   = deltaPhi(outTree->jet2Phi,outTree->u_phiZ);
        outTree->jet2DPhiUPho = deltaPhi(outTree->jet2Phi,outTree->u_phiPho);

        outTree->dPhi_j1j2 = deltaPhi(outTree->jet1Phi,outTree->jet2Phi);
        outTree->dR_j1j2   = deltaR(outTree->jet1Phi,outTree->jet1Eta,outTree->jet2Phi,outTree->jet2Eta);
      }
    }    
    outTree->triggerFired = inTree->triggerFired;
    
    outTree->Fill();
  }

  outTree->WriteToFile(outFile);

  outFile->Close();
  inFile->Close();

}
