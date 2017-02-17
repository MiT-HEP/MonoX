#include "selectors.h"

#include "TString.h"
#include "TTree.h"
#include "TLeaf.h"

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
  void run(TTree* input, char const* outputDir, char const* sampleName, long nEntries = -1);

private:
  std::vector<EventSelector*> selectors_{};
  GoodLumiFilter* goodLumiFilter_{};
  bool useLumiFilter_ = false;
};

void
Skimmer::run(TTree* _input, char const* _outputDir, char const* _sampleName, long _nEntries/* = -1*/)
{
  TString outputDir(_outputDir);
  TString sampleName(_sampleName);

  panda::EventMonophoton event;

  bool isMC = false;

  event.setAddress(*_input);
  auto* br = _input->GetBranch("isData");
  br->GetEntry(0);
  if (br->GetLeaf("isData")->GetValue() == 0.)
    isMC = true;

  
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
  while (iEntry != _nEntries && event.getEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << " " << iEntry << std::endl;

    if (goodLumiFilter_ && useLumiFilter_ && !goodLumiFilter_->isGoodLumi(event.runNumber, event.lumiNumber))
      continue;

    for (auto* sel : selectors_)
      sel->selectEvent(event);
  }

  for (auto* sel : selectors_)
    sel->finalize();
}
