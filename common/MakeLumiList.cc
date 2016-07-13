#include "TTree.h"

#include "GoodLumiFilter.h"

#include <fstream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <iostream>

typedef std::map<unsigned, std::set<unsigned>> LumiList;

void
makeJson(TTree* _input, char const* _outName, GoodLumiFilter* _mask = 0, char const* _runBranchName = "runNum", char const* _lumiBranchName = "lumiNum")
{
  // unsigned can take signed run numbers too (highest bit is never used anyway)
  unsigned run;
  unsigned lumi;

  _input->SetBranchStatus("*", false);
  _input->SetBranchStatus(_runBranchName, true);
  _input->SetBranchStatus(_lumiBranchName, true);
  _input->SetBranchAddress(_runBranchName, &run);
  _input->SetBranchAddress(_lumiBranchName, &lumi);

  LumiList lumiList;

  long iEntry(0);
  while (_input->GetEntry(iEntry++) > 0) {
    if (iEntry % 10000 == 1)
      std::cout << iEntry << std::endl;

    if (_mask && !_mask->isGoodLumi(run, lumi))
      continue;

    lumiList[run].insert(lumi);
  }

  std::stringstream ss;

  for (auto&& runAndList : lumiList) {
    if (runAndList.second.size() == 0) // should never happen
      continue;

    ss << "\n  \"" << runAndList.first << "\": [\n";

    unsigned current(-1);
    for (unsigned lumi : runAndList.second) {
      if (lumi == current + 1) {
        current = lumi;
        continue;
      }

      if (current != unsigned(-1))
        ss << current << "],\n";

      current = lumi;
      ss << "    [" << current << ", ";
    }

    ss << current << "]\n";
    ss << "  ],";
  }

  std::string json(ss.str());
  json.resize(json.size() - 1);

  std::ofstream output(_outName);
  output << "{" << json << "\n}";
}
