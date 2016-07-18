#include "TreeEntries_simpletree.h"

#include "TTree.h"
#include "TFile.h"
#include "TH1.h"

void
monoph(TTree* _input, char const* _outputName, double _sampleWeight = 1., TH1* _puweight = 0)
{
  simpletree::Event event;
  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"photons.matchL1", "partons.pid", "promptFinalStates.ancestor"}, false);

  TFile* outputFile(TFile::Open(_outputName, "recreate"));
  TTree* output(new TTree("skim", "efficiency"));
  double weight;
  float mass;
  bool eleveto;
  bool muveto;
  unsigned short njet;
  float ht;

  output->Branch("lumi", &event.lumi, "lumi/i");
  output->Branch("event", &event.event, "event/i");
  output->Branch("weight", &weight, "weight/D");
  output->Branch("mass", &mass, "mass/F");
  output->Branch("eleveto", &eleveto, "eleveto/O");
  output->Branch("muveto", &muveto, "muveto/O");
  output->Branch("njet", &njet, "njet/s");
  output->Branch("ht", &ht, "ht/F");
  output->Branch("npv", &event.npv, "npv/s");
  output->Branch("npvTrue", &event.npvTrue, "npvTrue/F");

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    auto& particles(event.promptFinalStates);

    unsigned iF(0);
    for (; iF != particles.size(); ++iF) {
      auto& particle(particles[iF]);
      if (particle.pid == 22 && std::abs(particle.eta) < 1.4442 && particle.pt > 175.)
        break;
    }
    if (iF == particles.size())
      continue;
    
    auto& photon(particles[iF]);

    auto& muons(event.muons);
    auto& electrons(event.electrons);

    muveto = false;
    for (unsigned iMu(0); iMu != muons.size(); ++iMu) {
      auto& muon(muons[iMu]);
      if (muon.loose && muon.pt > 10.) {
        muveto =true;
        break;
      }
    }

    eleveto = false;
    for (unsigned iEle(0); iEle != electrons.size(); ++iEle) {
      auto& electron(electrons[iEle]);
      if (electron.loose && electron.pt > 10.) {
        eleveto =true;
        break;
      }
    }

    njet = 0;
    ht = 0.;
    for (unsigned iJ(0); iJ != event.jets.size(); ++iJ) {
      auto& jet(event.jets[iJ]);
      if (jet.dR2(photon) < 0.16)
        continue;

      ++njet;
      ht += event.jets[iJ].pt;
    }

    weight = _sampleWeight * event.weight;
    if (_puweight) {
      int iX(_puweight->FindFixBin(event.npvTrue));
      if (iX == 0)
        iX = 1;
      if (iX > _puweight->GetNbinsX())
        iX = _puweight->GetNbinsX();
      weight *= _puweight->GetBinContent(iX);
    }

    output->Fill();
  }

  outputFile->cd();
  output->Write();
  delete outputFile;
}
