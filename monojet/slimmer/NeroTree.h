//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Thu Dec  3 12:47:22 2015 by ROOT version 6.02/13
// from TTree events/events
// found on file: root://eoscms//eos/cms/store/user/dmytro/Nero/v1.1.1/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISpring15MiniAODv2_TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_p2/151104_133348/0000/NeroNtuples_skimmed_3.root
//////////////////////////////////////////////////////////

#ifndef NeroTree_h
#define NeroTree_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.
#include "TClonesArray.h"
#include "vector"
#include "vector"
#include "vector"
#include "TLorentzVector.h"

class NeroTree {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   Int_t           isRealData;
   Int_t           runNum;
   Int_t           lumiNum;
   ULong64_t       eventNum;
   Float_t         rho;
   Int_t           npv;
   TClonesArray    *jetP4;
   vector<int>     *jetMatch;
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
   vector<unsigned int> *jetSelBits;
   vector<float>   *jetQ;
   vector<float>   *jetQnoPU;
   TClonesArray    *tauP4;
   vector<int>     *tauMatch;
   vector<unsigned int> *tauSelBits;
   vector<int>     *tauQ;
   vector<float>   *tauM;
   vector<float>   *tauIso;
   vector<float>   *tauChargedIsoPtSum;
   vector<float>   *tauNeutralIsoPtSum;
   vector<float>   *tauIsoDeltaBetaCorr;
   TClonesArray    *lepP4;
   vector<int>     *lepMatch;
   vector<int>     *lepPdgId;
   vector<float>   *lepIso;
   vector<unsigned int> *lepSelBits;
   vector<float>   *lepPfPt;
   vector<float>   *lepChIso;
   vector<float>   *lepNhIso;
   vector<float>   *lepPhoIso;
   vector<float>   *lepPuIso;
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
   vector<float>   *fatjettopMVA;
   TClonesArray    *metP4;
   vector<float>   *metPtJESUP;
   vector<float>   *metPtJESDOWN;
   TClonesArray    *metP4_GEN;
   TLorentzVector  *metPuppi;
   TClonesArray    *metPuppiSyst;
   TLorentzVector  *metNoMu;
   TLorentzVector  *metNoHF;
   TLorentzVector  *pfMet_e3p0;
   TLorentzVector  *trackMet;
   Float_t         caloMet_Pt;
   Float_t         caloMet_Phi;
   Float_t         caloMet_SumEt;
   TClonesArray    *photonP4;
   vector<float>   *photonIso;
   vector<float>   *photonSieie;
   vector<unsigned int> *photonSelBits;
   vector<float>   *photonChIso;
   vector<float>   *photonChIsoRC;
   vector<float>   *photonNhIso;
   vector<float>   *photonNhIsoRC;
   vector<float>   *photonPhoIso;
   vector<float>   *photonPhoIsoRC;
   vector<float>   *photonPuIso;
   vector<float>   *photonPuIsoRC;
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
   vector<int>     *triggerFired;
   vector<float>   *triggerPrescale;
   vector<int>     *triggerLeps;
   vector<int>     *triggerJets;
   vector<int>     *triggerTaus;
   vector<int>     *triggerPhotons;

   // List of branches
   TBranch        *b_isRealData;   //!
   TBranch        *b_runNum;   //!
   TBranch        *b_lumiNum;   //!
   TBranch        *b_eventNum;   //!
   TBranch        *b_rho;   //!
   TBranch        *b_npv;   //!
   TBranch        *b_jetP4;   //!
   TBranch        *b_jetMatch;   //!
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
   TBranch        *b_jetSelBits;   //!
   TBranch        *b_jetQ;   //!
   TBranch        *b_jetQnoPU;   //!
   TBranch        *b_tauP4;   //!
   TBranch        *b_tauMatch;   //!
   TBranch        *b_tauSelBits;   //!
   TBranch        *b_tauQ;   //!
   TBranch        *b_tauM;   //!
   TBranch        *b_tauIso;   //!
   TBranch        *b_tauChargedIsoPtSum;   //!
   TBranch        *b_tauNeutralIsoPtSum;   //!
   TBranch        *b_tauIsoDeltaBetaCorr;   //!
   TBranch        *b_lepP4;   //!
   TBranch        *b_lepMatch;   //!
   TBranch        *b_lepPdgId;   //!
   TBranch        *b_lepIso;   //!
   TBranch        *b_lepSelBits;   //!
   TBranch        *b_lepPfPt;   //!
   TBranch        *b_lepChIso;   //!
   TBranch        *b_lepNhIso;   //!
   TBranch        *b_lepPhoIso;   //!
   TBranch        *b_lepPuIso;   //!
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
   TBranch        *b_fatjettopMVA;   //!
   TBranch        *b_metP4;   //!
   TBranch        *b_metPtJESUP;   //!
   TBranch        *b_metPtJESDOWN;   //!
   TBranch        *b_metP4_GEN;   //!
   TBranch        *b_metPuppi;   //!
   TBranch        *b_metPuppiSyst;   //!
   TBranch        *b_metNoMu;   //!
   TBranch        *b_metNoHF;   //!
   TBranch        *b_pfMet_e3p0;   //!
   TBranch        *b_trackMet;   //!
   TBranch        *b_caloMet_Pt;   //!
   TBranch        *b_caloMet_Phi;   //!
   TBranch        *b_caloMet_SumEt;   //!
   TBranch        *b_photonP4;   //!
   TBranch        *b_photonIso;   //!
   TBranch        *b_photonSieie;   //!
   TBranch        *b_photonSelBits;   //!
   TBranch        *b_photonChIso;   //!
   TBranch        *b_photonChIsoRC;   //!
   TBranch        *b_photonNhIso;   //!
   TBranch        *b_photonNhIsoRC;   //!
   TBranch        *b_photonPhoIso;   //!
   TBranch        *b_photonPhoIsoRC;   //!
   TBranch        *b_photonPuIso;   //!
   TBranch        *b_photonPuIsoRC;   //!
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
   TBranch        *b_triggerFired;   //!
   TBranch        *b_triggerPrescale;   //!
   TBranch        *b_triggerLeps;   //!
   TBranch        *b_triggerJets;   //!
   TBranch        *b_triggerTaus;   //!
   TBranch        *b_triggerPhotons;   //!

   NeroTree(TTree *tree=0);
   virtual ~NeroTree();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif
