#include "TreeEntries_simpletree.h"
#include "SimpleTreeUtils.h"

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

  simpletree::Event event;
  simpletree::Run run;
  TTree* runTree(0);
  std::vector<TString>* hltPaths(new std::vector<TString>);
  TTree* hltTree(0);

  event.setStatus(*_input, false, {"*"});
  event.setAddress(*_input, {"run", "hltBits"});

  int currentTree(-1);

  int nBinLabels(0);

  long iEntry(0);
  while (iEntry != nEntries && _input->GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << iEntry << std::endl;

    if (_input->GetTreeNumber() != currentTree) {
      currentTree = _input->GetTreeNumber();
      
      auto* file(_input->GetCurrentFile());
      runTree = static_cast<TTree*>(file->Get("runs"));
      hltTree = static_cast<TTree*>(file->Get("hlt"));

      run.setAddress(*runTree);
      hltTree->SetBranchAddress("paths", &hltPaths);

      run.run = 0;
    }

    if (event.run != run.run) {
      long iRunEntry(0);
      while (run.run != event.run && runTree->GetEntry(iRunEntry++) > 0)
        continue;

      hltTree->GetEntry(run.hltMenu);
    }

    if (!rates->GetXaxis()->GetLabels()) {
      for (auto& path : *hltPaths) {
        TString pathBody(path(0, path.Last('_')));
        rates->GetXaxis()->SetBinLabel(nBinLabels + 1, pathBody);
        if (event.hltBits.pass(nBinLabels))
          rates->Fill(nBinLabels + 0.5);

        ++nBinLabels;
      }
    }
    else {
      unsigned iPath(0);
      for (auto& path : *hltPaths) {
        TString pathBody(path(0, path.Last('_')));
        int iBin(rates->GetXaxis()->FindBin(pathBody));
        if (iBin == rates->GetNbinsX() + 1) {
          rates->GetXaxis()->SetBinLabel(++nBinLabels, pathBody);
          iBin = nBinLabels;
        }

        if (event.hltBits.pass(iPath++))
          rates->Fill(iBin - 0.5);
      }
    }
  }

  outputFile->cd();
  rates->Write();
  delete outputFile;
  delete hltPaths;
}

