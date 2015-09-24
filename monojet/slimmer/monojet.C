#define monojet_cxx

#include "monojet.h"
#include <TH2.h>
#include <TStyle.h>
#include <TLorentzVector.h>
#include <vector>

using namespace std;

float dR_cut = 0.4;

void monojet::Begin(TTree *tree)
{
  // The Begin() function is called at the start of the query.
  // When running with PROOF Begin() is only called on the client.
  // The tree argument is deprecated (on PROOF 0 is passed).
  
  TString option = GetOption();
  
  // Get total weight from all
  TFile   *inFile         = tree->GetCurrentFile();
  
  TString outputName("monojet");
  if (suffix_.Length() != 0)
    outputName += "_" + suffix_;
  outputName += ".root";
  histoFile = new TFile(outputName,"RECREATE");
  histoFile->cd();
  
  tree->SetBranchStatus("*",0);
  tree->SetBranchStatus("isRealData",1);
  tree->SetBranchStatus("runNum",1);
  tree->SetBranchStatus("lumiNum",1);
  tree->SetBranchStatus("eventNum",1);
  tree->SetBranchStatus("rho",1);
  tree->SetBranchStatus("jetP4",1);
  tree->SetBranchStatus("jetPuId",1);
  tree->SetBranchStatus("jetMonojetId",1);
  tree->SetBranchStatus("jetMonojetIdLoose",1);
  tree->SetBranchStatus("lep*",1);
  tree->SetBranchStatus("metP4",1);
  tree->SetBranchStatus("genP4",1);
  tree->SetBranchStatus("photon*",1);
  tree->SetBranchStatus("tauP4",1);
  tree->SetBranchStatus("tauId",1);
  tree->SetBranchStatus("tauIso",1);
  tree->SetBranchStatus("mcWeight",1);   
  tree->SetBranchStatus("triggerFired",1);
  
  eventstree = tree->CloneTree(0);
  
  //Setting up new tree
  tm = new TreeManager("type", "Monojet signal Tree" /*, histoFile*/);
  
  tm->AddVar("run","int");
  tm->AddVar("lumi","int");
  tm->AddVar("event","int");
  tm->AddVar("event_type","int");
  tm->AddVar("upar","float");
  tm->AddVar("uperp","float");
  tm->AddVar("mt","float");
  tm->AddVar("n_tightlep","int");
  tm->AddVar("n_looselep","int");
  //tm->AddVar("weight","int");
  
  tm->InitVars();
  
}

void monojet::SlaveBegin(TTree * /*tree*/)
{
  // The SlaveBegin() function is called after the Begin() function.
  // When running with PROOF SlaveBegin() is called on each slave server.
  // The tree argument is deprecated (on PROOF 0 is passed).
  
  TString option = GetOption();
  
}

