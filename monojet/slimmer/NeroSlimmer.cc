#include <iostream>
#include <vector>

#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TH1F.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TF1.h"
#include "TMath.h"

#include "functions.h"
#include "MonoJetTree.h"
#include "NeroTree76.h"

enum IsoType {
  kIsoVeto = 0,  
  kIsoLoose,
  kIsoMedium,
  kIsoTight  
};

Bool_t PassIso(Float_t lepPt, Float_t lepEta, Float_t lepIso, Int_t lepPdgId, IsoType isoType) {

  Float_t isoCut = 0.;

  if (abs(lepPdgId) == 13) {
    isoCut = (isoType == kIsoTight) ? 0.12 : 0.20;
  }
  else {
    switch (isoType) {
    case kIsoVeto:
      isoCut = (fabs(lepEta) <= 1.479) ? 0.126 : 0.144;
      break;  
    case kIsoLoose:
      isoCut = (fabs(lepEta) <= 1.479) ? 0.0893 : 0.121;
      break;
    case kIsoMedium:
      isoCut = (fabs(lepEta) <= 1.479) ? 0.0766 : 0.0678;
      break;
    case kIsoTight:
      isoCut = (fabs(lepEta) <= 1.479) ? 0.0354 : 0.0646;
      break;
    default:
      break;
    }
  }
  return (lepIso/lepPt) < isoCut;
}

