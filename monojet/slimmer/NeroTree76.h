//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Wed Feb 17 11:46:55 2016 by ROOT version 6.06/00
// from TTree events/events
// found on file: /scratch5/ceballos/hist/monov_all/t2mit/filefi/043/VectorMonoW_Mphi-50_Mchi-10_gSM-1p0_gDM-1p0_13TeV-madgraph+RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1+AODSIM/nero_0000.root
//////////////////////////////////////////////////////////

#ifndef NeroTree76_h
#define NeroTree76_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.
#include "TClonesArray.h"
#include "vector"
#include "vector"
#include "vector"
#include "TLorentzVector.h"

class NeroTree76 {
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
   vector<unsigned int> *jetSelBits;
   vector<float>   *jetQ;
   vector<float>   *jetQnoPU;
   TClonesArray    *jetpuppiP4;
   vector<float>   *jetpuppiRawPt;
   vector<float>   *jetpuppiBdiscr;
   vector<float>   *jetpuppiBdiscrLegacy;
   vector<float>   *jetpuppiPuId;
   vector<float>   *jetpuppiUnc;
   vector<float>   *jetpuppiQGL;
   vector<int>     *jetpuppiFlavour;
   vector<int>     *jetpuppiMatchedPartonPdgId;
   vector<int>     *jetpuppiMotherPdgId;
   vector<int>     *jetpuppiGrMotherPdgId;
   vector<unsigned int> *jetpuppiSelBits;
   vector<float>   *jetpuppiQ;
   vector<float>   *jetpuppiQnoPU;
   TClonesArray    *fatjetAK8CHSP4;
   vector<float>   *fatjetAK8CHSRawPt;
   vector<int>     *fatjetAK8CHSFlavour;
   vector<float>   *fatjetAK8CHSTau1;
   vector<float>   *fatjetAK8CHSTau2;
   vector<float>   *fatjetAK8CHSTau3;
   vector<float>   *fatjetAK8CHSTrimmedMass;
   vector<float>   *fatjetAK8CHSPrunedMass;
   vector<float>   *fatjetAK8CHSFilteredMass;
   vector<float>   *fatjetAK8CHSSoftdropMass;
   TClonesArray    *fatjetAK8CHSsubjet;
   vector<int>     *fatjetAK8CHSnSubjets;
   vector<int>     *fatjetAK8CHSfirstSubjet;
   vector<float>   *fatjetAK8CHSsubjet_btag;
   vector<float>   *fatjetAK8CHSHbb;
   vector<float>   *fatjetAK8CHStopMVA;
   TClonesArray    *fatjetCA15CHSP4;
   vector<float>   *fatjetCA15CHSRawPt;
   vector<int>     *fatjetCA15CHSFlavour;
   vector<float>   *fatjetCA15CHSTau1;
   vector<float>   *fatjetCA15CHSTau2;
   vector<float>   *fatjetCA15CHSTau3;
   vector<float>   *fatjetCA15CHSTrimmedMass;
   vector<float>   *fatjetCA15CHSPrunedMass;
   vector<float>   *fatjetCA15CHSFilteredMass;
   vector<float>   *fatjetCA15CHSSoftdropMass;
   TClonesArray    *fatjetCA15CHSsubjet;
   vector<int>     *fatjetCA15CHSnSubjets;
   vector<int>     *fatjetCA15CHSfirstSubjet;
   vector<float>   *fatjetCA15CHSsubjet_btag;
   vector<float>   *fatjetCA15CHSHbb;
   vector<float>   *fatjetCA15CHStopMVA;
   TClonesArray    *fatjetAK8PuppiP4;
   vector<float>   *fatjetAK8PuppiRawPt;
   vector<int>     *fatjetAK8PuppiFlavour;
   vector<float>   *fatjetAK8PuppiTau1;
   vector<float>   *fatjetAK8PuppiTau2;
   vector<float>   *fatjetAK8PuppiTau3;
   vector<float>   *fatjetAK8PuppiTrimmedMass;
   vector<float>   *fatjetAK8PuppiPrunedMass;
   vector<float>   *fatjetAK8PuppiFilteredMass;
   vector<float>   *fatjetAK8PuppiSoftdropMass;
   TClonesArray    *fatjetAK8Puppisubjet;
   vector<int>     *fatjetAK8PuppinSubjets;
   vector<int>     *fatjetAK8PuppifirstSubjet;
   vector<float>   *fatjetAK8Puppisubjet_btag;
   vector<float>   *fatjetAK8PuppiHbb;
   vector<float>   *fatjetAK8PuppitopMVA;
   TClonesArray    *fatjetCA15PuppiP4;
   vector<float>   *fatjetCA15PuppiRawPt;
   vector<int>     *fatjetCA15PuppiFlavour;
   vector<float>   *fatjetCA15PuppiTau1;
   vector<float>   *fatjetCA15PuppiTau2;
   vector<float>   *fatjetCA15PuppiTau3;
   vector<float>   *fatjetCA15PuppiTrimmedMass;
   vector<float>   *fatjetCA15PuppiPrunedMass;
   vector<float>   *fatjetCA15PuppiFilteredMass;
   vector<float>   *fatjetCA15PuppiSoftdropMass;
   TClonesArray    *fatjetCA15Puppisubjet;
   vector<int>     *fatjetCA15PuppinSubjets;
   vector<int>     *fatjetCA15PuppifirstSubjet;
   vector<float>   *fatjetCA15Puppisubjet_btag;
   vector<float>   *fatjetCA15PuppiHbb;
   vector<float>   *fatjetCA15PuppitopMVA;
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
   Float_t         metSumEtRaw;
   vector<float>   *metPtJESUP;
   vector<float>   *metPtJESDOWN;
   TClonesArray    *metP4_GEN;
   TLorentzVector  *metPuppi;
   TClonesArray    *metPuppiSyst;
   Float_t         metSumEtRawPuppi;
   TLorentzVector  *metNoMu;
   TLorentzVector  *metNoHF;
   Float_t         metSumEtRawNoHF;
   TLorentzVector  *pfMet_e3p0;
   TLorentzVector  *trackMet;
   Float_t         caloMet_Pt;
   Float_t         caloMet_Phi;
   Float_t         caloMet_SumEt;
   Float_t         rawMet_Pt;
   Float_t         rawMet_Phi;
   TClonesArray    *genP4;
   TClonesArray    *genjetP4;
   vector<int>     *genPdgId;
   vector<unsigned int> *genFlags;
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
   Float_t         r2f1;
   Float_t         r5f1;
   Float_t         r1f2;
   Float_t         r2f2;
   Float_t         r1f5;
   Float_t         r5f5;
   vector<float>   *pdfRwgt;
   vector<float>   *genIso;
   vector<float>   *genIsoFrixione;
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
   vector<float>   *photonRawPt;
   vector<float>   *photonR9;
   TClonesArray    *tauP4;
   vector<unsigned int> *tauSelBits;
   vector<int>     *tauQ;
   vector<float>   *tauM;
   vector<float>   *tauIso;
   vector<float>   *tauChargedIsoPtSum;
   vector<float>   *tauNeutralIsoPtSum;
   vector<float>   *tauIsoDeltaBetaCorr;
   vector<float>   *tauIsoPileupWeightedRaw;
   vector<int>     *triggerFired;
   vector<float>   *triggerPrescale;
   vector<int>     *triggerLeps;
   vector<int>     *triggerJets;
   vector<int>     *triggerTaus;
   vector<int>     *triggerPhotons;
   vector<unsigned int> *triggerNoneTaus;
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
   TBranch        *b_jetSelBits;   //!
   TBranch        *b_jetQ;   //!
   TBranch        *b_jetQnoPU;   //!
   TBranch        *b_jetpuppiP4;   //!
   TBranch        *b_jetpuppiRawPt;   //!
   TBranch        *b_jetpuppiBdiscr;   //!
   TBranch        *b_jetpuppiBdiscrLegacy;   //!
   TBranch        *b_jetpuppiPuId;   //!
   TBranch        *b_jetpuppiUnc;   //!
   TBranch        *b_jetpuppiQGL;   //!
   TBranch        *b_jetpuppiFlavour;   //!
   TBranch        *b_jetpuppiMatchedPartonPdgId;   //!
   TBranch        *b_jetpuppiMotherPdgId;   //!
   TBranch        *b_jetpuppiGrMotherPdgId;   //!
   TBranch        *b_jetpuppiSelBits;   //!
   TBranch        *b_jetpuppiQ;   //!
   TBranch        *b_jetpuppiQnoPU;   //!
   TBranch        *b_fatjetAK8CHSP4;   //!
   TBranch        *b_fatjetAK8CHSRawPt;   //!
   TBranch        *b_fatjetAK8CHSFlavour;   //!
   TBranch        *b_fatjetAK8CHSTau1;   //!
   TBranch        *b_fatjetAK8CHSTau2;   //!
   TBranch        *b_fatjetAK8CHSTau3;   //!
   TBranch        *b_fatjetAK8CHSTrimmedMass;   //!
   TBranch        *b_fatjetAK8CHSPrunedMass;   //!
   TBranch        *b_fatjetAK8CHSFilteredMass;   //!
   TBranch        *b_fatjetAK8CHSSoftdropMass;   //!
   TBranch        *b_fatjetAK8CHSsubjet;   //!
   TBranch        *b_fatjetAK8CHSnSubjets;   //!
   TBranch        *b_fatjetAK8CHSfirstSubjet;   //!
   TBranch        *b_fatjetAK8CHSsubjet_btag;   //!
   TBranch        *b_fatjetAK8CHSHbb;   //!
   TBranch        *b_fatjetAK8CHStopMVA;   //!
   TBranch        *b_fatjetCA15CHSP4;   //!
   TBranch        *b_fatjetCA15CHSRawPt;   //!
   TBranch        *b_fatjetCA15CHSFlavour;   //!
   TBranch        *b_fatjetCA15CHSTau1;   //!
   TBranch        *b_fatjetCA15CHSTau2;   //!
   TBranch        *b_fatjetCA15CHSTau3;   //!
   TBranch        *b_fatjetCA15CHSTrimmedMass;   //!
   TBranch        *b_fatjetCA15CHSPrunedMass;   //!
   TBranch        *b_fatjetCA15CHSFilteredMass;   //!
   TBranch        *b_fatjetCA15CHSSoftdropMass;   //!
   TBranch        *b_fatjetCA15CHSsubjet;   //!
   TBranch        *b_fatjetCA15CHSnSubjets;   //!
   TBranch        *b_fatjetCA15CHSfirstSubjet;   //!
   TBranch        *b_fatjetCA15CHSsubjet_btag;   //!
   TBranch        *b_fatjetCA15CHSHbb;   //!
   TBranch        *b_fatjetCA15CHStopMVA;   //!
   TBranch        *b_fatjetAK8PuppiP4;   //!
   TBranch        *b_fatjetAK8PuppiRawPt;   //!
   TBranch        *b_fatjetAK8PuppiFlavour;   //!
   TBranch        *b_fatjetAK8PuppiTau1;   //!
   TBranch        *b_fatjetAK8PuppiTau2;   //!
   TBranch        *b_fatjetAK8PuppiTau3;   //!
   TBranch        *b_fatjetAK8PuppiTrimmedMass;   //!
   TBranch        *b_fatjetAK8PuppiPrunedMass;   //!
   TBranch        *b_fatjetAK8PuppiFilteredMass;   //!
   TBranch        *b_fatjetAK8PuppiSoftdropMass;   //!
   TBranch        *b_fatjetAK8Puppisubjet;   //!
   TBranch        *b_fatjetAK8PuppinSubjets;   //!
   TBranch        *b_fatjetAK8PuppifirstSubjet;   //!
   TBranch        *b_fatjetAK8Puppisubjet_btag;   //!
   TBranch        *b_fatjetAK8PuppiHbb;   //!
   TBranch        *b_fatjetAK8PuppitopMVA;   //!
   TBranch        *b_fatjetCA15PuppiP4;   //!
   TBranch        *b_fatjetCA15PuppiRawPt;   //!
   TBranch        *b_fatjetCA15PuppiFlavour;   //!
   TBranch        *b_fatjetCA15PuppiTau1;   //!
   TBranch        *b_fatjetCA15PuppiTau2;   //!
   TBranch        *b_fatjetCA15PuppiTau3;   //!
   TBranch        *b_fatjetCA15PuppiTrimmedMass;   //!
   TBranch        *b_fatjetCA15PuppiPrunedMass;   //!
   TBranch        *b_fatjetCA15PuppiFilteredMass;   //!
   TBranch        *b_fatjetCA15PuppiSoftdropMass;   //!
   TBranch        *b_fatjetCA15Puppisubjet;   //!
   TBranch        *b_fatjetCA15PuppinSubjets;   //!
   TBranch        *b_fatjetCA15PuppifirstSubjet;   //!
   TBranch        *b_fatjetCA15Puppisubjet_btag;   //!
   TBranch        *b_fatjetCA15PuppiHbb;   //!
   TBranch        *b_fatjetCA15PuppitopMVA;   //!
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
   TBranch        *b_metSumEtRaw;   //!
   TBranch        *b_metPtJESUP;   //!
   TBranch        *b_metPtJESDOWN;   //!
   TBranch        *b_metP4_GEN;   //!
   TBranch        *b_metPuppi;   //!
   TBranch        *b_metPuppiSyst;   //!
   TBranch        *b_metSumEtRawPuppi;   //!
   TBranch        *b_metNoMu;   //!
   TBranch        *b_metNoHF;   //!
   TBranch        *b_metSumEtRawNoHF;   //!
   TBranch        *b_pfMet_e3p0;   //!
   TBranch        *b_trackMet;   //!
   TBranch        *b_caloMet_Pt;   //!
   TBranch        *b_caloMet_Phi;   //!
   TBranch        *b_caloMet_SumEt;   //!
   TBranch        *b_rawMet_Pt;   //!
   TBranch        *b_rawMet_Phi;   //!
   TBranch        *b_genP4;   //!
   TBranch        *b_genjetP4;   //!
   TBranch        *b_genPdgId;   //!
   TBranch        *b_genFlags;   //!
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
   TBranch        *b_r2f1;   //!
   TBranch        *b_r5f1;   //!
   TBranch        *b_r1f2;   //!
   TBranch        *b_r2f2;   //!
   TBranch        *b_r1f5;   //!
   TBranch        *b_r5f5;   //!
   TBranch        *b_pdfRwgt;   //!
   TBranch        *b_genIso;   //!
   TBranch        *b_genIsoFrixione;   //!
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
   TBranch        *b_photonRawPt;   //!
   TBranch        *b_photonR9;   //!
   TBranch        *b_tauP4;   //!
   TBranch        *b_tauSelBits;   //!
   TBranch        *b_tauQ;   //!
   TBranch        *b_tauM;   //!
   TBranch        *b_tauIso;   //!
   TBranch        *b_tauChargedIsoPtSum;   //!
   TBranch        *b_tauNeutralIsoPtSum;   //!
   TBranch        *b_tauIsoDeltaBetaCorr;   //!
   TBranch        *b_tauIsoPileupWeightedRaw;   //!
   TBranch        *b_triggerFired;   //!
   TBranch        *b_triggerPrescale;   //!
   TBranch        *b_triggerLeps;   //!
   TBranch        *b_triggerJets;   //!
   TBranch        *b_triggerTaus;   //!
   TBranch        *b_triggerPhotons;   //!
   TBranch        *b_triggerNoneTaus;   //!
   TBranch        *b_npv;   //!

   NeroTree76(TTree *tree=0);
   virtual ~NeroTree76();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif
