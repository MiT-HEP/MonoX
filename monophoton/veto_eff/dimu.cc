#include "TreeEntries_simpletree.h"

#include "TTree.h"
#include "TFile.h"
#include "TH1.h"

void
dimu(TTree* _input, char const* _outputName, double _sampleWeight = 1., TH1* _npvweight = 0)
{
  simpletree::Event event;
  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"weight", "muons", "electrons", "jets", "npv"});

  TFile* outputFile(TFile::Open(_outputName, "recreate"));
  TTree* output(new TTree("skim", "efficiency"));
  double weight;
  float mass;
  bool eleveto;
  bool muveto;
  unsigned short njet;
  float ht;
  float leadjetpt;

  output->Branch("weight", &weight, "weight/D");
  output->Branch("mass", &mass, "mass/F");
  output->Branch("eleveto", &eleveto, "eleveto/O");
  output->Branch("muveto", &muveto, "muveto/O");
  output->Branch("njet", &njet, "njet/s");
  output->Branch("ht", &ht, "ht/F");
  output->Branch("npv", &event.npv, "npv/s");
  output->Branch("leadjetpt", &leadjetpt, "leadjetpt/F");

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    auto& muons(event.muons);
    auto& electrons(event.electrons);

    unsigned tights[] = {unsigned(-1), unsigned(-1)};

    for (unsigned iMu1(0); iMu1 != muons.size(); ++iMu1) {
      auto& mu1(muons[iMu1]);
      if (!mu1.tight)
        continue;

      for (unsigned iMu2(iMu1 + 1); iMu2 != muons.size(); ++iMu2) {
        auto& mu2(muons[iMu2]);
        if (!mu2.tight)
          continue;

        mass = (mu1.p4() + mu2.p4()).M();
        if (mass > 61. && mass < 121.) {
          tights[0] = iMu1;
          tights[1] = iMu2;
          break;
        }
      }
      if (tights[0] < muons.size())
        break;
    }
    if (tights[0] > muons.size())
      continue;

    muveto = false;
    for (unsigned iMu(0); iMu != muons.size(); ++iMu) {
      auto& muon(muons[iMu]);
      if (muon.loose && muon.pt > 10. && iMu != tights[0] && iMu != tights[1]) {
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
    leadjetpt = 0.;
    ht = 0.;
    for (unsigned iJ(0); iJ != event.jets.size(); ++iJ) {
      auto& jet(event.jets[iJ]);
      if (jet.dR2(muons[tights[0]]) < 0.16 || jet.dR2(muons[tights[1]]) < 0.16)
        continue;

      ++njet;
      ht += jet.pt;
      if (jet.pt > leadjetpt)
        leadjetpt = jet.pt;
    }

    weight = _sampleWeight * event.weight;
    if (_npvweight) {
      int iX(_npvweight->FindFixBin(event.npv));
      if (iX == 0)
        iX = 1;
      if (iX > _npvweight->GetNbinsX())
        iX = _npvweight->GetNbinsX();
      weight *= _npvweight->GetBinContent(iX);
    }

    output->Fill();
  }

  outputFile->cd();
  output->Write();
  delete outputFile;
}
