#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TDirectory.h"
#include "TLorentzVector.h"
#include "TROOT.h"
#include "TEntryListArray.h"
#include "TEfficiency.h"

#include "PandaTree/Objects/interface/EventMonophoton.h"

#include <cmath>

class Calculator {
public:
  enum WP {
    WPloose,
    WPmedium,
    WPtight,
    WPhighpt
  };

  enum Cut {
    sMatch,
    sHoverE,
    sSieie,
    sNHIso,
    sPhIso,
    sCHIso,
    sEveto,
    sSpike,
    sHalo,
    sCHMaxIso,
    sPFVeto,
    nCuts
  };

  static TString cutNames[nCuts];

  Calculator() {}
  unsigned calculate(TTree* _input, TFile* _outputFile, TString _sname);

  void setMinPhoPt(float minPhoPt) { minPhoPt_ = minPhoPt; }
  void setMaxPhoPt(float maxPhoPt) { maxPhoPt_ = maxPhoPt; }
  void setMinMet(float minMet) { minMet_ = minMet; }
  void setMaxMet(float maxMet) { maxMet_ = maxMet; }
  void setMinEta(float minEta) { minEta_ = minEta; }
  void setMaxEta(float maxEta) { maxEta_ = maxEta; }
  
  void setMaxDR(float maxDR) { maxDR_ = maxDR; }
  void setMaxDPt(float maxDPt) { maxDPt_ = maxDPt; }

  void setWorkingPoint(WP wp) { wp_ = wp; }
  void setEra(panda::XPhoton::IDTune era) { era_ = era; }

private:
  double minPhoPt_{175.};
  double maxPhoPt_{6500.};
  double minMet_{0.};
  double maxMet_{60.};
  double minEta_{0.};
  double maxEta_{1.5};
  
  double maxDR_{0.2};
  double maxDPt_{0.2};

  WP wp_{WPmedium};
  panda::XPhoton::IDTune era_{panda::XPhoton::kSpring16};
};

TString Calculator::cutNames[Calculator::nCuts] = {
  "Match",
  "HoverE",
  "Sieie",
  "NHIso",
  "PhIso",
  "CHIso",
  "Eveto",
  "Spike",
  "Halo",
  "CHMaxIso",
  "PFVeto"
};

unsigned
Calculator::calculate(TTree* _input, TFile* _outputFile, TString _sname)
{
  panda::EventMonophoton event;
  event.setReadRunTree(false);

  _input->SetBranchStatus("*", false);
  event.setAddress(*_input, {"runNumber", "lumiNumber", "eventNumber", "weight", "npv", "npvTrue", "genParticles", "photons", "t1Met", "rho", "superClusters"});
  
  bool chargedPFVeto[256];
  TBranch* bPFVeto{0};
  _input->SetBranchAddress("photons.chargedPFVeto", chargedPFVeto);

  double minGenPt_ = minPhoPt_ / ( 1 + maxDPt_ );
  double maxGenPt_ = maxPhoPt_ / ( 1 - maxDPt_ );
  double minGenEta_ = std::max(0., minEta_ - maxDR_);
  double maxGenEta_ = maxEta_ + maxDR_;

  printf("%.0f < gen pt  < %.0f \n", minGenPt_, maxGenPt_);
  printf("%.2f < gen eta < %.2f \n", minGenEta_, maxGenEta_);

  _outputFile->cd();
  auto* output(new TTree(TString("cutflow_")+_sname, TString("cutflow_")+_sname));
  event.book(*output, {"runNumber", "lumiNumber", "eventNumber", "npv"});

  float weight;
  float pt;
  float eta;
  float phi;
  output->Branch("weight", &weight, "weight/F");
  output->Branch("pt", &pt, "pt/F");
  output->Branch("eta", &eta, "eta/F");
  output->Branch("phi", &phi, "phi/F");

  bool results[nCuts]{};
  for (unsigned iC(0); iC != nCuts; ++iC)
    output->Branch(cutNames[iC], results + iC, cutNames[iC] + "/O");

  unsigned nGenPhotons(0);
  unsigned nMatchedPhotons(0);

  long iEntry(0);
  int iTree(-1);
  while (event.getEntry(*_input, iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << " " << iEntry << std::endl;

    long localEntry(_input->LoadTree(iEntry++));
    if (localEntry < 0)
      break;

    if (_input->GetTreeNumber() != iTree) {
      iTree = _input->GetTreeNumber();

      bPFVeto = _input->GetBranch("photons.chargedPFVeto");
    }

    bPFVeto->GetEntry(localEntry);

    weight = event.weight;
    
    if (event.t1Met.pt > maxMet_ || event.t1Met.pt < minMet_)
      continue;

    std::fill_n(results, nCuts, false);

    std::vector<panda::UnpackedGenParticle const*> genPhotons;

    for (auto& gen : event.genParticles) {
      // 22 is already testFlag-ed to be IsPrompt in EventMonophoton::copyGenParticles
      if ( !( (gen.pdgid == 22) || (std::abs(gen.pdgid) == 11) ) )
        continue;

      if ( gen.pt() < minGenPt_ || gen.pt() > maxGenPt_ )
        continue;

      if ( std::abs(gen.eta()) < minGenEta_ || std::abs(gen.eta()) > maxGenEta_ )
        continue;

      genPhotons.push_back(&gen);
    }

    nGenPhotons += genPhotons.size();
      
    // for (auto& pho : event.photons) {
    for (unsigned iP(0); iP != event.photons.size(); iP++) {
      auto& pho = event.photons[iP];

      if ( pho.scRawPt > maxPhoPt_ || pho.scRawPt < minPhoPt_ )
        continue;
      
      if ( std::abs(pho.eta()) > maxEta_ || std::abs(pho.eta()) < minEta_ )
        continue;
      
      pt = pho.pt();
      eta = pho.eta();
      phi = pho.phi();

      for (auto* gen : genPhotons) {
        if (gen->dR2(pho) < maxDR_ * maxDR_ &&
            std::abs(gen->pt() - pho.scRawPt) / gen->pt() < maxDPt_) {
          results[sMatch] = true;
          break;
        }
      }

      double pt2(pt * pt);
      //        double scEta(std::abs(pho.superCluster->eta));
      double scEta(std::abs(pho.eta()));

      results[sHoverE] = pho.passHOverE(wp_, era_);
      results[sSieie] = pho.passSieie(wp_, era_);
      results[sNHIso] = pho.passNHIso(wp_, era_);
      results[sPhIso] = pho.passPhIso(wp_, era_);
      results[sCHIso] = pho.passCHIso(wp_, era_);
      results[sCHMaxIso] = pho.passCHIsoMax(wp_, era_);
      results[sEveto] = pho.pixelVeto;
      results[sSpike] = std::abs(pho.time) < 3. && pho.sieie > 0.001 && pho.sipip > 0.001 && !(pho.eta() > 0. && pho.eta() < 0.15 && pho.phi() > 0.527580 && pho.phi() < 0.541795);
      results[sHalo] = pho.mipEnergy < 4.9;
      results[sPFVeto] = chargedPFVeto[iP];

      output->Fill();
    }
  }

  _outputFile->cd();
  TObjString(TString::Format("gen=%d", nGenPhotons)).Write();

  return nGenPhotons;
}
