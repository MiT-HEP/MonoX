#include <map>
#include <set>

class GoodLumiFilter {
public:
  GoodLumiFilter() {}
  ~GoodLumiFilter() {}

  void addLumi(unsigned run, unsigned lumi) { goodLumiList_[run].insert(lumi); }
  bool isGoodLumi(unsigned run, unsigned lumi) const;

private:
  std::map<unsigned, std::set<unsigned>> goodLumiList_;
  mutable unsigned currentRun_{0};
  mutable unsigned currentLumi_{0};
  mutable bool currentStatus_{false};
};

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
