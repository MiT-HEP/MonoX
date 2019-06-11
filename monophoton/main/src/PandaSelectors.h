#ifndef PandaSelectors_h
#define PandaSelectors_h

#include "PandaTree/Objects/interface/Event.h"

#include "SelectorBase.h"

class PandaEventSelectorBase : public EventSelectorBase {
 public:
  PandaEventSelectorBase(char const* name) : EventSelectorBase(name) {}
  ~PandaEventSelectorBase() {}

  InputEventType inputEventType() const override { return kEvent; }

 protected:
  void setInEvent_(panda::EventBase& inEvent) override { inEvent_ = static_cast<panda::Event*>(&inEvent); }

  panda::Event* inEvent_{nullptr};
};

class PandaEventSelector : public PandaEventSelectorBase {
 public:
  PandaEventSelector(char const* name) : PandaEventSelectorBase(name) {}
  ~PandaEventSelector() {}

  void addOperator(Operator*, unsigned idx = -1) override;
  void selectEvent() override;

  char const* className() const override { return "PandaEventSelector"; }

 protected:
  void setupSkim_(bool isMC) override;
  void prepareFill_();

  panda::Event outEvent_;
};

#endif
