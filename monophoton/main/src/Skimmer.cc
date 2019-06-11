#include "SelectorBase.h"
#include "logging.h"
#include "photon_extra.h"

#include "TString.h"
#include "TFile.h"
#include "TChain.h"
#include "TKey.h"
#include "TError.h"
#include "TSystem.h"
#include "TROOT.h"
#include "TDirectory.h"
#include "TTreeFormula.h"

#include "GoodLumiFilter.h"

#include "PandaTree/Objects/interface/Event.h"
#include "PandaTree/Objects/interface/EventMonophoton.h"
#include "PandaTree/Objects/interface/EventTP.h"

#include <vector>
#include <iostream>
#include <fstream>
#include <stdexcept>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
typedef std::chrono::steady_clock SClock;

unsigned TIMEOUT(300);

void prepareEvent(panda::Event const&, panda::EventMonophoton&, bool isData);
void prepareEvent(panda::Event const&, panda::EventTP&, bool isData);

class Skimmer {
public:
  Skimmer() {}
  ~Skimmer();

  void addPath(char const* _path) { paths_.emplace_back(_path); }
  void clearPaths() { paths_.clear(); }
  void addSelector(EventSelectorBase* _sel) { selectors_.push_back(_sel); }
  void setOwnSelectors(bool b) { ownSelectors_ = b; }
  void setGoodLumiFilter(GoodLumiFilter* _filt) { goodLumiFilter_ = _filt; }
  void setSkipMissingFiles(bool b) { skipMissingFiles_ = b; }
  void setPrintEvery(unsigned i) { printEvery_ = i; }
  void run(char const* outputDir, char const* sampleName, bool isData, long nEntries = -1, long firstEntry = 0);
  void setPrintLevel(unsigned l) { printLevel_ = l; }
  void setNThreads(unsigned n) { nThreads_ = n; }
  void setCompatibilityMode(bool r) { compatibilityMode_ = r; }

private:
  std::vector<TString> paths_{};
  std::vector<EventSelectorBase*> selectors_{};
  bool ownSelectors_{true};
  GoodLumiFilter* goodLumiFilter_{nullptr};
  bool skipMissingFiles_{false};
  unsigned printEvery_{10000};
  unsigned printLevel_{0};
  int nThreads_{1};
  bool compatibilityMode_{false};
};

Skimmer::~Skimmer()
{
  if (ownSelectors_) {
    for (auto* sel : selectors_)
      delete sel;
  }
}

