#include "selectors.h"

#include "TString.h"
#include "TTree.h"

#include "NeroToSimple.h"

#include <vector>
#include <iostream>
#include <stdexcept>

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
    std::cout << "Setting up translator" << std::endl;
    translator = new NeroToSimple(*_input, event);
    _input->LoadTree(0);
    auto* file(_input->GetCurrentFile());
    auto* triggerNames(file->Get("triggerNames"));
    if (triggerNames) {
      std::cout << "Translating trigger names" << std::endl;
      translator->setTriggerNames(triggerNames->GetTitle());
    }
    std::cout << "Translator set up" << std::endl;
  }
  else
    event.setAddress(*_input);
  
  for (auto* sel : selectors_) {
    TString outputPath = outputDir + "/" + sampleName + "_" + sel->name() + ".root";
    std::cout << "Saving to " << outputPath << std::endl;
    sel->initialize(outputPath, event);
    std::cout << "Selector initialized" << std::endl;
  }
  
  std::cout << "Selectors set up" << std::endl;

  long iEntry(0);
  TFile* currentFile(0);
  while (iEntry != _nEntries && _input->GetEntry(iEntry++) > 0) {
    //if (iEntry % 100000 == 1)
    std::cout << " " << iEntry << std::endl;

    if (translator)
      translator->translate();
    std::cout << "Translated" << std::endl;

    for (auto* sel : selectors_)
      sel->selectEvent(event);
  }

  for (auto* sel : selectors_)
    sel->finalize();
}
