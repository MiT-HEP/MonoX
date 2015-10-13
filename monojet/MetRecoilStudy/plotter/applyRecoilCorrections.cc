#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TVector2.h"
#include "TMath.h"
#include <iostream>
#include <fstream>
#include <string>
#include "RecoilCorrector.h"

// must call gSystem->Load("libMitPandaFillers.so") before running
// or load loadLibs.C

using namespace std;
using namespace TMath;

void applyRecoilCorrections(TString fileListPath, TString correctionFilePath, TString inName, TString outName, bool single, int offset=0, int toRun=-1) {

  // setup recoil corrector
  RecoilCorrector *rc = new RecoilCorrector();
  rc->SetSingleGaus(single);
  TFile *fCorrections = new TFile(correctionFilePath);
  rc->SetInputName(inName);
  rc->SetOutputName(outName);
  rc->LoadAllFits(fCorrections);
  string line;
  ifstream fileList(fileListPath.Data());
  int counter=0;
  TFile *fIn;
  TTree *tIn;
  TTree *tOut;
  if (fileList.is_open()) {
    while (getline(fileList,line)) {
	    // check if we want to run over this file
	    if (counter<offset) {
	      ++counter;
	      continue;
	    } else if (toRun>0 && counter>offset+toRun) {
	      break;
	    }
	
	    // file io
	    fIn = new TFile(line.c_str(),"UPDATE");
	    tIn = (TTree*)fIn->FindObjectAny("events");
	    tOut = new TTree("recoilVars","recoilVars");
	
	    float u1,u2,met_smeared,metphi_smeared;
	    tOut->Branch("u1",&u1,"u1/F");
	    tOut->Branch("u2",&u2,"u2/F");
	    tOut->Branch("met_smeared",&met_smeared,"met_smeared/F");
	    tOut->Branch("metphi_smeared",&metphi_smeared,"metphi_smeared/F");
		
	    float bosonpt,bosonphi,lep1pt,lep1phi,lep2pt,lep2phi;
	    int nLep, lep1Good,lep2Good; // - medium?
	    
	    // tIn->SetBranchAddress("dilep_pt",&bosonpt);
	    // tIn->SetBranchAddress("dilep_phi",&bosonphi);
	    tIn->SetBranchAddress("dilep_pt",&bosonpt);
	    tIn->SetBranchAddress("dilep_phi",&bosonphi);
	    tIn->SetBranchAddress("lep1Pt",&lep1pt);
	    tIn->SetBranchAddress("lep1Phi",&lep1phi);
	    tIn->SetBranchAddress("lep2Pt",&lep2pt);
	    tIn->SetBranchAddress("lep2Phi",&lep2phi);
	    tIn->SetBranchAddress("n_tightlep",&nLep);
	    tIn->SetBranchAddress("lep1IsTight",&lep1Good);
	    tIn->SetBranchAddress("lep2IsTight",&lep2Good);
	
	    unsigned int nEntries = tIn->GetEntries();
	    for (unsigned int iE=0; iE!=nEntries; ++iE) {
	      tIn->GetEntry(iE);
	      TVector2 tmpVec(0,0); // will be used to contain leptons
	      TVector2 lepVec(0,0);
	      if (nLep>=1) {
	          tmpVec.Set(lep1pt*Cos(lep1phi),lep1pt*Sin(lep1phi));
	          lepVec += tmpVec;
	        if ((nLep>=2)) {
	          tmpVec.Set(lep1pt*Cos(lep1phi),lep1pt*Sin(lep1phi));
	          lepVec += tmpVec;
	        }
	      }
        if (bosonpt<0 || bosonpt>1000) {
          u1 = -999;
          u2 = -998;
          met_smeared = -5;
          metphi_smeared = -5;
        } else {
  	      // compute u1, u2, met
	        rc->ComputeU(bosonpt,u1,u2);
	        rc->CorrectMET(bosonpt,bosonphi,lepVec.Mod(),lepVec.Phi(),met_smeared,metphi_smeared,0,u1,u2);
        }
	
	      tOut->Fill();
	    }
     tIn->AddFriend(tOut);
     fIn->WriteTObject(tOut,"recoilVariables","Overwrite");
     fIn->Close();
   }
  }
}
