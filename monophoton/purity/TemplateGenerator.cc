#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TDirectory.h"
#include "TMath.h"

#include "TreeEntries_simpletree.h"

#include <fstream>
#include <stdexcept>
#include <string>
#include <iostream>
#include <cstring>

enum TemplateType {
  kPhoton,
  kBackground,
  kElectron,
  nTemplateTypes
};

enum TemplateVar {
  kSigmaIetaIeta,
  kSigmaIetaIetaScaled,
  kChargedHadronIsolation,
  kPhotonIsolation,
  nTemplateVars
};

enum FakeVar {
  kChIso,
  kNhIso,
  kPhIso,
  kHOverE,
  kSieie,
  nFakeVars
};

enum PhotonId {
  kLoose,
  kMedium,
  kTight,
  nPhotonIds
};

enum PhotonLocation {
  kBarrel,
  kEndcap,
  nPhotonLocations
};

class TemplateGenerator {
public:
  TemplateGenerator(TemplateType, TemplateVar, char const* fileName, bool write = false);
  ~TemplateGenerator() { delete [] binEdges_; }

  void fillSkim(TTree* _input, FakeVar _fakevar, PhotonId _id, Double_t _xsec, Double_t _lumi);
  void writeSkim();
  void closeFile();
  void setTemplateBinning(int _nBins, double _xmin, double _xmax);
  void setTemplateBinning(int _nBins, double* _binEdges);
  TH1D* makeTemplate(char const* name, char const* expr);

private:
  TemplateType tType_;
  TemplateVar tVar_;

  int nBins_;
  double xmin_;
  double xmax_;
  double* binEdges_ = NULL;

  TTree* skimTree_{0};
};

TemplateGenerator::TemplateGenerator(TemplateType _type, TemplateVar _var, char const* _fileName, bool _write/* = false*/) :
  tType_(_type),
  tVar_(_var),
  nBins_(40),
  xmin_(0.),
  xmax_(0.02)
{
  bool exists(false);
  std::ifstream fs(_fileName, std::ifstream::in | std::ifstream::binary);
  if (fs.is_open())
    exists = true;
  fs.close();

  TFile* file = 0;
  if (_write)
    file = TFile::Open(_fileName, "recreate");
  else
    file = TFile::Open(_fileName);

  if (!file || file->IsZombie())
    throw std::runtime_error(std::string("File ") + _fileName + " could not be opened.");

  if (_write) {
    file->cd();
    skimTree_ = new TTree("skimmedEvents", "template skim");
  }
  else
    skimTree_ = static_cast<TTree*>(file->Get("skimmedEvents"));
}

