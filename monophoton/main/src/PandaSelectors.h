#ifndef PandaSelectors_h
#define PandaSelectors_h

#include "PandaTree/Objects/interface/Event.h"

#include "SelectorBase.h"

class PandaEventSelectorBase : public EventSelectorBase {
public:
  PandaEventSelectorBase(char const* name) : EventSelectorBase(name) {}
  ~PandaEventSelectorBase() {}

  void selectEvent(panda::EventBase& event) final { selectEvent(static_cast<panda::Event&>(event)); }
  virtual void selectEvent(panda::Event&) = 0;

protected:
  void setupSkim_(panda::EventBase& inEvent, bool isMC) final { setupSkim_(static_cast<panda::Event&>(inEvent), isMC); }
  virtual void setupSkim_(panda::Event& inEvent, bool isMC) {}
};

class PandaEventSelector : public PandaEventSelectorBase {
public:
  PandaEventSelector(char const* name) : PandaEventSelectorBase(name) {}
  ~PandaEventSelector() {}

  void addOperator(Operator*, unsigned idx = -1) override;
  void selectEvent(panda::Event&) override;

  char const* className() const override { return "PandaEventSelector"; }

 protected:
  void setupSkim_(panda::Event& event, bool isMC) override;
  void prepareFill_(panda::Event&);

  panda::Event outEvent_;
};

#endif
