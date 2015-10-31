#include <iostream>
#include <vector>

#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TH1F.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TF1.h"

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

  TFile *phoCorrections = new TFile("fitTest_0.root");
  TF1 *ZmmFunc   = (TF1*) phoCorrections->Get("mu_Zmm_Data");
  TF1 *GJetsFunc = (TF1*) phoCorrections->Get("mu_gjets_Data");
  TF1 *ZmmFuncUp   = (TF1*) phoCorrections->Get("mu_up_Zmm_Data");
  TF1 *GJetsFuncUp = (TF1*) phoCorrections->Get("mu_up_gjets_Data");
  TF1 *ZmmFuncDown   = (TF1*) phoCorrections->Get("mu_down_Zmm_Data");
  TF1 *GJetsFuncDown = (TF1*) phoCorrections->Get("mu_down_gjets_Data");

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
  Float_t minKPt = 100;
  Float_t maxKPt = 1000;

  Float_t dROverlap  = 0.4;
  Float_t dRGenMatch = 0.2;
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
    
    //// Clear out the saved vectors for cleaning ////

    leptonVecs.resize(0);
    photonVecs.resize(0);
    jetVecs.resize(0);
    
    if (iEntry % 10000 == 0)
      std::cout << "Processing events: ... " << float(iEntry)/float(nentries)*100 << "%" << std::endl;
    
    inTree->GetEntry(iEntry);
    
    //// Fill some global event values ////

    outTree->runNum    = inTree->runNum;
    outTree->lumiNum   = inTree->lumiNum;
    outTree->eventNum  = inTree->eventNum;
    // outTree->rho       = inTree->rho;
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

    outTree->triggerFired = inTree->triggerFired;
    
    //// Here is the lepton filling ////

    for (Int_t iLepton = 0; iLepton < inTree->lepP4->GetEntries(); iLepton++) {
      TLorentzVector* tempLepton = (TLorentzVector*) inTree->lepP4->At(iLepton);
      
      //// Rejecting leptons with Eta cuts ////

      if ((fabs(tempLepton->Eta()) > 2.5) ||
          (fabs(tempLepton->Eta()) > 2.4 && fabs((*(inTree->lepPdgId))[iLepton]) == 13))
        continue;

      //// Filling lepton values based on loose cut ////

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

          //// We are cleaning tight leptons from jets, apparently ////

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
    
    //// Do the Scale Factor for one lepton, if there ////

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

    //// Do the Scale Factor for the second lepton, if there ////
    
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

      if (tempPhoton->Pt() < 15. || fabs(tempPhoton->Eta()) > 2.5)
        continue;

      outTree->n_loosepho++;
      
      //// We clean only tight photons ////

      if (tempPhoton->Pt() > 175 && (*(inTree->photonTightId))[iPhoton] == 1) {

        //// Check for overlap with leptons ////

        Bool_t match = false;
        
        for (UInt_t iLepton = 0; iLepton < leptonVecs.size(); iLepton++) {
          if (deltaR(leptonVecs[iLepton]->Phi(),leptonVecs[iLepton]->Eta(),tempPhoton->Phi(),tempPhoton->Eta()) < dROverlap) {
            match = true;
            break;
          }
        }
        
        if (match)
          continue;
      
        photonVecs.push_back(tempPhoton);
        outTree->n_tightpho++;
      }
      
      //// If it's the first photon, save the kinematics ////

      if (outTree->n_loosepho == 1) {
        outTree->photonPtRaw  = tempPhoton->Pt();
        outTree->photonPt     = tempPhoton->Pt() + (ZmmFunc->Eval(outTree->photonPtRaw) - GJetsFunc->Eval(outTree->photonPtRaw))/(1 - ZmmFunc->GetParameter(1));
        outTree->photonPtUp   = tempPhoton->Pt() + (ZmmFuncUp->Eval(outTree->photonPtRaw) - GJetsFuncDown->Eval(outTree->photonPtRaw))/(1 - ZmmFuncUp->GetParameter(1));
        outTree->photonPtDown = tempPhoton->Pt() + (ZmmFuncDown->Eval(outTree->photonPtRaw) - GJetsFuncUp->Eval(outTree->photonPtRaw))/(1 - ZmmFuncDown->GetParameter(1));
        outTree->photonEta    = tempPhoton->Eta();
        outTree->photonPhi    = tempPhoton->Phi();
        if (outTree->n_tightpho == 1)
          outTree->photonIsTight = 1;
        else
          outTree->photonIsTight = 0;
        
        //// If there's no leptons, define recoil quantities ////

        if (outTree->n_looselep == 0) {
          vec1.SetPtEtaPhiM(outTree->photonPtRaw,0,outTree->photonPhi,0);
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

    if (outTree->met < 0) {
      outTree->met    = outTree->trueMet;
      outTree->metPhi = outTree->trueMetPhi;
    }
    else {
      outTree->u_perp = uPerp(outTree->met,outTree->metPhi,outTree->boson_phi);
      outTree->u_para = uPara(outTree->met,outTree->metPhi,outTree->boson_phi);
    }


    //// Now we go on to clean jets ////
    
    for (Int_t iJet = 0; iJet < inTree->jetP4->GetEntries(); iJet++) {
      TLorentzVector* tempJet = (TLorentzVector*) inTree->jetP4->At(iJet);
      
      //// Ignore jets that are not in this region ////

      if (fabs(tempJet->Eta()) > 2.5 || (*(inTree->jetPuId))[iJet] < -0.62)
        continue;

      //// Count jets for b-tagging ////

      if (tempJet->Pt() > 15.0 && (*(inTree->jetBdiscr))[iJet] > bCutTight)
        outTree->n_bjetsTight++;
      if (tempJet->Pt() > 15.0 && (*(inTree->jetBdiscr))[iJet] > bCutMedium)
        outTree->n_bjetsMedium++;
      if (tempJet->Pt() > 15.0 && (*(inTree->jetBdiscr))[iJet] > bCutLoose)
        outTree->n_bjetsLoose++;
      
      //// Now apply a pt cut ////

      if (tempJet->Pt() < 30.0) 
        continue;
      
      outTree->n_jets++;

      //// Get MinDPhi with first four uncleaned jets ////
      if (outTree->n_jets < 5)
        jetVecs.push_back(tempJet);
      
      //// Store uncleaned jet for fun ////

      if (outTree->n_jets == 1) {
        outTree->leadingjetPt  = tempJet->Pt();
        outTree->leadingjetEta = tempJet->Eta();
        outTree->leadingjetPhi = tempJet->Phi();
        outTree->leadingjetM   = tempJet->M();
        
        // outTree->leadingjetisMonoJetIdNew   = ????
        outTree->leadingjetisMonoJetId      = (*(inTree->jetMonojetId))[iJet];
      }

      //// Now do cleaning ////
      
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

      if (outTree->n_cleanedjets == 1) {
        outTree->jet1Pt  = tempJet->Pt();
        outTree->jet1Eta = tempJet->Eta();
        outTree->jet1Phi = tempJet->Phi();
        outTree->jet1M   = tempJet->M();
        
        outTree->jet1BTag             = (*(inTree->jetBdiscr))[iJet];
        outTree->jet1PuId             = (*(inTree->jetPuId))[iJet];
        // outTree->jet1isMonoJetIdNew   = ????
        outTree->jet1isMonoJetId      = (*(inTree->jetMonojetId))[iJet];
        outTree->jet1isLooseMonoJetId = (*(inTree->jetMonojetIdLoose))[iJet];
        
        outTree->jet1DPhiMet     = abs(deltaPhi(outTree->jet1Phi,outTree->metPhi));
        outTree->jet1DPhiTrueMet = abs(deltaPhi(outTree->jet1Phi,outTree->trueMetPhi));
      }
      
      else if (outTree->n_cleanedjets == 2) {
        outTree->jet2Pt  = tempJet->Pt();
        outTree->jet2Eta = tempJet->Eta();
        outTree->jet2Phi = tempJet->Phi();
        outTree->jet2M   = tempJet->M();
        
        outTree->jet2BTag             = (*(inTree->jetBdiscr))[iJet];
        outTree->jet2PuId             = (*(inTree->jetPuId))[iJet];
        // outTree->jet2isMonoJetIdNew   = ????
        outTree->jet2isMonoJetId      = (*(inTree->jetMonojetId))[iJet];
        outTree->jet2isLooseMonoJetId = (*(inTree->jetMonojetIdLoose))[iJet];
        
        outTree->jet2DPhiMet     = abs(deltaPhi(outTree->jet2Phi,outTree->metPhi));
        outTree->jet2DPhiTrueMet = abs(deltaPhi(outTree->jet2Phi,outTree->trueMetPhi));
        
        outTree->dPhi_j1j2 = abs(deltaPhi(outTree->jet1Phi,outTree->jet2Phi));
      }
    }

    //// Now find the minimum Delta Phi from MET ////

    Double_t checkDPhi = 5.0;
    
    for (UInt_t iLead = 0; iLead < jetVecs.size(); iLead++) {
      checkDPhi = abs(deltaPhi(jetVecs[iLead]->Phi(),outTree->metPhi));
      if (checkDPhi < outTree->minJetMetDPhi)
        outTree->minJetMetDPhi = checkDPhi;

      checkDPhi = abs(deltaPhi(jetVecs[iLead]->Phi(),outTree->trueMetPhi));
      if (checkDPhi < outTree->minJetTrueMetDPhi)
        outTree->minJetTrueMetDPhi = checkDPhi;
    }

    //// Now check number of non-overlapping taus ////

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
    
    //// Now look for generator information ////

    if (inTree->metP4_GEN->GetEntries() > 0) {
      TLorentzVector *genMet = (TLorentzVector*) inTree->metP4_GEN->At(0);
      outTree->genMet = genMet->Pt();
      outTree->genMetPhi = genMet->Phi();
      
      TLorentzVector saveGenVec;
      
      saveGenVec.SetPtEtaPhiM(0,0,0,0);
      
      Bool_t isFound = false;
      
      for (Int_t iGen = 0; iGen < inTree->genP4->GetEntries(); iGen++) {
        TLorentzVector* tempGen = (TLorentzVector*) inTree->genP4->At(iGen);
        Int_t checkPdgId = abs((*(inTree->genPdgId))[iGen]);
        
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
            if (tempGen->Pt() > outTree->genBos_pt) {
              outTree->genBos_pt = tempGen->Pt();
              saveGenVec = *tempGen;
              outTree->genBos_PdgId = 22;
            }        
          }
        }
        //// Look for Z to nunu here or perhaps a W with missed lepton ////
        else if (checkPdgId == 23 || checkPdgId == 24) {
          if ((tempGen->Pt() > outTree->genBos_pt && !(checkPdgId == 24 && outTree->genBos_PdgId == 23)) || (abs(outTree->genBos_PdgId) == 24 && checkPdgId == 23)) {
            saveGenVec = *tempGen;
            outTree->genBos_PdgId = abs((*(inTree->genPdgId))[iGen]);
          }
        }
      }
      
      if (outTree->genBos_PdgId != 0) {
        outTree->genBos_pt  = saveGenVec.Pt();
        outTree->genBos_phi = saveGenVec.Phi();
        
        outTree->u_perpGen = uPerp(outTree->met,outTree->metPhi,outTree->genBos_phi);
        outTree->u_paraGen = uPara(outTree->met,outTree->metPhi,outTree->genBos_phi);
      }
      
      if (outTree->genBos_PdgId == 22 && outTree->genBos_pt > minKPt && outTree->genBos_pt < maxKPt)
        outTree->kfactor = kfactorHist->GetBinContent(kfactorHist->FindBin(outTree->genBos_pt));
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
