#include "selectors.h"

#include "TString.h"
#include "TTree.h"

#include "NeroToSimple.h"

#include <vector>

class Skimmer {
public:
  Skimmer() {}

  void reset() { selectors_.clear(); }
  void addSelector(EventSelector* _sel) { selectors_.push_back(_sel); }
  void run(TTree* input, char const* outputDir, char const* sampleName, long nEntries = -1, bool neroInput = false);

private:
  std::vector<EventSelector*> selectors_{};
};

void
Skimmer::run(TTree* _input, char const* _outputDir, char const* _sampleName, long _nEntries/* = -1*/, bool _neroInput)
{
  TString outputDir(_outputDir);
  TString sampleName(_sampleName);

  simpletree::Event event;

  NeroToSimple* translator(0);
  if (_neroInput) {
    translator = new NeroToSimple(*_input, event);
    _input->LoadTree(0);
    auto* file(_input->GetCurrentFile());
    auto* triggerNames(file->Get("triggerNames"));
    if (triggerNames)
      translator->setTriggerNames(triggerNames->GetTitle());
  }
  else
    event.setAddress(*_input);
  
  for (auto* sel : selectors_)
    sel->initialize(outputDir + "/" + sampleName + "_" + sel->name() + ".root", event);

  long iEntry(0);
  while (iEntry != _nEntries && _input->GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << " " << iEntry << std::endl;

    if (translator)
      translator->translate();
    // std::cout << "Translated" << std::endl;

    for (auto* sel : selectors_)
      sel->selectEvent(event);
  }

  for (auto* sel : selectors_)
    sel->finalize();
}
