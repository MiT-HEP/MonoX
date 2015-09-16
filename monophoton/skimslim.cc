#include "TFile.h"
#include "TChain.h"
#include "TTree.h"
#include "TLorentzVector.h"
#include "TString.h"

#include "NeroProducer/Core/interface/BareEvent.hpp"
#include "NeroProducer/Core/interface/BareJets.hpp"
#include "NeroProducer/Core/interface/BareLeptons.hpp"
#include "NeroProducer/Core/interface/BareMet.hpp"
#include "NeroProducer/Core/interface/BarePhotons.hpp"
#include "NeroProducer/Core/interface/BareTaus.hpp"
#include "NeroProducer/Core/interface/BareMonteCarlo.hpp"

#include <iostream>

class Skimmer {
public:
  Skimmer() {}
  ~Skimmer() {}

  void reset() { inputPaths_.clear(); goodLumis_.clear(); }
  void addInputPath(char const* path) { inputPaths_.push_back(path); }
  void addGoodLumi(unsigned run, unsigned lumi) { goodLumis_[run].insert(lumi); }
  void run(TFile* outputFile);

private:
  BareEvent event_{};
  BareJets jets_{};
  BareLeptons leptons_{};
  BareMet met_{};
  BarePhotons photons_{};
  BareTaus taus_{};
  BareMonteCarlo mc_{};

  std::vector<TString> inputPaths_{};
  std::map<int, std::set<int>> goodLumis_{};
};  

void
Skimmer::run(TFile* _outputFile)
{
  TChain cutInput("nero/events");
  TChain fullInput("nero/events");
  TChain allInput("nero/all");

  for (auto&& path : inputPaths_) {
    cutInput.Add(path);
    fullInput.Add(path);
    allInput.Add(path);
  }

  bool isMC(fullInput.GetBranch("mcWeight") != 0);

  _outputFile->cd();
  auto* output(new TTree("events", "events"));

  auto* clone = allInput.CloneTree();
  clone->Write();
  delete clone;
  
  // if we want to slim more we'll need to define branches "a la carte"
  event_.defineBranches(output);
  jets_.defineBranches(output);
  leptons_.defineBranches(output);
  met_.defineBranches(output);
  photons_.defineBranches(output);
  taus_.defineBranches(output);
  if (isMC)
    mc_.defineBranches(output);

  event_.setBranchAddresses(&fullInput);
  jets_.setBranchAddresses(&fullInput);
  leptons_.setBranchAddresses(&fullInput);
  met_.setBranchAddresses(&fullInput);
  photons_.setBranchAddresses(&fullInput);
  taus_.setBranchAddresses(&fullInput);
  if (isMC)
    mc_.setBranchAddresses(&fullInput);

  cutInput.SetBranchStatus("*", 0);
  cutInput.SetBranchStatus("runNum", 1);
  cutInput.SetBranchStatus("lumiNum", 1);
  cutInput.SetBranchStatus("lepP4", 1);
  cutInput.SetBranchStatus("lepSelBits", 1);
  cutInput.SetBranchStatus("photonP4", 1);

  event_.setBranchAddresses(&cutInput);
  leptons_.setBranchAddresses(&cutInput);
  photons_.setBranchAddresses(&cutInput);

  int currentRun(0);
  int currentLumi(0);
  bool doLumiFilter(!isMC && goodLumis_.size() != 0);
  auto glEnd(goodLumis_.end());
  bool skipEvent(false);

  long iEntry(0);
  while (cutInput.GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << iEntry << std::endl;

    if (doLumiFilter && (event_.runNum != currentRun || event_.lumiNum != currentLumi)) {
      skipEvent = false;
      currentRun = event_.runNum;
      currentLumi = event_.lumiNum;
      auto rItr(goodLumis_.find(currentRun));
      if (rItr == glEnd)
	skipEvent = true;
      else {
	auto lItr(rItr->second.find(currentLumi));
	if (lItr == rItr->second.end())
	  skipEvent = true;
      }
    }

    if (skipEvent)
      continue;

    unsigned iL(0);
    for (; iL != leptons_.size(); ++iL) {
      if ((leptons_.passSelection(iL, BareLeptons::LepLoose)))
        break;
    }
    if (iL != leptons_.size())
      continue;

    unsigned nLoose(0);
    unsigned iMedium(-1);
    for (unsigned iP(0); iP != photons_.size(); ++iP) {
      if (photons_.pt(iP) < 15.)
        continue;
      ++nLoose;

      //      if (photons_.pt(iP) > 180. && photons_.mediumid->at(iP) == 1)
      if (photons_.pt(iP) > 180.)
        iMedium = iP;
    }

    if (nLoose > 1)
      continue;

    if (iMedium > photons_.size())
      continue;

    fullInput.GetEntry(iEntry - 1);

    output->Fill();
  }

  _outputFile->cd();
  output->Write();
  delete output;
}