Bool_t monojet::Process(Long64_t entry)
{
  GetEntry(entry);
  
  if( entry % 100000 == 0 ) cout << "Processing event number: " << entry << endl;
  //cout << "Processing event number: " << entry << endl;
  
  // To make the processing fast, apply a very looose selection
  if (jetP4->GetEntries() < 1) return kTRUE;
  
  //this is the type tree
  tm->SetValue("run",runNum);
  tm->SetValue("event",eventNum);
  tm->SetValue("lumi",lumiNum);    
  
  float dR = 0.;
  
  cleaningVecs.clear();

  lepPdgId_clean.clear();
  lepIso_clean.clear();
  lepSelBits_clean.clear();
  lepPfPt_clean.clear();
  lepChIso_clean.clear();
  lepNhIso_clean.clear();
  lepPhoIso_clean.clear();
  lepPuIso_clean.clear();

  jetMonojetId_clean.clear();
  jetMonojetIdLoose_clean.clear();
  jetPuId_clean.clear();
  
  tauId_clean.clear();
  tauIso_clean.clear();

  cleanLep = new TClonesArray("TLorentzVector",20);
  cleanJet = new TClonesArray("TLorentzVector",20);
  cleanTau = new TClonesArray("TLorentzVector",20);
  
  cleanLep->Clear();
  cleanJet->Clear();
  cleanTau->Clear();
  
  int n_tightlep = 0;
  int n_looselep = 0;
  
  int lepIndex1 = -1;
  int lepIndex2 = -1;

  // ********* Leptons ********** //
  for(int lepton = 0; lepton < lepP4->GetEntries(); lepton++){
    TLorentzVector* Lepton = (TLorentzVector*) lepP4->At(lepton);
    
    // check if this is a tight lep, and check the overlap
    if (Lepton->Pt() > 10. && ((*lepSelBits)[lepton] & 8) == 8) {
      n_looselep++;

      new ( (*cleanLep)[cleanLep->GetEntriesFast()]) TLorentzVector(Lepton->Px(), Lepton->Py(), Lepton->Pz(), Lepton->Energy());
      lepPdgId_clean.push_back((*lepPdgId)[lepton]);
      lepIso_clean.push_back((*lepIso)[lepton]);
      lepSelBits_clean.push_back((*lepSelBits)[lepton]);
      lepPfPt_clean.push_back((*lepPfPt)[lepton]);
      lepChIso_clean.push_back((*lepChIso)[lepton]);
      lepNhIso_clean.push_back((*lepNhIso)[lepton]);
      lepPhoIso_clean.push_back((*lepPhoIso)[lepton]);
      lepPuIso_clean.push_back((*lepPuIso)[lepton]);

      if (lepIndex1 < 0)
        lepIndex1 = lepton;
      else if (lepIndex2 < 0)
        lepIndex2 = lepton;
    }
    if (Lepton->Pt() > 20. && ((*lepSelBits)[lepton] & 32) == 32){
      n_tightlep +=1;
      cleaningVecs.push_back(Lepton);
    }
  }//lepton loop

  // ********* Leptons ********** //
  for (Int_t iPhoton = 0; iPhoton < photonP4->GetEntries(); iPhoton++) {
    TLorentzVector* tempPhoton = (TLorentzVector*) photonP4->At(iPhoton);

    if (tempPhoton->Pt() > 175 && (*photonTightId)[iPhoton] == 1)
      cleaningVecs.push_back(tempPhoton);
  }

  for (UInt_t iVec = 0; iVec < cleaningVecs.size(); iVec++) {

    TLorentzVector *theVec = cleaningVecs[iVec];

    //check overlap with jets
    for(int j = 0; j < jetP4->GetEntries(); j++){
      TLorentzVector* Jet = (TLorentzVector*) jetP4->At(j);
      dR = deltaR(theVec,Jet);
      if (dR > dR_cut) {
        new ( (*cleanJet)[cleanJet->GetEntriesFast()]) TLorentzVector(Jet->Px(), Jet->Py(), Jet->Pz(), Jet->Energy());
        jetMonojetId_clean.push_back((*jetMonojetId)[j]);
        jetMonojetIdLoose_clean.push_back((*jetMonojetIdLoose)[j]);
        jetPuId_clean.push_back((*jetPuId)[j]);
      }
    }
    //check overlap with taus
    for(int tau = 0; tau < tauP4->GetEntries(); tau++){
      TLorentzVector* Tau = (TLorentzVector*) tauP4->At(tau);
      dR = deltaR(theVec,Tau);
      if (dR > dR_cut) new ( (*cleanTau)[cleanTau->GetEntriesFast()]) TLorentzVector(Tau->Px(), Tau->Py(), Tau->Pz(), Tau->Energy());
      tauId_clean.push_back((*tauId)[tau]);
      tauIso_clean.push_back((*tauIso)[tau]);
    } // tau overlap
  }

  
  tm->SetValue("n_tightlep",n_tightlep);
  tm->SetValue("n_looselep",n_looselep);
  
  TLorentzVector fakeMET;
  
  // Z Selection
  TLorentzVector Z;
  if(n_looselep == 2 && n_tightlep > 0){
    if (((*lepPdgId)[lepIndex1]+(*lepPdgId)[lepIndex2])==0 ){
      Z = *((TLorentzVector*)((*lepP4)[lepIndex1])) + *((TLorentzVector*)((*lepP4)[lepIndex2])); 
      fakeMET = *((TLorentzVector*)((*metP4)[0])) + Z;
    }
  }    
  
  float MT = 0.0;
  //// W Selection                                                                         
  if(n_tightlep == 1 && n_looselep == 1){
    fakeMET = *((TLorentzVector*)((*metP4)[0])) + *((TLorentzVector*)((*lepP4)[lepIndex1])) ;
    MT = transverseMass( ((TLorentzVector*)((*lepP4)[lepIndex1]))->Pt(), ((TLorentzVector*)((*lepP4)[lepIndex1]))->Phi(), 
                         ((TLorentzVector*)((*metP4)[0]))->Pt(), ((TLorentzVector*)((*metP4)[0]))->Phi());
  }
  
  // Gamma Selection
  if(n_looselep == 0 && photonP4->GetEntries() == 1 && (*photonTightId)[0] == 1)
    fakeMET = *((TLorentzVector*)((*metP4)[0])) + *((TLorentzVector*)((*photonP4)[0]));
  
  tm->SetValue("mt",MT);    
  
  // ********* Jets ********** //
  for(int jet = 0; jet < jetP4->GetEntries(); jet++){
    TLorentzVector* Jet = (TLorentzVector*) jetP4->At(jet);
    //cout << (*jetMonojetId)[0] <<endl;
    //cout << Jet->Pt()<<endl;
  }
  
  // ********* Met ********** //
  // Here try to save all possible met variables
  // and the recoil vectors (for Z and Photon)
  
  TLorentzVector Recoil(-9999.,-9999.,-9999.,-9999);
  float uPar = -9999. ; float uPerp = -9999.;
  
  if(Z.Pt() > 0){
    Recoil = *((TLorentzVector*)((*metP4)[0])) + Z;
    Recoil.RotateZ(TMath::Pi());
    Recoil.RotateZ(-Z.Phi());
    if (Z.Phi() > TMath::Pi())  uPar = Recoil.Px() - Z.Pt() ;
    else uPar = Recoil.Px() + Z.Pt();
    uPerp = Recoil.Py(); 
  }
  
  tm->SetValue("uperp",uPerp);    
  tm->SetValue("upar",uPar);    
  
  // Decide on the type of the event and fill the
  // type tree
  
  int type_event = -1;
  
  // forcing all regions to be orthogonal wrt to each other
  if (n_looselep == 0 && photonP4->GetEntries() == 0 && ((TLorentzVector*)((*metP4)[0]))->Pt() > 100. && jetP4->GetEntries() > 0) 
    type_event=0;
  else if (n_looselep == 1 && n_looselep == 1 && photonP4->GetEntries() == 0) 
    type_event=1;
  else if (n_looselep == 2 && n_tightlep > 0 && photonP4->GetEntries() == 0) 
    type_event=2;
  else if (n_looselep == 0 && photonP4->GetEntries() == 1 && (*photonTightId)[0] == 1) 
    type_event = 3;
  
  // if (  lepP4->GetEntriesFast() == 2 && type_event!=2 ) std::cout << "WTF??" << std::endl;
  tm->SetValue("event_type",type_event);
  
  // Now replace all the needed collections based
  // on the type
  
  if (type_event > 0) {
    jetP4 = cleanJet;
    *jetMonojetId = jetMonojetId_clean;
    *jetMonojetIdLoose = jetMonojetIdLoose_clean;
    *jetPuId = jetPuId_clean;
    *(TLorentzVector*)((*metP4)[0]) = fakeMET;
    tauP4 = cleanTau;
    *tauId = tauId_clean;
    *tauIso = tauIso_clean;
  }

  *lepPdgId = lepPdgId_clean;
  *lepIso = lepIso_clean;
  *lepSelBits = lepSelBits_clean;
  *lepPfPt = lepPfPt_clean;
  *lepChIso = lepChIso_clean;
  *lepNhIso = lepNhIso_clean;
  *lepPhoIso = lepPhoIso_clean;
  *lepPuIso = lepPuIso_clean;

  lepP4 = cleanLep;
  
  // final skim
  if (((TLorentzVector*)((*metP4)[0]))->Pt() < 100. || type_event == -1) 
    return kTRUE;
  
  //re-write the mc weight content to be +1 or -1
  if(mcWeight < 0)
    mcWeight = -1.0;
  if(mcWeight > 0)
    mcWeight =  1.0;
  
  // and fill both trees;
  tm->TreeFill();
  eventstree->Fill();
  
  return kTRUE;
}

