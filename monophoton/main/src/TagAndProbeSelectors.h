#ifndef TagAndProbeSelectors_h
#define TagAndProbeSelectors_h

#include "PandaTree/Objects/interface/EventTP.h"

#include "SelectorBase.h"

class TagAndProbeEventSelectorBase : public EventSelectorBase {
public:
  TagAndProbeEventSelectorBase(char const* name) : EventSelectorBase(name) {}
  ~TagAndProbeEventSelectorBase() {}

  InputEventType inputEventType() const override { return kEventMonophoton; }

protected:
  void setInEvent_(panda::EventBase& inEvent) override { inEvent_ = static_cast<panda::EventMonophoton*>(&inEvent); }

  panda::EventMonophoton* inEvent_{nullptr};
};

class TagAndProbeSelector : public TagAndProbeEventSelectorBase {
public:
  TagAndProbeSelector(char const* name) : TagAndProbeEventSelectorBase(name) {}
  ~TagAndProbeSelector() {}

  void addOperator(Operator*, unsigned idx = -1) override;

  void setOutEventType(TPEventType t) { outType_ = t; }
  void selectEvent() override;

  char const* className() const override { return "TagAndProbeSelector"; }

  void setSampleId(unsigned id) { sampleId_ = id; }

 protected:
  void setupSkim_(bool isMC) override;

  TPEventType outType_{nOutTypes};
  panda::EventTP* outEvent_{0};
  unsigned sampleId_; // outEvent_.sample gets reset at the beginning of each event
};

#endif
