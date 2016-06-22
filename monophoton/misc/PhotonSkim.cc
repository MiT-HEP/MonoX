#include "TreeEntries_simpletree.h"
#include "SimpleTreeUtils.h"

#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TSystem.h"
#include "TH1D.h"
#include "TChain.h"

#include <vector>
#include <map>
#include <iostream>
#include <stdexcept>

void
PhotonSkim(char const* _sourceDir, char const* _outputPath, long _nEvents = -1)
{
  std::vector<TString> sourcePaths;

  auto* dirp(gSystem->OpenDirectory(_sourceDir));
  
  while (true) {
    TString path(gSystem->GetDirEntry(dirp));
    if (path.Length() == 0)
      break;

    if (path == "." || path == "..")
      continue;

    if (path.EndsWith(".root"))
      sourcePaths.push_back(TString(_sourceDir) + "/" + path);
  }
  
  gSystem->FreeDirectory(dirp);

  std::cout << sourcePaths.size() << " files to merge" << std::endl;

  auto* outputFile(TFile::Open(_outputPath, "recreate"));

  TChain inEventTree("events");
  for (auto& path : sourcePaths)
    inEventTree.Add(path);

  simpletree::Event event;
  event.setAddress(inEventTree);

  outputFile->cd();
  auto* outEventTree(inEventTree.CloneTree(0));

  bool hltPhoton165HE10(false);
  outEventTree->Branch("hlt.photon165HE10", &hltPhoton165HE10, "photon165HE10/O");

  simpletree::TriggerHelper hltPhoton165HE10Helper("HLT_Photon165_HE10");

  auto pass([&event]()->bool {
      for (auto& photon : event.photons) {
        if (photon.isEB && photon.pt > 175.)
          return true;
      }
      return false;
    });

  std::cout << "skimming events" << std::endl;

  long nPass(0);
  long iEntry(0);
  while (iEntry != _nEvents && inEventTree.GetEntry(iEntry++) > 0) {
    if (iEntry % 100000 == 1)
      std::cout << " " << iEntry << std::endl;

    if (pass()) {
      ++nPass;
      hltPhoton165HE10 = hltPhoton165HE10Helper.pass(event);
      outEventTree->Fill();
    }
  }

  std::cout << "Event reduction: " << nPass << " / " << iEntry << std::endl;

  simpletree::Run run;
  std::vector<TString>* hltPaths(0);
  std::map<unsigned, std::vector<TString>> hltMenus;

  TH1D* allEvents(0);
  TH1D* eventCounter(0);

  std::cout << "merging runs and counters" << std::endl;

  for (auto& path : sourcePaths) {
    auto* source(TFile::Open(path));
    auto* inRunTree(static_cast<TTree*>(source->Get("runs")));
    run.setAddress(*inRunTree);

    auto* inHLTTree(static_cast<TTree*>(source->Get("hlt")));
    if (inHLTTree) {
      if (!hltPaths)
        hltPaths = new std::vector<TString>;

      inHLTTree->SetBranchAddress("paths", &hltPaths);
    }

    iEntry = 0;
    while (inRunTree->GetEntry(iEntry++) > 0) {
      if (inHLTTree) {
        inHLTTree->GetEntry(run.hltMenu);

        auto hltItr(hltMenus.find(run.run));
        if (hltItr == hltMenus.end())
          hltMenus.emplace(run.run, *hltPaths);
        else if (hltItr->second != *hltPaths) {
          std::cerr << "Inconsistent HLT menu found for run " << run.run << " in file " << path << std::endl;
          throw std::runtime_error("HLT");
        }
      }
      else
        hltMenus.emplace(run.run, std::vector<TString>());
    }

    if (!allEvents) {
      outputFile->cd();
      allEvents = static_cast<TH1D*>(source->Get("hDAllEvents")->Clone());
    }
    else
      allEvents->Add(static_cast<TH1D*>(source->Get("hDAllEvents")));

    if (!eventCounter) {
      outputFile->cd();
      eventCounter = static_cast<TH1D*>(source->Get("counter")->Clone());
    }
    else
      eventCounter->Add(static_cast<TH1D*>(source->Get("counter")));

    delete source;
  }

  outputFile->cd();
  auto* outRunTree(new TTree("runs", "Runs"));
  run.book(*outRunTree);
  
  TTree* outHLTTree(0);
  if (hltPaths) {
    outHLTTree = new TTree("hlt", "HLT");
    outHLTTree->Branch("paths", "std::vector<TString>", &hltPaths);
  }

  unsigned iMenu(-1);
  if (hltPaths)
    hltPaths->clear();

  std::cout << "writing runs and HLT menus" << std::endl;

  for (auto& runHLT : hltMenus) {
    run.run = runHLT.first;

    if (hltPaths && runHLT.second != *hltPaths) {
      *hltPaths = runHLT.second;
      outHLTTree->Fill();
      ++iMenu;
    }

    run.hltMenu = iMenu;

    outRunTree->Fill();
  }

  outputFile->cd();
  outputFile->Write();
}
