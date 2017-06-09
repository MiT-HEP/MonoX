#include "PandaTree/Objects/interface/EventMonophoton.h"

#include "TH2D.h"
#include "TString.h"
#include "TChain.h"
#include "TBranch.h"
#include "TRandom3.h"
#include "TTree.h"
#include "TEntryList.h"
#include "TMath.h"

#include <vector>
#include <iostream>

class RandomConeIso {
public:
  RandomConeIso() {}
  ~RandomConeIso() {}

  void addPath(char const* p) { paths_.emplace_back(p); }
  TH1* run(int nEntries = -1, bool normalize = true);

private:
  std::vector<TString> paths_;
};

TH1*
RandomConeIso::run(int _nEntries/* = -1*/, bool _normalize/* = true*/)
{
  /*
    Throw eta-phi circles to Zmumu events where Z vertex is not PV post-lepton removal and add up the new PV ICH.
    With 10 circles, the probability of having overlapping ones is 50%.
  */

  auto* output(new TH2D("chIso", "", 100, -1.5, 1.5, 100, 0., 10.));

  panda::RecoVertexCollection vertices("vertices", 64);
  panda::PFCandCollection pfCandidates("pfCandidates", 1024);
  short ivtx;
  short ivtxNoL;

  TChain input("events");

  for (auto& p : paths_)
    input.Add(p);

  input.Draw(">>elist", "lvertex.idx != 0 || lvertex.idxNoL != 0", "entrylist");
  auto* elist(static_cast<TEntryList*>(gDirectory->Get("elist")));
  input.SetEntryList(elist);

  input.SetBranchStatus("*", false);
  vertices.setAddress(input, {"pfRangeMax"});
  pfCandidates.setAddress(input);
  input.SetBranchStatus("lvertex.idx", true);
  input.SetBranchAddress("lvertex.idx", &ivtx);
  input.SetBranchStatus("lvertex.idxNoL", true);
  input.SetBranchAddress("lvertex.idxNoL", &ivtxNoL);

  TRandom3 random;

  long iEntry(0);
  long entryNumber;
  while (iEntry != _nEntries && (entryNumber = input.GetEntryNumber(iEntry++)) >= 0) {
    if (iEntry % 100000 == 1)
      std::cout << iEntry << std::endl;

    int localEntry(input.LoadTree(entryNumber));
    if (localEntry < 0)
      break;

    pfCandidates.prepareGetEntry(input, entryNumber, localEntry);
    vertices.prepareGetEntry(input, entryNumber, localEntry);
    if (pfCandidates.getEntry(input, entryNumber) <= 0)
      break;

    if (vertices.empty())
      continue;

    unsigned iV(0);
    unsigned iPFMin(0);
    if (ivtx == 0) {
      if (vertices.size() == 1)
        continue;

      iV = 1;
      iPFMin = vertices[0].pfRangeMax;
    }

    std::vector<panda::PFCand const*> pfs;
    for (unsigned iPF(iPFMin); iPF != vertices[iV].pfRangeMax; ++iPF) {
      auto& pf(pfCandidates[iPF]);

      if (pf.ptype != panda::PFCand::hp && pf.ptype != panda::PFCand::hm)
        continue;

      pfs.push_back(&pf);
    }

    // throw toys
    std::vector<std::pair<double, double>> centers;
    for (unsigned iC(0); iC != 10; ++iC) {
      double eta(random.Uniform(-1.5, 1.5));
      double phi(random.Uniform(-TMath::Pi(), TMath::Pi()));

      bool overlap(false);
      for (auto& center : centers) {
        double dEta(center.first - eta);
        double dPhi(center.second - eta);

        if (dEta * dEta + dPhi * dPhi < 0.09) {
          overlap = true;
          break;
        }
      }

      if (overlap)
        continue;

      centers.emplace_back(eta, phi);

      double iso(0.);
      for (auto* pf : pfs) {
        double dEta(eta - pf->eta());
        double dPhi(eta - pf->phi());

        if (dEta * dEta + dPhi * dPhi < 0.09)
          iso += pf->pt();
      }

      output->Fill(eta, iso);
    }
  }

  if (_normalize) {
    for (int iX(1); iX <= output->GetNbinsX(); ++iX) {
      double sliceTotal(0.);
      for (int iY(1); iY <= output->GetNbinsY(); ++iY)
        sliceTotal += output->GetBinContent(iX, iY);

      for (int iY(1); iY <= output->GetNbinsY(); ++iY)
        output->SetBinContent(iX, iY, output->GetBinContent(iX, iY) / sliceTotal);
    }
  }

  return output;
}