void
TemplateGenerator::fillSkim(TTree* _input, FakeVar _fakevar, PhotonId _id, Double_t _xsec, Double_t _lumi)
{
  if (skimTree_->GetListOfBranches()->GetEntries() != 0)
    throw std::runtime_error("Skim already exists.");

  simpletree::Event event;
  event.setAddress(*_input);
  event.book(*skimTree_, {"run", "lumi", "event", "weight", "rho", "npv", "ntau", "jets", "electrons" , "muons", "t1Met"});

  simpletree::PhotonCollection selectedPhotons("selPhotons");
  selectedPhotons.book(*skimTree_);
  
  Double_t eventWeight;
  if (_xsec < 0) eventWeight = 1;
  else {
    TH1D* hWeight = new TH1D("hWeight","Sum of Weights", 1, 0.0, 1.0);
    _input->Draw("0.5>>hWeight","weight","goff");
    Double_t nEvents =  hWeight->GetBinContent(1);
    printf("Calculating event weight to be: %f * %f / %f \n", _xsec, _lumi, nEvents);
    eventWeight = _xsec * _lumi / nEvents; 
    printf("Event weight is: %f \n", eventWeight);
  }

  Long_t pass[20]{};
  

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    if (iEntry % 10000 == 1)
      std::cout << "Processing event " << iEntry << std::endl;

    event.weight *= eventWeight;

    selectedPhotons.clear();
    unsigned iSel(0);

    auto& photons(event.photons);
    auto& electrons(event.electrons);
    
    UInt_t kObject = 0; // 0 = photon
    UInt_t nObjects = photons.size();
    
    if (tType_ == kElectron) {
      kObject = 1; // 1 = electron
      nObjects = electrons.size();
    }
    Float_t* eta[2] = { event.photons.data.eta, event.electrons.data.eta };
    Float_t* hOverE[2] = { event.photons.data.hOverE, event.electrons.data.hOverE };
    Float_t* sieie[2] = { event.photons.data.sieie, event.electrons.data.sieie };
    Float_t* chIso[2] = { event.photons.data.chIso, event.electrons.data.chIsoPh };
    Float_t* nhIso[2] = { event.photons.data.nhIso, event.electrons.data.nhIsoPh };
    Float_t* phIso[2] = { event.photons.data.phIso, event.electrons.data.phIsoPh };

    for (unsigned iP(0); iP != nObjects; ++iP) {
      Bool_t PassCut[nFakeVars];
      Bool_t PassSel = true;
      for (unsigned iC(0); iC < nFakeVars; iC++) {
	PassCut[iC] = false;
      }

      // barrel photons
      UInt_t kLocation;
      if (TMath::Abs(eta[kObject][iP]) < 1.5) kLocation = kBarrel;
      else kLocation = kEndcap;
		
      
      pass[0]++;

      // baseline photon selection
      if (hOverE[kObject][iP] < simpletree::Photon::hOverECuts[kLocation][_id]) {
	PassCut[kHOverE] = true;
      }
      if (tVar_ == kChargedHadronIsolation) {
	PassCut[kChIso] = true;
      }
      else {
	if (chIso[kObject][iP] < simpletree::Photon::chIsoCuts[kLocation][_id]) {
	  PassCut[kChIso] = true;
	}
      }
      if (nhIso[kObject][iP] < simpletree::Photon::nhIsoCuts[kLocation][_id]) { 
	PassCut[kNhIso] = true;
      }
      if (tVar_ == kPhotonIsolation) {
	PassCut[kPhIso] = true;
      }
      else {
	if (phIso[kObject][iP] < simpletree::Photon::phIsoCuts[kLocation][_id]) {
	  PassCut[kPhIso] = true;
	}
      }
      if ( (tVar_ == kSigmaIetaIeta) || (tVar_ == kSigmaIetaIetaScaled) || (tVar_ == kChargedHadronIsolation) ) {
	PassCut[kSieie] = true;
      }
      else {
	if (sieie[kObject][iP] < simpletree::Photon::sieieCuts[kLocation][_id]) {
	  PassCut[kSieie] = true;
	}
      }
      if (tType_ != kElectron) {
	if (!photons[iP].csafeVeto) continue; // !veto for v5 and beyond
      }
      pass[1]++;

      // real vs fake selection
      if (tType_ == kPhoton) {
	for (unsigned iC(0); iC < nFakeVars; iC++) {
	  if (!PassCut[iC]) {
	    PassSel = false;
	    break;
	  }
	  else pass[iC+2]++;
	}
      }
      
      else if (tType_ == kBackground) {
	for (unsigned iC(0); iC < nFakeVars; iC++) {
	  if (iC == _fakevar) {
	    if (PassCut[iC]) PassSel = false;
	    else pass[iC]++;
	    
	    if (_fakevar == kChIso) {
	      if (chIso[kObject][iP] > simpletree::Photon::chIsoCuts[kLocation][kTight]) {
		PassSel = true;
		pass[7]++;
	      }
	    }
	    else if (_fakevar == kNhIso) {
	      if (nhIso[kObject][iP] > simpletree::Photon::nhIsoCuts[kLocation][kTight]) {
		PassSel = true;
		pass[8]++;
	      }
	    }
	    else if (_fakevar == kPhIso) {
	      if (phIso[kObject][iP] > simpletree::Photon::chIsoCuts[kLocation][kTight]) {
		PassSel = true;
		pass[9]++;
	      }
	    }
	    else if (_fakevar == kHOverE) {
	      if (hOverE[kObject][iP] > simpletree::Photon::hOverECuts[kLocation][kTight]) {
		PassSel = true;
		pass[10]++;
	      }
	    }
	    else if (_fakevar == kSieie) {
	      if (sieie[kObject][iP] > simpletree::Photon::sieieCuts[kLocation][kTight]) {
		PassSel = true;
		pass[11]++;
	      }
	    }
	  }
	  
	  else { 
	    if (!PassCut[iC]) {
	      PassSel = false;
	      break;
	    }
	    else pass[iC+2]++;
	  }
	}
      }
      
      if (!PassSel) continue;
    
      selectedPhotons.resize(iSel + 1);
      simpletree::Photon& selected(selectedPhotons[iSel]);
      
      if (tType_ == kElectron) {
	selected.pt = electrons[iP].pt;
	selected.eta = electrons[iP].eta;
	selected.phi = electrons[iP].phi;    
	selected.chIso = electrons[iP].chIsoPh; 
	selected.nhIso = electrons[iP].nhIsoPh;
	selected.phIso = electrons[iP].phIsoPh;
	selected.sieie = electrons[iP].sieie;
	selected.hOverE = electrons[iP].hOverE;
	selected.matchedGen = electrons[iP].matchedGen;
	// selected.isEB = electrons[iP].isEB;
	selected.hadDecay = electrons[iP].hadDecay;
	selected.pixelVeto = true;
	selected.csafeVeto = true;
      }
      else {
	selected.pt = photons[iP].pt;
	selected.eta = photons[iP].eta;
	selected.phi = photons[iP].phi;    
	selected.chIso = photons[iP].chIso; 
	selected.nhIso = photons[iP].nhIso;
	selected.phIso = photons[iP].phIso;
	selected.sieie = photons[iP].sieie;
	selected.hOverE = photons[iP].hOverE;
	selected.drParton = photons[iP].drParton;
	selected.matchedGen = photons[iP].matchedGen;
	selected.isEB = photons[iP].isEB;
	selected.hadDecay = photons[iP].hadDecay;
	selected.pixelVeto = photons[iP].pixelVeto;
	selected.csafeVeto = photons[iP].csafeVeto;
	selected.loose = photons[iP].loose;
	selected.medium = photons[iP].medium;
	selected.tight = photons[iP].tight;
	selected.matchHLT120 = photons[iP].matchHLT120;
	selected.matchHLT135MET100 = photons[iP].matchHLT135MET100;
	selected.matchHLT165HE10 = photons[iP].matchHLT165HE10;
	selected.matchHLT175 = photons[iP].matchHLT175;
      } 
      ++iSel;
    }
      
    if (iSel != 0)
      skimTree_->Fill();
  }

  TString passing[12] = {"Total: ", "csafeVeto: ", "chIso: ", "nhIso: ", "phIso: ", "hOverE: ", "sieie: ", "chIso SB: ", "nhIso SB: ", "phIso SB: ", "hOverE SB: ", "sieie SB: "};
  for (UInt_t iPass = 0; iPass < 12; iPass++) {
    std::cout << passing[iPass] << pass[iPass] << std::endl;
  }
}

