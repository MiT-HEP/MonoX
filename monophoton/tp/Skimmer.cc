#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TDirectory.h"
#include "TLorentzVector.h"
#include "TROOT.h"
#include "TEntryListArray.h"

#include "TreeEntries_simpletree.h"

#include <stdexcept>
#include <string>
#include <iostream>
#include <cstring>
#include <bitset>
#include <functional>

enum SkimType {
  kEG,
  kMG,
  kMMG,
  nSkimTypes
};

class Skimmer {
public:
  Skimmer() {}
  ~Skimmer();

  void addSkim(SkimType, char const* fileName);
  void limitSkim(SkimType t) { enabled_.set(t); }
  void resetLimit() { enabled_.reset(); }
  void fillSkim(TTree*, double weight, unsigned sampleId, long nEntries = -1);
  void writeSkim();
  void setReweight(TH1* _rwgt) { reweight_ = _rwgt; }

  TTree* getSkimTree(SkimType _t) const { return skimTrees_[_t]; }

private:
  static unsigned const NMAX{simpletree::Particle::array_data::NMAX};

  TTree* skimTrees_[nSkimTypes]{};
  std::bitset<nSkimTypes> enabled_{};
  simpletree::Event fullEvent_{};

  unsigned nPairs_[nSkimTypes]{};
  float mass_[nSkimTypes][NMAX * (NMAX - 1) / 2]{};
  float mass2_[nSkimTypes][NMAX * (NMAX - 1) / 2]{};
  simpletree::LeptonCollection tags_[nSkimTypes];
  simpletree::LeptonCollection looseTags_[nSkimTypes];
  simpletree::PhotonCollection probes_[nSkimTypes];
  unsigned sampleId_{0};

  TH1* reweight_{0};
};

Skimmer::~Skimmer()
{
  for (auto* tree : skimTrees_) {
    if (tree && tree->InheritsFrom(TChain::Class()))
      delete tree;
  }
}

void
Skimmer::addSkim(SkimType _type, char const* _fileName)
{
  std::cout << "Adding " << _fileName << " to skim" << std::endl;

  TFile* file = TFile::Open(_fileName, "recreate");

  if (!file || file->IsZombie())
    throw std::runtime_error(std::string("File ") + _fileName + " could not be opened.");

  file->cd();

  auto* tree(new TTree("skimmedEvents", "template skim"));
  fullEvent_.book(*tree, {"run", "lumi", "event", "weight", "rho", "npv", "jets", "t1Met", "hlt"});

  tree->Branch("tp.size", nPairs_ + _type, "size/i");
  tree->Branch("tp.mass", mass_[_type], "mass[tp.size]/F");
  tags_[_type].setName("tags");
  probes_[_type].setName("probes");
  tags_[_type].book(*tree);
  probes_[_type].book(*tree);
  if (_type == kMMG) {
    tree->Branch("tp.mass2", mass2_[_type], "mass2[tp.size]/F");
    looseTags_[_type].setName("looseTags");
    looseTags_[_type].book(*tree);
  }
  tree->Branch("sample", &sampleId_, "sample/i");

  skimTrees_[_type] = tree;
}

