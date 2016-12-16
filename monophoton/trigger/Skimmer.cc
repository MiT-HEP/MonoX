#include "TreeEntries_simpletree.h"
#include "SimpleTreeUtils.h"

#include "TTree.h"
#include "TFile.h"
#include "TString.h"

#include <iostream>

enum EventType {
  kDiphoton,
  kElectronPhoton,
  kMuonPhoton,
  kJetHT,
  kDimuon,
  kDielectron,
  kElectronMET,
  nEventTypes
};

void
skim(TTree* _input, EventType _eventType, char const* _outputName, long _nEntries = -1)
{
  auto* outputFile(TFile::Open(_outputName, "recreate"));
  auto* output(new TTree("triggerTree", "trigger matching"));

  simpletree::Event event;

  bool hltPhoton135PFMET100;
  simpletree::Muon outMuon("probe");
  simpletree::Electron outElectron("probe");
  simpletree::Photon outPhoton("probe");
  simpletree::CorrectedMet outMet("probe");
  simpletree::TriggerHelper hltPhoton135PFMET100Helper("HLT_Photon135_PFMET100");

  event.book(*output, {"run", "lumi", "event", "rho", "npv"});
  
  switch (_eventType) {
  case kDimuon:
    outMuon.book(*output);
    break;
  case kDielectron:
    outElectron.book(*output);
    break;
  case kElectronMET:
    outMet.book(*output);
    output->Branch("hltPhoton135PFMET100", &hltPhoton135PFMET100, "hltPhoton135PFMET100/O");
    break;
  default:
    outPhoton.book(*output);
    break;
  }

  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"run", "lumi", "event", "rho", "npv", "hltBits", "photons", "electrons", "muons", "t1Met"});

  std::vector<simpletree::TriggerHelper> triggers;

  switch (_eventType) {
  case kDiphoton:
    triggers.emplace_back("HLT_Photon36_R9Id90_HE10_Iso40_EBOnly_PFMET40");
    break;
  case kElectronPhoton:
    triggers.emplace_back("HLT_Ele27_WPTight_Gsf");
    break;
  case kMuonPhoton:
    triggers.emplace_back("HLT_IsoMu20");
    break;
  case kJetHT:
    triggers.emplace_back("HLT_DiPFJetAve80");
    triggers.emplace_back("HLT_PFHT400_SixJet30");
    triggers.emplace_back("HLT_HT650");
    break;
  case kDimuon:
    triggers.emplace_back("HLT_IsoMu20");
    triggers.emplace_back("HLT_IsoTkMu20");
    break;
  case kDielectron:
    triggers.emplace_back("HLT_Ele27_WPTight_Gsf");
    break;
  case kElectronMET:
    triggers.emplace_back("HLT_Ele27_WPTight_Gsf");
    break;
  default:
    break;
  }

  auto passTrigger([&triggers, &event]()->bool {
      if (triggers.size() == 0)
        return true;

      for (auto& h : triggers) {
        if (h.pass(event))
          return true;
      }
      return false;
    });

  long iEntry(0);
  while (iEntry != _nEntries && _input->GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << iEntry << std::endl;

    try {
      if (!passTrigger())
        continue;
    }
    catch (std::exception& ex) {
      std::cerr << ex.what() << std::endl;
      return;
    }

    if (_eventType == kDimuon) {
      for (auto& muon : event.muons) {
        if (!muon.tight)
          continue;
        
        unsigned iTag(0);
        for (; iTag != event.muons.size(); ++iTag) {
          auto& tag(event.muons[iTag]);
          if (&tag == &muon)
            continue;

          if (!tag.tight)
            continue;

          if (tag.pt < 25.)
            continue;

          if (!tag.matchHLT[simpletree::fMu20] && !tag.matchHLT[simpletree::fMuTrk20])
            continue;

          float mass = (muon.p4() + tag.p4()).M();
          if (mass > 61. && mass < 121.)
            break;
        }
        if (iTag == event.muons.size())
          continue;
        
        outMuon = muon;
        output->Fill();
      }
    }      
    else if (_eventType == kDielectron) {
      for (auto& electron : event.electrons) {
        if (!electron.tight)
          continue;
        
        unsigned iTag(0);
        for (; iTag != event.electrons.size(); ++iTag) {
          auto& tag(event.electrons[iTag]);
          if (&tag == &electron)
            continue;
          
          if (!(tag.pt > 29. && tag.tight && tag.matchHLT[simpletree::fEl27Tight]))
            continue;

          float mass = (electron.p4() + tag.p4()).M();
          if (mass > 61. && mass < 121.)
            break;
        }
        if (iTag == event.electrons.size())
          continue;
        
        outElectron = electron;
        output->Fill();
      }
    }
    else if (_eventType == kElectronMET) {
      unsigned iTag(0);
      for (; iTag != event.electrons.size(); ++iTag) {
        auto& electron(event.electrons[iTag]);
        if (electron.tight && electron.pt > 140.)
          break;
      }
      if (iTag == event.electrons.size())
        continue;

      hltPhoton135PFMET100 = hltPhoton135PFMET100Helper.pass(event);

      outMet = event.t1Met;
      output->Fill();
    }
    else {
      int iPh(-1);
      for (auto& photon : event.photons) {
        ++iPh;
        if (!photon.medium)
          continue;
        
        switch (_eventType) {
        case kDiphoton:
          if (!photon.pixelVeto)
            continue;
          break;
        case kDielectron:
          if (photon.pixelVeto)
            continue;
          break;
        default:
          break;
        }

        if (_eventType == kDiphoton) {
          unsigned iTag(0);
          for (; iTag != event.photons.size(); ++iTag) {
            auto& tag(event.photons[iTag]);
            if (&tag == &photon)
              continue;

            if (tag.matchHLT[simpletree::fPh36EBR9Iso])
              break;
          }
          if (iTag == event.photons.size())
            continue;
        }
        else if (_eventType == kElectronPhoton) {
          unsigned iTag(0);
          for (; iTag != event.electrons.size(); ++iTag) {
            auto& tag(event.electrons[iTag]);
            if (tag.dR2(photon) < 0.09)
              continue;

            if (tag.matchHLT[simpletree::fEl27Tight])
              break;
          }
          if (iTag == event.electrons.size())
            continue;
        }
        else if (_eventType == kMuonPhoton) {
          unsigned iTag(0);
          for (; iTag != event.muons.size(); ++iTag) {
            auto& tag(event.muons[iTag]);
            if (tag.dR2(photon) < 0.09)
              continue;

            if (tag.matchHLT[simpletree::fMu20] || tag.matchHLT[simpletree::fMuTrk20])
              break;
          }
          if (iTag == event.muons.size())
            continue;
        }
        
        outPhoton = photon;
        output->Fill();
      } // probe photons
    } // skim switch
  } // nEntries

  outputFile->cd();
  output->Write();
  delete outputFile;
}