void monojet::SlaveTerminate()
{
  // The SlaveTerminate() function is called after all entries or objects
  // have been processed. When running with PROOF SlaveTerminate() is called
  // on each slave server.
}

void monojet::Terminate()
{
  // The Terminate() function is the last function to be called during
  // a query. It always runs on the client, it can be used to present
  // the results graphically or save the results to file.
  
  histoFile->cd();
  tm->TreeWrite();
  eventstree->Write();
  
  histoFile->SaveSelf(kTRUE);
  histoFile->Close();
}

float monojet::deltaPhi(float phi1, float phi2){
  float PHI = TMath::Abs(phi1-phi2);
  if (PHI <= 3.14159265)
    return PHI;
  else
    return 2*3.14159265-PHI;
}

float monojet::deltaR(TLorentzVector *a, TLorentzVector *b){
  return TMath::Sqrt( (a->Eta() - b->Eta()) * (a->Eta() - b->Eta()) + ( deltaPhi(a->Phi(),b->Phi()) ) * ( deltaPhi(a->Phi(),b->Phi()) ) );
}

float monojet::transverseMass(float lepPt, float lepPhi, float met,  float metPhi) {
  double cosDPhi = cos(deltaPhi(lepPhi,metPhi));
  return sqrt(2*lepPt*met*(1-cosDPhi));
}

