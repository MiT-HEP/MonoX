#include "TTree.h"
#include "TString.h"

#include <vector>
#include <algorithm>
#include <iostream>
#include <sstream>

class PhaseSpaceChopper {
public:
  PhaseSpaceChopper() {}

  void setBinning(char const* vName, unsigned nBins, double* binning);
  void resetCounts();
  void chop(TTree*);
  void dump() const;

private:
  std::vector<TString> vNames_{};
  std::vector<float> variables_{};
  std::vector<std::vector<double>> binnings_{};
  std::vector<unsigned> entries_{};
};

void
PhaseSpaceChopper::setBinning(char const* _vName, unsigned _nBins, double* _binning)
{
  TString vName(_vName);

  auto vItr(std::find(vNames_.begin(), vNames_.end(), vName));

  if (vItr == vNames_.end()) {
    vNames_.push_back(vName);
    variables_.push_back(0.);
    binnings_.emplace_back(_binning, _binning + (_nBins + 1));
  }
  else {
    binnings_[vItr - vNames_.begin()].assign(_binning, _binning + (_nBins + 1));
  }

  resetCounts();
}

void
PhaseSpaceChopper::resetCounts()
{
  unsigned nBins(1);
  for (auto& b : binnings_)
    nBins *= b.size() + 1; // binnings array has size nBins + 1

  entries_.assign(nBins + 1, 0);
}  

void
PhaseSpaceChopper::chop(TTree* _input)
{
  for (unsigned iV(0); iV != vNames_.size(); ++iV) {
    auto& vName(vNames_[iV]);

    _input->SetBranchAddress(vName, &variables_[iV]);
  }

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    unsigned step(1);
    unsigned iBin(0);
    for (unsigned iV(0); iV != variables_.size(); ++iV) {
      auto& binning(binnings_[iV]);
      auto bound(std::upper_bound(binning.begin(), binning.end(), variables_[iV]));
      iBin += step * (bound - binning.begin());
      step *= binning.size() + 1;
    }

    entries_[iBin] += 1;
    entries_.back() += 1;
  }
}

void
PhaseSpaceChopper::dump() const
{
  if (vNames_.size() == 0)
    return;

  std::stringstream sout;
  sout << "{";
  for (unsigned iN(0); iN != vNames_.size() - 1; ++iN)
    sout << vNames_[iN] << ",";
  sout << vNames_.back() << "}" << std::endl;

  for (unsigned iE(0); iE != entries_.size() - 1; ++iE) {
    unsigned globalBin(iE);

    for (unsigned iV(0); iV != variables_.size(); ++iV) {
      auto& binning(binnings_[iV]);

      unsigned iBin(globalBin % (binning.size() + 1));

      if (iBin == 0)
        sout << "[-inf," << binning.front() << "]";
      else if (iBin == binning.size())
        sout << "[" << binning.back() << ",inf]";
      else
        sout << "[" << binning[iBin - 1] << "," << binning[iBin] << "]";

      if (iV != variables_.size() - 1)
        sout << "x";

      globalBin /= binning.size() + 1;
    }

    sout << ": " << entries_[iE] << std::endl;
  }

  std::cout << sout.str();
}
