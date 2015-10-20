#include <iostream>
#include <vector>

#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TH1F.h"
#include "TH1D.h"
#include "TH2D.h"

#include "functions.h"
#include "MonoJetTree.h"
#include "NeroTree.h"

enum IsoType {
  kIsoLoose = 0,
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

void NeroSlimmer(TString inFileName, TString outFileName) {

  TFile *elecSFFile  = new TFile("scalefactors_ele.root");
  TH2D *elecSFLoose  = (TH2D*) elecSFFile->Get("unfactorized_scalefactors_Loose_ele");
  TH2D *elecSFMedium = (TH2D*) elecSFFile->Get("unfactorized_scalefactors_Medium_ele");
  TH2D *elecSFTight  = (TH2D*) elecSFFile->Get("unfactorized_scalefactors_Tight_ele");

  TFile *muonSFFile  = new TFile("scalefactors_mu.root");
  TH2D *muonSFLoose  = (TH2D*) muonSFFile->Get("unfactorized_scalefactors_Loose_mu");
  TH2D *muonSFMedium = (TH2D*) muonSFFile->Get("unfactorized_scalefactors_Medium_mu");
  TH2D *muonSFTight  = (TH2D*) muonSFFile->Get("unfactorized_scalefactors_Tight_mu");

  Float_t SFEtaMin = 0;
  Float_t SFEtaMax = 2.5;

  Float_t SFPtMin = 10;
  Float_t SFPtMax = 100;

  TFile *puWeightFile = new TFile("puWeights_13TeV_25ns.root");
  TH1D  *puWeightHist = (TH1D*) puWeightFile->Get("puWeights");
  Int_t puMin = 1;
  Int_t puMax = 30;

  TFile *kfactorFile  = new TFile("kfactor.root");
  TH1F  *kfactorHist  = (TH1F*) kfactorFile->FindObjectAny("pho_pt");
  Float_t minKPt = 175;
  Float_t maxKPt = 500;

  Float_t dROverlap  = 0.4;
  Float_t bCutLoose  = 0.605;
  Float_t bCutMedium = 0.89;
  Float_t bCutTight  = 0.97;

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

  std::vector<TLorentzVector*> jetVecs;
  
  for (Int_t iEntry = 0; iEntry < nentries; iEntry++) {
    
    leptonVecs.resize(0);
    photonVecs.resize(0);
    
    if (iEntry % 10000 == 0)
      std::cout << "Processing events: ... " << float(iEntry)/float(nentries)*100 << "%" << std::endl;
    
    inTree->GetEntry(iEntry);
    
    outTree->runNum    = inTree->runNum;
    outTree->lumiNum   = inTree->lumiNum;
    outTree->eventNum  = inTree->eventNum;
    outTree->rho       = inTree->rho;
    outTree->npv       = inTree->npv;
    if (outTree->npv < puMin)
      outTree->npvWeight = puWeightHist->GetBinContent(puWeightHist->FindBin(puMin));
    else if (outTree->npv > puMax)
      outTree->npvWeight = puWeightHist->GetBinContent(puWeightHist->FindBin(puMax));
    else
      outTree->npvWeight = puWeightHist->GetBinContent(puWeightHist->FindBin(outTree->npv));
    
    if (inTree->mcWeight < 0)
      outTree->mcWeight = -1;
    else
      outTree->mcWeight = 1;

    outTree->trueMet    = ((TLorentzVector*)((*(inTree->metP4))[0]))->Pt();
    outTree->trueMetPhi = ((TLorentzVector*)((*(inTree->metP4))[0]))->Phi();
    
    for (Int_t iLepton = 0; iLepton < inTree->lepP4->GetEntries(); iLepton++) {
      TLorentzVector* tempLepton = (TLorentzVector*) inTree->lepP4->At(iLepton);
      
      if ((fabs(tempLepton->Eta()) > 2.5) ||
          (fabs(tempLepton->Eta()) > 2.4 && fabs((*(inTree->lepPdgId))[iLepton]) == 13))
        continue;

      if (tempLepton->Pt() > 10. && ((*(inTree->lepSelBits))[iLepton] & 16) == 16 &&
          PassIso(tempLepton->Pt(),tempLepton->Eta(),(*(inTree->lepIso))[iLepton],(*(inTree->lepPdgId))[iLepton],kIsoLoose)) {
        outTree->n_looselep++;
        if (outTree->n_looselep == 1) {
          outTree->lep1Pt    = tempLepton->Pt();
          outTree->lep1Eta   = tempLepton->Eta();
          outTree->lep1Phi   = tempLepton->Phi();
          outTree->lep1PdgId = (*(inTree->lepPdgId))[iLepton];
          outTree->lep1IsMedium = 0;
          outTree->lep1IsTight  = 0;
          outTree->lep1RelIso = (*(inTree->lepIso))[iLepton]/outTree->lep1Pt;
          
          outTree->lep1DPhiMet  = abs(deltaPhi(outTree->lep1Phi,outTree->trueMetPhi));
        }          
        else if (outTree->n_looselep == 2) {
          outTree->lep2Pt    = tempLepton->Pt();
          outTree->lep2Eta   = tempLepton->Eta();
          outTree->lep2Phi   = tempLepton->Phi();
          outTree->lep2PdgId = (*(inTree->lepPdgId))[iLepton];
          outTree->lep2IsMedium = 0;
          outTree->lep2IsTight  = 0;
          outTree->lep2RelIso = (*(inTree->lepIso))[iLepton]/outTree->lep2Pt;
        }          
        if (tempLepton->Pt() > 20. && ((*(inTree->lepSelBits))[iLepton] & 32) == 32 &&
            PassIso(tempLepton->Pt(),tempLepton->Eta(),(*(inTree->lepIso))[iLepton],(*(inTree->lepPdgId))[iLepton],kIsoMedium)) {
          outTree->n_mediumlep +=1;

          if (outTree->n_looselep == 1)
            outTree->lep1IsMedium = 1;
          else if (outTree->n_looselep == 2)
            outTree->lep2IsMedium = 1;

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
    }
    
    if (outTree->n_looselep > 0) {

      Double_t theEta = fabs(outTree->lep1Eta);
      if (theEta > SFEtaMax)
        theEta = SFEtaMax;
      else if (theEta > SFEtaMin)
        theEta = SFEtaMin;

      Double_t thePt  = outTree->lep1Pt;
      if (thePt > SFPtMax)
        thePt = SFPtMax;
      else if (thePt > SFPtMin)
        thePt = SFPtMin;

      if (abs(outTree->lep1PdgId) == 11) {
        if (outTree->lep1IsTight)
          outTree->leptonSF = elecSFTight->GetBinContent(elecSFTight->FindBin(theEta,thePt));
        else if (outTree->lep1IsMedium)
          outTree->leptonSF = elecSFMedium->GetBinContent(elecSFMedium->FindBin(theEta,thePt));
        else
          outTree->leptonSF = elecSFLoose->GetBinContent(elecSFLoose->FindBin(theEta,thePt));
      }
      else {
        if (outTree->lep1IsTight)
          outTree->leptonSF = muonSFTight->GetBinContent(muonSFTight->FindBin(theEta,thePt));
        else if (outTree->lep1IsMedium)
          outTree->leptonSF = muonSFMedium->GetBinContent(muonSFMedium->FindBin(theEta,thePt));
        else
          outTree->leptonSF = muonSFLoose->GetBinContent(muonSFLoose->FindBin(theEta,thePt));
      }
    }
    
    if (outTree->n_looselep > 1) {

      Double_t theEta = fabs(outTree->lep2Eta);
      if (theEta > SFEtaMax)
        theEta = SFEtaMax;
      else if (theEta > SFEtaMin)
        theEta = SFEtaMin;

      Double_t thePt  = outTree->lep2Pt;
      if (thePt > SFPtMax)
        thePt = SFPtMax;
      else if (thePt > SFPtMin)
        thePt = SFPtMin;

      if (abs(outTree->lep2PdgId) == 11) {
        if (outTree->lep2IsTight)
          outTree->leptonSF = outTree->leptonSF * elecSFTight->GetBinContent(elecSFTight->FindBin(theEta,thePt));
        else if (outTree->lep2IsMedium)
          outTree->leptonSF = outTree->leptonSF * elecSFMedium->GetBinContent(elecSFMedium->FindBin(theEta,thePt));
        else
          outTree->leptonSF = outTree->leptonSF * elecSFLoose->GetBinContent(elecSFLoose->FindBin(theEta,thePt));
      }
      else {
        if (outTree->lep2IsTight)
          outTree->leptonSF = outTree->leptonSF * muonSFTight->GetBinContent(muonSFTight->FindBin(theEta,thePt));
        else if (outTree->lep2IsMedium)
          outTree->leptonSF = outTree->leptonSF * muonSFMedium->GetBinContent(muonSFMedium->FindBin(theEta,thePt));
        else
          outTree->leptonSF = outTree->leptonSF * muonSFLoose->GetBinContent(muonSFLoose->FindBin(theEta,thePt));
      }
    }

    if (outTree->n_looselep > 0) {
      vec1.SetPtEtaPhiM(outTree->lep1Pt,0.,outTree->lep1Phi,0);
      vec2.SetPtEtaPhiM(outTree->trueMet,0,outTree->trueMetPhi,0);
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
      
      vec2.SetPtEtaPhiM(outTree->trueMet,0,outTree->trueMetPhi,0);
      vec1 = vec2 + vec3;
      
      outTree->u_magZ  = vec1.Pt();
      outTree->u_phiZ  = vec1.Phi();
      outTree->u_perpZ = uPerp(outTree->u_magZ,outTree->u_phiZ,outTree->dilep_phi);
      outTree->u_paraZ = uPara(outTree->u_magZ,outTree->u_phiZ,outTree->dilep_phi);
    }
    
    for (Int_t iPhoton = 0; iPhoton < inTree->photonP4->GetEntries(); iPhoton++) {
      TLorentzVector* tempPhoton = (TLorentzVector*) inTree->photonP4->At(iPhoton);
      
      if (tempPhoton->Pt() < 15. || fabs(tempPhoton->Eta()) > 2.5)
        continue;

      Bool_t match = false;
      
      for (UInt_t iLepton = 0; iLepton < leptonVecs.size(); iLepton++) {
        if (deltaR(leptonVecs[iLepton]->Phi(),leptonVecs[iLepton]->Eta(),tempPhoton->Phi(),tempPhoton->Eta()) < dROverlap) {
          match = true;
          break;
        }
      }
      
      if (match)
        continue;
      
      outTree->n_loosepho++;
      
      if (tempPhoton->Pt() > 175 && (*(inTree->photonTightId))[iPhoton] == 1) {
        photonVecs.push_back(tempPhoton);
        outTree->n_tightpho++;
      }
      
      if (outTree->n_loosepho == 1) {
        outTree->photonPt  = tempPhoton->Pt();
        outTree->photonEta = tempPhoton->Eta();
        outTree->photonPhi = tempPhoton->Phi();
        if (outTree->n_tightpho == 1)
          outTree->photonIsTight = 1;
        else
          outTree->photonIsTight = 0;
        
        vec1.SetPtEtaPhiM(outTree->photonPt,0,outTree->photonPhi,0);
        vec2.SetPtEtaPhiM(outTree->trueMet,0,outTree->trueMetPhi,0);
        vec3 = vec1 + vec2;
        
        outTree->u_magPho  = vec3.Pt();
        outTree->u_phiPho  = vec3.Phi();
        outTree->u_perpPho = uPerp(outTree->u_magPho,outTree->u_phiPho,outTree->photonPhi);
        outTree->u_paraPho = uPara(outTree->u_magPho,outTree->u_phiPho,outTree->photonPhi);
        
        if (outTree->photonPt > minKPt && outTree->photonPt < maxKPt)
          outTree->kfactor = kfactorHist->GetBinContent(kfactorHist->FindBin(outTree->photonPt));
      }
    }
    
    if (outTree->u_magZ > 0) {
      outTree->met    = outTree->u_magZ;
      outTree->metPhi = outTree->u_phiZ;
    }
    else if (outTree->u_magW > 0) {
      outTree->met    = outTree->u_magW;
      outTree->metPhi = outTree->u_phiW;
    }
    else if (outTree->u_magPho > 0) {
      outTree->met    = outTree->u_magPho;
      outTree->metPhi = outTree->u_phiPho;
    }
    else {
      outTree->met    = outTree->trueMet;
      outTree->metPhi = outTree->trueMetPhi;
    }
    
    for (Int_t iJet = 0; iJet < inTree->jetP4->GetEntries(); iJet++) {
      TLorentzVector* tempJet = (TLorentzVector*) inTree->jetP4->At(iJet);
      
      if (fabs(tempJet->Eta()) > 2.5 || (*(inTree->jetPuId))[iJet] < -0.62)
        continue;

      if (tempJet->Pt() > 15.0 && (*(inTree->jetBdiscr))[iJet] > bCutTight)
        outTree->n_bjetsTight++;
      if (tempJet->Pt() > 15.0 && (*(inTree->jetBdiscr))[iJet] > bCutMedium)
        outTree->n_bjetsMedium++;
      if (tempJet->Pt() > 15.0 && (*(inTree->jetBdiscr))[iJet] > bCutLoose)
        outTree->n_bjetsLoose++;
      
      if (tempJet->Pt() < 30.0) 
        continue;
      
      outTree->n_jets++;
      
      if (outTree->n_jets == 1) {
        outTree->leadingjetPt  = tempJet->Pt();
        outTree->leadingjetEta = tempJet->Eta();
        outTree->leadingjetPhi = tempJet->Phi();
        outTree->leadingjetM   = tempJet->M();
        
        outTree->leadingjetBTag             = (*(inTree->jetBdiscr))[iJet];
        outTree->leadingjetPuId             = (*(inTree->jetPuId))[iJet];
        /////        outTree->leadingjetisMonoJetIdNew   = /////
        outTree->leadingjetisMonoJetId      = (*(inTree->jetMonojetId))[iJet];
        outTree->leadingjetisLooseMonoJetId = (*(inTree->jetMonojetIdLoose))[iJet];
      }
      
      Bool_t match = false;
      
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
      jetVecs.push_back(tempJet);
      
      if (outTree->n_cleanedjets == 1) {
        outTree->jet1Pt  = tempJet->Pt();
        outTree->jet1Eta = tempJet->Eta();
        outTree->jet1Phi = tempJet->Phi();
        outTree->jet1M   = tempJet->M();
        
        outTree->jet1BTag             = (*(inTree->jetBdiscr))[iJet];
        outTree->jet1PuId             = (*(inTree->jetPuId))[iJet];
        /////        outTree->jet1isMonoJetIdNew   = /////
        outTree->jet1isMonoJetId      = (*(inTree->jetMonojetId))[iJet];
        outTree->jet1isLooseMonoJetId = (*(inTree->jetMonojetIdLoose))[iJet];
        
        outTree->jet1DPhiMet     = abs(deltaPhi(outTree->jet1Phi,outTree->metPhi));
        outTree->jet1DPhiTrueMet = abs(deltaPhi(outTree->jet1Phi,outTree->trueMetPhi));
        outTree->jet1DPhiUZ      = abs(deltaPhi(outTree->jet1Phi,outTree->u_phiZ));
        outTree->jet1DPhiUW      = abs(deltaPhi(outTree->jet1Phi,outTree->u_phiW));
        outTree->jet1DPhiUPho    = abs(deltaPhi(outTree->jet1Phi,outTree->u_phiPho));
      }
      
      else if (outTree->n_cleanedjets == 2) {
        outTree->jet2Pt  = tempJet->Pt();
        outTree->jet2Eta = tempJet->Eta();
        outTree->jet2Phi = tempJet->Phi();
        outTree->jet2M   = tempJet->M();
        
        outTree->jet2BTag             = (*(inTree->jetBdiscr))[iJet];
        outTree->jet2PuId             = (*(inTree->jetPuId))[iJet];
        /////        outTree->jet2isMonoJetIdNew   = /////
        outTree->jet2isMonoJetId      = (*(inTree->jetMonojetId))[iJet];
        outTree->jet2isLooseMonoJetId = (*(inTree->jetMonojetIdLoose))[iJet];
        
        outTree->jet2DPhiMet     = abs(deltaPhi(outTree->jet2Phi,outTree->metPhi));
        outTree->jet2DPhiTrueMet = abs(deltaPhi(outTree->jet2Phi,outTree->trueMetPhi));
        outTree->jet2DPhiUZ      = abs(deltaPhi(outTree->jet2Phi,outTree->u_phiZ));
        outTree->jet2DPhiUW      = abs(deltaPhi(outTree->jet2Phi,outTree->u_phiW));
        outTree->jet2DPhiUPho    = abs(deltaPhi(outTree->jet2Phi,outTree->u_phiPho));
        
        outTree->dPhi_j1j2 = abs(deltaPhi(outTree->jet1Phi,outTree->jet2Phi));
      }
    }

    Double_t checkDPhi = 5.0;
    
    for (Int_t iLead = 0; iLead < outTree->n_cleanedjets; iLead++) {
      checkDPhi = (outTree->met > 0) ? abs(deltaPhi(jetVecs[iLead]->Phi(),outTree->metPhi)) : 5;
      if (checkDPhi < outTree->minJetMetDPhi)
        outTree->minJetMetDPhi = checkDPhi;

      checkDPhi = (outTree->trueMet > 0) ? abs(deltaPhi(jetVecs[iLead]->Phi(),outTree->trueMetPhi)) : 5;
      if (checkDPhi < outTree->minJetTrueMetDPhi)
        outTree->minJetTrueMetDPhi = checkDPhi;

      checkDPhi = (outTree->u_magZ > 0) ? abs(deltaPhi(jetVecs[iLead]->Phi(),outTree->u_phiZ)) : 5;
      if (checkDPhi < outTree->minJetUZDPhi)
        outTree->minJetUZDPhi = checkDPhi;

      checkDPhi = (outTree->u_magW > 0) ? abs(deltaPhi(jetVecs[iLead]->Phi(),outTree->u_phiW)) : 5;
      if (checkDPhi < outTree->minJetUWDPhi)
        outTree->minJetUWDPhi = checkDPhi;

      checkDPhi = (outTree->u_magPho > 0) ? abs(deltaPhi(jetVecs[iLead]->Phi(),outTree->u_phiPho)) : 5;
      if (checkDPhi < outTree->minJetUPhoDPhi)
        outTree->minJetUPhoDPhi = checkDPhi;
    }
    
    outTree->triggerFired = inTree->triggerFired;
    
    for (Int_t iTau = 0; iTau < inTree->tauP4->GetEntries(); iTau++) {
      TLorentzVector* tempTau = (TLorentzVector*) inTree->tauP4->At(iTau);

      if (tempTau->Pt() < 18. || fabs(tempTau->Eta()) > 2.3)
        continue;
      
      Bool_t match = false;
      
      for (UInt_t iLepton = 0; iLepton < leptonVecs.size(); iLepton++) {
        if (deltaR(leptonVecs[iLepton]->Phi(),leptonVecs[iLepton]->Eta(),tempTau->Phi(),tempTau->Eta()) < dROverlap) {
          match = true;
          break;
        }
      }
      
      if (!match)
        outTree->n_tau++;
    }
    
    TLorentzVector *saveGenVec;
    
    for (Int_t iGen = 0; iGen < inTree->genP4->GetEntries(); iGen++) {
      TLorentzVector* tempGen = (TLorentzVector*) inTree->genP4->At(iGen);
      Int_t checkPdgId = abs((*(inTree->genPdgId))[iGen]);
      Bool_t thisOne = false;
      if ((checkPdgId == 23 || checkPdgId == 24) ) {
        if ((abs(outTree->genBos_PdgId) == 23 || abs(outTree->genBos_PdgId) == 24) && tempGen->Pt() < outTree->genBos_pt)
          continue;
        thisOne = true;
      }
      else if (abs(outTree->genBos_PdgId) != 23 && abs(outTree->genBos_PdgId) != 24 && 
               checkPdgId == 22 && tempGen->Pt() > outTree->genBos_pt)
        thisOne = true;
      
      if (thisOne) {
        outTree->genBos_pt = tempGen->Pt();
        saveGenVec = tempGen;
        outTree->genBos_PdgId = (*(inTree->genPdgId))[iGen];
      }
    }
    
    if (outTree->genBos_PdgId != 0) {
      outTree->genBos_eta = saveGenVec->Eta();
      outTree->genBos_phi = saveGenVec->Phi();
      outTree->genBos_m   = saveGenVec->M();
      
      vec1.SetPtEtaPhiM(outTree->trueMet,0,outTree->trueMetPhi,0);
      vec2 = vec1 + *saveGenVec;
      
      outTree->u_perpGen = uPerp(vec2.Pt(),vec2.Phi(),outTree->genBos_phi);
      outTree->u_paraGen = uPara(vec2.Pt(),vec2.Phi(),outTree->genBos_phi);
    }
    
    outTree->Fill();
  }
  
  outTree->WriteToFile(outFile);
  
  outFile->Close();
  inFile->Close();
  
  kfactorFile->Close();
  puWeightFile->Close();

  muonSFFile->Close();
  elecSFFile->Close();
}
