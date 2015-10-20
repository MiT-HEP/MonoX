#include "TFile.h"
#include "TTree.h"
#include "TBranch.h"
#include "TF1.h"

#include "MergedTree.h"
#include "MonoJetReader.h"

void mergeData() {

  float metSwitch = 225.;

  TFile *corrections = new TFile("fitTest_0.root");
  TF1 *ZmmFunc   = (TF1*) corrections->Get("mu_Zmm_Data");
  TF1 *GJetsFunc = (TF1*) corrections->Get("mu_gjets_Data");

  TFile *binned = new TFile("fitResults.root");
  TF1 *ZmmBin   = (TF1*) binned->Get("fcn_mu_u1_Data_Zmm");
  TF1 *GJetsBin = (TF1*) binned->Get("fcn_mu_u1_Data_gjets");

  TFile *muonFile = new TFile("/Users/dabercro/GradSchool/Winter15/GoodRunsV3/monojet_SingleMuon.root");
  TTree *muonTree = (TTree*) muonFile->Get("events");
  MonoJetReader *muonReader = new MonoJetReader(muonTree);

  TFile *gjetFile = new TFile("/Users/dabercro/GradSchool/Winter15/GoodRunsV3/monojet_SinglePhoton.root");
  TTree *gjetTree = (TTree*) gjetFile->Get("events");
  MonoJetReader *gjetReader = new MonoJetReader(gjetTree);

  TFile *mergedFile = new TFile("mergedData.root","RECREATE");
  MergedTree *mergedTree = new MergedTree("events");

  Int_t nentries = 0;

  nentries = gjetTree->GetEntries();

  for (Int_t iEntry = 0; iEntry != nentries; ++iEntry) {

    if (iEntry % 100000 == 0)
      std::cout << "Processing Single Photon: " << float(iEntry) * 100/float(nentries) << "%" << std::endl;

    gjetReader->GetEntry(iEntry);

    mergedTree->runNum = gjetReader->runNum;
    mergedTree->lumiNum = gjetReader->lumiNum;
    mergedTree->eventNum = gjetReader->eventNum;
    mergedTree->rho = gjetReader->rho;
    mergedTree->npv = gjetReader->npv;
    mergedTree->jet1Pt = gjetReader->jet1Pt;
    mergedTree->jet1Eta = gjetReader->jet1Eta;
    mergedTree->jet1Phi = gjetReader->jet1Phi;
    mergedTree->jet1M = gjetReader->jet1M;
    mergedTree->jet1BTag = gjetReader->jet1BTag;
    mergedTree->jet1PuId = gjetReader->jet1PuId;
    mergedTree->jet1isMonoJetIdNew = gjetReader->jet1isMonoJetIdNew;
    mergedTree->jet1isMonoJetId = gjetReader->jet1isMonoJetId;
    mergedTree->jet1isLooseMonoJetId = gjetReader->jet1isLooseMonoJetId;
    mergedTree->jet1DPhiMet = gjetReader->jet1DPhiUPho;
    mergedTree->jet1DPhiTrueMet = gjetReader->jet1DPhiTrueMet;
    mergedTree->jet2Pt = gjetReader->jet2Pt;
    mergedTree->jet2Eta = gjetReader->jet2Eta;
    mergedTree->jet2Phi = gjetReader->jet2Phi;
    mergedTree->jet2M = gjetReader->jet2M;
    mergedTree->jet2BTag = gjetReader->jet2BTag;
    mergedTree->jet2PuId = gjetReader->jet2PuId;
    mergedTree->jet2isMonoJetIdNew = gjetReader->jet2isMonoJetIdNew;
    mergedTree->jet2isMonoJetId = gjetReader->jet2isMonoJetId;
    mergedTree->jet2isLooseMonoJetId = gjetReader->jet2isLooseMonoJetId;
    mergedTree->jet2DPhiMet = gjetReader->jet2DPhiUPho;
    mergedTree->jet2DPhiTrueMet = gjetReader->jet2DPhiTrueMet;
    mergedTree->n_cleanedjets = gjetReader->n_cleanedjets;
    mergedTree->n_jets = gjetReader->n_jets;
    mergedTree->n_bjetsLoose = gjetReader->n_bjetsLoose;
    mergedTree->n_bjetsMedium = gjetReader->n_bjetsMedium;
    mergedTree->n_bjetsTight = gjetReader->n_bjetsTight;
    mergedTree->dPhi_j1j2 = gjetReader->dPhi_j1j2;
    mergedTree->minJetMetDPhi = gjetReader->minJetUPhoDPhi;
    mergedTree->minJetTrueMetDPhi = gjetReader->minJetTrueMetDPhi;
    mergedTree->n_tightlep = gjetReader->n_tightlep;
    mergedTree->n_mediumlep = gjetReader->n_mediumlep;
    mergedTree->n_looselep = gjetReader->n_looselep;
    mergedTree->photonPtRaw = gjetReader->photonPt;

    mergedTree->photonPt = gjetReader->photonPt + (ZmmFunc->Eval(gjetReader->photonPt) - GJetsFunc->Eval(gjetReader->photonPt))/(1 - ZmmFunc->GetParameter(1));
    mergedTree->photonPtCheck = gjetReader->photonPt + (ZmmBin->Eval(gjetReader->photonPt) - GJetsBin->Eval(gjetReader->photonPt))/(1 - ZmmBin->GetParameter(1));

    mergedTree->photonEta = gjetReader->photonEta;
    mergedTree->photonPhi = gjetReader->photonPhi;
    mergedTree->photonIsTight = gjetReader->photonIsTight;
    mergedTree->n_tightpho = gjetReader->n_tightpho;
    mergedTree->n_loosepho = gjetReader->n_loosepho;
    mergedTree->n_tau = gjetReader->n_tau;
    mergedTree->trueMet = gjetReader->trueMet;
    mergedTree->trueMetPhi = gjetReader->trueMetPhi;
    mergedTree->u_perp = gjetReader->u_perpPho;
    mergedTree->u_para = gjetReader->u_paraPho;

    mergedTree->met = gjetReader->u_magPho;
    mergedTree->metPhi = gjetReader->u_phiPho;

    mergedTree->boson_pt = gjetReader->photonPt;
    mergedTree->boson_phi = gjetReader->photonPhi;
    mergedTree->triggerFired = gjetReader->triggerFired;

    if (mergedTree->photonPt > metSwitch)
      mergedTree->correctEvent = true;
    else
      mergedTree->correctEvent = false;

    mergedTree->Fill();

  }

  nentries = muonTree->GetEntries();

  for (Int_t iEntry = 0; iEntry != nentries; ++iEntry) {

    if (iEntry % 100000 == 0)
      std::cout << "Processing Single Muon: " << float(iEntry) * 100/float(nentries) << "%" << std::endl;

    muonReader->GetEntry(iEntry);

    mergedTree->runNum = muonReader->runNum;
    mergedTree->lumiNum = muonReader->lumiNum;
    mergedTree->eventNum = muonReader->eventNum;
    mergedTree->rho = muonReader->rho;
    mergedTree->npv = muonReader->npv;
    mergedTree->jet1Pt = muonReader->jet1Pt;
    mergedTree->jet1Eta = muonReader->jet1Eta;
    mergedTree->jet1Phi = muonReader->jet1Phi;
    mergedTree->jet1M = muonReader->jet1M;
    mergedTree->jet1BTag = muonReader->jet1BTag;
    mergedTree->jet1PuId = muonReader->jet1PuId;
    mergedTree->jet1isMonoJetIdNew = muonReader->jet1isMonoJetIdNew;
    mergedTree->jet1isMonoJetId = muonReader->jet1isMonoJetId;
    mergedTree->jet1isLooseMonoJetId = muonReader->jet1isLooseMonoJetId;
    mergedTree->jet1DPhiMet = muonReader->jet1DPhiUZ;
    mergedTree->jet1DPhiTrueMet = muonReader->jet1DPhiTrueMet;
    mergedTree->jet2Pt = muonReader->jet2Pt;
    mergedTree->jet2Eta = muonReader->jet2Eta;
    mergedTree->jet2Phi = muonReader->jet2Phi;
    mergedTree->jet2M = muonReader->jet2M;
    mergedTree->jet2BTag = muonReader->jet2BTag;
    mergedTree->jet2PuId = muonReader->jet2PuId;
    mergedTree->jet2isMonoJetIdNew = muonReader->jet2isMonoJetIdNew;
    mergedTree->jet2isMonoJetId = muonReader->jet2isMonoJetId;
    mergedTree->jet2isLooseMonoJetId = muonReader->jet2isLooseMonoJetId;
    mergedTree->jet2DPhiMet = muonReader->jet2DPhiUZ;
    mergedTree->jet2DPhiTrueMet = muonReader->jet2DPhiTrueMet;
    mergedTree->n_cleanedjets = muonReader->n_cleanedjets;
    mergedTree->n_jets = muonReader->n_jets;
    mergedTree->n_bjetsLoose = muonReader->n_bjetsLoose;
    mergedTree->n_bjetsMedium = muonReader->n_bjetsMedium;
    mergedTree->n_bjetsTight = muonReader->n_bjetsTight;
    mergedTree->dPhi_j1j2 = muonReader->dPhi_j1j2;
    mergedTree->minJetMetDPhi = muonReader->minJetUZDPhi;
    mergedTree->minJetTrueMetDPhi = muonReader->minJetTrueMetDPhi;
    mergedTree->lep1Pt = muonReader->lep1Pt;
    mergedTree->lep1Eta = muonReader->lep1Eta;
    mergedTree->lep1Phi = muonReader->lep1Phi;
    mergedTree->lep1PdgId = muonReader->lep1PdgId;
    mergedTree->lep1IsTight = muonReader->lep1IsTight;
    mergedTree->lep1IsMedium = muonReader->lep1IsMedium;
    mergedTree->lep1DPhiMet = muonReader->lep1DPhiMet;
    mergedTree->lep1RelIso = muonReader->lep1RelIso;
    mergedTree->lep2Pt = muonReader->lep2Pt;
    mergedTree->lep2Eta = muonReader->lep2Eta;
    mergedTree->lep2Phi = muonReader->lep2Phi;
    mergedTree->lep2PdgId = muonReader->lep2PdgId;
    mergedTree->lep2IsTight = muonReader->lep2IsTight;
    mergedTree->lep2IsMedium = muonReader->lep2IsMedium;
    mergedTree->lep2RelIso = muonReader->lep2RelIso;
    mergedTree->dilep_pt = muonReader->dilep_pt;
    mergedTree->dilep_eta = muonReader->dilep_eta;
    mergedTree->dilep_phi = muonReader->dilep_phi;
    mergedTree->dilep_m = muonReader->dilep_m;
    mergedTree->n_tightlep = muonReader->n_tightlep;
    mergedTree->n_mediumlep = muonReader->n_mediumlep;
    mergedTree->n_looselep = muonReader->n_looselep;
    mergedTree->n_tightpho = muonReader->n_tightpho;
    mergedTree->n_loosepho = muonReader->n_loosepho;
    mergedTree->n_tau = muonReader->n_tau;
    mergedTree->met = muonReader->u_magZ;
    mergedTree->metPhi = muonReader->u_phiZ;
    mergedTree->trueMet = muonReader->trueMet;
    mergedTree->trueMetPhi = muonReader->trueMetPhi;
    mergedTree->u_perp = muonReader->u_perpZ;
    mergedTree->u_para = muonReader->u_paraZ;
    mergedTree->boson_pt = gjetReader->dilep_pt;
    mergedTree->boson_phi = gjetReader->dilep_phi;
    mergedTree->triggerFired = muonReader->triggerFired;

    if (mergedTree->dilep_pt <= metSwitch)
      mergedTree->correctEvent = true;
    else
      mergedTree->correctEvent = false;

    mergedTree->Fill();
  }

  mergedTree->WriteToFile(mergedFile);

  mergedFile->Close();
  gjetFile->Close();
  muonFile->Close();
  binned->Close();
  corrections->Close();
}