void
Skimmer::run(char const* _outputDir, char const* _sampleName, bool isData, long _nEntries/* = -1*/, long _firstEntry/* = 0*/)
{
  if (selectors_.size() == 0)
    throw std::runtime_error("No selectors set");

  // check all input exists
  for (auto&& pItr(paths_.begin()); pItr != paths_.end(); ++pItr) {
    TFile* source(0);

    auto originalErrorIgnoreLevel(gErrorIgnoreLevel);
    gErrorIgnoreLevel = kError + 1;

    unsigned const tryEvery(30);
    for (unsigned iAtt(0); iAtt <= TIMEOUT / tryEvery; ++iAtt) {
      source = TFile::Open(*pItr);
      if (source) {
        if (!source->IsZombie())
          break;
        delete source;
      }

      if (skipMissingFiles_)
        break;

      std::cerr << *pItr << " is not available. Waiting for " << tryEvery << " seconds.." << std::endl;

      gSystem->Sleep(tryEvery * 1000.);
    }

    gErrorIgnoreLevel = originalErrorIgnoreLevel;

    if ((!source || source->IsZombie())) {
      if (skipMissingFiles_) {
        std::cerr << "Skipping missing file " << *pItr << std::endl;
        auto pos(pItr);
        --pItr;
        paths_.erase(pos);
      }
      else {
        std::cerr << "Cannot open file " << *pItr << std::endl;
        delete source;
        throw std::runtime_error("source");
      }
    }
    else {
      auto* inputKey(static_cast<TKey*>(source->GetListOfKeys()->FindObject("events")));
      if (!inputKey) {
        std::cerr << "Events tree missing from " << source->GetName() << std::endl;
        delete source;
        throw std::runtime_error("source");
      }
    }

    delete source;
  }

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

  // will get updated by individual operators
  panda::utils::BranchList branchList = {
    "!*",
    "runNumber",
    "lumiNumber",
    "eventNumber",
    "isData",
    "weight",
    "npv",
    "rho",
    "rhoCentralCalo",
    "triggers",
    "vertices",
    "superClusters",
    "electrons",
    "muons",
    "taus",
    "photons",
    "chsAK4Jets",
    "!chsAK4Jets.constituents_",
    "pfMet",
    "metFilters",
    "metMuOnlyFix"
  };

  if (!isData)
    branchList += {"npvTrue", "genParticles", "genReweight", "genVertex", "partons"}; //  , "genMet"};

  if (compatibilityMode_)
    branchList += {"!eventNumber", "!electrons.triggerMatch", "!muons.triggerMatch", "!photons.triggerMatch"};

  if (printLevel_ > 0 && printLevel_ <= DEBUG)
    branchList.setVerbosity(1);

  std::vector<std::thread> threads;
  std::mutex mutex;
  std::condition_variable cv;
  std::atomic_int activate{0};
  std::atomic_int nActive{0};

  int nSel(selectors_.size());
  activate = nSel;

  TString commonSelection(selectors_[0]->getPreskim());

  panda::EventBase* alternativeEvents[EventSelectorBase::nInputEventTypes]{};
  std::function<void()> alternativeEventFactory[EventSelectorBase::nInputEventTypes]{};
  std::function<void()> prepareAlternativeEvent[EventSelectorBase::nInputEventTypes]{};
  alternativeEventFactory[EventSelectorBase::kEventMonophoton] = [&alternativeEvents]() {
    alternativeEvents[EventSelectorBase::kEventMonophoton] = new panda::EventMonophoton();
  };
  alternativeEventFactory[EventSelectorBase::kEventTP] = [&alternativeEvents]() {
    alternativeEvents[EventSelectorBase::kEventTP] = new panda::EventTP();
  };
  prepareAlternativeEvent[EventSelectorBase::kEventMonophoton] = [&event, &alternativeEvents, isData]() {
    prepareEvent(event, static_cast<panda::EventMonophoton&>(*alternativeEvents[EventSelectorBase::kEventMonophoton]), isData);
  };
  prepareAlternativeEvent[EventSelectorBase::kEventTP] = [&event, &alternativeEvents, isData]() {
    prepareEvent(event, static_cast<panda::EventTP&>(*alternativeEvents[EventSelectorBase::kEventTP]), isData);
  };

  int iSel(0);
  for (auto* sel : selectors_) {
    sel->setPrintLevel(printLevel_, stream);

    panda::EventBase* inEvent{nullptr};

    auto eventType(sel->inputEventType());
    if (eventType == EventSelectorBase::kEvent)
      inEvent = &event;
    else {
      if (alternativeEvents[eventType] == nullptr)
        alternativeEventFactory[eventType]();

      inEvent = alternativeEvents[eventType];
    }

    TString outputPath(outputDir + "/" + sampleName + "_" + sel->name() + ".root");
    sel->initialize(outputPath, *inEvent, branchList, !isData);

    if (TString(sel->getPreskim()) != commonSelection) {
      // this case is filtered out by ssw2.py
      throw std::runtime_error("inconsistent preskims");
    }

    if (nThreads_ > 1) {
      threads.emplace_back([this, sel, &mutex, &cv, &activate, &nActive, iSel]() {
          std::unique_lock<std::mutex> lock(mutex);

          while (true) {
            cv.wait(lock, [this, &activate, &nActive, iSel]() {
                //              std::cout << "woken " << iSel << " " << activate.load() << " " << nActive.load() << std::endl;
                return activate.load() == iSel && nActive.load() < this->nThreads_; });

            ++activate;

            if (nActive.load() < 0)
              break;

            ++nActive;
            lock.unlock();

            //          std::cout << "upped activate " << iSel << std::endl;

            cv.notify_all();

            //          std::cout << "notified and unlocked " << iSel << std::endl;

            sel->selectEvent();

            //          std::cout << "event selected " << iSel << std::endl;

            lock.lock();
            --nActive;
            cv.notify_all();
          }

          cv.notify_all();
        });
    }

    ++iSel;
  }

  for (auto* alt : alternativeEvents) {
    // if the selectors register triggers, make sure the information is passed to the actual input event
    if (alt == nullptr)
      continue;
    static_cast<panda::EventBase&>(event).operator=(*alt);
    alt->triggerObjects.setIgnoreMissing(true);
  }

  if (goodLumiFilter_ != nullptr)
    *stream << "Applying good lumi filter." << std::endl;

  TChain preInput("events");
  TChain mainInput("events");
  int mainTreeNumber(-1);

  for (auto& path : paths_) {
    preInput.Add(path);
    mainInput.Add(path);
  }

  TTreeFormula* preselection{nullptr};
  int preTreeNumber(-1);
  if (commonSelection != "") {
    *stream << "Applying baseline selection \"" << commonSelection << "\"" << std::endl;

    preselection = new TTreeFormula("preselection", commonSelection, &preInput);
  }

  event.setStatus(mainInput, branchList);
  event.setAddress(mainInput, {"*"}, false);
  UInt_t runNumber{};
  UInt_t lumiNumber{};
  TBranch* bRunNumber{nullptr};
  TBranch* bLumiNumber{nullptr};
  if (goodLumiFilter_ != nullptr) {
    // this "steals" the branch address from event
    preInput.SetBranchAddress("runNumber", &runNumber);
    preInput.SetBranchAddress("lumiNumber", &lumiNumber);
  }

  auto now(SClock::now());
  auto start(now);

  long iEntry(0);
  while (iEntry++ != _nEntries) {
    if ((iEntry - 1) % printEvery_ == 0 && printLevel_ > 0) {
      auto past = now;
      now = SClock::now();
      *stream << " " << iEntry << " (took " << std::chrono::duration_cast<std::chrono::milliseconds>(now - past).count() / 1000. << " s)" << std::endl;
    }

    if (preselection != nullptr || goodLumiFilter_ != nullptr) {
      if (preInput.LoadTree(_firstEntry + iEntry - 1) < 0)
        break;

      if (preTreeNumber != preInput.GetTreeNumber()) {
        preTreeNumber = preInput.GetTreeNumber();
        if (preselection != nullptr)
          preselection->UpdateFormulaLeaves();

        if (goodLumiFilter_ != nullptr) {
          bRunNumber = preInput.GetBranch("runNumber");
          bLumiNumber = preInput.GetBranch("lumiNumber");
        }
      }

      if (preselection != nullptr) {
        int nD(preselection->GetNdata());
        int iD(0);
        for (; iD != nD; ++iD) {
          if (preselection->EvalInstance(iD) != 0.)
            break;
        }
        if (iD == nD)
          continue;
      }

      if (goodLumiFilter_ != nullptr) {
        bRunNumber->GetEntry(_firstEntry + iEntry - 1);
        bLumiNumber->GetEntry(_firstEntry + iEntry - 1);
        if (!goodLumiFilter_->isGoodLumi(runNumber, lumiNumber))
          continue;
      }
    }

    try {
      if (event.getEntry(mainInput, _firstEntry + iEntry - 1) <= 0)
        break;
    }
    catch (std::exception& _ex) {
      *stream << "Error while reading " << mainInput.GetCurrentFile()->GetName() << std::endl;
      throw;
    }

    if (goodLumiFilter_ != nullptr) {
      event.runNumber = runNumber;
      event.lumiNumber = lumiNumber;
    }

    if (mainTreeNumber != mainInput.GetTreeNumber()) {
      if (printLevel_ > 0 && printLevel_ <= INFO)
        *stream << "Opened a new file " << mainInput.GetCurrentFile()->GetName() << std::endl;

      mainTreeNumber = mainInput.GetTreeNumber();

      // invalidate output event run number so it gets updated in prepareEvent
      for (auto* alt : alternativeEvents) {
        if (alt != nullptr)
          alt->run.runNumber = 0;
      }
    }

    for (unsigned iA(0); iA != EventSelectorBase::nInputEventTypes; ++iA) {
      if (alternativeEvents[iA] != nullptr)
        prepareAlternativeEvent[iA]();
    }

    if (printLevel_ > 0 && printLevel_ <= INFO) {
      debugFile << std::endl << ">>>>> Printing event " << iEntry <<" !!! <<<<<" << std::endl;
      debugFile << event.runNumber << ":" << event.lumiNumber << ":" << event.eventNumber << std::endl;
      event.print(debugFile, 2);
      debugFile << std::endl;
      event.photons.print(debugFile, 2);
      // debugFile << "photons.size() = " << event.photons.size() << std::endl;
      debugFile << std::endl;
      event.muons.print(debugFile, 2);
      // debugFile << "muons.size() = " << event.muons.size() << std::endl;
      debugFile << std::endl;
      event.electrons.print(debugFile, 2);
      // debugFile << "electrons.size() = " << event.electrons.size() << std::endl;
      debugFile << std::endl;
      event.chsAK4Jets.print(debugFile, 2);
      // debugFile << "jets.size() = " << event.jets.size() << std::endl;
      debugFile << std::endl;
      event.pfMet.print(debugFile, 2);
      // debugFile << std::endl;
      /*
      event.metMuOnlyFix.print(debugFile, 2);
      debugFile << std::endl;
      event.metNoFix.print(debugFile, 2);
      debugFile << std::endl;
      */
      debugFile << ">>>>> Event " << iEntry << " done!!! <<<<<" << std::endl << std::endl;
    }

    try {
      if (nThreads_ > 1) {
        std::unique_lock<std::mutex> lock(mutex);
        activate = 0;
        nActive = 0;
        cv.notify_all();
        cv.wait(lock, [&activate, &nActive, nSel]() { return activate.load() == nSel && nActive.load() == 0; });
      }
      else {
        for (auto* sel : selectors_)
          sel->selectEvent();
      }
    }
    catch (std::exception& ex) {
      *stream << "Error while processing event " << event.runNumber << ":" << event.lumiNumber << ":" << event.eventNumber;
      *stream << " in file " << mainInput.GetCurrentFile()->GetName() << std::endl;
      *stream << ex.what() << std::endl;
      throw;
    }
  }

  if (nThreads_ > 1) {
    {
      std::unique_lock<std::mutex> lock(mutex);
      activate = 0;
      nActive = -1;
      cv.notify_all();
    }

    for (auto& th : threads)
      th.join();
  }

  delete preselection;

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

void
prepareEvent(panda::Event const& _event, panda::EventMonophoton& _outEvent, bool _isData)
{
  // copy most of the event content
  _outEvent.copy(_event);

  if (_outEvent.run.runNumber != _event.run.runNumber)
    _outEvent.run = _event.run;

  for (unsigned iPh(0); iPh != _event.photons.size(); ++iPh)
    panda::photon_extra(_outEvent.photons[iPh], _event.photons[iPh], _event.rho, _isData ? nullptr : &_outEvent.genParticles);
}

void
prepareEvent(panda::Event const& _event, panda::EventTP& _outEvent, bool _isData)
{
  // copy most of the event content
  static_cast<panda::EventBase&>(_outEvent).operator=(_event);

  if (_outEvent.run.runNumber != _event.run.runNumber)
    _outEvent.run = _event.run;
}
