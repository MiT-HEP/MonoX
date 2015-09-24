//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Tue Sep 15 17:09:55 2015 by ROOT version 5.34/32
// from TTree events/events
// found on file: /data/blue/dmdata/V0001/bambu2nero/common/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v3/nero_0000.root
//////////////////////////////////////////////////////////

#ifndef monojet_h
#define monojet_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>

// Header file for the classes stored in the TTree if any.
#include <TClonesArray.h>
#include <vector>

#include <TVector3.h>

#include <stdlib.h>
#include <stdio.h>

#include <TStyle.h>
#include <TF1.h>
#include <TMath.h>
#include "Math/Minimizer.h"
#include "Math/Factory.h"
#include "Math/Functor.h"

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <set>
#include <map>

#include "TreeManager.h"

using namespace std;


// Fixed size dimensions of array or collections stored in the TTree if any.

class monojet : public TSelector {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   TreeManager    *tm;
   TTree          *clonetree;
   TTree          *eventstree;

   // Declaration of leaf types
   Int_t           isRealData;
   Int_t           runNum;
   Int_t           lumiNum;
   ULong64_t       eventNum;
   Float_t         rho;
   TClonesArray    *jetP4;
   vector<float>   *jetRawPt;
   vector<float>   *jetBdiscr;
   vector<float>   *jetBdiscrLegacy;
   vector<float>   *jetPuId;
   vector<float>   *jetUnc;
   vector<float>   *jetQGL;
   vector<int>     *jetFlavour;
   vector<int>     *jetMatchedPartonPdgId;
   vector<int>     *jetMotherPdgId;
   vector<int>     *jetGrMotherPdgId;
   vector<bool>    *jetMonojetId;
   vector<bool>    *jetMonojetIdLoose;
   vector<float>   *jetQ;
   vector<float>   *jetQnoPU;
   TClonesArray    *fatjetak8P4;
   vector<float>   *fatjetak8RawPt;
   vector<int>     *fatjetak8Flavour;
   vector<float>   *fatjetak8Tau1;
   vector<float>   *fatjetak8Tau2;
   vector<float>   *fatjetak8Tau3;
   vector<float>   *fatjetak8TrimmedMass;
   vector<float>   *fatjetak8PrunedMass;
   vector<float>   *fatjetak8FilteredMass;
   vector<float>   *fatjetak8SoftdropMass;
   TClonesArray    *ak8_subjet;
   vector<int>     *ak8jet_hasSubjet;
   vector<float>   *ak8subjet_btag;
   vector<float>   *fatjetak8Hbb;
   TClonesArray    *fatjetca15P4;
   vector<float>   *fatjetca15RawPt;
   vector<int>     *fatjetca15Flavour;
   vector<float>   *fatjetca15Tau1;
   vector<float>   *fatjetca15Tau2;
   vector<float>   *fatjetca15Tau3;
   vector<float>   *fatjetca15TrimmedMass;
   vector<float>   *fatjetca15PrunedMass;
   vector<float>   *fatjetca15FilteredMass;
   vector<float>   *fatjetca15SoftdropMass;
   TClonesArray    *ca15_subjet;
   vector<int>     *ca15jet_hasSubjet;
   vector<float>   *ca15subjet_btag;
   vector<float>   *fatjetca15Hbb;
   TClonesArray    *lepP4;
   vector<int>     *lepPdgId;
   vector<float>   *lepIso;
   vector<unsigned int> *lepSelBits;
   vector<float>   *lepPfPt;
   vector<float>   *lepChIso;
   vector<float>   *lepNhIso;
   vector<float>   *lepPhoIso;
   vector<float>   *lepPuIso;
   TClonesArray    *metP4;
   vector<float>   *metPtJESUP;
   vector<float>   *metPtJESDOWN;
   TClonesArray    *metP4_GEN;
   TLorentzVector  *metNoMu;
   TLorentzVector  *pfMet_e3p0;
   TLorentzVector  *trackMet;
   Float_t         caloMet_Pt;
   Float_t         caloMet_Phi;
   Float_t         caloMet_SumEt;
   TClonesArray    *genP4;
   TClonesArray    *genjetP4;
   vector<int>     *genPdgId;
   Int_t           puTrueInt;
   Float_t         mcWeight;
   Float_t         pdfQscale;
   Float_t         pdfAlphaQED;
   Float_t         pdfAlphaQCD;
   Float_t         pdfX1;
   Float_t         pdfX2;
   Int_t           pdfId1;
   Int_t           pdfId2;
   Float_t         pdfScalePdf;
   TClonesArray    *photonP4;
   vector<float>   *photonIso;
   vector<float>   *photonSieie;
   vector<int>     *photonTightId;
   vector<int>     *photonMediumId;
   vector<int>     *photonLooseId;
   vector<float>   *photonChIso;
   vector<float>   *photonChIsoRC;
   vector<float>   *photonNhIso;
   vector<float>   *photonNhIsoRC;
   vector<float>   *photonPhoIso;
   vector<float>   *photonPhoIsoRC;
   vector<float>   *photonPuIso;
   vector<float>   *photonPuIsoRC;
   TClonesArray    *tauP4;
   vector<float>   *tauId;
   vector<int>     *tauQ;
   vector<float>   *tauM;
   vector<float>   *tauIso;
   vector<int>     *triggerFired;
   vector<float>   *triggerPrescale;
   vector<int>     *triggerLeps;
   vector<int>     *triggerJets;
   vector<int>     *triggerTaus;
   vector<int>     *triggerPhotons;
   Int_t           npv;

