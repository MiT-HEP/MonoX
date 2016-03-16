#include "TTree.h"
#include "TEntryList.h"
#include "TDirectory.h"

#include <cstring>

void
metTree(TTree* _input, TTree* _output, char const* _selection = 0, double _addWeight = 1.)
{
  float met;
  double weight;

  if (!_output->GetBranch("met")) {
    _output->Branch("met", &met, "met/F");
    _output->Branch("weight", &weight, "weight/D");
  }
  else {
    _output->SetBranchAddress("met", &met);
    _output->SetBranchAddress("weight", &weight);
  }

  _input->SetBranchStatus("t1Met.met", 1);
  _input->SetBranchStatus("weight", 1);
  _input->SetBranchAddress("t1Met.met", &met);
  _input->SetBranchAddress("weight", &weight);

  if (_selection && std::strlen(_selection) != 0) {
    _input->Draw(">>elist", _selection, "entrylist");
    auto* elist(static_cast<TEntryList*>(gDirectory->Get("elist")));
    _input->SetEntryList(elist);
  }

  long iEntry(0);
  long iTreeEntry(0);
  while ((iTreeEntry = _input->GetEntryNumber(iEntry++)) >= 0) {
    // if (iEntry % 10 != 0)
    //   continue;

    _input->GetEntry(iTreeEntry);
    weight *= _addWeight;
    _output->Fill();
  }

  _input->SetEntryList(0);
}
