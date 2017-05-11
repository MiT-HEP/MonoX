#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TDirectory.h"
#include "TLorentzVector.h"
#include "TROOT.h"
#include "TEntryListArray.h"

#include "EventTPPhoton.h"
#include "EventMonophoton.h"

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
  void fillSkim(TTree*, double weight, unsigned sampleId, long nEntries = -1);
  void writeSkim();
  void setReweight(TH1* _rwgt) { reweight_ = _rwgt; }

  TTree* getSkimTree(SkimType _t) const { return skimTrees_[_t]; }

private:
  TTree* skimTrees_[nSkimTypes]{};
  panda::EventTPPhoton outEvent_[nSkimTypes]{};

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

  auto* tree(new TTree("events", "template skim events"));
  panda::utils::BranchList blist{{"*"}};
  if (_type == kEG || _type == kMG)
    blist += {"!tp.mass2", "!looseTags"};

  outEvent_[_type].book(*tree, blist);
  skimTrees_[_type] = tree;
}

void
Skimmer::fillSkim(TTree* _input, double _weight, unsigned _sampleId, long _nEntries/* = -1*/)
{
  std::bitset<nSkimTypes> fill;
  for (unsigned iT(0); iT != nSkimTypes; ++iT) {
    if (skimTrees_[iT]) {
      fill.set(iT);
      outEvent_[iT].sample = _sampleId;
    }
  }

  if (fill.none())
    return;

  panda::EventMonophoton event;
  panda::utils::BranchList blist{{"photons"}};
  if (fill[kEG])
    blist += {"electrons"};
  if (fill[kMG] || fill[kMMG])
    blist += {"muons"};

  event.setAddress(*_input, blist);

  TChain fullInput("events");
  if (_input->InheritsFrom(TChain::Class())) {
    auto& chain(*static_cast<TChain*>(_input));
    for (auto* elem : *chain.GetListOfFiles())
      fullInput.Add(elem->GetTitle());
  }
  else {
    fullInput.Add(_input->GetCurrentFile()->GetName());
  }

  panda::EventMonophoton fullEvent;

  blist = {"run", "lumi", "event", "weight", "rho", "npv", "npvTrue", "jets", "t1Met"};

  fullEvent.setAddress(fullInput, blist);

  enum Lepton {
    lElectron,
    lMuon,
    nLeptons
  };

  std::bitset<nSkimTypes> leptonMask[2];
  leptonMask[lElectron].set(kEG);
  leptonMask[lMuon].set(kMG);
  leptonMask[lMuon].set(kMMG);

  panda::LeptonCollection* leptons[nLeptons] = {
    &event.electrons,
    &event.muons
  };

  std::function<bool(unsigned)> leptonTriggerMatch[nLeptons] = {
    [&event](unsigned iL)->bool { return event.electrons[iL].ecalIso < 0.1 && event.electrons[iL].hcalIso < 0.1; },
    [&event](unsigned iL)->bool { return event.muons[iL].triggerMatch[panda::Muon::fIsoMu24]; }
  };

  long iEntry(0);
  while (iEntry != _nEntries && event.getEntry(*_input, iEntry++) > 0) {
    if (iEntry % 1000000 == 1)
      std::cout << "Processing event " << iEntry << std::endl;

    for (unsigned iT(0); iT != nSkimTypes; ++iT) {
      if (skimTrees_[iT])
        outEvent_[iT].init();
    }

    bool loadEvent(false);

    for (auto& photon : event.photons) {
      std::cout << "photon" << std::endl;

      if (!photon.isEB || photon.scRawPt < 175.)
        continue;

      std::cout << "iseb" << std::endl;

      auto&& phoP(photon.p4());
      TLorentzVector pg(phoP.X(), phoP.Y(), phoP.Z(), phoP.E());

      for (auto iLepton : {lElectron, lMuon}) {
        auto& mask(leptonMask[iLepton]);

        if ((fill & mask).none())
          continue;

        std::cout << "mask" << std::endl;

        auto& lCol(*leptons[iLepton]);

        for (unsigned iL(0); iL != lCol.size(); ++iL) {
          auto& lepton(lCol[iL]);
          if (!lepton.tight)
            continue;

          std::cout << "lepton" << std::endl;

          if ((lepton.pt() < 27. && std::abs(lepton.eta()) < 2.1) || (_sampleId == 0 && !leptonTriggerMatch[iLepton](iL)))
            continue;

          std::cout << "trigger" << std::endl;

          if (photon.dR2(lepton) < 0.01)
            continue;

          // veto additional loose lepton
          unsigned iVeto(0);
          for (; iVeto != lCol.size(); ++iVeto) {
            if (iVeto == iL)
              continue;

            auto& veto(lCol[iVeto]);
            if (veto.pt() < 10.)
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

            if (iLepton == lElectron && static_cast<panda::Electron const&>(veto).veto)
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

            auto& tp(outEvent_[iT].tp.create_back());
            tp.mass = mlg;
            
            outEvent_[iT].tags.push_back(lepton);
            outEvent_[iT].probes.push_back(photon);

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

              auto& tp(outEvent_[iT].tp.create_back());
              tp.mass = mllg;
              tp.mass2 = pll.M();

              outEvent_[iT].tags.push_back(lepton);
              outEvent_[iT].looseTags.push_back(looseLepton);
              outEvent_[iT].probes.push_back(photon);

              loadEvent = true;
            }
          }
        }
      }
    }

    if (!loadEvent)
      continue;

    fullEvent.getEntry(fullInput, iEntry - 1);

    fullEvent.weight *= _weight;

    if (reweight_) {
      int iBin(reweight_->FindFixBin(fullEvent.npvTrue));
      //      int iBin(reweight_->FindFixBin(fullEvent_.npv)); // used for testing data PU reweight
      if (iBin == 0)
        iBin = 1;
      else if (iBin >= reweight_->GetNbinsX())
        iBin = reweight_->GetNbinsX();

      double w(reweight_->GetBinContent(iBin));
      if (w != w)
        w = 0.;
      if (w > 20.)
        w = 20.;

      fullEvent.weight *= w;
    }

    for (unsigned iT(0); iT != nSkimTypes; ++iT) {
      if (outEvent_[iT].tp.size() != 0)
        outEvent_[iT].fill(*skimTrees_[iT]);
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