   // List of branches
   TBranch        *b_isRealData;   //!
   TBranch        *b_runNum;   //!
   TBranch        *b_lumiNum;   //!
   TBranch        *b_eventNum;   //!
   TBranch        *b_rho;   //!
   TBranch        *b_jetP4;   //!
   TBranch        *b_jetRawPt;   //!
   TBranch        *b_jetBdiscr;   //!
   TBranch        *b_jetBdiscrLegacy;   //!
   TBranch        *b_jetPuId;   //!
   TBranch        *b_jetUnc;   //!
   TBranch        *b_jetQGL;   //!
   TBranch        *b_jetFlavour;   //!
   TBranch        *b_jetMatchedPartonPdgId;   //!
   TBranch        *b_jetMotherPdgId;   //!
   TBranch        *b_jetGrMotherPdgId;   //!
   TBranch        *b_jetMonojetId;   //!
   TBranch        *b_jetMonojetIdLoose;   //!
   TBranch        *b_jetQ;   //!
   TBranch        *b_jetQnoPU;   //!
   TBranch        *b_fatjetak8P4;   //!
   TBranch        *b_fatjetak8RawPt;   //!
   TBranch        *b_fatjetak8Flavour;   //!
   TBranch        *b_fatjetak8Tau1;   //!
   TBranch        *b_fatjetak8Tau2;   //!
   TBranch        *b_fatjetak8Tau3;   //!
   TBranch        *b_fatjetak8TrimmedMass;   //!
   TBranch        *b_fatjetak8PrunedMass;   //!
   TBranch        *b_fatjetak8FilteredMass;   //!
   TBranch        *b_fatjetak8SoftdropMass;   //!
   TBranch        *b_ak8_subjet;   //!
   TBranch        *b_ak8jet_hasSubjet;   //!
   TBranch        *b_ak8subjet_btag;   //!
   TBranch        *b_fatjetak8Hbb;   //!
   TBranch        *b_fatjetca15P4;   //!
   TBranch        *b_fatjetca15RawPt;   //!
   TBranch        *b_fatjetca15Flavour;   //!
   TBranch        *b_fatjetca15Tau1;   //!
   TBranch        *b_fatjetca15Tau2;   //!
   TBranch        *b_fatjetca15Tau3;   //!
   TBranch        *b_fatjetca15TrimmedMass;   //!
   TBranch        *b_fatjetca15PrunedMass;   //!
   TBranch        *b_fatjetca15FilteredMass;   //!
   TBranch        *b_fatjetca15SoftdropMass;   //!
   TBranch        *b_ca15_subjet;   //!
   TBranch        *b_ca15jet_hasSubjet;   //!
   TBranch        *b_ca15subjet_btag;   //!
   TBranch        *b_fatjetca15Hbb;   //!
   TBranch        *b_lepP4;   //!
   TBranch        *b_lepPdgId;   //!
   TBranch        *b_lepIso;   //!
   TBranch        *b_lepSelBits;   //!
   TBranch        *b_lepPfPt;   //!
   TBranch        *b_lepChIso;   //!
   TBranch        *b_lepNhIso;   //!
   TBranch        *b_lepPhoIso;   //!
   TBranch        *b_lepPuIso;   //!
   TBranch        *b_metP4;   //!
   TBranch        *b_metPtJESUP;   //!
   TBranch        *b_metPtJESDOWN;   //!
   TBranch        *b_metP4_GEN;   //!
   TBranch        *b_metNoMu;   //!
   TBranch        *b_pfMet_e3p0;   //!
   TBranch        *b_trackMet;   //!
   TBranch        *b_caloMet_Pt;   //!
   TBranch        *b_caloMet_Phi;   //!
   TBranch        *b_caloMet_SumEt;   //!
   TBranch        *b_genP4;   //!
   TBranch        *b_genjetP4;   //!
   TBranch        *b_genPdgId;   //!
   TBranch        *b_puTrueInt;   //!
   TBranch        *b_mcWeight;   //!
   TBranch        *b_pdfQscale;   //!
   TBranch        *b_pdfAlphaQED;   //!
   TBranch        *b_pdfAlphaQCD;   //!
   TBranch        *b_pdfX1;   //!
   TBranch        *b_pdfX2;   //!
   TBranch        *b_pdfId1;   //!
   TBranch        *b_pdfId2;   //!
   TBranch        *b_pdfScalePdf;   //!
   TBranch        *b_photonP4;   //!
   TBranch        *b_photonIso;   //!
   TBranch        *b_photonSieie;   //!
   TBranch        *b_photonTightId;   //!
   TBranch        *b_photonMediumId;   //!
   TBranch        *b_photonLooseId;   //!
   TBranch        *b_photonChIso;   //!
   TBranch        *b_photonChIsoRC;   //!
   TBranch        *b_photonNhIso;   //!
   TBranch        *b_photonNhIsoRC;   //!
   TBranch        *b_photonPhoIso;   //!
   TBranch        *b_photonPhoIsoRC;   //!
   TBranch        *b_photonPuIso;   //!
   TBranch        *b_photonPuIsoRC;   //!
   TBranch        *b_tauP4;   //!
   TBranch        *b_tauId;   //!
   TBranch        *b_tauQ;   //!
   TBranch        *b_tauM;   //!
   TBranch        *b_tauIso;   //!
   TBranch        *b_triggerFired;   //!
   TBranch        *b_triggerPrescale;   //!
   TBranch        *b_triggerLeps;   //!
   TBranch        *b_triggerJets;   //!
   TBranch        *b_triggerTaus;   //!
   TBranch        *b_triggerPhotons;   //!
   TBranch        *b_npv;   //!