void
Skimmer::fillSkim(TTree* _input, double _weight, unsigned _sampleId, long _nEntries/* = -1*/)
{
  std::bitset<nSkimTypes> fill;
  for (unsigned iT(0); iT != nSkimTypes; ++iT) {
    if ((enabled_.none() || enabled_[iT]) && skimTrees_[iT]) {
      fill.set(iT);
    }
  }

  if (fill.none())
    return;

  sampleId_ = _sampleId;

  simpletree::Event event;
  event.setStatus(*_input, false);
  flatutils::BranchList bList{"photons.pt", "photons.eta", "photons.phi", "photons.scRawPt",
      "photons.chIso", "photons.nhIso", "photons.phIso", "photons.sieie", "photons.sipip", "photons.sieip",
      "photons.hOverE", "photons.pixelVeto", "photons.csafeVeto", "photons.medium"};
  if (fill[kEG])
    bList.push_back("electrons");
  if (fill[kMG] || fill[kMMG])
    bList.push_back("muons");

  event.setAddress(*_input, bList);

  TChain fullInput("events");
  if (_input->InheritsFrom(TChain::Class())) {
    auto& chain(*static_cast<TChain*>(_input));
    for (auto* elem : *chain.GetListOfFiles())
      fullInput.Add(elem->GetTitle());
  }
  else {
    fullInput.Add(_input->GetCurrentFile()->GetName());
  }

  bList = {"run", "lumi", "event", "weight", "rho", "npv", "npvTrue", "jets", "t1Met", "hlt"};

  fullEvent_.setStatus(fullInput, false);
  fullEvent_.setAddress(fullInput, bList);

  enum Lepton {
    lElectron,
    lMuon,
    nLeptons
  };

  std::bitset<nSkimTypes> leptonMask[2];
  leptonMask[lElectron].set(kEG);
  leptonMask[lMuon].set(kMG);
  leptonMask[lMuon].set(kMMG);

  simpletree::LeptonCollection* leptons[nLeptons] = {
    &event.electrons,
    &event.muons
  };

  std::function<bool(unsigned)> leptonTriggerMatch[nLeptons] = {
    [&event](unsigned iL)->bool { return event.electrons[iL].matchHLT[simpletree::fEl23Loose]; },
    [](unsigned)->bool { return true; }
    //    [&event](unsigned iL)->bool { return event.muons[iL].matchHLT[simpletree::fMu24]; }
  };

  long iEntry(0);
  while (iEntry != _nEntries && _input->GetEntry(iEntry++) > 0) {
    if (iEntry % 1000000 == 1)
      std::cout << "Processing event " << iEntry << std::endl;

    for (unsigned iT(0); iT != nSkimTypes; ++iT) {
      nPairs_[iT] = 0;
      tags_[iT].clear();
      looseTags_[iT].clear();
      probes_[iT].clear();
    }

    bool loadEvent(false);

    for (unsigned iP(0); iP != event.photons.size(); ++iP) {
      auto& photon(event.photons[iP]);

      if (!photon.isEB)
        continue;

      auto&& phoP(photon.p4());
      TLorentzVector pg(phoP.X(), phoP.Y(), phoP.Z(), phoP.E());

      for (auto iLepton : {lElectron, lMuon}) {
        auto& mask(leptonMask[iLepton]);

        if ((fill & mask).none())
          continue;

        auto& lCol(*leptons[iLepton]);

        for (unsigned iL(0); iL != lCol.size(); ++iL) {
          auto& lepton(lCol[iL]);
          if (!lepton.tight)
            continue;

          if (lepton.pt < 25. || (sampleId_ == 0 && !leptonTriggerMatch[iLepton](iL)))
            continue;

          if (photon.dR2(lepton) < 0.01)
            continue;

          // veto additional loose lepton
          unsigned iVeto(0);
          for (; iVeto != lCol.size(); ++iVeto) {
            if (iVeto == iL)
              continue;

            auto& veto(lCol[iVeto]);
            if (veto.pt < 10.)
              continue;
            
            // Our electron veto does not reject photons overlapping with e/mu
            // Cases:
            // 1. One electron radiates hard, gets deflected by a large angle
            //   -> The radiation is a photon. Do not consider it in the set of probes for e->g fake rate measurement.
            // 2. One electron radiates hard but stays collinear with the radiation
            //   -> This is a fake photon.
            // Large angle is defined by the isolation cone of the lepton; if the photon is within the cone, the lepton will fail the
            // veto identification and therefore the event will stay in the candidate sample.
            if (photon.dR2(veto) < 0.09)
              continue;

            if (iLepton == lElectron && static_cast<simpletree::Electron const&>(veto).veto)
              break;
            if (iLepton == lMuon && veto.loose)
              break;
          }
          if (iVeto != lCol.size())
            continue;

          auto&& tagP(lepton.p4());

          double mlg((pg + TLorentzVector(tagP.X(), tagP.Y(), tagP.Z(), tagP.E())).M());

          for (unsigned iT : {kEG, kMG}) {
            if (!mask[iT] || !fill[iT])
              continue;

            if (mlg < 20. || mlg > 160.)
              continue;

            mass_[iT][nPairs_[iT]] = mlg;
            tags_[iT].push_back(lepton);
            probes_[iT].push_back(photon);

            ++nPairs_[iT];
            loadEvent = true;
          }

          if (iLepton != lMuon || !fill[kMMG])
            continue;

          for (unsigned iL2(0); iL2 != leptons[iLepton]->size(); ++iL2) {
            if (iL2 == iL)
              continue;

            auto& looseLepton((*leptons[iLepton])[iL2]);
            if (!looseLepton.loose)
              continue;

            if (photon.dR2(looseLepton) < 0.01)
              continue;

            auto&& looseTagP(looseLepton.p4());

            TLorentzVector pll(tagP.X() + looseTagP.X(), tagP.Y() + looseTagP.Y(), tagP.Z() + looseTagP.Z(), tagP.E() + looseTagP.E());
            double mllg((pg + pll).M());

            for (unsigned iT : {kMMG}) {
              if (!mask[iT] || !fill[iT])
                continue;

              if (mllg < 20. || mllg > 160.)
                continue;

              mass_[iT][nPairs_[iT]] = mllg;
              mass2_[iT][nPairs_[iT]] = pll.M();
              tags_[iT].push_back(lepton);
              looseTags_[iT].push_back(looseLepton);
              probes_[iT].push_back(photon);

              ++nPairs_[iT];
              loadEvent = true;
            }
          }
        }
      }
    }

    if (loadEvent)
      fullInput.GetEntry(iEntry - 1);
    else
      continue;

    fullEvent_.weight *= _weight;
    
    if (reweight_) {
      int iBin(reweight_->FindFixBin(fullEvent_.npvTrue));
      if (iBin == 0)
        iBin = 1;
      else if (iBin >= reweight_->GetNbinsX())
        iBin = reweight_->GetNbinsX();

      fullEvent_.weight *= reweight_->GetBinContent(iBin);
    }

    for (unsigned iT(0); iT != nSkimTypes; ++iT) {
      if (nPairs_[iT] != 0)
        skimTrees_[iT]->Fill();
    }
  }

  for (unsigned iT(0); iT != nSkimTypes; ++iT) {
    if (!skimTrees_[iT])
      continue;

    auto* file = skimTrees_[iT]->GetCurrentFile();
    file->cd();
    skimTrees_[iT]->Write();

    delete file;
    skimTrees_[iT] = 0;
  }
}
