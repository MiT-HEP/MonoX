#include "Objects/interface/Event.h"
#include "TTree.h"
#include "TFile.h"
#include "TDirectory.h"
#include "TVector2.h"
#include "TString.h"
#include <vector>
#include <utility>

// NEED TO DO THIS WITH PANDA 003

class GenKinematics {
public:
  void addPath(char const* path) { paths_.push_back(path); }
  void makeTree(TDirectory* _outputDir, long _nEntries = -1);

private:
  std::vector<TString> paths_{};
};

void
GenKinematics::makeTree(TDirectory* _outputDir, long _nEntries/* = -1*/)
{
  //mkbranch
  float weight;
  float gammaPt;
  float gammaEta;
  float jet1Pt;
  float jet1Eta;
  float jet2Pt;
  float jet2Eta;
  float vPt;
  float vEta;
  float vgammaDPhi;
  float jgammaDPhi;
  bool hasPhoton;
  bool hasMatchingPhoton;
  bool hasBoson;
  //mkbranch

  _outputDir->cd();

  auto* output(new TTree("genkine", "gen kinematics"));
  output->Branch("weight", &weight, "weight/F");
  output->Branch("gammaPt", &gammaPt, "gammaPt/F");
  output->Branch("gammaEta", &gammaEta, "gammaEta/F");
  output->Branch("jet1Pt", &jet1Pt, "jet1Pt/F");
  output->Branch("jet1Eta", &jet1Eta, "jet1Eta/F");
  output->Branch("jet2Pt", &jet2Pt, "jet2Pt/F");
  output->Branch("jet2Eta", &jet2Eta, "jet2Eta/F");
  output->Branch("vPt", &vPt, "vPt/F");
  output->Branch("vEta", &vEta, "vEta/F");
  output->Branch("vgammaDPhi", &vgammaDPhi, "vgammaDPhi/F");
  output->Branch("jgammaDPhi", &jgammaDPhi, "jgammaDPhi/F");
  output->Branch("hasPhoton", &hasPhoton, "hasPhoton/O");
  output->Branch("hasMatchingPhoton", &hasMatchingPhoton, "hasMatchingPhoton/O");
  output->Branch("hasBoson", &hasBoson, "hasBoson/O");

  long iGlobalEntry(0);

  for (auto& path : paths_) {
    auto* source(TFile::Open(path));
    auto* input(static_cast<TTree*>(source->Get("events")));
    
    panda::Event event;

    event.setAddress(*input, {"!*", "weight", "partons", "genParticles", "ak4GenJets"});

    long iEntry(0);
    while (iGlobalEntry != _nEntries && event.getEntry(*input, iEntry++) > 0) {
      if (++iGlobalEntry % 100000 == 1)
        std::cout << iGlobalEntry << std::endl;

      weight = event.weight;

      gammaPt = 0.;
      gammaEta = 0.;
      jet1Pt = 0.;
      jet1Eta = 0.;
      jet2Pt = 0.;
      jet2Eta = 0.;
      vPt = 0.;
      vEta = 0.;
      vgammaDPhi = 0.;
      jgammaDPhi = 0.;
      hasPhoton = false;
      hasMatchingPhoton = false;
      hasBoson = false;

      panda::GenParticle* photon(0);
      typedef std::pair<panda::GenParticle*, panda::GenParticle*> DecayPair;
      std::vector<DecayPair> leptonPairs;
      panda::GenParticle* nullp(0);

      for (auto& gen : event.genParticles) {
        if (!gen.finalState)
          continue;

        unsigned absId(std::abs(gen.pdgid));

        if (absId == 22) {
          if (!photon || gen.pt() > photon->pt()) {
            hasPhoton = true;
            photon = &gen;
          }
        }
        else if (absId > 10 && absId < 17) {
          for (auto& part : event.partons) {
            if (part.pdgid == gen.pdgid && part.dR2(gen) < 0.8) {
              bool needNew(true);
              for (auto& p : leptonPairs) {
                if (gen.pdgid > 0 && !p.first && std::abs(part.pdgid + p.second->pdgid) <= 1) {
                  p.first = &gen;
                  needNew = false;
                }
                else if (gen.pdgid < 0 && !p.second && std::abs(part.pdgid + p.first->pdgid) <= 1) {
                  p.second = &gen;
                  needNew = false;
                }
              }
              if (needNew) {
                if (gen.pdgid > 0)
                  leptonPairs.emplace_back(&gen, nullp);
                else
                  leptonPairs.emplace_back(nullp, &gen);
              }

              break;
            }
          }
        }
      }

      TLorentzVector pBoson;
      for (auto& p : leptonPairs) {
        if (!p.first || !p.second)
          continue;
          
        hasBoson = true;
        
        TLorentzVector p4(p.first->p4() + p.second->p4());
        if (p4.Pt() > pBoson.Pt())
          pBoson = p4;
      }

      if (hasPhoton) {
        gammaPt = photon->pt();
        gammaEta = photon->eta();

        for (auto& part : event.partons) {
          if (part.pdgid == 22 && part.dR2(*photon) < 0.8) {
            hasMatchingPhoton = true;
            break;
          }
        }
      }

      if (hasBoson) {
        vPt = pBoson.Pt();
        vEta = pBoson.Eta();
      }

      if (hasPhoton && hasBoson)
        vgammaDPhi = std::abs(TVector2::Phi_mpi_pi(photon->phi() - pBoson.Phi()));

      // genJets are sorted by pt

      for (auto& jet : event.ak4GenJets) {
        if (hasPhoton && jet.dR2(*photon) < 0.16)
          continue;

        if (jet1Pt == 0.) {
          jet1Pt = jet.pt();
          jet1Eta = jet.eta();
          if (hasPhoton)
            jgammaDPhi = std::abs(TVector2::Phi_mpi_pi(photon->phi() - jet.phi()));
        }
        else {
          jet2Pt = jet.pt();
          jet2Eta = jet.eta();
          break;
        }
      }

      output->Fill();
    }

    delete source;
  }

  _outputDir->cd();
  output->Write();

  delete output;
}
