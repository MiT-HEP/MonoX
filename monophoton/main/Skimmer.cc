#include "selectors.h"

#include "TString.h"
#include "TTree.h"
#include "TLeaf.h"

#include "NeroToSimple.h"

#include "GoodLumiFilter.h"

#include <vector>
#include <iostream>
#include <stdexcept>

class Skimmer {
public:
  Skimmer() {}

  void reset() { selectors_.clear(); useLumiFilter_ = false; }
  void addSelector(EventSelector* _sel) { selectors_.push_back(_sel); }
  void addGoodLumiFilter(GoodLumiFilter* _filt) { goodLumiFilter_ = _filt; }
  void setUseLumiFilter(bool _setFilter) { useLumiFilter_ = _setFilter; }
  void run(TTree* input, char const* outputDir, char const* sampleName, long nEntries = -1, bool neroInput = false);

private:
  std::vector<EventSelector*> selectors_{};
  GoodLumiFilter* goodLumiFilter_{};
  bool useLumiFilter_ = false;
};

void
Skimmer::run(TTree* _input, char const* _outputDir, char const* _sampleName, long _nEntries/* = -1*/, bool _neroInput)
{
  TString outputDir(_outputDir);
  TString sampleName(_sampleName);

  simpletree::Event event;

  bool isMC = false;

  NeroToSimple* translator(0);
  if (_neroInput) {
    std::cout << "Setting up translator" << std::endl;
    translator = new NeroToSimple(*_input, event);
    _input->LoadTree(0);

    auto* br = _input->GetBranch("isRealData");
    br->GetEntry(0);
    if (br->GetLeaf("isRealData")->GetValue() == 0.)
      isMC = true;

    auto* file(_input->GetCurrentFile());
    auto* triggerNames(file->Get("nero/triggerNames"));
    if (triggerNames) {
      std::cout << "Translating trigger names" << std::endl;
      translator->setTriggerNames(triggerNames->GetTitle());
    }
    std::cout << "Translator set up" << std::endl;
  }
  else {
    event.setAddress(*_input, {"photons.matchL1", "partons.pid", "promptFinalStates.ancestor"}, false);
    if (_input->GetBranch("weight"))
      isMC = true;
  }
  
  // printf("isMC %u \n", isMC);

  if (goodLumiFilter_ && useLumiFilter_)
    printf("Appyling good lumi filter. \n");

  for (auto* sel : selectors_) {
    TString outputPath = outputDir + "/" + sampleName + "_" + sel->name() + ".root";
    // std::cout << "Saving to " << outputPath << std::endl;
    sel->initialize(outputPath, event, isMC);
    // std::cout << "Selector initialized" << std::endl;
  }
  
  // std::cout<< "Selectors set up" << std::endl;

  long iEntry(0);
  TFile* currentFile(0);
  while (iEntry != _nEntries && _input->GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << " " << iEntry << std::endl;

    if (translator)
      translator->translate();

    if (goodLumiFilter_ && useLumiFilter_ && !goodLumiFilter_->isGoodLumi(event.run, event.lumi))
      continue;

    for (auto* sel : selectors_)
      sel->selectEvent(event);
  }

  for (auto* sel : selectors_)
    sel->finalize();
}
