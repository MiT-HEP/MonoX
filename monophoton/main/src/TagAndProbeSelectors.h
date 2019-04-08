#ifndef TagAndProbeSelectors_h
#define TagAndProbeSelectors_h

#include "base/SelectorBase.h"
#include "TPOperators.h"

class TagAndProbeSelector : public EventSelectorBase {
public:
  TagAndProbeSelector(char const* name) : EventSelectorBase(name) {}
  ~TagAndProbeSelector() {}

  void addOperator(Operator*, unsigned idx = -1) override;

  void setOutEventType(TPEventType t) { outType_ = t; }
  void selectEvent(panda::EventMonophoton&) override;

  char const* className() const override { return "TagAndProbeSelector"; }

  void setSampleId(unsigned id) { sampleId_ = id; }

 protected:
  void setupSkim_(panda::EventMonophoton& inEvent, bool isMC) override;

  TPEventType outType_{nOutTypes};
  panda::EventTP* outEvent_{0};
  unsigned sampleId_; // outEvent_.sample gets reset at the beginning of each event
};

#endif
