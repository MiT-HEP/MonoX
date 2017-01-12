#include "TreeEntries_simpletree.h"

#include "../../common/GoodLumiFilter.h"

#include "TFile.h"
#include "TTree.h"

#include <iostream>

void
skimUncleaned(TTree* _input, TFile* _outputFile, GoodLumiFilter* _goodLumi = 0)
{
  _outputFile->cd();
  auto* output(new TTree("events", "Events"));

  unsigned run;
  unsigned lumi;

  _input->SetBranchAddress("run", &run);
  _input->SetBranchAddress("lumi", &lumi);

  output->Branch("run", &run, "run/i");
  output->Branch("lumi", &lumi, "lumi/i");

  TBranch* runBranch(_input->GetBranch("run"));
  TBranch* lumiBranch(_input->GetBranch("lumi"));

  simpletree::Event event;
  event.setAddress(*_input, {"run", "lumi"}, false);
  event.book(*output, {"run", "lumi"}, false);

  unsigned currentRun(0);
  unsigned currentLumi(0);
  bool skipRun(false);
  bool skipLumi(false);

  long iEntry(0);
  while (true) {
    if (iEntry % 100000 == 0)
      std::cout << iEntry << std::endl;

    if (runBranch->GetEntry(iEntry) <= 0)
      break;

    if (run != currentRun) {
      currentRun = run;
      if (_goodLumi && !_goodLumi->hasGoodLumi(run)) {
        skipRun = true;
        ++iEntry;
        continue;
      }
      else
        skipRun = false;
    }
    else if (skipRun) {
      ++iEntry;
      continue;
    }

    lumiBranch->GetEntry(iEntry);

    if (lumi != currentLumi) {
      currentLumi = lumi;
      if (_goodLumi && !_goodLumi->isGoodLumi(run, lumi)) {
        skipLumi = true;
        ++iEntry;
        continue;
      }
      else
        skipLumi = false;
    }
    else if (skipLumi) {
      ++iEntry;
      continue;
    }

    _input->GetEntry(iEntry++);

    for (auto& sc : event.superClusters) {
      if (sc.rawPt > 175.) {
        output->Fill();
        break;
      }
    }
  }

  _outputFile->cd();
  output->Write();
}