void
TemplateGenerator::writeSkim()
{
  auto* file = skimTree_->GetCurrentFile();
  file->cd();
  skimTree_->Write();
}

void
TemplateGenerator::closeFile()
{
  auto* file = skimTree_->GetCurrentFile();
  file->Close();
}

void
TemplateGenerator::setTemplateBinning(int _nBins, double _xmin, double _xmax)
{
  nBins_ = _nBins;
  xmin_ = _xmin;
  xmax_ = _xmax;
}

void
TemplateGenerator::setTemplateBinning(int _nBins, double* _binEdges)
{
  nBins_ = _nBins;
  delete [] binEdges_;
  binEdges_ = new double[_nBins];
  for(int iBin = 0; !(iBin >  nBins_); iBin++) {
    binEdges_[iBin] = _binEdges[iBin];
    // std::cout << "Bin Edge " << iBin << " is " << binEdges_[iBin] << std::endl;
  }
}

TH1D*
TemplateGenerator::makeTemplate(char const* _name, char const* _expr)
{
  auto* gd = gDirectory;
  skimTree_->GetCurrentFile()->cd();
  TH1D* tmp = NULL;
  if (binEdges_) {
    tmp = new TH1D(_name, "", nBins_, binEdges_);
    for (int iBin = 0; !(iBin > tmp->GetNbinsX()+1); iBin++) {
      // std::cout << "Bin Edge " << iBin << " is " << tmp->GetXaxis()->GetBinLowEdge(iBin) << " " << tmp->GetXaxis()->GetBinUpEdge(iBin) << std::endl;
    }
  }
  else {
    tmp = new TH1D(_name, "", nBins_, xmin_, xmax_);
  }
  tmp->Sumw2();

  TString var;
  if (tVar_ == kSigmaIetaIeta)
    var = "selPhotons.sieie";
  else if (tVar_ == kPhotonIsolation)
    var = "selPhotons.phIso";
  else if (tVar_ == kSigmaIetaIetaScaled)
    var = "0.891832 * selPhotons.sieie + 0.0009133";
  else if (tVar_ == kChargedHadronIsolation)
    var = "selPhotons.chIso";

  TString weight("weight");
  if (std::strlen(_expr) != 0) {
    weight += " * (";
    weight += _expr;
    weight += ")";
  }

  skimTree_->Draw(var + ">>" + TString(_name), weight, "goff");

  gd->cd();

  return tmp;
}