   TFile         *histoFile;
   float         unskimmedEvents;
   float         unskimmedEventsTotal;
   int           fileCount;
   TTree         *thisTree;
   TFile         *file0;
   TH1F          *h1_numOfEvents;
   TVector3      *pvPosition;
   float         weight;
   TString       suffix_{""};
   TClonesArray  *cleanJet{0};
   TClonesArray  *cleanTau{0};
   TClonesArray  *cleanLep{0};

   std::vector<int>     lepPdgId_clean;
   std::vector<float>   lepIso_clean;
   std::vector<unsigned int> lepSelBits_clean;
   std::vector<float>   lepPfPt_clean;
   std::vector<float>   lepChIso_clean;
   std::vector<float>   lepNhIso_clean;
   std::vector<float>   lepPhoIso_clean;
   std::vector<float>   lepPuIso_clean;
   std::vector<bool>  jetMonojetId_clean;
   std::vector<bool>  jetMonojetIdLoose_clean;
   std::vector<float> jetPuId_clean; 
   std::vector<float>  tauId_clean;
   std::vector<float>  tauIso_clean;

   monojet(TTree * /*tree*/ =0) : fChain(0) { }
   virtual ~monojet() { }
   virtual Int_t   Version() const { return 2; }
   virtual void    Begin(TTree *tree);
   virtual void    SlaveBegin(TTree *tree);
   virtual void    Init(TTree *tree);
   virtual Bool_t  Notify();
   virtual Bool_t  Process(Long64_t entry);
   virtual Int_t   GetEntry(Long64_t entry, Int_t getall = 0) { return fChain ? fChain->GetTree()->GetEntry(entry, getall) : 0; }
   virtual void    SetOption(const char *option) { fOption = option; }
   virtual void    SetObject(TObject *obj) { fObject = obj; }
   virtual void    SetInputList(TList *input) { fInput = input; }
   virtual TList  *GetOutputList() const { return fOutput; }
   virtual void    SlaveTerminate();
   virtual void    Terminate();

