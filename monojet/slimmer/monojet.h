//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Sat Aug 15 11:47:51 2015 by ROOT version 5.34/32
// from TTree events/events
// found on file: nero_dy.root
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
    
    TreeManager* tm;

    TTree *clonetree;
    TTree *eventstree;
    
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
   TClonesArray    *fatjetP4;
   vector<float>   *fatjetRawPt;
   vector<int>     *fatjetFlavour;
   vector<float>   *fatjetTau1;
   vector<float>   *fatjetTau2;
   vector<float>   *fatjetTau3;
   vector<float>   *fatjetTrimmedMass;
   vector<float>   *fatjetPrunedMass;
   vector<float>   *fatjetFilteredMass;
   vector<float>   *fatjetSoftdropMass;
   TClonesArray    *ak8_subjet;
   vector<int>     *ak8jet_hasSubjet;
   vector<float>   *ak8subjet_btag;
   vector<float>   *fatjetHbb;
   TClonesArray    *lepP4;
   vector<int>     *lepPdgId;
   vector<float>   *lepIso;
   vector<unsigned> *lepSelBits;
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
   TLorentzVector  *metChargedHadron;
   TLorentzVector  *metNeutralHadron;
   TLorentzVector  *metNeutralEM;
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
   TBranch        *b_fatjetP4;   //!
   TBranch        *b_fatjetRawPt;   //!
   TBranch        *b_fatjetFlavour;   //!
   TBranch        *b_fatjetTau1;   //!
   TBranch        *b_fatjetTau2;   //!
   TBranch        *b_fatjetTau3;   //!
   TBranch        *b_fatjetTrimmedMass;   //!
   TBranch        *b_fatjetPrunedMass;   //!
   TBranch        *b_fatjetFilteredMass;   //!
   TBranch        *b_fatjetSoftdropMass;   //!
   TBranch        *b_ak8_subjet;   //!
   TBranch        *b_ak8jet_hasSubjet;   //!
   TBranch        *b_ak8subjet_btag;   //!
   TBranch        *b_fatjetHbb;   //!
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
   TBranch        *b_metChargedHadron;   //!
   TBranch        *b_metNeutralHadron;   //!
   TBranch        *b_metNeutralEM;   //!
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

    TFile        *histoFile;
    float        unskimmedEvents;
    float        unskimmedEventsTotal;
    int          fileCount;
    TTree        *thisTree;
    TFile        *file0;
    TH1F         *h1_numOfEvents;
    TVector3     *pvPosition;
    float        weight;
    
    
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

 private:
   TString suffix_{""};
   TClonesArray* cleanJet{0};
   TClonesArray* cleanTau{0};

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
   fatjetP4 = 0;
   fatjetRawPt = 0;
   fatjetFlavour = 0;
   fatjetTau1 = 0;
   fatjetTau2 = 0;
   fatjetTau3 = 0;
   fatjetTrimmedMass = 0;
   fatjetPrunedMass = 0;
   fatjetFilteredMass = 0;
   fatjetSoftdropMass = 0;
   ak8_subjet = 0;
   ak8jet_hasSubjet = 0;
   ak8subjet_btag = 0;
   fatjetHbb = 0;
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
   metChargedHadron = 0;
   metNeutralHadron = 0;
   metNeutralEM = 0;
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
   fChain->SetBranchAddress("fatjetP4", &fatjetP4, &b_fatjetP4);
   fChain->SetBranchAddress("fatjetRawPt", &fatjetRawPt, &b_fatjetRawPt);
   fChain->SetBranchAddress("fatjetFlavour", &fatjetFlavour, &b_fatjetFlavour);
   fChain->SetBranchAddress("fatjetTau1", &fatjetTau1, &b_fatjetTau1);
   fChain->SetBranchAddress("fatjetTau2", &fatjetTau2, &b_fatjetTau2);
   fChain->SetBranchAddress("fatjetTau3", &fatjetTau3, &b_fatjetTau3);
   fChain->SetBranchAddress("fatjetTrimmedMass", &fatjetTrimmedMass, &b_fatjetTrimmedMass);
   fChain->SetBranchAddress("fatjetPrunedMass", &fatjetPrunedMass, &b_fatjetPrunedMass);
   fChain->SetBranchAddress("fatjetFilteredMass", &fatjetFilteredMass, &b_fatjetFilteredMass);
   fChain->SetBranchAddress("fatjetSoftdropMass", &fatjetSoftdropMass, &b_fatjetSoftdropMass);
   fChain->SetBranchAddress("ak8_subjet", &ak8_subjet, &b_ak8_subjet);
   fChain->SetBranchAddress("ak8jet_hasSubjet", &ak8jet_hasSubjet, &b_ak8jet_hasSubjet);
   fChain->SetBranchAddress("ak8subjet_btag", &ak8subjet_btag, &b_ak8subjet_btag);
   fChain->SetBranchAddress("fatjetHbb", &fatjetHbb, &b_fatjetHbb);
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
   fChain->SetBranchAddress("metChargedHadron", &metChargedHadron, &b_metChargedHadron);
   fChain->SetBranchAddress("metNeutralHadron", &metNeutralHadron, &b_metNeutralHadron);
   fChain->SetBranchAddress("metNeutralEM", &metNeutralEM, &b_metNeutralEM);
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
