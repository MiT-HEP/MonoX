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
  kSingleElectron,
  nEventTypes
};

void
skim(TTree* _input, EventType _eventType, char const* _outputName, bool st19, long _nEntries = -1)
{
  auto* outputFile(TFile::Open(_outputName, "recreate"));
  auto* output(new TTree("triggerTree", "trigger matching"));

  unsigned runNum;
  unsigned lumiNum;
  unsigned eventNum;
  float rho;
  unsigned short npv;
  bool hltPhoton135PFMET100;

  simpletree::MuonCollection outMuons("probe");
  simpletree::ElectronCollection outElectrons("probe");
  simpletree::PhotonCollection outPhotons("probe"); // will only have one element
  simpletree::CorrectedMet outMet("probe");
  simpletree::TriggerHelper hltPhoton135PFMET100Helper("HLT_Photon135_PFMET100");

  output->Branch("run", &runNum, "run/i");
  output->Branch("lumi", &lumiNum, "lumi/i");
  output->Branch("event", &eventNum, "event/i");
  output->Branch("rho", &rho, "rho/F");
  output->Branch("npv", &npv, "npv/s");
  
  switch (_eventType) {
  case kDimuon:
    outMuons.book(*output);
    outMuons.resize(1);
    break;
  case kDielectron:
    outElectrons.book(*output);
    outElectrons.resize(1);
    break;
  case kSingleElectron:
    outMet.book(*output);
    output->Branch("hltPhoton135PFMET100", &hltPhoton135PFMET100, "hltPhoton135PFMET100/O");
    break;
  default:
    outPhotons.book(*output);
    outPhotons.resize(1);
    break;
  }

  simpletree::Event event;
  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"run", "lumi", "event", "rho", "npv", "hltBits", "photons", "electrons", "muons", "t1Met"});

  bool matchL1[simpletree::Particle::array_data::NMAX][simpletree::nPhotonL1Objects];
  if (st19)
    _input->SetBranchAddress("photons.matchL1", matchL1);

  std::vector<simpletree::TriggerHelper*> triggers;
  switch (_eventType) {
  case kDiphoton:
    triggers.push_back(new simpletree::TriggerHelper("HLT_Photon36_R9Id90_HE10_Iso40_EBOnly_PFMET40"));
    break;
  case kElectronPhoton:
    triggers.push_back(new simpletree::TriggerHelper("HLT_Ele27_WPTight_Gsf"));
    break;
  case kMuonPhoton:
    triggers.push_back(new simpletree::TriggerHelper("HLT_IsoMu20"));
    break;
  case kJetHT:
    triggers.push_back(new simpletree::TriggerHelper("HLT_DiPFJetAve80"));
    triggers.push_back(new simpletree::TriggerHelper("HLT_PFHT400_SixJet30"));
    triggers.push_back(new simpletree::TriggerHelper("HLT_HT650"));
    break;
  case kDimuon:
    triggers.push_back(new simpletree::TriggerHelper("HLT_IsoMu20"));
    triggers.push_back(new simpletree::TriggerHelper("HLT_IsoTkMu20"));
    break;
  case kDielectron:
    triggers.push_back(new simpletree::TriggerHelper("HLT_Ele27_WPTight_Gsf"));
    break;
  case kSingleElectron:
    triggers.push_back(new simpletree::TriggerHelper("HLT_Ele27_WPTight_Gsf"));
    break;
  default:
    break;
  }

  auto passTrigger([&triggers, &event]()->bool {
      if (triggers.size() == 0)
        return true;

      for (auto* h : triggers) {
        if (h->pass(event))
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

    runNum = event.run;
    lumiNum = event.lumi;
    eventNum = event.event;
    rho = event.rho;
    npv = event.npv;

    if (_eventType == kDimuon) {
      for (auto& muon : event.muons) {
	if (!muon.tight)
	  continue;
	
	unsigned iTag(0);
	for (; iTag != event.muons.size(); ++iTag) {
	  auto& tag(event.muons[iTag]);
	  if (&tag == &muon)
	    continue;
	  
	  if ( !(tag.pt > 25. && tag.tight && tag.matchHLT[simpletree::fMu20]))
	    continue;

	  float mass = (muon.p4() + tag.p4()).M();
	  if (mass > 61. && mass < 121.)
	    break;
	}
	if (iTag == event.muons.size())
	  continue;
	
	outMuons[0] = muon;
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
	  
	  if ( !(tag.pt > 25. && tag.tight && tag.matchHLT[simpletree::fEl23Loose]))
	    continue;

	  float mass = (electron.p4() + tag.p4()).M();
	  if (mass > 61. && mass < 121.)
	    break;
	}
	if (iTag == event.electrons.size())
	  continue;
	
	outElectrons[0] = electron;
	output->Fill();
      }
    }
    else if (_eventType == kSingleElectron) {
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

	    if (tag.matchHLT[simpletree::fMu20] || tag.matchHLT[simpletree::fMuTrk20])
	      break;
	  }
	  if (iTag == event.muons.size())
	    continue;
	}
        
        if (st19) {
          for (unsigned iL1(0); iL1 != simpletree::nPhotonL1Objects; ++iL1) {
            if (matchL1[iPh][iL1])
              photon.matchL1[iL1] = 0.1;
            else
              photon.matchL1[iL1] = 3.0;
          }
        }
	
	outPhotons[0] = photon;
	output->Fill();
      } // probe photons
    } // skim switch
  } // nEntries

  outputFile->cd();
  output->Write();
  delete outputFile;
}
