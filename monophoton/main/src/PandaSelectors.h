#ifndef PandaSelectors_h
#define PandaSelectors_h

#include "PandaTree/Objects/interface/Event.h"

#include "SelectorBase.h"

class PandaEventSelector : public EventSelectorBase {
 public:
  PandaEventSelector(char const* name);
  ~PandaEventSelector() {}

  void addOperator(Operator*, unsigned idx = -1) final;

  char const* className() const override { return "PandaEventSelector"; }

 protected:
  void castInEvent_() override { inEvent_ = static_cast<panda::Event*>(inEventBase_); }
  panda::utils::BranchList directCopyBranches_(bool isMC) override;

  panda::Event* inEvent_{nullptr};
  panda::Event& outEvent_;
};

#endif
