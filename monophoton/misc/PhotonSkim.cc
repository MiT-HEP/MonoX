#include "TreeEntries_simpletree.h"
#include "SimpleTreeUtils.h"

#include "GoodLumiFilter.h"

#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TSystem.h"
#include "TH1D.h"
#include "TKey.h"

#include <vector>
#include <map>
#include <iostream>
#include <stdexcept>
#include <cstring>

// fix for simpletree18 bug (latest cycle not necessarily the biggest tree)
TTree*
getLongestTree(TFile* _source, char const* _name)
{
  TTree* longestTree(0);
  
  auto* keys(_source->GetListOfKeys());
  for (auto* keyObj : *keys) {
    auto* key(static_cast<TKey*>(keyObj));
    if (std::strcmp(key->GetName(), _name) != 0)
      continue;

    auto* tree(static_cast<TTree*>(key->ReadObj()));

    if (!longestTree || tree->GetEntries() > longestTree->GetEntries()) {
      delete longestTree;
      longestTree = tree;
    }
    else
      delete tree;
  }

  return longestTree;
}

void
PhotonSkim(char const* _sourceDir, char const* _outputPath, long _nEvents = -1, GoodLumiFilter* _goodlumi = 0)
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
  TTree* outEventTree(0);
  TH1D* allEvents(0);
  TH1D* eventCounter(0);

  simpletree::Event event;

  simpletree::TriggerHelper hltPhoton165HE10Helper("HLT_Photon165_HE10");
  bool hltPhoton165HE10(false);

  simpletree::Run run;
  std::vector<TString>* hltPaths(0);
  std::map<unsigned, std::vector<TString>> hltMenus;

  auto pass([&event]()->bool {
      for (auto& photon : event.photons) {
        if (photon.isEB && photon.pt > 175.)
          return true;
      }
      return false;
    });

  std::cout << "skimming events" << std::endl;

  long nTotal(0);
  long nPass(0);

  for (auto& path : sourcePaths) {
    auto* source(TFile::Open(path));

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

    TTree* inEventTree(getLongestTree(source, "events"));

    TTree* inRunTree(getLongestTree(source, "runs"));
    run.setAddress(*inRunTree);

    TTree* inHLTTree(getLongestTree(source, "hlt"));
    if (inHLTTree) {
      if (!hltPaths)
        hltPaths = new std::vector<TString>;

      inHLTTree->SetBranchAddress("paths", &hltPaths);
    }

    if (!outEventTree) {
      outputFile->cd();
      outEventTree = inEventTree->CloneTree(0);

      // event branch addresses are copied through CloneTree
      outEventTree->Branch("hlt.photon165HE10", &hltPhoton165HE10, "photon165HE10/O");
    }

    event.setAddress(*outEventTree);
    event.setAddress(*inEventTree, {"photons.matchL1", "partons.pid", "promptFinalStates.ancestor"}, false);

    if (inHLTTree)
      hltPhoton165HE10Helper.reset();

    long iEntry(0);
    while (nTotal != _nEvents && inEventTree->GetEntry(iEntry++) > 0) {
      ++nTotal;
      if (nTotal % 100000 == 1)
        std::cout << " " << nTotal << std::endl;

      if (_goodlumi && !_goodlumi->isGoodLumi(event.run, event.lumi))
        continue;

      if (pass()) {
        ++nPass;
        if (inHLTTree)
          hltPhoton165HE10 = hltPhoton165HE10Helper.pass(event);
        outEventTree->Fill();
      }
    }

    iEntry = 0;
    while (inRunTree->GetEntry(iEntry++) > 0) {
      if (_goodlumi && !_goodlumi->hasGoodLumi(run.run))
        continue;

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
        hltMenus[run.run];
    }

    delete source;
  }

  std::cout << "Event reduction: " << nPass << " / " << nTotal << std::endl;

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