void NeroSlimmer(TString inFileName, TString outFileName, Bool_t isSig = false) {

  Float_t dROverlap  = 0.4;
  Float_t dRGenMatch = 0.2;
  Float_t bCutLoose  = 0.605;
  Float_t bCutMedium = 0.89;
  Float_t bCutTight  = 0.97;

  TFile *outFile = new TFile(outFileName,"RECREATE");
  MonoJetTree *outTree = new MonoJetTree("events", outFile);
  TH1F *allHist = new TH1F("htotal","htotal",1,-1,1);

  TFile *inFile           = TFile::Open(inFileName);
  TTree *inTreeFetch      = (TTree*) inFile->Get("nero/events");
  NeroTree76 *inTree      = new NeroTree76(inTreeFetch);
  TTree *allTree          = (TTree*) inFile->Get("nero/all");
  Float_t mcWeight        = 0.;
  TBranch *mcWeightBranch = allTree->GetBranch("mcWeight");
  mcWeightBranch->SetAddress(&mcWeight);

  TLorentzVector vec1;
  TLorentzVector vec2;
  TLorentzVector vec3;

  TLorentzVector saveGenVec;
  TLorentzVector saveDMVec;

  Int_t nentries = inTreeFetch->GetEntriesFast();

  std::vector<TLorentzVector*> leptonVecs;
  std::vector<TLorentzVector*> photonVecs;

  Float_t checkDR = 0.0;
  
  for (Int_t iEntry = 0; iEntry < allTree->GetEntriesFast(); iEntry++) {
    mcWeightBranch->GetEntry(iEntry);
    if (mcWeight > 0)
      allHist->Fill(0.0,1.0);
    else if (mcWeight < 0)
      allHist->Fill(0.0,-1.0);
  }

  outFile->WriteTObject(allHist,allHist->GetName());

  for (Int_t iEntry = 0; iEntry < nentries; iEntry++) {
    
    //// Clear out the saved vectors for cleaning ////

    leptonVecs.resize(0);
    photonVecs.resize(0);

    if (iEntry % 10000 == 0)
      std::cout << "Processing events: ... " << float(iEntry)/float(nentries)*100 << "%" << std::endl;
    
    inTree->GetEntry(iEntry);
    
    //// Fill some global event values ////

    outTree->runNum    = inTree->runNum;
    outTree->lumiNum   = inTree->lumiNum;
    outTree->eventNum  = inTree->eventNum;
    outTree->npv       = inTree->npv;
    outTree->npvTrue   = inTree->puTrueInt;
    outTree->rho       = inTree->rho;

    if (isSig)
      outTree->mcWeight = inTree->mcWeight;
    else {
      if (inTree->mcWeight < 0)
        outTree->mcWeight = -1;
      else
        outTree->mcWeight = 1;
    }

    outTree->trueMet    = ((TLorentzVector*)((*(inTree->metP4))[0]))->Pt();
    outTree->trueMetPhi = ((TLorentzVector*)((*(inTree->metP4))[0]))->Phi();

    outTree->rawMet    = ((TLorentzVector*)((*(inTree->metP4))[0]))->Pt();
    outTree->rawMetPhi = ((TLorentzVector*)((*(inTree->metP4))[0]))->Phi();

    outTree->triggerFired = inTree->triggerFired;
    
    //// Here is the lepton filling ////

    for (Int_t iLepton = 0; iLepton < inTree->lepP4->GetEntries(); iLepton++) {
      TLorentzVector* tempLepton = (TLorentzVector*) inTree->lepP4->At(iLepton);
      
      //// Rejecting leptons with Eta cuts ////

      if ((fabs(tempLepton->Eta()) > 2.5) ||
          (fabs(tempLepton->Eta()) > 2.4 && fabs((*(inTree->lepPdgId))[iLepton]) == 13))
        continue;

      //// Filling lepton values based on loose cut for muons and veto cut for electrons ////

      if (tempLepton->Pt() > 10. && (
          ( fabs((*(inTree->lepPdgId))[iLepton]) == 13 && ((*(inTree->lepSelBits))[iLepton] & 16) == 16 &&
            PassIso(tempLepton->Pt(),tempLepton->Eta(),(*(inTree->lepIso))[iLepton],(*(inTree->lepPdgId))[iLepton],kIsoLoose)
          ) ||
          (fabs((*(inTree->lepPdgId))[iLepton]) == 11 && ((*(inTree->lepSelBits))[iLepton] & 2) == 2 &&
            PassIso(tempLepton->Pt(),tempLepton->Eta(),(*(inTree->lepIso))[iLepton],(*(inTree->lepPdgId))[iLepton],kIsoVeto)
          )  
          )) {

        outTree->n_looselep++;
        if (outTree->n_looselep == 1) {
          outTree->lep1Pt    = tempLepton->Pt();
          outTree->lep1Eta   = tempLepton->Eta();
          outTree->lep1Phi   = tempLepton->Phi();
          outTree->lep1PdgId = (*(inTree->lepPdgId))[iLepton];
          outTree->lep1IsMedium = 0;
          outTree->lep1IsTight  = 0;
          outTree->lep1RelIso = (*(inTree->lepIso))[iLepton]/outTree->lep1Pt;
          outTree->lep1DPhiTrueMet  = abs(deltaPhi(outTree->lep1Phi,outTree->trueMetPhi));
        }          
        else if (outTree->n_looselep == 2) {
          outTree->lep2Pt    = tempLepton->Pt();
          outTree->lep2Eta   = tempLepton->Eta();
          outTree->lep2Phi   = tempLepton->Phi();
          outTree->lep2PdgId = (*(inTree->lepPdgId))[iLepton];
          outTree->lep2IsMedium = 0;
          outTree->lep2IsTight  = 0;
          outTree->lep2RelIso = (*(inTree->lepIso))[iLepton]/outTree->lep2Pt;
          outTree->lep2DPhiTrueMet  = abs(deltaPhi(outTree->lep2Phi,outTree->trueMetPhi));
        }          

        if (tempLepton->Pt() > 20. && ((*(inTree->lepSelBits))[iLepton] & 32) == 32 &&
            PassIso(tempLepton->Pt(),tempLepton->Eta(),(*(inTree->lepIso))[iLepton],(*(inTree->lepPdgId))[iLepton],kIsoMedium)) {

          outTree->n_mediumlep +=1;
          if (outTree->n_looselep == 1)
            outTree->lep1IsMedium = 1;
          else if (outTree->n_looselep == 2)
            outTree->lep2IsMedium = 1;
        }

        //// We are cleaning tight leptons from jets ////

        if (tempLepton->Pt() > 20. && ((*(inTree->lepSelBits))[iLepton] & 64) == 64 &&
            PassIso(tempLepton->Pt(),tempLepton->Eta(),(*(inTree->lepIso))[iLepton],(*(inTree->lepPdgId))[iLepton],kIsoTight) &&
            (abs((*(inTree->lepPdgId))[iLepton]) == 13 || tempLepton->Pt() > 40.)) {

          leptonVecs.push_back(tempLepton);
          outTree->n_tightlep +=1;
          if (outTree->n_looselep == 1)
            outTree->lep1IsTight = 1;
          else if (outTree->n_looselep == 2)
            outTree->lep2IsTight = 1;
        }
      }
    }
    
    //// If there are identified leptons, we will define our recoil using them ////

    if (outTree->n_looselep > 1) {
      vec1.SetPtEtaPhiM(outTree->lep1Pt,outTree->lep1Eta,outTree->lep1Phi,0);
      vec2.SetPtEtaPhiM(outTree->lep2Pt,outTree->lep2Eta,outTree->lep2Phi,0);
      vec3 = vec1 + vec2;
      outTree->dilep_pt  = vec3.Pt();
      outTree->dilep_eta = vec3.Eta();
      outTree->dilep_phi = vec3.Phi();
      outTree->dilep_m   = vec3.M();
      
      vec2.SetPtEtaPhiM(outTree->trueMet,0,outTree->trueMetPhi,0);
      vec1 = vec2 + vec3;
      
      outTree->met    = vec1.Pt();
      outTree->metPhi = vec1.Phi();

      outTree->boson_pt  = outTree->dilep_pt;
      outTree->boson_phi = outTree->dilep_phi;
    }
    else if (outTree->n_looselep > 0) {
      vec1.SetPtEtaPhiM(outTree->lep1Pt,0.,outTree->lep1Phi,0);
      vec2.SetPtEtaPhiM(outTree->trueMet,0,outTree->trueMetPhi,0);
      vec3 = vec1 + vec2;
      
      outTree->mt     = vec3.M();
      outTree->met    = vec3.Pt();
      outTree->metPhi = vec3.Phi();

      outTree->boson_pt  = outTree->met;
      outTree->boson_phi = outTree->metPhi;
    }
    
    //// Now we go on to look at photons ////
    
    for (Int_t iPhoton = 0; iPhoton < inTree->photonP4->GetEntries(); iPhoton++) {
      TLorentzVector* tempPhoton = (TLorentzVector*) inTree->photonP4->At(iPhoton);
      
      //// Set photon cuts at some pt and eta ////

      if (tempPhoton->Pt() < 15. || fabs(tempPhoton->Eta()) > 2.5 || 
          // ((*(inTree->photonSelBits))[iPhoton] & 128) != 128 ||
          ((*(inTree->photonSelBits))[iPhoton] & 8) != 8)
        continue;

      outTree->n_loosepho++;

      //// Usign the medium photon collection for futher cleaning ////
      if (tempPhoton->Pt() > 175 && ((*(inTree->photonSelBits))[iPhoton] & 16) == 16) {
        photonVecs.push_back(tempPhoton);
        outTree->n_mediumpho++;
      }
      
      //// If it's the first photon, save the kinematics ////

      if (outTree->n_loosepho == 1) {
        outTree->photonPt = tempPhoton->Pt();
        outTree->photonEta   = tempPhoton->Eta();
        outTree->photonPhi   = tempPhoton->Phi();
        if (outTree->n_mediumpho == 1)
          outTree->photonIsMedium = 1;
        else
          outTree->photonIsMedium = 0;
        
        //// If there's no leptons, define recoil quantities ////
        
        if (outTree->n_looselep == 0) {
          vec1.SetPtEtaPhiM(outTree->photonPt,0,outTree->photonPhi,0);
          vec2.SetPtEtaPhiM(outTree->trueMet,0,outTree->trueMetPhi,0);
          vec3 = vec1 + vec2;
          
          outTree->met     = vec3.Pt();
          outTree->metPhi  = vec3.Phi();
          
          outTree->boson_pt  = outTree->photonPt;
          outTree->boson_phi = outTree->photonPhi;
        }
      }
    }
    
    //// If we're in signal selection, fill MET, otherwise, fill recoil vars ////

    if (outTree->met < 100) {
      outTree->met    = outTree->trueMet;
      outTree->metPhi = outTree->trueMetPhi;
    }
    else {
      outTree->u_perp = uPerp(outTree->met,outTree->metPhi,outTree->boson_phi);
      outTree->u_para = uPara(outTree->met,outTree->metPhi,outTree->boson_phi);
    }

    // Place met cut here //
    if (outTree->met < 150) {
      outTree->Reset();
      continue;
    }

    Double_t checkDPhi = 5.0;
    Double_t clean_checkDPhi = 5.0;

    //// Now we go on to clean jets ////

    for (Int_t iJet = 0; iJet < inTree->jetP4->GetEntries(); iJet++) {
      TLorentzVector* tempJet = (TLorentzVector*) inTree->jetP4->At(iJet);
      
      // Avoid overlap with veto electrons in Zee control region
      if (abs(outTree->lep2PdgId) == 11 && 
          (deltaR(tempJet->Phi(),tempJet->Eta(),outTree->lep1Phi,outTree->lep1Phi) < 0.4 ||
           deltaR(tempJet->Phi(),tempJet->Eta(),outTree->lep2Phi,outTree->lep2Phi) < 0.4)) {
        continue;
      }

      Bool_t match = false;
      
      for (UInt_t iLepton = 0; iLepton < leptonVecs.size(); iLepton++) {
        if (deltaR(leptonVecs[iLepton]->Phi(),leptonVecs[iLepton]->Eta(),tempJet->Phi(),tempJet->Eta()) < dROverlap) {
          match = true;
          break;
        }
      }
      
      if (match == false) {
        for (UInt_t iPhoton = 0; iPhoton < photonVecs.size(); iPhoton++) {
          if (deltaR(photonVecs[iPhoton]->Phi(),photonVecs[iPhoton]->Eta(),tempJet->Phi(),tempJet->Eta()) < dROverlap) {
            match = true;
            break;
          }
        }
      }
      
      if (match == false && tempJet->Pt() > 30.0) {
        outTree->n_jetsCleanWithEndcap++;

        if (outTree->n_jetsCleanWithEndcap < 5) {

          checkDPhi = abs(deltaPhi(tempJet->Phi(),outTree->trueMetPhi));
          if (checkDPhi < outTree->minJetTrueMetDPhi_withendcap)
            outTree->minJetTrueMetDPhi_withendcap = checkDPhi;
          
          checkDPhi = abs(deltaPhi(tempJet->Phi(),outTree->metPhi));
          if (checkDPhi < outTree->minJetMetDPhi_withendcap)
            outTree->minJetMetDPhi_withendcap = checkDPhi;
        }
      }

      if (iJet == 0 && fabs(tempJet->Eta()) > 2.4)
        outTree->leadingJet_outaccp = 1;

      //// Ignore jets that are not in this region ////
      if (fabs(tempJet->Eta()) > 2.4 || (*(inTree->jetPuId))[iJet] < -0.62 || tempJet->Pt() < 15.0)
        continue;

      //// Count jets for b-tagging ////

      float dR_1 = dROverlap + 0.1;
      float dR_2 = dROverlap + 0.1;

      if (outTree->lep1Pt > 0)
        dR_1 = deltaR(outTree->lep1Phi, outTree->lep1Eta, tempJet->Phi(),tempJet->Eta());
      if (outTree->lep2Pt > 0)
        dR_2 = deltaR(outTree->lep2Phi, outTree->lep2Eta, tempJet->Phi(),tempJet->Eta());

      if (dR_1 > dROverlap && dR_2 > dROverlap) {
        if ((*(inTree->jetBdiscr))[iJet] > bCutTight)
          outTree->n_bjetsTight++;
        if ((*(inTree->jetBdiscr))[iJet] > bCutMedium)
          outTree->n_bjetsMedium++;   
        if ((*(inTree->jetBdiscr))[iJet] > bCutLoose)
          outTree->n_bjetsLoose++;
      }
      
      //// Now apply a pt cut ////

      if (tempJet->Pt() < 30.0) 
        continue;
      
      outTree->n_jets++;

      if (outTree->n_jets < 5) {
          // Check for delta phi from met for all jets
          checkDPhi = abs(deltaPhi(tempJet->Phi(),outTree->metPhi));
          if (checkDPhi < outTree->minJetMetDPhi)
            outTree->minJetMetDPhi = checkDPhi;

          // Check for delta phi from true met for all jets
          checkDPhi = abs(deltaPhi(tempJet->Phi(),outTree->trueMetPhi));
          if (checkDPhi < outTree->minJetTrueMetDPhi)
            outTree->minJetTrueMetDPhi = checkDPhi;
      }

      //// Store uncleaned jet for fun ////

      if (outTree->n_jets == 1) {
        outTree->leadingjetPt  = tempJet->Pt();
        outTree->leadingjetEta = tempJet->Eta();
        outTree->leadingjetPhi = tempJet->Phi();
        outTree->leadingjetM   = tempJet->M();
      }

      //// Now do cleaning ////
      
      match = false;
      
      for (UInt_t iLepton = 0; iLepton < leptonVecs.size(); iLepton++) {
        if (deltaR(leptonVecs[iLepton]->Phi(),leptonVecs[iLepton]->Eta(),tempJet->Phi(),tempJet->Eta()) < dROverlap) {
          match = true;
          break;
        }
      }
      
      if (match)
        continue;
      
      for (UInt_t iPhoton = 0; iPhoton < photonVecs.size(); iPhoton++) {
        if (deltaR(photonVecs[iPhoton]->Phi(),photonVecs[iPhoton]->Eta(),tempJet->Phi(),tempJet->Eta()) < dROverlap) {
          match = true;
          break;
        }
      }
      
      if (match)
        continue;
      
      outTree->n_cleanedjets++;
      outTree->ht_cleanedjets += tempJet->Pt();

      if (outTree->n_cleanedjets < 5){
        // Check for delta phi from met for all jets:
        clean_checkDPhi = abs(deltaPhi(tempJet->Phi(),outTree->metPhi));
        if (clean_checkDPhi < outTree->minJetMetDPhi_clean)
          outTree->minJetMetDPhi_clean = clean_checkDPhi;
      }

      if (outTree->n_cleanedjets == 1) {
          outTree->jet1Pt  = tempJet->Pt();
          outTree->jet1Eta = tempJet->Eta();
          outTree->jet1Phi = tempJet->Phi();
          outTree->jet1M   = tempJet->M();
          
          outTree->jet1BTag             = (*(inTree->jetBdiscr))[iJet];
          outTree->jet1PuId             = (*(inTree->jetPuId))[iJet];
          outTree->jet1isMonoJetId      = ((*(inTree->jetSelBits))[iJet] & 256) == 256;
          outTree->jet1isMonoJetIdNew   = ((*(inTree->jetSelBits))[iJet] & 1024) == 1024;
          outTree->jet1isLooseMonoJetId = ((*(inTree->jetSelBits))[iJet] & 512) == 512;
          
          outTree->jet1DPhiMet     = abs(deltaPhi(outTree->jet1Phi,outTree->metPhi));
          outTree->jet1DPhiTrueMet = abs(deltaPhi(outTree->jet1Phi,outTree->trueMetPhi));

          outTree->jet1QGL    = (*(inTree->jetQGL))[iJet];
          outTree->jet1Flavor = (*(inTree->jetFlavour))[iJet];
      }
      
      else if (outTree->n_cleanedjets == 2) {
          outTree->jet2Pt  = tempJet->Pt();
          outTree->jet2Eta = tempJet->Eta();
          outTree->jet2Phi = tempJet->Phi();
          outTree->jet2M   = tempJet->M();
          
          outTree->jet2BTag             = (*(inTree->jetBdiscr))[iJet];
          outTree->jet2PuId             = (*(inTree->jetPuId))[iJet];
          outTree->jet2isMonoJetId      = ((*(inTree->jetSelBits))[iJet] & 256) == 256;
          outTree->jet2isMonoJetIdNew   = ((*(inTree->jetSelBits))[iJet] & 1024) == 1024;
          outTree->jet2isLooseMonoJetId = ((*(inTree->jetSelBits))[iJet] & 512) == 512;
          
          outTree->jet2DPhiMet     = abs(deltaPhi(outTree->jet2Phi,outTree->metPhi));
          outTree->jet2DPhiTrueMet = abs(deltaPhi(outTree->jet2Phi,outTree->trueMetPhi));
          
          outTree->jet2QGL = (*(inTree->jetQGL))[iJet];

          outTree->dPhi_j1j2 = abs(deltaPhi(outTree->jet1Phi,outTree->jet2Phi));
      }
    }
    
    //// Now check number of non-overlapping taus ////

    for (Int_t iTau = 0; iTau < inTree->tauP4->GetEntries(); iTau++) {
      TLorentzVector* tempTau = (TLorentzVector*) inTree->tauP4->At(iTau);

      if (tempTau->Pt() < 18. || fabs(tempTau->Eta()) > 2.3)
        continue;

      if (((*(inTree->tauSelBits))[iTau] & 7) != 7) 
        continue;
      if ((*(inTree->tauIsoDeltaBetaCorr))[iTau] > 4.5)
        continue;

      //// Now do cleaning ////
      
      Bool_t match = false;
      
      for (UInt_t iLepton = 0; iLepton < leptonVecs.size(); iLepton++) {
        if (deltaR(leptonVecs[iLepton]->Phi(),leptonVecs[iLepton]->Eta(),tempTau->Phi(),tempTau->Eta()) < dROverlap) {
          match = true;
          break;
        }
      }
      
      if (match)
        continue;

      float dR_1 = dROverlap + 0.1;
      float dR_2 = dROverlap + 0.1;

      if (outTree->lep1Pt > 0)
        dR_1 = deltaR(outTree->lep1Phi, outTree->lep1Eta, tempTau->Phi(),tempTau->Eta());
      if (outTree->lep2Pt > 0)
        dR_2 = deltaR(outTree->lep2Phi, outTree->lep2Eta, tempTau->Phi(),tempTau->Eta());

      if (dR_1 > dROverlap && dR_2 > dROverlap)
        outTree->n_tau++;
    }
    
    //// Now look for generator information ////

    if (inTree->metP4_GEN->GetEntries() > 0) {
      TLorentzVector *genMet = (TLorentzVector*) inTree->metP4_GEN->At(0);
      outTree->genMet = genMet->Pt();
      outTree->genMetPhi = genMet->Phi();
      
      saveGenVec.SetPtEtaPhiM(0,0,0,0);
      saveDMVec.SetPtEtaPhiM(0,0,0,0);
      Bool_t saveThisDM = false;
      
      Bool_t isFound = false;
      
      for (Int_t iGen = 0; iGen < inTree->genP4->GetEntries(); iGen++) {
        TLorentzVector* tempGen = (TLorentzVector*) inTree->genP4->At(iGen);
        Int_t checkPdgId = abs((*(inTree->genPdgId))[iGen]);
      
        if (checkPdgId == 25){
          outTree->genDM_pt = tempGen->Pt();
          outTree->genDM_eta = tempGen->Eta();
          outTree->genDM_phi = tempGen->Phi();
          outTree->genDM_mass = tempGen->M();
          outTree->genDM_PdgId = checkPdgId;
        }
        else if (checkPdgId > 900000 && outTree->genDM_PdgId != 25) {
          if (saveDMVec.Pt() > 1) {
            if (saveThisDM)
              std::cout << "Uh oh, found three DM particles... Fix slimmer." << std::endl;
            saveThisDM = true;
          }
          saveDMVec = saveDMVec + *tempGen;
          if (saveThisDM) {
            outTree->genDM_pt = saveDMVec.Pt();
            outTree->genDM_eta = saveDMVec.Eta();
            outTree->genDM_phi = saveDMVec.Phi();
            outTree->genDM_mass = saveDMVec.M();
            outTree->genDM_PdgId = checkPdgId;
          }
        }
  
        if ((checkPdgId != 11 && checkPdgId != 13 && checkPdgId != 22) && !(outTree->boson_pt < 0 && (checkPdgId == 23 || checkPdgId == 24)))
          continue;
        
        //// Look for two leptons here ////
        if (outTree->n_looselep > 1) {
          if (outTree->lep2Pt > 0 && outTree->lep1PdgId + outTree->lep2PdgId == 0 && checkPdgId % 2 == 1) {
            if (deltaR(tempGen->Phi(),tempGen->Eta(),outTree->lep1Phi,outTree->lep1Eta) < dRGenMatch ||
                deltaR(tempGen->Phi(),tempGen->Eta(),outTree->lep2Phi,outTree->lep2Eta) < dRGenMatch) {
              if (saveGenVec.Pt() > 5) {
                outTree->genBos_PdgId = 23;
                saveGenVec = saveGenVec + *tempGen;
                break;
              }
              else
                saveGenVec = *tempGen;
            }
          }
        }
        //// Look for 'W' here ////
        else if (outTree->n_looselep == 1) {
          if (outTree->lep1Pt > 0 && checkPdgId % 2 == 1) {
            if (deltaR(tempGen->Phi(),tempGen->Eta(),outTree->lep1Phi,outTree->lep1Eta) < dRGenMatch) {
              saveGenVec = *tempGen + *genMet;
              outTree->genBos_PdgId = (outTree->lep1PdgId < 0) ? 24 : -24;
              break;
            }
          }
        }
        //// Look for photon here ////
        else if (outTree->n_loosepho > 0) {
          if (outTree->photonPt > 0 && checkPdgId == 22) {
            // if (deltaR(tempGen->Phi(),tempGen->Eta(),outTree->photonPhi,outTree->photonEta) < dRGenMatch) {
            //// Look for highest pT for kfactor reasons ////
            if (tempGen->Pt() > saveGenVec.Pt()) {
              saveGenVec = *tempGen;
              outTree->genBos_PdgId = 22;
            }        
          }
        }
        //// Look for Z to nunu here or perhaps a W with missed lepton ////
        else if (checkPdgId == 23 || checkPdgId == 24) {
          if ((tempGen->Pt() > saveGenVec.Pt() && !(checkPdgId == 24 && outTree->genBos_PdgId == 23)) || (abs(outTree->genBos_PdgId) == 24 && checkPdgId == 23)) {
            saveGenVec = *tempGen;
            outTree->genBos_PdgId = abs((*(inTree->genPdgId))[iGen]);
          }
        }
      }

      outTree->genBos_pt   = saveGenVec.Pt();
      outTree->genBos_eta  = saveGenVec.Eta();
      outTree->genBos_phi  = saveGenVec.Phi();
      outTree->genBos_mass = saveGenVec.M();
    }

    for (Int_t iFatJet = 0; iFatJet < inTree->fatjetAK8CHSP4->GetEntries(); iFatJet++) {
      TLorentzVector* tempFatJet = (TLorentzVector*) inTree->fatjetAK8CHSP4->At(iFatJet);

      Bool_t match = false;

      for (UInt_t iLepton = 0; iLepton < leptonVecs.size(); iLepton++) {
        if (deltaR(leptonVecs[iLepton]->Phi(),leptonVecs[iLepton]->Eta(),tempFatJet->Phi(),tempFatJet->Eta()) < 2.0 * dROverlap) {
          match = true;
          break;
        }
      }
      
      for (UInt_t iPhoton = 0; iPhoton < photonVecs.size(); iPhoton++) {
        if (deltaR(photonVecs[iPhoton]->Phi(),photonVecs[iPhoton]->Eta(),tempFatJet->Phi(),tempFatJet->Eta()) < 2.0 * dROverlap) {
          match = true;
          break;
        }
      }

      if (match)
        continue;

      if (outTree->fatjet1Pt < 0) {
        outTree->fatjet1Pt   = tempFatJet->Pt();
        outTree->fatjet1Eta  = tempFatJet->Eta();
        outTree->fatjet1Phi  = tempFatJet->Phi();
        outTree->fatjet1Mass = tempFatJet->M();
        outTree->fatjet1TrimmedM  = (*(inTree->fatjetAK8CHSTrimmedMass))[iFatJet];
        outTree->fatjet1PrunedM   = (*(inTree->fatjetAK8CHSPrunedMass))[iFatJet];
        outTree->fatjet1FilteredM = (*(inTree->fatjetAK8CHSFilteredMass))[iFatJet];
        outTree->fatjet1SoftDropM = (*(inTree->fatjetAK8CHSSoftdropMass))[iFatJet];
        outTree->fatjet1tau1  = (*(inTree->fatjetAK8CHSTau1))[iFatJet];
        outTree->fatjet1tau2  = (*(inTree->fatjetAK8CHSTau2))[iFatJet];
        outTree->fatjet1tau21 = outTree->fatjet1tau2/outTree->fatjet1tau1;

        // outTree->fatjet1MonojetId = (*(inTree->fatjetAK8CHSMonojetid))[iFatJet];

        if (deltaR(outTree->jet1Phi,outTree->jet1Eta,outTree->fatjet1Phi,outTree->fatjet1Eta) < 0.8)
          outTree->fatjet1isLeading = 1;
        else
          outTree->fatjet1isLeading = 0;

        outTree->fatjet1DPhiMet     = deltaPhi(outTree->metPhi,outTree->fatjet1Phi);
        outTree->fatjet1DPhiTrueMet = deltaPhi(outTree->trueMetPhi,outTree->fatjet1Phi);

        for (Int_t iJet = 0; iJet < inTree->jetP4->GetEntries(); iJet++) {
          TLorentzVector* tempJet = (TLorentzVector*) inTree->jetP4->At(iJet);
          checkDR = deltaR(outTree->fatjet1Phi,outTree->fatjet1Eta,tempJet->Phi(),tempJet->Eta());

          // Check loose distance
          if ((*(inTree->jetBdiscr))[iJet] > bCutLoose) {
            if (checkDR < outTree->fatjet1DRLooseB)
                outTree->fatjet1DRLooseB = checkDR;

            // Check medium distance
            if ((*(inTree->jetBdiscr))[iJet] > bCutMedium) {
              if (checkDR < outTree->fatjet1DRMediumB)
                outTree->fatjet1DRMediumB = checkDR;

              // Check tight distance
              if ((*(inTree->jetBdiscr))[iJet] > bCutTight) {
                if (checkDR < outTree->fatjet1DRTightB)
                  outTree->fatjet1DRTightB = checkDR;
              }
            }
          }
        }

        if (inTree->metP4_GEN->GetEntries() > 0) {
          for (Int_t iGen = 0; iGen < inTree->genP4->GetEntries(); iGen++) {
            Int_t checkPdgId = abs((*(inTree->genPdgId))[iGen]);
            if (checkPdgId != 23 && checkPdgId != 24)
              continue;

            TLorentzVector *tempGen = (TLorentzVector*) inTree->genP4->At(iGen);
            checkDR = deltaR(outTree->fatjet1Phi,outTree->fatjet1Eta,tempGen->Phi(),tempGen->Eta());
            if (checkDR < outTree->fatjet1DRGenW) {
              outTree->fatjet1DRGenW   = checkDR;
              outTree->fatjet1GenWPt   = tempGen->Pt();
              outTree->fatjet1GenWMass = tempGen->M();
            }
          }
        }
      }
    }

    if (inTree->metP4_GEN->GetEntries() > 0) {
      // Loop through to find gen jet information matched to leading jets.
      for (Int_t iGen = 0; iGen < inTree->genjetP4->GetEntries(); ++iGen) {
        TLorentzVector *tempGenJet = (TLorentzVector*) inTree->genjetP4->At(iGen);
        checkDR = deltaR(outTree->jet1Phi,outTree->jet1Eta,tempGenJet->Phi(),tempGenJet->Eta());
        if (checkDR < outTree->genJetDRjet1) {
          outTree->genJet_pt = tempGenJet->Pt();
          outTree->genJet_eta = tempGenJet->Eta();
          outTree->genJet_phi = tempGenJet->Phi();
          outTree->genJet_mass = tempGenJet->M();
          outTree->genJetDRjet1 = checkDR;
        }
      }
    }

    // Now do the VBF cut
    if (outTree->n_jetsCleanWithEndcap > 1) {
      TLorentzVector* tempJet1 = (TLorentzVector*) inTree->jetP4->At(0);
      TLorentzVector* tempJet2 = (TLorentzVector*) inTree->jetP4->At(1);

      outTree->jot1Pt = tempJet1->Pt();
      outTree->jot1Eta = tempJet1->Eta();
      outTree->jot1Phi = tempJet1->Phi();
      outTree->jot1M = tempJet1->M();
      outTree->jot2Pt = tempJet2->Pt();
      outTree->jot2Eta = tempJet2->Eta();
      outTree->jot2Phi = tempJet2->Phi();
      outTree->jot2M = tempJet2->M();
      outTree->mjj = vectorSumMass(tempJet1->Pt(), tempJet1->Eta(), tempJet1->Phi(), tempJet1->M(), tempJet2->Pt(), tempJet2->Eta(), tempJet2->Phi(), tempJet2->M());
      outTree->jjDEta = fabs(tempJet1->Eta() - tempJet2->Eta());

      outTree->IsVBF = tempJet1->Pt() > 80 && tempJet2->Pt() > 70 && vectorSumMass(tempJet1->Pt(), tempJet1->Eta(), tempJet1->Phi(), tempJet1->M(), tempJet2->Pt(), tempJet2->Eta(), tempJet2->Phi(), tempJet2->M()) > 1100 && fabs(tempJet1->Eta() - tempJet2->Eta()) > 3.6 && outTree->minJetMetDPhi_clean > 2.3;
    }

    outTree->Fill();

  }

  outTree->WriteToFile(outFile);
  outFile->Close();
  inFile->Close();
}
