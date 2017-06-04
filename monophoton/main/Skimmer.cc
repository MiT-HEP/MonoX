#include "selectors.h"
#include "logging.h"
#include "../misc/photon_extra.h"

#include "TString.h"
#include "TFile.h"
#include "TTree.h"
#include "TKey.h"
#include "TEntryList.h"
#include "TError.h"
#include "TSystem.h"
#include "TROOT.h"
#include "TDirectory.h"
#include "TTreeFormula.h"

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

  void addPath(char const* _path) { paths_.emplace_back(_path); }
  void clearPaths() { paths_.clear(); }
  void addSelector(EventSelectorBase* _sel) { selectors_.push_back(_sel); }
  void setOwnSelectors(bool b) { ownSelectors_ = b; }
  void setCommonSelection(char const* _sel) { commonSelection_ = _sel; }
  void setGoodLumiFilter(GoodLumiFilter* _filt) { goodLumiFilter_ = _filt; }
  void setForceAllEvents(bool b) { forceAllEvents_ = b; }
  void setSkipMissingFiles(bool b) { skipMissingFiles_ = b; }
  void setPrintEvery(unsigned i) { printEvery_ = i; }
  void run(char const* outputDir, char const* sampleName, bool isData, long nEntries = -1);
  bool preskim(panda::Event const&, TTreeFormula*) const;
  void prepareEvent(panda::Event const&, panda::EventMonophoton&);
  void setPrintLevel(unsigned l) { printLevel_ = l; }

private:
  std::vector<TString> paths_{};
  std::vector<EventSelectorBase*> selectors_{};
  bool ownSelectors_{true};
  TString commonSelection_{};
  GoodLumiFilter* goodLumiFilter_{};
  bool forceAllEvents_{false}; // Override photon skim decisions made by the selectors
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
  genParticles.data.parentContainer_ = &genParticles;
  panda::EventMonophoton skimmedEvent;

  // will get updated by individual operators
  panda::utils::BranchList branchList = {
    "*",
    "!pfCandidates",
    "!tracks",
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

  if (printLevel_ == INFO)
    branchList.setVerbosity(1);

  bool doPreskim(true);

  for (auto* sel : selectors_) {
    sel->setPrintLevel(printLevel_, stream);

    TString outputPath(outputDir + "/" + sampleName + "_" + sel->name() + ".root");
    sel->initialize(outputPath, skimmedEvent, branchList, !isData);

    if (!sel->getCanPhotonSkim())
      doPreskim = false;
  }

  if (forceAllEvents_)
    doPreskim = false;

  // if the selectors register triggers, make sure the information is passed to the actual input event
  event.run = skimmedEvent.run;

  if (goodLumiFilter_)
    *stream << "Applying good lumi filter." << std::endl;

  if (commonSelection_.Length() != 0)
    *stream << "Applying baseline selection \"" << commonSelection_ << "\"" << std::endl;

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

    input->SetCacheSize(100000000);

    TTreeFormula* commonSelection(0);
    if (commonSelection_.Length() != 0 && doPreskim)
      commonSelection = new TTreeFormula("preskim", commonSelection_, input);

    event.setStatus(*input, branchList);
    if (commonSelection) {
      TLeaf* leaf(0);
      int iL(0);
      while ((leaf = commonSelection->GetLeaf(iL++)))
        input->SetBranchStatus(leaf->GetBranch()->GetName(), true);
    }

    event.setAddress(*input, {"*"}, false);

    auto* genInput(static_cast<TTree*>(inputKey->ReadObj()));
    genInput->SetBranchStatus("*", false);
    genParticles.setAddress(*genInput);

    event.electrons.data.matchedGenContainer_ = &genParticles;
    event.muons.data.matchedGenContainer_ = &genParticles;
    event.taus.data.matchedGenContainer_ = &genParticles;
    event.photons.data.matchedGenContainer_ = &genParticles;

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

      if (doPreskim && !preskim(event, commonSelection))
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
Skimmer::preskim(panda::Event const& _event, TTreeFormula* _formula) const
{
  if (_formula) {
    int iD(0);
    int nD(_formula->GetNdata());
    for (; iD != nD; ++iD) {
      if (_formula->EvalInstance64(iD) != 0)
        break;
    }
    if (iD == nD)
      return false;
  }

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

  for (unsigned iPh(0); iPh != _event.photons.size(); ++iPh)
    panda::photon_extra(_outEvent.photons[iPh], _event.photons[iPh], _event.rho);
}
