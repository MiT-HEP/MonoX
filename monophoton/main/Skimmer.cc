#include "selectors.h"

#include "TString.h"
#include "TTree.h"

#include <vector>

class Skimmer {
public:
  Skimmer() {}

  void reset() { selectors_.clear(); }
  void addSelector(EventSelector* _sel) { selectors_.push_back(_sel); }
  void run(TTree* input, char const* outputDir, char const* sampleName, long nEntries = -1);

private:
  std::vector<EventSelector*> selectors_{};
};

void
Skimmer::run(TTree* _input, char const* _outputDir, char const* _sampleName, long _nEntries/* = -1*/)
{
  TString outputDir(_outputDir);
  TString sampleName(_sampleName);

  simpletree::Event event;
  event.setAddress(*_input);
  
  for (auto* sel : selectors_)
    sel->initialize(outputDir + "/" + sampleName + "_" + sel->name() + ".root", event);

  long iEntry(0);
  while (iEntry != _nEntries && _input->GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << " " << iEntry << std::endl;

    for (auto* sel : selectors_)
      sel->selectEvent(event);
  }

  for (auto* sel : selectors_)
    sel->finalize();
}
