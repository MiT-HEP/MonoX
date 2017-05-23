#include "selectors.h"
#include "logging.h"

#include "TString.h"
#include "TFile.h"
#include "TTree.h"
#include "TKey.h"
#include "TEntryList.h"
#include "TError.h"
#include "TSystem.h"
#include "TROOT.h"
#include "TDirectory.h"

#include "GoodLumiFilter.h"

#include <vector>
#include <iostream>
#include <stdexcept>
#include <chrono>
typedef std::chrono::steady_clock SClock;

unsigned TIMEOUT(300);

class Skimmer {
public:
  Skimmer() {}
  ~Skimmer();

  void reset() { paths_.clear(); selectors_.clear(); }
  void addPath(char const* _path) { paths_.emplace_back(_path); }
  void addSelector(EventSelectorBase* _sel) { selectors_.push_back(_sel); }
  void setOwnSelectors(bool b) { ownSelectors_ = b; }
  void setCommonSelection(char const* _sel) { commonSelection_ = _sel; }
  void setGoodLumiFilter(GoodLumiFilter* _filt) { goodLumiFilter_ = _filt; }
  void setSkipMissingFiles(bool b) { skipMissingFiles_ = b; }
  void setPrintEvery(unsigned i) { printEvery_ = i; }
  void run(char const* outputDir, char const* sampleName, bool isData, long nEntries = -1);
  bool photonSkim(panda::Event const&) const;
  void prepareEvent(panda::Event const&, panda::EventMonophoton&);
  void setPrintLevel(unsigned l) { printLevel_ = l; }

private:
  std::vector<TString> paths_{};
  std::vector<EventSelectorBase*> selectors_{};
  bool ownSelectors_{true};
  TString commonSelection_{}; // ANDed with superClusters.rawPt > 175. && TMath::Abs(superClusters.eta) < 1.4442 if doPhotonSkim_ = true
  GoodLumiFilter* goodLumiFilter_{};
  bool skipMissingFiles_{false};
  unsigned printEvery_{10000};
  unsigned printLevel_{0};
};

Skimmer::~Skimmer()
{
  if (ownSelectors_) {
    for (auto* sel : selectors_)
      delete sel;
  }
}

