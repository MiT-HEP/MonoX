#include "TreeEntries_simpletree.h"
#include "SimpleTreeUtils.h"

#include "TTree.h"
#include "TFile.h"
#include "TString.h"

#include <iostream>

enum EventType {
  kDiphoton,
  kDielectron,
  kMuonPhoton,
  kJetHT,
  nEventTypes
};

void
skim(TTree* _input, EventType _eventType, char const* _outputName, long _nEntries = -1)
{
  auto* outputFile(TFile::Open(_outputName, "recreate"));
  auto* output(new TTree("triggerTree", "trigger matching"));

  unsigned runNum;
  unsigned lumiNum;
  unsigned eventNum;
  float rho;
  unsigned short npv;
  simpletree::PhotonCollection outPhotons("probes");
  output->Branch("run", &runNum, "run/i");
  output->Branch("lumi", &lumiNum, "lumi/i");
  output->Branch("event", &eventNum, "event/i");
  output->Branch("rho", &rho, "rho/F");
  output->Branch("npv", &npv, "npv/s");
  outPhotons.book(*output);

  simpletree::Event event;
  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"run", "lumi", "event", "rho", "npv", "hlt", "photons", "electrons", "muons"});

  simpletree::TriggerHelper* trigger(0);
  switch (_eventType) {
  case kDiphoton:
    trigger = new simpletree::TriggerHelper("HLT_Photon36_R9Id90_HE10_Iso40_EBOnly_PFMET40");
    break;
  case kDielectron:
    trigger = new simpletree::TriggerHelper("HLT_Ele23_WPLoose_Gsf");
    break;
  case kMuonPhoton:
    trigger = new simpletree::TriggerHelper("HLT_IsoMu20");
    break;
  default:
    break;
  }

  unsigned count[10]{};

  long iEntry(0);
  while (iEntry != _nEntries && _input->GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << iEntry << std::endl;

    if (trigger && !trigger->pass(event))
      continue;

    ++count[0];

    outPhotons.clear();

    bool passCut[10]{};

    for (auto& photon : event.photons) {
      if (!photon.medium)
        continue;

      passCut[0] = true;

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

      passCut[1] = true;

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
      else if (_eventType == kDielectron) {
        unsigned iTag(0);
        for (; iTag != event.electrons.size(); ++iTag) {
          auto& tag(event.electrons[iTag]);
          if (tag.dR2(photon) < 0.09)
            continue;

          if (tag.matchHLT[simpletree::fEl23Loose])
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

          if (tag.matchHLT[simpletree::fMu20])
            break;
        }
        if (iTag == event.muons.size())
          continue;
      }

      passCut[2] = true;

      outPhotons.push_back(photon);
    }

    for (unsigned iP(0); iP != 3; ++iP) {
      if (passCut[iP])
        ++count[iP + 1];
    }

    if (outPhotons.size() == 0)
      continue;

    runNum = event.run;
    lumiNum = event.lumi;
    eventNum = event.event;
    rho = event.rho;
    npv = event.npv;

    output->Fill();
  }

  // for (unsigned c : count)
  //   std::cout << c << std::endl;

  outputFile->cd();
  output->Write();
  delete outputFile;
}
