#include "TreeEntries_simpletree.h"

#include "TTree.h"
#include "TBranch.h"
#include "TEntryList.h"
#include "TDirectory.h"
#include "TString.h"

#include <vector>
#include <utility>
#include <iostream>

void
MonophotonTreeMaker(TTree* _input, TTree* _output, char const* _selection, bool _isData, bool _useReweights = true, double _prescale = 1.)
{
  simpletree::Event event;
  event.setAddress(*_input);

  std::vector<std::tuple<TString, void*, char>> branches;

  // branches to save
  if (_isData) {
    branches.emplace_back("run", &event.run, 'i');
    branches.emplace_back("lumi", &event.lumi, 'i');
    branches.emplace_back("event", &event.event, 'i');
  }

  branches.emplace_back("weight", &event.weight, 'D');
  branches.emplace_back("photonPt", event.photons.data.pt, 'F');
  branches.emplace_back("photonPhi", event.photons.data.phi, 'F');
  branches.emplace_back("met", &event.t1Met.met, 'F');

  // other reweight factors
  std::map<TString, double> reweights;
  if (_useReweights) {
    for (auto* branch : *_input->GetListOfBranches()) {
      TString bname(branch->GetName());
      if (bname.Index("reweight_") != 0)
        continue;

      double* rw(&reweights[bname]);
      static_cast<TBranch*>(branch)->SetAddress(rw);
      branches.emplace_back(bname, rw, 'D');
    }
  }

  // set reweight to 1 if the output tree has a branch that is not in the input
  for (auto* branch : *_output->GetListOfBranches()) {
    TString bname(branch->GetName());
    if (bname.Index("reweight_") != 0)
      continue;

    if (reweights.find(bname) == reweights.end()) {
      reweights[bname] = 1.;
      branches.emplace_back(bname, &reweights[bname], 'D');
    }
  }

  for (auto& br : branches) {
    if (_output->GetBranch(std::get<0>(br)))
      _output->SetBranchAddress(std::get<0>(br), std::get<1>(br));
    else
      _output->Branch(std::get<0>(br), std::get<1>(br), std::get<0>(br) + '/' + std::get<2>(br));
  }

  if (_input->GetEntries() == 0)
    return;

  // apply selection to input
  _input->Draw(">>elist", _selection, "entrylist");
  auto* elist(static_cast<TEntryList*>(gDirectory->Get("elist")));
  
  _input->SetEntryList(elist);

  long iListEntry(0);
  long iTreeEntry(-1);
  while ((iTreeEntry = _input->GetEntryNumber(iListEntry++)) >= 0) {
    _input->GetEntry(iTreeEntry);

    event.weight /= _prescale;
    if (_useReweights) {
      for (auto& rw : reweights)
        rw.second /= _prescale;
    }

    _output->Fill();
  }
}