void
Skimmer::run(char const* _outputDir, char const* _sampleName, bool isData, long _nEntries/* = -1*/)
{
  TString outputDir(_outputDir);
  TString sampleName(_sampleName);

  std::ostream* stream(&std::cout);
  std::ofstream debugFile;
  if (printLevel_ > 0 && printLevel_ <= DEBUG) {
    TString debugPath("debug_" + sampleName + ".txt");
    debugFile.open(debugPath.Data());
    stream = &debugFile;
  }

  panda::Event event;
  panda::GenParticleCollection genParticles("genParticles");
  panda::EventMonophoton skimmedEvent;

  // will get updated by individual operators
  panda::utils::BranchList branchList = {
    "*",
    "!pfCandidates",
    "!puppiAK4Jets",
    "!chsAK8Jets",
    "!chsAK8Subjets",
    "!puppiAK8Jets",
    "!puppiAK8Subjets",
    "!chsCA15Jets",
    "!chsCA15Subjets",
    "!puppiCA15Jets",
    "!puppiCA15Subjets",
    "!ak8GenJets",
    "!ca15GenJets",
    "!puppiMet",
    "!rawMet",
    "!caloMet",
    "!noMuMet",
    "!noHFMet",
    "!trkMet",
    "!neutralMet",
    "!photonMet",
    "!hfMet",
    "!genMet",
    // "!metMuOnlyFix",
    // "!metNoFix",
    "!recoil"
  };

  // will take care of genParticles individually
  branchList += {"!genParticles"};

  bool doPhotonSkim(true);

  for (auto* sel : selectors_) {
    sel->setPrintLevel(printLevel_, stream);

    TString outputPath(outputDir + "/" + sampleName + "_" + sel->name() + ".root");
    sel->initialize(outputPath, skimmedEvent, branchList, !isData);

    if (!sel->getCanPhotonSkim())
      doPhotonSkim = false;
  }

  TString commonSelection;
  if (doPhotonSkim)
    commonSelection = "superClusters.rawPt > 175. && TMath::Abs(superClusters.eta) < 1.4442";
  if (commonSelection_.Length() != 0)
    commonSelection = "(" + commonSelection + ") && (" + commonSelection_ + ")";

  // if the selectors register triggers, make sure the information is passed to the actual input event
  event.run = skimmedEvent.run;

  if (goodLumiFilter_)
    *stream << "Appyling good lumi filter." << std::endl;

  if (commonSelection.Length() != 0)
    *stream << "Applying baseline selection \"" << commonSelection << "\"" << std::endl;

  long iEntryGlobal(0);
  auto now = SClock::now();
  auto start = now;

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

      if (skipMissingFiles_)
        break;

      gSystem->Sleep(tryEvery * 1000.);
    }

    gErrorIgnoreLevel = originalErrorIgnoreLevel;

    if ((!source || source->IsZombie())) {
      if (skipMissingFiles_) {
        std::cerr << "Skipping missing file " << path << std::endl;
        delete source;
        continue;
      }
      else {
        std::cerr << "Cannot open file " << path << std::endl;
        delete source;
        throw std::runtime_error("source");
      }
    }

    auto* inputKey(static_cast<TKey*>(source->GetListOfKeys()->FindObject("events")));

    auto* input(static_cast<TTree*>(inputKey->ReadObj()));
    if (!input) {
      std::cerr << "Events tree missing from " << source->GetName() << std::endl;
      delete source;
      throw std::runtime_error("source");
    }

    if (commonSelection.Length() != 0) {
      gROOT->cd();
      input->Draw(">>elist", commonSelection, "entrylist");
      auto* elist(static_cast<TEntryList*>(gDirectory->Get("elist")));
      input->SetEntryList(elist);
    }

    event.setAddress(*input, branchList);

    auto* genInput(static_cast<TTree*>(inputKey->ReadObj()));
    genInput->SetBranchStatus("*", false);
    genParticles.setAddress(*genInput);

    long iEntry(0);
    while (iEntryGlobal != _nEntries) {
      int entryNumber(input->GetEntryNumber(iEntry++));

      if (entryNumber < 0) // no more entries in this tree
        break;

      ++iEntryGlobal;

      if (event.getEntry(*input, entryNumber) <= 0) // I/O error
        break;

      if (iEntryGlobal % printEvery_ == 1 && printLevel_ > 0) {
        auto past = now;
        now = SClock::now();
        *stream << " " << iEntryGlobal << " (took " << std::chrono::duration_cast<std::chrono::milliseconds>(now - past).count() / 1000. << " s)" << std::endl;
      }

      if (goodLumiFilter_ && !goodLumiFilter_->isGoodLumi(event.runNumber, event.lumiNumber))
        continue;

      if (doPhotonSkim && !photonSkim(event))
        continue;

      prepareEvent(event, skimmedEvent);

      if (!event.isData) {
        genParticles.getEntry(*genInput, entryNumber);
        skimmedEvent.copyGenParticles(genParticles);
      }

      if (printLevel_ > 0 && printLevel_ <= INFO) {
	debugFile << std::endl << ">>>>> Printing event " << iEntryGlobal <<" !!! <<<<<" << std::endl;
	debugFile << skimmedEvent.runNumber << ":" << skimmedEvent.lumiNumber << ":" << skimmedEvent.eventNumber << std::endl;
	skimmedEvent.print(debugFile, 2);
	debugFile << std::endl;
	skimmedEvent.photons.print(debugFile, 2);
	// debugFile << "photons.size() = " << skimmedEvent.photons.size() << std::endl;
	debugFile << std::endl;
	skimmedEvent.muons.print(debugFile, 2);
	// debugFile << "muons.size() = " << skimmedEvent.muons.size() << std::endl;
	debugFile << std::endl;
	skimmedEvent.electrons.print(debugFile, 2);
	// debugFile << "electrons.size() = " << skimmedEvent.electrons.size() << std::endl;
	debugFile << std::endl;
	skimmedEvent.jets.print(debugFile, 2);
	// debugFile << "jets.size() = " << skimmedEvent.jets.size() << std::endl;
	debugFile << std::endl;
	skimmedEvent.t1Met.print(debugFile, 2);
	// debugFile << std::endl;
	skimmedEvent.metMuOnlyFix.print(debugFile, 2);
	debugFile << std::endl;
	skimmedEvent.metNoFix.print(debugFile, 2);
	debugFile << std::endl;
	debugFile << ">>>>> Event " << iEntryGlobal << " done!!! <<<<<" << std::endl << std::endl;
      }

      for (auto* sel : selectors_)
        sel->selectEvent(skimmedEvent);
    }

    delete source;

    if (iEntryGlobal == _nEntries)
      break;
  }

  for (auto* sel : selectors_)
    sel->finalize();

  if (printLevel_ > 0 && printLevel_ <= INFO) {
    debugFile.close();
  }

  if (printLevel_ > 0) {
    now = SClock::now();
    *stream << "Finished. Took " << std::chrono::duration_cast<std::chrono::seconds>(now - start).count() / 60. << " minutes in total. " << std::endl;
  }
}