   void setSuffix(char const* suffix) { suffix_ = suffix; }
   float deltaR(TLorentzVector *a, TLorentzVector *b);
   float deltaPhi(float phi1, float phi2);
   float transverseMass(float lepPt, float lepPhi, float met,  float metPhi);

   ClassDef(monojet,0);
};

#endif

#ifdef monojet_cxx
void monojet::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set object pointer
   jetP4 = 0;
   jetRawPt = 0;
   jetBdiscr = 0;
   jetBdiscrLegacy = 0;
   jetPuId = 0;
   jetUnc = 0;
   jetQGL = 0;
   jetFlavour = 0;
   jetMatchedPartonPdgId = 0;
   jetMotherPdgId = 0;
   jetGrMotherPdgId = 0;
   jetMonojetId = 0;
   jetMonojetIdLoose = 0;
   jetQ = 0;
   jetQnoPU = 0;
   fatjetak8P4 = 0;
   fatjetak8RawPt = 0;
   fatjetak8Flavour = 0;
   fatjetak8Tau1 = 0;
   fatjetak8Tau2 = 0;
   fatjetak8Tau3 = 0;
   fatjetak8TrimmedMass = 0;
   fatjetak8PrunedMass = 0;
   fatjetak8FilteredMass = 0;
   fatjetak8SoftdropMass = 0;
   ak8_subjet = 0;
   ak8jet_hasSubjet = 0;
   ak8subjet_btag = 0;
   fatjetak8Hbb = 0;
   fatjetca15P4 = 0;
   fatjetca15RawPt = 0;
   fatjetca15Flavour = 0;
   fatjetca15Tau1 = 0;
   fatjetca15Tau2 = 0;
   fatjetca15Tau3 = 0;
   fatjetca15TrimmedMass = 0;
   fatjetca15PrunedMass = 0;
   fatjetca15FilteredMass = 0;
   fatjetca15SoftdropMass = 0;
   ca15_subjet = 0;
   ca15jet_hasSubjet = 0;
   ca15subjet_btag = 0;
   fatjetca15Hbb = 0;
   lepP4 = 0;
   lepPdgId = 0;
   lepIso = 0;
   lepSelBits = 0;
   lepPfPt = 0;
   lepChIso = 0;
   lepNhIso = 0;
   lepPhoIso = 0;
   lepPuIso = 0;
   metP4 = 0;
   metPtJESUP = 0;
   metPtJESDOWN = 0;
   metP4_GEN = 0;
   metNoMu = 0;
   pfMet_e3p0 = 0;
   trackMet = 0;
   genP4 = 0;
   genjetP4 = 0;
   genPdgId = 0;
   photonP4 = 0;
   photonIso = 0;
   photonSieie = 0;
   photonTightId = 0;
   photonMediumId = 0;
   photonLooseId = 0;
   photonChIso = 0;
   photonChIsoRC = 0;
   photonNhIso = 0;
   photonNhIsoRC = 0;
   photonPhoIso = 0;
   photonPhoIsoRC = 0;
   photonPuIso = 0;
   photonPuIsoRC = 0;
   tauP4 = 0;
   tauId = 0;
   tauQ = 0;
   tauM = 0;
   tauIso = 0;
   triggerFired = 0;
   triggerPrescale = 0;
   triggerLeps = 0;
   triggerJets = 0;
   triggerTaus = 0;
   triggerPhotons = 0;
   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("isRealData", &isRealData, &b_isRealData);
   fChain->SetBranchAddress("runNum", &runNum, &b_runNum);
   fChain->SetBranchAddress("lumiNum", &lumiNum, &b_lumiNum);
   fChain->SetBranchAddress("eventNum", &eventNum, &b_eventNum);
   fChain->SetBranchAddress("rho", &rho, &b_rho);
   fChain->SetBranchAddress("jetP4", &jetP4, &b_jetP4);
   fChain->SetBranchAddress("jetRawPt", &jetRawPt, &b_jetRawPt);
   fChain->SetBranchAddress("jetBdiscr", &jetBdiscr, &b_jetBdiscr);
   fChain->SetBranchAddress("jetBdiscrLegacy", &jetBdiscrLegacy, &b_jetBdiscrLegacy);
   fChain->SetBranchAddress("jetPuId", &jetPuId, &b_jetPuId);
   fChain->SetBranchAddress("jetUnc", &jetUnc, &b_jetUnc);
   fChain->SetBranchAddress("jetQGL", &jetQGL, &b_jetQGL);
   fChain->SetBranchAddress("jetFlavour", &jetFlavour, &b_jetFlavour);
   fChain->SetBranchAddress("jetMatchedPartonPdgId", &jetMatchedPartonPdgId, &b_jetMatchedPartonPdgId);
   fChain->SetBranchAddress("jetMotherPdgId", &jetMotherPdgId, &b_jetMotherPdgId);
   fChain->SetBranchAddress("jetGrMotherPdgId", &jetGrMotherPdgId, &b_jetGrMotherPdgId);
   fChain->SetBranchAddress("jetMonojetId", &jetMonojetId, &b_jetMonojetId);
   fChain->SetBranchAddress("jetMonojetIdLoose", &jetMonojetIdLoose, &b_jetMonojetIdLoose);
   fChain->SetBranchAddress("jetQ", &jetQ, &b_jetQ);
   fChain->SetBranchAddress("jetQnoPU", &jetQnoPU, &b_jetQnoPU);
   fChain->SetBranchAddress("fatjetak8P4", &fatjetak8P4, &b_fatjetak8P4);
   fChain->SetBranchAddress("fatjetak8RawPt", &fatjetak8RawPt, &b_fatjetak8RawPt);
   fChain->SetBranchAddress("fatjetak8Flavour", &fatjetak8Flavour, &b_fatjetak8Flavour);
   fChain->SetBranchAddress("fatjetak8Tau1", &fatjetak8Tau1, &b_fatjetak8Tau1);
   fChain->SetBranchAddress("fatjetak8Tau2", &fatjetak8Tau2, &b_fatjetak8Tau2);
   fChain->SetBranchAddress("fatjetak8Tau3", &fatjetak8Tau3, &b_fatjetak8Tau3);
   fChain->SetBranchAddress("fatjetak8TrimmedMass", &fatjetak8TrimmedMass, &b_fatjetak8TrimmedMass);
   fChain->SetBranchAddress("fatjetak8PrunedMass", &fatjetak8PrunedMass, &b_fatjetak8PrunedMass);
   fChain->SetBranchAddress("fatjetak8FilteredMass", &fatjetak8FilteredMass, &b_fatjetak8FilteredMass);
   fChain->SetBranchAddress("fatjetak8SoftdropMass", &fatjetak8SoftdropMass, &b_fatjetak8SoftdropMass);
   fChain->SetBranchAddress("ak8_subjet", &ak8_subjet, &b_ak8_subjet);
   fChain->SetBranchAddress("ak8jet_hasSubjet", &ak8jet_hasSubjet, &b_ak8jet_hasSubjet);
   fChain->SetBranchAddress("ak8subjet_btag", &ak8subjet_btag, &b_ak8subjet_btag);
   fChain->SetBranchAddress("fatjetak8Hbb", &fatjetak8Hbb, &b_fatjetak8Hbb);
   fChain->SetBranchAddress("fatjetca15P4", &fatjetca15P4, &b_fatjetca15P4);
   fChain->SetBranchAddress("fatjetca15RawPt", &fatjetca15RawPt, &b_fatjetca15RawPt);
   fChain->SetBranchAddress("fatjetca15Flavour", &fatjetca15Flavour, &b_fatjetca15Flavour);
   fChain->SetBranchAddress("fatjetca15Tau1", &fatjetca15Tau1, &b_fatjetca15Tau1);
   fChain->SetBranchAddress("fatjetca15Tau2", &fatjetca15Tau2, &b_fatjetca15Tau2);
   fChain->SetBranchAddress("fatjetca15Tau3", &fatjetca15Tau3, &b_fatjetca15Tau3);
   fChain->SetBranchAddress("fatjetca15TrimmedMass", &fatjetca15TrimmedMass, &b_fatjetca15TrimmedMass);
   fChain->SetBranchAddress("fatjetca15PrunedMass", &fatjetca15PrunedMass, &b_fatjetca15PrunedMass);
   fChain->SetBranchAddress("fatjetca15FilteredMass", &fatjetca15FilteredMass, &b_fatjetca15FilteredMass);
   fChain->SetBranchAddress("fatjetca15SoftdropMass", &fatjetca15SoftdropMass, &b_fatjetca15SoftdropMass);
   fChain->SetBranchAddress("ca15_subjet", &ca15_subjet, &b_ca15_subjet);
   fChain->SetBranchAddress("ca15jet_hasSubjet", &ca15jet_hasSubjet, &b_ca15jet_hasSubjet);
   fChain->SetBranchAddress("ca15subjet_btag", &ca15subjet_btag, &b_ca15subjet_btag);
   fChain->SetBranchAddress("fatjetca15Hbb", &fatjetca15Hbb, &b_fatjetca15Hbb);
   fChain->SetBranchAddress("lepP4", &lepP4, &b_lepP4);
   fChain->SetBranchAddress("lepPdgId", &lepPdgId, &b_lepPdgId);
   fChain->SetBranchAddress("lepIso", &lepIso, &b_lepIso);
   fChain->SetBranchAddress("lepSelBits", &lepSelBits, &b_lepSelBits);
   fChain->SetBranchAddress("lepPfPt", &lepPfPt, &b_lepPfPt);
   fChain->SetBranchAddress("lepChIso", &lepChIso, &b_lepChIso);
   fChain->SetBranchAddress("lepNhIso", &lepNhIso, &b_lepNhIso);
   fChain->SetBranchAddress("lepPhoIso", &lepPhoIso, &b_lepPhoIso);
   fChain->SetBranchAddress("lepPuIso", &lepPuIso, &b_lepPuIso);
   fChain->SetBranchAddress("metP4", &metP4, &b_metP4);
   fChain->SetBranchAddress("metPtJESUP", &metPtJESUP, &b_metPtJESUP);
   fChain->SetBranchAddress("metPtJESDOWN", &metPtJESDOWN, &b_metPtJESDOWN);
   fChain->SetBranchAddress("metP4_GEN", &metP4_GEN, &b_metP4_GEN);
   fChain->SetBranchAddress("metNoMu", &metNoMu, &b_metNoMu);
   fChain->SetBranchAddress("pfMet_e3p0", &pfMet_e3p0, &b_pfMet_e3p0);
   fChain->SetBranchAddress("trackMet", &trackMet, &b_trackMet);
   fChain->SetBranchAddress("caloMet_Pt", &caloMet_Pt, &b_caloMet_Pt);
   fChain->SetBranchAddress("caloMet_Phi", &caloMet_Phi, &b_caloMet_Phi);
   fChain->SetBranchAddress("caloMet_SumEt", &caloMet_SumEt, &b_caloMet_SumEt);
   fChain->SetBranchAddress("genP4", &genP4, &b_genP4);
   fChain->SetBranchAddress("genjetP4", &genjetP4, &b_genjetP4);
   fChain->SetBranchAddress("genPdgId", &genPdgId, &b_genPdgId);
   fChain->SetBranchAddress("puTrueInt", &puTrueInt, &b_puTrueInt);
   fChain->SetBranchAddress("mcWeight", &mcWeight, &b_mcWeight);
   fChain->SetBranchAddress("pdfQscale", &pdfQscale, &b_pdfQscale);
   fChain->SetBranchAddress("pdfAlphaQED", &pdfAlphaQED, &b_pdfAlphaQED);
   fChain->SetBranchAddress("pdfAlphaQCD", &pdfAlphaQCD, &b_pdfAlphaQCD);
   fChain->SetBranchAddress("pdfX1", &pdfX1, &b_pdfX1);
   fChain->SetBranchAddress("pdfX2", &pdfX2, &b_pdfX2);
   fChain->SetBranchAddress("pdfId1", &pdfId1, &b_pdfId1);
   fChain->SetBranchAddress("pdfId2", &pdfId2, &b_pdfId2);
   fChain->SetBranchAddress("pdfScalePdf", &pdfScalePdf, &b_pdfScalePdf);
   fChain->SetBranchAddress("photonP4", &photonP4, &b_photonP4);
   fChain->SetBranchAddress("photonIso", &photonIso, &b_photonIso);
   fChain->SetBranchAddress("photonSieie", &photonSieie, &b_photonSieie);
   fChain->SetBranchAddress("photonTightId", &photonTightId, &b_photonTightId);
   fChain->SetBranchAddress("photonMediumId", &photonMediumId, &b_photonMediumId);
   fChain->SetBranchAddress("photonLooseId", &photonLooseId, &b_photonLooseId);
   fChain->SetBranchAddress("photonChIso", &photonChIso, &b_photonChIso);
   fChain->SetBranchAddress("photonChIsoRC", &photonChIsoRC, &b_photonChIsoRC);
   fChain->SetBranchAddress("photonNhIso", &photonNhIso, &b_photonNhIso);
   fChain->SetBranchAddress("photonNhIsoRC", &photonNhIsoRC, &b_photonNhIsoRC);
   fChain->SetBranchAddress("photonPhoIso", &photonPhoIso, &b_photonPhoIso);
   fChain->SetBranchAddress("photonPhoIsoRC", &photonPhoIsoRC, &b_photonPhoIsoRC);
   fChain->SetBranchAddress("photonPuIso", &photonPuIso, &b_photonPuIso);
   fChain->SetBranchAddress("photonPuIsoRC", &photonPuIsoRC, &b_photonPuIsoRC);
   fChain->SetBranchAddress("tauP4", &tauP4, &b_tauP4);
   fChain->SetBranchAddress("tauId", &tauId, &b_tauId);
   fChain->SetBranchAddress("tauQ", &tauQ, &b_tauQ);
   fChain->SetBranchAddress("tauM", &tauM, &b_tauM);
   fChain->SetBranchAddress("tauIso", &tauIso, &b_tauIso);
   fChain->SetBranchAddress("triggerFired", &triggerFired, &b_triggerFired);
   fChain->SetBranchAddress("triggerPrescale", &triggerPrescale, &b_triggerPrescale);
   fChain->SetBranchAddress("triggerLeps", &triggerLeps, &b_triggerLeps);
   fChain->SetBranchAddress("triggerJets", &triggerJets, &b_triggerJets);
   fChain->SetBranchAddress("triggerTaus", &triggerTaus, &b_triggerTaus);
   fChain->SetBranchAddress("triggerPhotons", &triggerPhotons, &b_triggerPhotons);
   fChain->SetBranchAddress("npv", &npv, &b_npv);
}

Bool_t monojet::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

#endif // #ifdef monojet_cxx
