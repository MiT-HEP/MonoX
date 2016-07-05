#include "GoodLumiFilter.h"

bool
GoodLumiFilter::isGoodLumi(unsigned run, unsigned lumi) const
{
  if (goodLumiList_.size() == 0)
    return true;

  if (run == currentRun_ && lumi == currentLumi_)
    return currentStatus_;

  currentRun_ = run;
  currentLumi_ = lumi;

  auto rItr(goodLumiList_.find(run));
  if (rItr != goodLumiList_.end()) {
    auto lItr(rItr->second.find(lumi));
    if (lItr != rItr->second.end()) {
      currentStatus_ = true;
      return currentStatus_;
    }
  }

  currentStatus_ = false;
  return currentStatus_;
}

bool
GoodLumiFilter::hasGoodLumi(unsigned run) const
{
  if (goodLumiList_.size() == 0)
    return true;

  return goodLumiList_.find(run) != goodLumiList_.end();
}
