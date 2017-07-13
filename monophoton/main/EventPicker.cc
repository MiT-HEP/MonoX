#include "PandaTree/Objects/interface/Event.h"

#include "TChain.h"
#include "TString.h"
#include "TFile.h"
#include "TTree.h"
#include "TKey.h"

class EventPicker {
public:
  EventPicker() {}
  ~EventPicker() {}
  void addPath(char const* _path) { paths_.emplace_back(_path); }
  void addEvent(unsigned r, unsigned l, unsigned e) { eventIds_.emplace_back(r, l, e); }
  void setPrintEvery(unsigned i) { printEvery_ = i; }
  void setPrintLevel(unsigned l) { printLevel_ = l; }

  void run(char const* outputDir, long nEntries = -1);

  struct EventId {
    EventId() {}
    EventId(unsigned r, unsigned l, unsigned e) : runNumber(r), lumiNumber(l), eventNumber(e) {}

    unsigned runNumber{0};
    unsigned lumiNumber{0};
    unsigned eventNumber{0};
  };

private:
  std::vector<TString> paths_{};
  std::vector<EventId> eventIds_{};
  unsigned printEvery_{10000};
  unsigned printLevel_{0};
};

void
EventPicker::run(char const* _outputDir, long _nEntries/* = -1*/)
{
  panda::Event event;
  panda::Run run;

  TChain idInput("events");
  TChain fullInput("events");

  for (auto& path : paths_) {
    idInput.Add(path);
    fullInput.Add(path);
  }

  event.setStatus(idInput, {"!*"});
  event.setAddress(idInput, {"runNumber", "lumiNumber", "eventNumber"});
  event.setAddress(fullInput);

  int treeNumber(-1);
  TTree* runTree(0);

  long iEntry(0);
  while (iEntry != _nEntries && event.getEntry(idInput, iEntry++) > 0) {
    if (iEntry % printEvery_ == 1 && printLevel_ > 0)
      std::cout << " " << iEntry << std::endl;

    // not the most efficient implementation, but we don't need ultimate speed here.
    for (auto idItr(eventIds_.begin()); idItr != eventIds_.end(); ++idItr) {
      auto& id(*idItr);
      if (id.runNumber == event.runNumber && id.lumiNumber == event.lumiNumber && id.eventNumber == event.eventNumber) {
        if (printLevel_ > 0)
          std::cout << "Found event " << id.runNumber << ":" << id.lumiNumber << ":" << id.eventNumber << std::endl;

        event.getEntry(fullInput, iEntry - 1);

        if (treeNumber != fullInput.GetTreeNumber()) {
          treeNumber = fullInput.GetTreeNumber();
          run.runNumber = 0;

          runTree = static_cast<TTree*>(fullInput.GetCurrentFile()->Get("runs"));
          run.setAddress(*runTree);
        }

        run.findEntry(*runTree, id.runNumber);

        auto* outputFile(TFile::Open(TString::Format("%s/%d_%d_%d.root", _outputDir, id.runNumber, id.lumiNumber, id.eventNumber), "recreate"));
        auto* outputEvents(new TTree("events", "events"));
        auto* outputRuns(new TTree("runs", "runs"));

        event.book(*outputEvents);
        event.run.book(*outputRuns);
        event.fill(*outputEvents);
        event.run.fill(*outputRuns);

        outputFile->cd();
        outputEvents->Write();
        outputRuns->Write();

        for (auto* key : *fullInput.GetCurrentFile()->GetListOfKeys()) {
          if (std::strcmp(key->GetName(), "events") == 0 || std::strcmp(key->GetName(), "runs") == 0)
            continue;

          outputFile->cd();
          auto* obj(static_cast<TKey*>(key)->ReadObj());
          obj->Write();
        }
        
        delete outputFile;
        
        eventIds_.erase(idItr);
        break;
      }
    }
  }
}
