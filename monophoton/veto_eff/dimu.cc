/*
  Compute the electron & muon veto flags on Z(mumu) samples (data & MC).
  Skim result will be used to derive the efficiency data/MC scale factor.
*/

#include "TreeEntries_simpletree.h"

#include "TTree.h"
#include "TFile.h"
#include "TH1.h"

void _dimu(TTree*, char const*, bool, double, TH1*);

void
dimu(TTree* _input, char const* _outputName, double _sampleWeight = 1., TH1* _puweight = 0)
{
  _dimu(_input, _outputName, false, _sampleWeight, _puweight);
}

void
mumug(TTree* _input, char const* _outputName, double _sampleWeight = 1., TH1* _puweight = 0)
{
  _dimu(_input, _outputName, true, _sampleWeight, _puweight);
}

void
_dimu(TTree* _input, char const* _outputName, bool _gamma, double _sampleWeight, TH1* _puweight)
{
  simpletree::Event event;
  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"weight", "muons", "electrons", "photons", "jets", "npv", "npvTrue"});

  TFile* outputFile(TFile::Open(_outputName, "recreate"));
  TTree* output(new TTree("skim", "efficiency"));
  double weight;
  float mass;
  float massg;
  bool eleveto;
  bool muveto;
  unsigned short njet;
  float ht;
  float leadjetpt;

  output->Branch("weight", &weight, "weight/D");
  output->Branch("mass", &mass, "mass/F");
  if (_gamma)
    output->Branch("massg", &massg, "massg/F");
  output->Branch("eleveto", &eleveto, "eleveto/O");
  output->Branch("muveto", &muveto, "muveto/O");
  output->Branch("njet", &njet, "njet/s");
  output->Branch("ht", &ht, "ht/F");
  output->Branch("npv", &event.npv, "npv/s");
  output->Branch("npvTrue", &event.npvTrue, "npvTrue/F");
  output->Branch("leadjetpt", &leadjetpt, "leadjetpt/F");

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    auto& muons(event.muons);
    auto& electrons(event.electrons);
    simpletree::Photon const* photon(0);

    if (_gamma) {
      for (auto& ph : event.photons) {
        if (ph.isEB && ph.scRawPt > 135. && ph.medium && ph.pixelVeto && ph.mipEnergy < 4.9 && ph.sipip > 0.001 && ph.sieie > 0.001) {
          photon = &ph;
          break;
        }
      }
      if (!photon)
        continue;
    }

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

    if (photon)
      massg = (muons[tights[0]].p4() + muons[tights[1]].p4() + photon->p4()).M();

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
