#ifndef TagAndProbeSelectors_h
#define TagAndProbeSelectors_h

#include "PandaTree/Objects/interface/EventTP.h"

#include "SelectorBase.h"
#include "TPOperators.h"

class TagAndProbeEventSelectorBase : public EventSelectorBase {
public:
  TagAndProbeEventSelectorBase(char const* name) : EventSelectorBase(name) {}
  ~TagAndProbeEventSelectorBase() {}
  
  void selectEvent(panda::EventBase& event) final { selectEvent(static_cast<panda::EventTP&>(event)); }
  virtual void selectEvent(panda::EventTP&) = 0;

protected:
  void setupSkim_(panda::EventBase& inEvent, bool isMC) final { setupSkim_(static_cast<panda::EventTP&>(inEvent), isMC); }
  virtual void setupSkim_(panda::EventTP& inEvent, bool isMC) {}
};

class TagAndProbeSelector : public TagAndProbeEventSelectorBase {
public:
  TagAndProbeSelector(char const* name) : EventSelectorBase(name) {}
  ~TagAndProbeSelector() {}

  void addOperator(Operator*, unsigned idx = -1) override;

  void setOutEventType(TPEventType t) { outType_ = t; }
  void selectEvent(panda::EventTP&) override;

  char const* className() const override { return "TagAndProbeSelector"; }

  void setSampleId(unsigned id) { sampleId_ = id; }

 protected:
  void setupSkim_(panda::EventTP& inEvent, bool isMC) override;

  TPEventType outType_{nOutTypes};
  panda::EventTP* outEvent_{0};
  unsigned sampleId_; // outEvent_.sample gets reset at the beginning of each event
};

#endif