bool
Skimmer::photonSkim(panda::Event const& _event) const
{
  for (auto& photon : _event.photons) {
    if (std::abs(photon.superCluster->eta) < 1.4442 && photon.superCluster->rawPt > 150.)
      return true;
  }
  return false;
}

void
Skimmer::prepareEvent(panda::Event const& _event, panda::EventMonophoton& _outEvent)
{
  // copy most of the event content (special operator= of EventMonophoton that takes Event as RHS)
  _outEvent.copy(_event);

  if (_outEvent.run.runNumber != _event.run.runNumber)
    _outEvent.run = _event.run;

  for (unsigned iPh(0); iPh != _event.photons.size(); ++iPh) {
    auto& inPhoton(_event.photons[iPh]);
    auto& superCluster(*inPhoton.superCluster);
    auto& outPhoton(_outEvent.photons[iPh]);

    outPhoton.scRawPt = superCluster.rawPt;
    outPhoton.scEta = superCluster.eta;
    outPhoton.e4 = inPhoton.eleft + inPhoton.eright + inPhoton.etop + inPhoton.ebottom;
    outPhoton.isEB = std::abs(outPhoton.scEta) < 1.4442;

    // Recomputing isolation with scRawPt
    // S15 isolation valid only for panda >= 003
    // In 002 we had Spring15 leakage correction but Spring16 effective areas (production error).

    double chIsoEAS16(0.);
    double nhIsoEAS16(0.);
    double phIsoEAS16(0.);
    double nhIsoEAS15(0.);
    double phIsoEAS15(0.);
    double absEta(std::abs(outPhoton.scEta));
    if (absEta < 1.) {
      nhIsoEAS15 = 0.0599;
      phIsoEAS15 = 0.1271;
      chIsoEAS16 = 0.0360;
      nhIsoEAS16 = 0.0597;
      phIsoEAS16 = 0.1210;
    }
    else if (absEta < 1.479) {
      nhIsoEAS15 = 0.0819;
      phIsoEAS15 = 0.1101;
      chIsoEAS16 = 0.0377;
      nhIsoEAS16 = 0.0807;
      phIsoEAS16 = 0.1107;
    }
    else if (absEta < 2.) {
      nhIsoEAS15 = 0.0696;
      phIsoEAS15 = 0.0756;
      chIsoEAS16 = 0.0306;
      nhIsoEAS16 = 0.0629;
      phIsoEAS16 = 0.0699;
    }
    else if (absEta < 2.2) {
      nhIsoEAS15 = 0.0360;
      phIsoEAS15 = 0.1175;
      chIsoEAS16 = 0.0283;
      nhIsoEAS16 = 0.0197;
      phIsoEAS16 = 0.1056;
    }
    else if (absEta < 2.3) {
      nhIsoEAS15 = 0.0360;
      phIsoEAS15 = 0.1498;
      chIsoEAS16 = 0.0254;
      nhIsoEAS16 = 0.0184;
      phIsoEAS16 = 0.1457;
    }
    else if (absEta < 2.4) {
      nhIsoEAS15 = 0.0462;
      phIsoEAS15 = 0.1857;
      chIsoEAS16 = 0.0217;
      nhIsoEAS16 = 0.0284;
      phIsoEAS16 = 0.1719;
    }
    else {
      nhIsoEAS15 = 0.0656;
      phIsoEAS15 = 0.2183;
      chIsoEAS16 = 0.0167;
      nhIsoEAS16 = 0.0591;
      phIsoEAS16 = 0.1998;
    }

    double nhIsoE1S15, nhIsoE2S15, phIsoE1S15;
    double nhIsoE1S16, nhIsoE2S16, phIsoE1S16;

    if (outPhoton.isEB) {
      nhIsoE1S15 = 0.014;
      nhIsoE2S15 = 0.000019;
      phIsoE1S15 = 0.0053;

      nhIsoE1S16 = 0.0148;
      nhIsoE2S16 = 0.000017;
      phIsoE1S16 = 0.0047;
    }
    else {
      nhIsoE1S15 = 0.0139;
      nhIsoE2S15 = 0.000025;
      phIsoE1S15 = 0.0034;

      nhIsoE1S16 = 0.0163;
      nhIsoE2S16 = 0.000014;
      phIsoE1S16 = 0.0034;
    }

    double pt(inPhoton.pt());
    double pt2(pt * pt);
    double scpt(outPhoton.scRawPt);
    double scpt2(scpt * scpt);
    double rho(_event.rho);

    double chIsoCore(inPhoton.chIso + chIsoEAS16 * rho);
    double nhIsoCore(inPhoton.nhIso + nhIsoEAS16 * rho + nhIsoE1S16 * pt + nhIsoE2S16 * pt2);
    double phIsoCore(inPhoton.phIso + phIsoEAS16 * rho + phIsoE1S16 * pt);

    // outPhoton.chIso = chIsoCore - chIsoEAS16 * rho; // identity
    outPhoton.nhIso = nhIsoCore - nhIsoEAS16 * rho - nhIsoE1S16 * scpt - nhIsoE2S16 * scpt2;
    outPhoton.phIso = phIsoCore - phIsoEAS16 * rho - phIsoE1S16 * scpt;

    outPhoton.loose = outPhoton.passHOverE(0, 0) && outPhoton.passSieie(0, 0) &&
      outPhoton.passCHIso(0) && outPhoton.passNHIso(0) && outPhoton.passCHIso(0);
    outPhoton.medium = outPhoton.passHOverE(1, 0) && outPhoton.passSieie(1, 0) &&
      outPhoton.passCHIso(1) && outPhoton.passNHIso(1) && outPhoton.passCHIso(1);
    outPhoton.tight = outPhoton.passHOverE(2, 0) && outPhoton.passSieie(2, 0) &&
      outPhoton.passCHIso(2) && outPhoton.passNHIso(2) && outPhoton.passCHIso(2);

    outPhoton.chIsoS15 = chIsoCore;        
    outPhoton.nhIsoS15 = nhIsoCore - nhIsoEAS15 * rho - nhIsoE1S15 * scpt - nhIsoE2S15 * scpt2;
    outPhoton.phIsoS15 = phIsoCore - nhIsoEAS15 * rho - phIsoE1S15 * scpt;

    // EA computed with iso/worstIsoEA.py
    outPhoton.chIsoMax -= 0.094 * rho;
    if (outPhoton.chIsoMax < outPhoton.chIso)
      outPhoton.chIsoMax = outPhoton.chIso;

    if (inPhoton.matchedGen.isValid())
      outPhoton.matchedGenId = inPhoton.matchedGen->pdgid;
  }
}
