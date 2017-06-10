#include "PandaTree/Objects/Event.h"

#include "TTree.h"
#include "TFile.h"
#include "TH1D.h"
#include "TString.h"

#include <vector>
#include <iostream>

void
triggerRates(TTree* _input, char const* _outputName, long nEntries = -1)
{
  auto* outputFile(TFile::Open(_outputName, "recreate"));
  auto* rates(new TH1D("rates", "triggered events", 512, 0., 512.));

  panda::Event event;

  _input->SetBranchStatus("*", false);
  event.setAddress(*_input, {"runNumber", "triggers"});
  event.setReadRunTree(true);
  event.run.setLoadTrigger(true);

  long iEntry(0);
  while (event.getEntry(*_input, iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << iEntry << std::endl;

    if (!rates->GetXaxis()->GetLabels()) {
      unsigned iPath(0);
      for (auto& path : *event.run.hlt.paths) {
        TString pathBody(path(0, path.Last('_')));
        rates->GetXaxis()->SetBinLabel(iPath + 1, pathBody);
        if (event.trigger.pass(iPath))
          rates->Fill(iPath + 0.5);

        ++iPath;
      }
    }
    else {
      unsigned iPath(0);
      for (auto& path : *event.run.hlt.paths) {
        TString pathBody(path(0, path.Last('_')));
        int iBin(rates->GetXaxis()->FindBin(pathBody));
        if (iBin == rates->GetNbinsX() + 1) {
          rates->SetBins(iBin, 0., iBin);
          rates->GetXaxis()->SetBinLabel(iBin, pathBody);
        }

        if (event.hltBits.pass(iPath))
          rates->Fill(iBin - 0.5);

        ++iPath;
      }
    }
  }

  outputFile->cd();
  rates->Write();
  delete outputFile;
  delete hltPaths;
}

