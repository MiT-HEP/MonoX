#ifndef TagAndProbeSelectors_h
#define TagAndProbeSelectors_h

#include "PandaTree/Objects/interface/EventTP.h"

#include "SelectorBase.h"

class TagAndProbeSelector : public EventSelectorBase {
public:
  TagAndProbeSelector(char const* name, TPEventType t);
  ~TagAndProbeSelector() {}

  void addOperator(Operator*, unsigned idx = -1) final;
  void selectEvent() override;
  char const* className() const override { return "TagAndProbeSelector"; }

  void setSampleId(unsigned id) { sampleId_ = id; }

protected:
  void castInEvent_() override { inEvent_ = static_cast<panda::EventMonophoton*>(inEventBase_); }
  panda::utils::BranchList directCopyBranches_(bool isMC) override;
  panda::utils::BranchList processedBranches_(bool isMC) const override;

  static panda::EventTP* makeOutEvent(TPEventType);

  panda::EventMonophoton* inEvent_{nullptr};
  panda::EventTP& outEvent_;

  TPEventType outType_{nOutTypes};
  unsigned sampleId_{0}; // outEvent_.sample gets reset at the beginning of each event
};

#endif
