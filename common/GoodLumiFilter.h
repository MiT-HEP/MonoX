#ifndef GoodLumiFilter_h
#define GoodLumiFilter_h

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

#endif
