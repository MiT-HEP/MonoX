#include "selectors.h"

#include "TString.h"
#include "TFile.h"
#include "TTree.h"
#include "TEntryList.h"
#include "TError.h"
#include "TSystem.h"
#include "TROOT.h"
#include "TDirectory.h"

#include "GoodLumiFilter.h"

#include <vector>
#include <iostream>
#include <stdexcept>
#include <ctime>

unsigned TIMEOUT(300);

class Skimmer {
public:
  Skimmer() {}

  void reset() { paths_.clear(); selectors_.clear(); }
  void addPath(char const* _path) { paths_.emplace_back(_path); }
  void addSelector(EventSelector* _sel) { selectors_.push_back(_sel); }
  void setCommonSelection(char const* _sel) { commonSelection_ = _sel; }
  void setGoodLumiFilter(GoodLumiFilter* _filt) { goodLumiFilter_ = _filt; }
  void run(char const* outputDir, char const* sampleName, bool isData, long nEntries = -1);
  bool passPhotonSkim(panda::Event& _event, panda::EventMonophoton& _outEvent);

private:
  std::vector<TString> paths_{};
  std::vector<EventSelector*> selectors_{};
  TString commonSelection_{};
  GoodLumiFilter* goodLumiFilter_{};
};

void
Skimmer::run(char const* _outputDir, char const* _sampleName, bool isData, long _nEntries/* = -1*/)
{
  TString outputDir(_outputDir);
  TString sampleName(_sampleName);

  panda::Event event;
  panda::EventMonophoton skimmedEvent;

  for (auto* sel : selectors_) {
    TString outputPath(outputDir + "/" + sampleName + "_" + sel->name() + ".root");
    sel->initialize(outputPath, skimmedEvent, !isData);
  }

  if (goodLumiFilter_)
    std::cout << "Appyling good lumi filter." << std::endl;

  if (commonSelection_.Length() != 0)
    std::cout << "Applying baseline selection \"" << commonSelection_ << "\"" << std::endl;

  long iEntryGlobal(0);
  clock_t now(clock());

  for (auto& path : paths_) {
    TFile* source(0);

    auto originalErrorIgnoreLevel(gErrorIgnoreLevel);
    gErrorIgnoreLevel = kError + 1;

    unsigned const tryEvery(30);
    for (unsigned iAtt(0); iAtt <= TIMEOUT / tryEvery; ++iAtt) {
      source = TFile::Open(path);
      if (source) {
        if (!source->IsZombie())
          break;
        delete source;
      }

      gSystem->Sleep(tryEvery * 1000.);
    }

    gErrorIgnoreLevel = originalErrorIgnoreLevel;

    if (!source || source->IsZombie()) {
      std::cerr << "Cannot open file " << path << std::endl;
      delete source;
      throw std::runtime_error("source");
    }

    auto* input(static_cast<TTree*>(source->Get("events")));
    if (!input) {
      std::cerr << "Events tree missing from " << source->GetName() << std::endl;
      delete source;
      throw std::runtime_error("source");
    }
    
    if (commonSelection_.Length() != 0) {
      gROOT->cd();
      input->Draw(">>elist", commonSelection_, "entrylist");
      auto* elist(static_cast<TEntryList*>(gDirectory->Get("elist")));
      input->SetEntryList(elist);
    }

    event.setAddress(*input);
  
    long iEntry(0);
    while (iEntryGlobal++ != _nEntries && event.getEntry(*input, input->GetEntryNumber(iEntry++)) > 0) {
      if (iEntryGlobal % 10000 == 1) {
        clock_t past(now);
        now = clock();
        std::cout << " " << iEntryGlobal << " (took " << ((now - past) / double(CLOCKS_PER_SEC)) << " s)" << std::endl;
      }

      if (goodLumiFilter_ && !goodLumiFilter_->isGoodLumi(event.runNumber, event.lumiNumber))
        continue;

      if (!passPhotonSkim(event, skimmedEvent))
        continue;

      for (auto* sel : selectors_)
        sel->selectEvent(skimmedEvent);
    }

    delete source;

    if (iEntryGlobal == _nEntries + 1)
      break;
  }

  for (auto* sel : selectors_)
    sel->finalize();
}


bool
Skimmer::passPhotonSkim(panda::Event& _event, panda::EventMonophoton& _outEvent)
{
  unsigned iPh(0);
  for (; iPh != _event.photons.size(); ++iPh) {
    auto& photon(_event.photons[iPh]);
    if (std::abs(photon.superCluster->eta) < 1.4442 && photon.superCluster->rawPt > 150.)
      break;
  }
  if (iPh == _event.photons.size())
    return false;

  // copy most of the event content (special operator= of EventMonophoton that takes Event as RHS)
  _outEvent = _event;
  
  for (unsigned iPh(0); iPh != _event.photons.size(); ++iPh) {
    auto& inPhoton(_event.photons[iPh]);
    auto& superCluster(*inPhoton.superCluster);
    auto& outPhoton(_outEvent.photons[iPh]);

    outPhoton.scRawPt = superCluster.rawPt;
    outPhoton.scEta = superCluster.eta;
    outPhoton.e4 = inPhoton.eleft + inPhoton.eright + inPhoton.etop + inPhoton.ebottom;
    outPhoton.isEB = std::abs(outPhoton.scEta) < 1.4442;
      
    double chIsoS16EA(0.);
    double nhIsoS16EA(0.);
    double phIsoS16EA(0.);
    double nhIsoS15EA(0.);
    double phIsoS15EA(0.);
    double absEta(std::abs(outPhoton.scEta));
    if (absEta < 1.) {
      nhIsoS15EA = 0.0599;
      phIsoS15EA = 0.1271;
      chIsoS16EA = 0.0360;
      nhIsoS16EA = 0.0597;
      phIsoS16EA = 0.1210;
    }
    else if (absEta < 1.479) {
      nhIsoS15EA = 0.0819;
      phIsoS15EA = 0.1101;
      chIsoS16EA = 0.0377;
      nhIsoS16EA = 0.0807;
      phIsoS16EA = 0.1107;
    }
    else if (absEta < 2.) {
      nhIsoS15EA = 0.0696;
      phIsoS15EA = 0.0756;
      chIsoS16EA = 0.0306;
      nhIsoS16EA = 0.0629;
      phIsoS16EA = 0.0699;
    }
    else if (absEta < 2.2) {
      nhIsoS15EA = 0.0360;
      phIsoS15EA = 0.1175;
      chIsoS16EA = 0.0283;
      nhIsoS16EA = 0.0197;
      phIsoS16EA = 0.1056;
    }
    else if (absEta < 2.3) {
      nhIsoS15EA = 0.0360;
      phIsoS15EA = 0.1498;
      chIsoS16EA = 0.0254;
      nhIsoS16EA = 0.0184;
      phIsoS16EA = 0.1457;
    }
    else if (absEta < 2.4) {
      nhIsoS15EA = 0.0462;
      phIsoS15EA = 0.1857;
      chIsoS16EA = 0.0217;
      nhIsoS16EA = 0.0284;
      phIsoS16EA = 0.1719;
    }
    else {
      nhIsoS15EA = 0.0656;
      phIsoS15EA = 0.2183;
      chIsoS16EA = 0.0167;
      nhIsoS16EA = 0.0591;
      phIsoS16EA = 0.1998;
    }

    outPhoton.chIsoS15 = inPhoton.chIso;
    if (outPhoton.isEB) {
      outPhoton.nhIsoS15 = inPhoton.nhIso + (0.014 - 0.0148) * inPhoton.pt() + (0.000019 - 0.000017) * inPhoton.pt() * inPhoton.pt();
      outPhoton.phIsoS15 = inPhoton.phIso + (0.0053 - 0.0047) * inPhoton.pt();
    }
    else {
      outPhoton.nhIsoS15 = inPhoton.nhIso + (0.0139 - 0.0163) * inPhoton.pt() + (0.000025 - 0.000014) * inPhoton.pt() * inPhoton.pt();
      outPhoton.phIsoS15 = inPhoton.phIso + (0.0034 - 0.0034) * inPhoton.pt();
    }

    outPhoton.chIsoS15 += chIsoS16EA * _event.rho;
    outPhoton.nhIsoS15 += (nhIsoS15EA - nhIsoS16EA) * _event.rho;
    outPhoton.phIsoS15 += (phIsoS15EA - phIsoS16EA) * _event.rho;

    // EA computed with iso/worstIsoEA.py
    outPhoton.chIsoMax -= 0.094 * _event.rho;
    if (outPhoton.chIsoMax < outPhoton.chIso)
      outPhoton.chIsoMax = outPhoton.chIso;
  }

  return true;
}
